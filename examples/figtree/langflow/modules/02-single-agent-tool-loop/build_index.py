#!/usr/bin/env python3
"""Build module 02 gallery index from diagram SVGs."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TITLES = {
    "overview": "Overview — tool loop hub",
    "01-tool-attachment": "Tool attachment workflow",
    "02-tool-loop-hub": "Single-agent tool loop",
    "03-playground-events": "Playground run events",
}


def main() -> None:
    cards = []
    order = ["overview", "01-tool-attachment", "02-tool-loop-hub", "03-playground-events"]
    for stem in order:
        svg_path = ROOT / f"{stem}.svg"
        if not svg_path.exists():
            continue
        score_path = ROOT / f"{stem}.score.json"
        overall = "—"
        if score_path.exists():
            overall = f"{json.loads(score_path.read_text())['overall']:.2f}"
        svg = svg_path.read_text(encoding="utf-8")
        title = TITLES.get(stem, stem)
        cards.append(
            f'<section class="card"><h2>{html.escape(title)}</h2>'
            f'<p class="meta">Score: <span class="score">{overall}</span></p>'
            f'<div class="fig">{svg}</div></section>'
        )
    page = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>Module 02 — Single-agent tool loop</title>"
        "<style>body{font-family:'IBM Plex Sans',system-ui,sans-serif;max-width:960px;margin:32px auto;padding:0 16px;color:#2B3A4A}"
        "h1{font-size:1.4rem}.lead{color:#555}.card{border:1px solid #D5D5D5;border-radius:6px;padding:16px;margin:20px 0}"
        ".meta{font-size:0.85rem;color:#666}.score{font-weight:bold;color:#4F7F3A}"
        ".fig svg{max-width:100%;height:auto;display:block}a{color:#2563eb}</style></head><body>"
        "<h1>Module 02 — Single-agent tool loop</h1>"
        "<p class='lead'>Teaching figures for tool registration and Playground events. "
        "<a href='../../index.html'>Back to Langflow gallery</a> · "
        "<a href='../../../../docs/research/langflow-agentic-workflows/modules/02-single-agent-tool-loop/diagrams/'>diagram sources</a></p>"
        + "".join(cards)
        + "</body></html>"
    )
    (ROOT / "index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
