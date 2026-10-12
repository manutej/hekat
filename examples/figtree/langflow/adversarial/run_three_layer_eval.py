#!/usr/bin/env python3
"""Three-layer adversarial evaluation for Langflow FigTree figures.

Layer 1 — Attack: score each production SVG with source; record issues as probe briefs.
Layer 2 — Repair: figtree refine up to 3 rounds per figure (--no-render for speed).
Layer 3 — Verify: re-score, write eval report and iteration log.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[4]
LANGFLOW = ROOT / "examples" / "figtree" / "langflow"
ADV = LANGFLOW / "adversarial"
PROBES = ROOT / "examples" / "figtree" / "probes" / "langflow-teaching"


@dataclass
class Unit:
    svg: Path
    source: Path
    unit_id: str


def units() -> List[Unit]:
    mapping = {
        "research-workflow.svg": ROOT / "docs/research/langflow-agentic-workflows/RESEARCH-WORKFLOW.md",
    }
    default_src = ROOT / "docs/research/langflow-agentic-workflows/SOURCE.md"
    out: List[Unit] = []
    for svg in sorted(LANGFLOW.glob("*.svg")):
        if "refined" in svg.name:
            continue
        src = mapping.get(svg.name, default_src)
        out.append(Unit(svg=svg, source=src, unit_id=svg.stem))
    return out


def run(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


def score_unit(u: Unit) -> Dict[str, Any]:
    report = ADV / f"{u.unit_id}.score.json"
    cp = run(
        [
            sys.executable,
            "-m",
            "figtree",
            "score",
            str(u.svg),
            "--rubric",
            "teaching",
            "--source",
            str(u.source),
            "--json",
        ]
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr or cp.stdout)
    data = json.loads(cp.stdout)
    report.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def refine_unit(u: Unit, rounds: int = 3) -> Dict[str, Any]:
    out_svg = ADV / f"{u.unit_id}.layer2.svg"
    traj = ADV / f"{u.unit_id}.layer2.trajectory.json"
    cp = run(
        [
            sys.executable,
            "-m",
            "figtree",
            "refine",
            str(u.svg),
            "--rubric",
            "teaching",
            "-o",
            str(out_svg),
            "--trajectory",
            str(traj),
            "--source",
            str(u.source),
            "--rounds",
            str(rounds),
            "--no-render",
        ]
    )
    print(cp.stdout)
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr or cp.stdout)
    after = score_path(out_svg, u.source)
    return {"output": str(out_svg), "trajectory": str(traj), "score": after}


def score_path(svg: Path, source: Path) -> Dict[str, Any]:
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
    return json.loads(cp.stdout)


def layer1_attack(rows: List[Dict[str, Any]]) -> None:
    PROBES.mkdir(parents=True, exist_ok=True)
    for row in rows:
        for issue in row.get("issues", [])[:3]:
            slug = f"langflow-{row['id']}-{issue.get('check_id', 'issue').replace('.', '-')}"
            brief = {
                "id": f"langflow-teaching.{slug}",
                "rubric": "teaching",
                "kind": "defect",
                "expect_fire": [issue.get("check_id", "unknown")],
                "expect_silent": [],
                "rationale": f"Production figure {row['id']}: {issue.get('fix', issue.get('message', ''))[:160]}",
                "source": "adversary-langflow-layer1",
                "production_svg": row["svg"],
            }
            (PROBES / f"{slug}.json").write_text(json.dumps(brief, indent=2), encoding="utf-8")


def main() -> int:
    ADV.mkdir(parents=True, exist_ok=True)
    layer1: List[Dict[str, Any]] = []
    print("=== Layer 1: adversarial score (attack) ===")
    for u in units():
        s = score_unit(u)
        row = {
            "id": u.unit_id,
            "svg": str(u.svg),
            "source": str(u.source),
            "overall": s.get("overall"),
            "issues": s.get("issues", []),
            "requests": s.get("requests", []),
        }
        layer1.append(row)
        print(f"  {u.unit_id:45s} {s.get('overall'):5.2f}  {len(s.get('issues', []))} issues")

    layer1_attack(layer1)
    (ADV / "layer1-attack.json").write_text(json.dumps(layer1, indent=2), encoding="utf-8")

    print("\n=== Layer 2: refine (3 rounds) ===")
    layer2: List[Dict[str, Any]] = []
    for u in units():
        before = next(r for r in layer1 if r["id"] == u.unit_id)["overall"]
        try:
            result = refine_unit(u, rounds=3)
            after = result["score"].get("overall")
            layer2.append(
                {
                    "id": u.unit_id,
                    "before": before,
                    "after": after,
                    "output": result["output"],
                    "delta": (after or 0) - (before or 0),
                }
            )
            print(f"  {u.unit_id:45s} {before:5.2f} -> {after:5.2f}")
        except RuntimeError as exc:
            layer2.append({"id": u.unit_id, "before": before, "error": str(exc)[:200]})
            print(f"  {u.unit_id:45s} FAILED")

    (ADV / "layer2-refine.json").write_text(json.dumps(layer2, indent=2), encoding="utf-8")

    print("\n=== Layer 3: verify + promote ===")
    layer3: List[Dict[str, Any]] = []
    for entry in layer2:
        if "error" in entry:
            continue
        out = Path(entry["output"])
        u = next(x for x in units() if x.unit_id == entry["id"])
        final_score = score_path(out, u.source)
        promoted = LANGFLOW / f"{entry['id']}.svg"
        promoted.write_text(out.read_text(encoding="utf-8"), encoding="utf-8")
        layer3.append(
            {
                "id": entry["id"],
                "promoted_to": str(promoted),
                "overall": final_score.get("overall"),
                "issues": len(final_score.get("issues", [])),
            }
        )
        print(f"  promoted {entry['id']:40s} -> {final_score.get('overall'):5.2f}")

    eval_before = ADV / "teaching-eval-layer0.json"
    eval_after = ADV / "teaching-eval-layer3.json"
    run([sys.executable, "-m", "figtree", "eval", "--rubric", "teaching", "--report", str(eval_before)])
    run([sys.executable, "-m", "figtree", "eval", "--rubric", "teaching", "--report", str(eval_after)])

    summary = {
        "layer1": layer1,
        "layer2": layer2,
        "layer3": layer3,
        "eval_before": json.loads(eval_before.read_text()) if eval_before.exists() else None,
        "eval_after": json.loads(eval_after.read_text()) if eval_after.exists() else None,
    }
    (ADV / "three-layer-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
