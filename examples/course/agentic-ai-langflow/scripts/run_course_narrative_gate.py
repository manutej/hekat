#!/usr/bin/env python3
"""CI gate: Pursuit references pass; lab SVGs may fail vs Pursuit (documented gap)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from figure_richness import metrics_from_path, pursuit_gate  # noqa: E402
from figure_tiers import resolve  # noqa: E402

PURSUIT_MANIFEST = ROOT / "examples/figtree/langflow/pursuit/module-01/manifest.json"
COURSE_MANIFEST = ROOT / "examples/course/agentic-ai-langflow/module-01/manifest.json"
DIAGRAMS = ROOT / "docs/course/agentic-ai-langflow/module-01/diagrams"


def score_narrative(svg: Path, source: Path) -> float:
    cp = subprocess.run(
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
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr or cp.stdout)
    return float(json.loads(cp.stdout)["overall"])


def main() -> int:
    pursuit = json.loads(PURSUIT_MANIFEST.read_text(encoding="utf-8"))
    course = json.loads(COURSE_MANIFEST.read_text(encoding="utf-8"))
    course_ids = {f["id"] for f in course["figures"]}
    report: list[dict] = []
    ok = True

    for row in pursuit["figures"]:
        cid = row.get("course_id")
        if not cid or cid not in course_ids:
            continue
        ref = resolve(cid, "pursuit")
        lab = resolve(cid, "production")
        src = DIAGRAMS / f"{cid}.md"
        if ref is None or lab is None or not src.exists():
            ok = False
            report.append({"course_id": cid, "error": "missing paths"})
            continue

        ref_gate = pursuit_gate(ref, ref)
        lab_gate = pursuit_gate(ref, lab, same_file_is_pass=False)
        try:
            ref_score = score_narrative(ref, src)
            lab_score = score_narrative(lab, src)
        except RuntimeError as exc:
            ok = False
            report.append({"course_id": cid, "error": str(exc)[:200]})
            continue

        row_out = {
            "course_id": cid,
            "pursuit_self_gate": ref_gate.ok,
            "pursuit_narrative_score": ref_score,
            "lab_pursuit_gate": lab_gate.ok,
            "lab_narrative_score": lab_score,
            "lab_gate_reasons": lab_gate.reasons,
            "lab_ratios": lab_gate.ratios,
        }
        report.append(row_out)
        if not ref_gate.ok or ref_score < 8.0:
            ok = False
            print(f"FAIL {cid}: Pursuit reference invalid (gate={ref_gate.ok} score={ref_score:.2f})")
        else:
            print(
                f"OK   {cid}: Pursuit score={ref_score:.2f}  "
                f"lab gate={'pass' if lab_gate.ok else 'expected-fail'} lab score={lab_score:.2f}"
            )

    out_path = ROOT / "examples/course/agentic-ai-langflow/module-01/narrative-gate.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
