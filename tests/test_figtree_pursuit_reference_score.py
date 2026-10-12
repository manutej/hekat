"""figtree score --reference adds Pursuit richness gaps for lab SVGs."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_lab_m1b_scores_lower_with_pursuit_reference() -> None:
    lab = ROOT / "examples/course/agentic-ai-langflow/module-01/m1b.svg"
    ref = ROOT / "examples/figtree/langflow/pursuit/module-01/figures/03-four-parts-real-contents.svg"
    src = ROOT / "docs/course/agentic-ai-langflow/module-01/diagrams/m1b.md"
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "figtree",
            "score",
            str(lab),
            "--rubric",
            "course-narrative",
            "--source",
            str(src),
            "--reference",
            str(ref),
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert cp.returncode == 0, cp.stderr
    report = json.loads(cp.stdout)
    ids = {i["check_id"] for i in report.get("issues", [])}
    assert "narrative.ref_height" in ids or "narrative.ref_annot" in ids
