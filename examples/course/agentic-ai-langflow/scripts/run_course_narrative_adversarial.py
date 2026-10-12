#!/usr/bin/env python3
"""Score Module 1 figures on course-narrative rubric; optional refine on lab tier."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = Path(__file__).resolve().parent
MODULE = ROOT / "examples/course/agentic-ai-langflow/module-01"
DIAGRAMS = ROOT / "docs/course/agentic-ai-langflow/module-01/diagrams"
ADV = MODULE / "adversarial" / "narrative"
sys.path.insert(0, str(SCRIPTS))

from figure_richness import pursuit_gate  # noqa: E402
from figure_tiers import resolve  # noqa: E402


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


def score(svg: Path, source: Path) -> dict:
    cp = run(
        [
            sys.executable,
            "-m",
            "figtree",
            "score",
            str(svg),
            "--rubric",
            "course-narrative",
            "--source",
            str(source),
            "--json",
        ]
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr or cp.stdout)
    return json.loads(cp.stdout)


def main() -> int:
    refine = "--refine" in sys.argv
    manifest = json.loads((MODULE / "manifest.json").read_text(encoding="utf-8"))
    ADV.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []

    for fig in manifest["figures"]:
        cid = fig["id"]
        src = DIAGRAMS / f"{cid}.md"
        purs = resolve(cid, "pursuit")
        lab = resolve(cid, "production")
        if not src.exists() or purs is None or lab is None:
            continue
        purs_s = score(purs, src)
        lab_s = score(lab, src)
        gate = pursuit_gate(purs, lab, same_file_is_pass=False)
        row = {
            "id": cid,
            "pursuit_overall": purs_s["overall"],
            "lab_overall": lab_s["overall"],
            "pursuit_gate_ok": gate.ok,
            "gate_reasons": gate.reasons,
        }
        if refine:
            out = ADV / f"{cid}.refined.svg"
            cp = run(
                [
                    sys.executable,
                    "-m",
                    "figtree",
                    "refine",
                    str(lab),
                    "--rubric",
                    "course-narrative",
                    "-o",
                    str(out),
                    "--source",
                    str(src),
                    "--rounds",
                    "2",
                    "--no-render",
                ]
            )
            if cp.returncode == 0 and out.exists():
                row["refined_overall"] = score(out, src)["overall"]
                row["refined_gate"] = pursuit_gate(purs, out, same_file_is_pass=False).ok
        rows.append(row)
        print(
            f"  {cid:14s} pursuit {purs_s['overall']:5.2f}  lab {lab_s['overall']:5.2f}  "
            f"gate={'ok' if gate.ok else 'gap'}"
        )

    (ADV / "summary.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
