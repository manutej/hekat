#!/usr/bin/env python3
"""Three-layer adversarial pass for a FigTree module directory.

Each ``*.svg`` in ``module_dir`` is scored against the matching
``diagrams/<stem>.md`` source (or an explicit map). Refined SVGs replace
the originals in place; logs go to ``module_dir/adversarial/``.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from compact_trim import trim_teaching_canvas  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]


@dataclass
class Figure:
    stem: str
    svg: Path
    source: Path


def discover(module_dir: Path, diagrams_dir: Path) -> List[Figure]:
    figures: List[Figure] = []
    for svg in sorted(module_dir.glob("*.svg")):
        if svg.stem == "overview":
            seconds = sorted(diagrams_dir.glob("02-*.md"))
            src = seconds[0] if seconds else diagrams_dir / "02-minimal-chat-flow.md"
        else:
            src = diagrams_dir / f"{svg.stem}.md"
        if not src.exists():
            continue
        figures.append(Figure(stem=svg.stem, svg=svg, source=src))
    return figures


def run(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


def score(svg: Path, source: Path) -> Dict[str, Any]:
    cp = run(
        [
            sys.executable,
            "-m",
            "figtree",
            "score",
            str(svg),
            "--rubric",
            "teaching",
            "--source",
            str(source),
            "--json",
        ]
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr or cp.stdout)
    return json.loads(cp.stdout)


def refine(svg: Path, source: Path, out: Path, rounds: int = 3) -> Dict[str, Any]:
    traj = out.parent / "adversarial" / f"{svg.stem}.trajectory.json"
    traj.parent.mkdir(parents=True, exist_ok=True)
    cp = run(
        [
            sys.executable,
            "-m",
            "figtree",
            "refine",
            str(svg),
            "--rubric",
            "teaching",
            "-o",
            str(out),
            "--trajectory",
            str(traj),
            "--source",
            str(source),
            "--rounds",
            str(rounds),
            "--no-render",
        ]
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr or cp.stdout)
    return score(out, source)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: run_module_adversarial.py MODULE_DIR [DIAGRAMS_DIR]", file=sys.stderr)
        return 2
    module_dir = (ROOT / sys.argv[1]).resolve()
    diagrams_dir = (
        (ROOT / sys.argv[2]).resolve()
        if len(sys.argv) > 2
        else module_dir.parent.parent.parent / "docs/research/langflow-agentic-workflows/modules/01-flow-topology/diagrams"
    )
    # fix diagrams path when module_dir is under examples
    if not diagrams_dir.exists():
        mod_id = module_dir.name
        diagrams_dir = ROOT / "docs/research/langflow-agentic-workflows/modules" / mod_id / "diagrams"

    adv = module_dir / "adversarial"
    adv.mkdir(parents=True, exist_ok=True)
    figures = discover(module_dir, diagrams_dir)
    if not figures:
        print(f"no figures in {module_dir}", file=sys.stderr)
        return 1

    layer1: List[Dict[str, Any]] = []
    print("=== Layer 1: attack (score with source) ===")
    for fig in figures:
        s = score(fig.svg, fig.source)
        row = {"stem": fig.stem, "overall": s["overall"], "issues": s.get("issues", [])}
        layer1.append(row)
        print(f"  {fig.stem:40s} {s['overall']:5.2f}  {len(s.get('issues', []))} issues")

    layer2: List[Dict[str, Any]] = []
    print("\n=== Layer 2: refine (3 rounds) ===")
    for fig in figures:
        before = next(r for r in layer1 if r["stem"] == fig.stem)["overall"]
        tmp = adv / f"{fig.stem}.refined.svg"
        try:
            after_s = refine(fig.svg, fig.source, tmp, rounds=3)
            svg_text = tmp.read_text(encoding="utf-8")
            if any(i.get("check_id") == "compactness.blank_margin" for i in after_s.get("issues", [])):
                svg_text = trim_teaching_canvas(svg_text)
                tmp.write_text(svg_text, encoding="utf-8")
                after_s = score(tmp, fig.source)
            after = after_s["overall"]
            fig.svg.write_text(svg_text, encoding="utf-8")
            (module_dir / f"{fig.stem}.score.json").write_text(json.dumps(after_s, indent=2), encoding="utf-8")
            layer2.append({"stem": fig.stem, "before": before, "after": after})
            print(f"  {fig.stem:40s} {before:5.2f} -> {after:5.2f}")
        except RuntimeError as exc:
            layer2.append({"stem": fig.stem, "before": before, "error": str(exc)[:200]})
            print(f"  {fig.stem:40s} FAILED")

    layer3: List[Dict[str, Any]] = []
    print("\n=== Layer 3: verify ===")
    for fig in figures:
        s = score(fig.svg, fig.source)
        layer3.append({"stem": fig.stem, "overall": s["overall"], "issues": len(s.get("issues", []))})
        print(f"  {fig.stem:40s} {s['overall']:5.2f}  {len(s.get('issues', []))} issues")

    summary = {"layer1": layer1, "layer2": layer2, "layer3": layer3}
    (adv / "three-layer-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    iteration = adv / "ITERATION-LOG.md"
    lines = [
        "# Adversarial iteration log",
        "",
        "| Figure | L1 | L3 |",
        "|--------|----|----|",
    ]
    for r1, r3 in zip(layer1, layer3):
        l2 = next((x for x in layer2 if x["stem"] == r1["stem"]), {})
        mid = l2.get("after", "—")
        lines.append(f"| {r1['stem']} | {r1['overall']:.2f} | {r3['overall']:.2f} |")
    iteration.write_text("\n".join(lines) + "\n", encoding="utf-8")

    build = module_dir / "build_index.py"
    if build.exists():
        run([sys.executable, str(build)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
