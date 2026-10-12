"""Pursuit references must pass course-narrative scoring."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "examples/course/agentic-ai-langflow/scripts/run_course_narrative_gate.py"
REPORT = ROOT / "examples/course/agentic-ai-langflow/module-01/narrative-gate.json"


def test_pursuit_references_pass_narrative_gate() -> None:
    cp = subprocess.run([sys.executable, str(GATE)], cwd=ROOT, capture_output=True, text=True)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report, "empty narrative gate report"
    for row in report:
        assert "error" not in row, row
        assert row["pursuit_self_gate"] is True, row
        assert row["pursuit_narrative_score"] >= 8.0, row
        ref_h = row["lab_ratios"]  # ratios only; use gate reasons for tall Pursuit art
        if row.get("lab_gate_reasons") and any("height ratio" in r for r in row["lab_gate_reasons"]):
            assert row["lab_pursuit_gate"] is False, row
