#!/usr/bin/env python3
"""Generate production SVGs from diagram briefs, safe-trim, score; optional guarded refine."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MODULE = Path(__file__).resolve().parent
DIAGRAMS = ROOT / "docs/course/agentic-ai-langflow/module-01/diagrams"
ADV = ROOT / "examples/figtree/langflow/adversarial"
sys.path.insert(0, str(ADV))
from compact_trim import components_in_svg, trim_teaching_canvas  # noqa: E402


def expected_components(md: Path) -> set[str]:
    found: set[str] = set()
    for line in md.read_text(encoding="utf-8").splitlines():
        if "->" not in line:
            continue
        for part in re.split(r"\s*->\s*", line.strip()):
            name = part.strip()
            if name:
                found.add(name)
    return found


def score(svg: Path, source: Path) -> dict:
    cp = subprocess.run(
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
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr or cp.stdout)
    return json.loads(cp.stdout)


def generate_one(src: Path, out: Path) -> None:
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "figtree",
            "generate",
            str(src),
            "-o",
            str(out),
            "--style",
            "teaching",
            "--icons",
            "--shapes",
            "--no-render",
        ],
        cwd=ROOT,
    )


def maybe_refine(src: Path, out: Path, exp: set[str], baseline: str) -> None:
    """Refine only if it keeps all expected components."""
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "figtree",
            "refine",
            str(out),
            "--rubric",
            "teaching",
            "-o",
            str(out),
            "--source",
            str(src),
            "--rounds",
            "2",
            "--no-render",
        ],
        cwd=ROOT,
    )
    refined = out.read_text(encoding="utf-8")
    if exp and not exp.issubset(components_in_svg(refined)):
        out.write_text(baseline, encoding="utf-8")


def main() -> int:
    manifest = json.loads((MODULE / "manifest.json").read_text(encoding="utf-8"))
    refine = "--refine" in sys.argv
    for fig in manifest["figures"]:
        fid = fig["id"]
        src = DIAGRAMS / f"{fid}.md"
        out = MODULE / f"{fid}.svg"
        if not src.exists():
            continue
        generate_one(src, out)
        baseline = out.read_text(encoding="utf-8")
        exp = expected_components(src)
        if refine:
            maybe_refine(src, out, exp, baseline)
        text = out.read_text(encoding="utf-8")
        trimmed = trim_teaching_canvas(text)
        if not exp or exp.issubset(components_in_svg(trimmed)):
            out.write_text(trimmed, encoding="utf-8")
        s = score(out, src)
        (MODULE / f"{fid}.score.json").write_text(json.dumps(s, indent=2) + "\n", encoding="utf-8")
        print(f"  {fid:16s} {s['overall']:5.2f}  {len(s.get('issues', []))} issues  comps={len(components_in_svg(out.read_text()))}")
    audit = ROOT / "examples/course/agentic-ai-langflow/scripts/figure_ascii_audit.py"
    subprocess.check_call([sys.executable, str(audit)], cwd=ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
