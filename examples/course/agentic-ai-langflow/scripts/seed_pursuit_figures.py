#!/usr/bin/env python3
"""Seed Pursuit Module 1 reference figures from course HTML gold (and hero journey)."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
COURSE = Path(__file__).resolve().parents[1]
HTML = COURSE / "Agentic_AI_with_Langflow.html"
GOLD = COURSE / "module-01/gold"
PURSUIT = ROOT / "examples/figtree/langflow/pursuit/module-01/figures"
PURSUIT_MANIFEST = ROOT / "examples/figtree/langflow/pursuit/module-01/manifest.json"

# course_id -> pursuit filename
def sanitize_svg(text: str) -> str:
    """Fix HTML-isms that break XML parsers (e.g. boolean ``hidden`` on title)."""
    return text.replace("<title hidden>", '<title id="figtree-hidden-title">')


FROM_GOLD = {
    "m1a": "02-script-or-agent.svg",
    "m1b": "03-four-parts-real-contents.svg",
    "m1c": "04-where-the-key-lives.svg",
    "m1d": "05-one-question-four-beats.svg",
    "m1e": "06-what-a-good-answer-looks-like.svg",
    "m1-capstone": "07-capstone-member-benefits-faq.svg",
}


def extract_svg_after(text: str, marker: str) -> str:
    pos = text.find(marker)
    if pos < 0:
        return ""
    i = text.find("<svg", pos)
    if i < 0:
        return ""
    depth = 0
    j = i
    while j < len(text):
        if text.startswith("<svg", j):
            depth += 1
            j += 4
            continue
        if text.startswith("</svg>", j):
            depth -= 1
            j += 6
            if depth == 0:
                return text[i:j]
            continue
        j += 1
    return ""


def main() -> int:
    PURSUIT.mkdir(parents=True, exist_ok=True)
    for cid, name in FROM_GOLD.items():
        src = GOLD / f"{cid}.svg"
        if not src.exists():
            print(f"skip missing gold {src}", file=sys.stderr)
            continue
        dst = PURSUIT / name
        dst.write_text(sanitize_svg(src.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"copied {src.name} -> figures/{name}")

    html = HTML.read_text(encoding="utf-8")
    journey = extract_svg_after(html, 'class="hero-figure"')
    if journey:
        journey = sanitize_svg(journey)
        (PURSUIT / "01-six-module-journey.svg").write_text(
            journey if journey.endswith("\n") else journey + "\n",
            encoding="utf-8",
        )
        print("extracted hero -> figures/01-six-module-journey.svg")
    else:
        print("warning: hero journey SVG not found in HTML", file=sys.stderr)

    if PURSUIT_MANIFEST.exists():
        print(f"manifest: {PURSUIT_MANIFEST.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
