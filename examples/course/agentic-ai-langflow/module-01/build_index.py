#!/usr/bin/env python3
"""Gallery index for course Module 1 figures."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))


def main() -> None:
    cards = []
    for fig in manifest["figures"]:
        fid = fig["id"]
        svg_path = ROOT / f"{fid}.svg"
        if not svg_path.exists():
            continue
        score = "—"
        sp = ROOT / f"{fid}.score.json"
        if sp.exists():
            score = f"{json.loads(sp.read_text())['overall']:.2f}"
        cards.append(
            f'<section class="card"><h2>{html.escape(fig.get("title") or fid)}</h2>'
            f'<p class="meta">Score: {score} · {html.escape(fig.get("figcaption",""))}</p>'
            f'<div class="fig">{svg_path.read_text(encoding="utf-8")}</div></section>'
        )
    page = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>Course Module 1 figures</title>"
        "<style>body{font-family:'IBM Plex Sans',system-ui,sans-serif;max-width:960px;margin:32px auto;padding:0 16px}"
        ".card{border:1px solid #D5D5D5;border-radius:6px;padding:16px;margin:20px 0}"
        ".meta{font-size:0.85rem;color:#666}.fig svg{max-width:100%;height:auto}a{color:#2563eb}</style></head><body>"
        "<h1>Course Module 1 — Introduction to Agentic AI</h1>"
        "<p><a href='preview.html'>Full module preview</a> · "
        "<a href='../../../figtree/langflow/modules/01-flow-topology/index.html'>Langflow topology module</a></p>"
        + "".join(cards)
        + "</body></html>"
    )
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print(f"wrote {ROOT / 'index.html'}")


if __name__ == "__main__":
    main()
