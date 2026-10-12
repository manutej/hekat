"""Course Module 1 manifest and diagram briefs stay in sync."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "examples/course/agentic-ai-langflow/module-01"
DIAGRAMS = ROOT / "docs/course/agentic-ai-langflow/module-01/diagrams"


def test_manifest_figures_have_briefs_and_svgs() -> None:
    manifest = json.loads((MODULE / "manifest.json").read_text(encoding="utf-8"))
    for fig in manifest["figures"]:
        fid = fig["id"]
        assert (DIAGRAMS / f"{fid}.md").exists(), fid
        assert (MODULE / f"{fid}.svg").exists(), fid
        assert (MODULE / "gold" / f"{fid}.svg").exists(), fid
