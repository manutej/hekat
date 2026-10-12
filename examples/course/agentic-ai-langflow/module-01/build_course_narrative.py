#!/usr/bin/env python3
"""Orchestrate course narrative pipeline: Pursuit bar, gates, preview."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MODULE = Path(__file__).resolve().parent
SCRIPTS = ROOT / "examples/course/agentic-ai-langflow/scripts"


def run(script: str, *args: str) -> None:
    subprocess.check_call([sys.executable, str(SCRIPTS / script), *args], cwd=ROOT)


def main() -> int:
    print("=== 1/4 Seed Pursuit reference figures (gold + hero) ===")
    run("seed_pursuit_figures.py")
    print("\n=== 2/5 Lab figures (teaching topology harness) ===")
    subprocess.check_call([sys.executable, str(MODULE / "build_figures.py")], cwd=ROOT)
    print("\n=== 3/5 Narrative candidates (Pursuit + generate/refine pilots) ===")
    subprocess.check_call([sys.executable, str(MODULE / "build_narrative_figures.py")], cwd=ROOT)
    print("\n=== 4/5 Narrative gate (Pursuit refs + lab gap report) ===")
    run("run_course_narrative_gate.py")
    print("\n=== 5/5 Preview HTML (narrative tier) ===")
    subprocess.check_call(
        [sys.executable, str(MODULE / "build_module_html.py"), "--tier", "narrative"],
        cwd=ROOT,
    )
    print("\nDone. See module-01/narrative-gate.json and docs/.../COURSE-NARRATIVE-STRATEGY.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
