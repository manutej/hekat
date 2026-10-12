"""Module 1 figures: topology (ASCII audit) and canvas fit."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "examples/course/agentic-ai-langflow/scripts/figure_ascii_audit.py"
REPORT = ROOT / "examples/course/agentic-ai-langflow/module-01/ascii-audit.json"


def test_ascii_topology_and_canvas() -> None:
    cp = subprocess.run([sys.executable, str(AUDIT)], cwd=ROOT, capture_output=True, text=True)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    for row in report:
        assert not row["missing"], row
        canvas = row["canvas"]
        assert not canvas["clipped"], row
        assert canvas["margin_ok"], row
