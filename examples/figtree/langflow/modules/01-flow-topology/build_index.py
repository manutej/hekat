#!/usr/bin/env python3
"""Build module 01 gallery index from diagram SVGs."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TITLES = {
    "overview": "Overview — minimal chat flow",
    "01-flow-canvas": "Flow canvas and ports",
    "02-minimal-chat-flow": "Minimal chat agent flow",
    "03-model-providers": "Model Providers chain",
    "04-playground-path": "Playground execution",
    "05-simple-agent-template": "Simple Agent template",
    "06-custom-language-model-port": "Custom Language Model port",
    "crosswalk-agent-vs-faq-chain": "Crosswalk — FAQ chain and Agent Component",
}


def main() -> None:
    cards = []
    order = [
        "overview",
        "01-flow-canvas",
        "02-minimal-chat-flow",
        "03-model-providers",
        "06-custom-language-model-port",
        "04-playground-path",
        "05-simple-agent-template",
        "crosswalk-agent-vs-faq-chain",
    ]
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
        "<title>Module 01 — Langflow flow topology</title>"
        "<style>body{font-family:'IBM Plex Sans',system-ui,sans-serif;max-width:960px;margin:32px auto;padding:0 16px;color:#2B3A4A}"
        "h1{font-size:1.4rem}.lead{color:#555}.card{border:1px solid #D5D5D5;border-radius:6px;padding:16px;margin:20px 0}"
        ".meta{font-size:0.85rem;color:#666}.score{font-weight:bold;color:#4F7F3A}"
        ".fig svg{max-width:100%;height:auto;display:block}a{color:#2563eb}</style></head><body>"
        "<h1>Module 01 — Langflow flow topology</h1>"
        "<p class='lead'>Deep-dive teaching figures (icons + shapes). "
        "<a href='../../index.html'>Back to Langflow gallery</a> · "
        "<a href='../../../../docs/research/langflow-agentic-workflows/modules/01-flow-topology/SOURCE.md'>SOURCE</a> · "
        "<a href='../../../../course/agentic-ai-langflow/module-01/index.html'>Course Module 1</a></p>"
        + "".join(cards)
        + "</body></html>"
    )
    out = ROOT / "index.html"
    out.write_text(page, encoding="utf-8")
    print(f"wrote {out} ({len(cards)} figures)")


if __name__ == "__main__":
    main()
