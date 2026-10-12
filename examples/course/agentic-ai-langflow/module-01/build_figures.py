#!/usr/bin/env python3
"""Generate production SVGs from diagram briefs, refine, trim, and score."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MODULE = Path(__file__).resolve().parent
GOLD = MODULE / "gold"
DIAGRAMS = ROOT / "docs/course/agentic-ai-langflow/module-01/diagrams"
ADV = ROOT / "examples/figtree/langflow/adversarial"
sys.path.insert(0, str(ADV))
from compact_trim import trim_teaching_canvas  # noqa: E402


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


def main() -> int:
    manifest = json.loads((MODULE / "manifest.json").read_text(encoding="utf-8"))
    for fig in manifest["figures"]:
        fid = fig["id"]
        gold = GOLD / f"{fid}.svg"
        out = MODULE / f"{fid}.svg"
        src = DIAGRAMS / f"{fid}.md"
        if not src.exists():
            print(f"skip missing brief {fid}")
            continue
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
                "3",
                "--no-render",
            ],
            cwd=ROOT,
        )
        out.write_text(trim_teaching_canvas(out.read_text(encoding="utf-8")), encoding="utf-8")
        if src.exists():
            s = score(out, src)
            (MODULE / f"{fid}.score.json").write_text(json.dumps(s, indent=2) + "\n", encoding="utf-8")
            print(f"  {fid:16s} {s['overall']:5.2f}  {len(s.get('issues', []))} issues")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
