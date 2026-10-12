#!/usr/bin/env python3
"""Assemble Module 1 preview HTML with production SVGs injected into sheet blocks."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
COURSE = Path(__file__).resolve().parents[1]
HTML_SRC = COURSE / "Agentic_AI_with_Langflow.html"
MODULE = Path(__file__).resolve().parent
OUT = MODULE / "preview.html"


def inject_figures(section: str, manifest: dict) -> str:
    for fig in manifest["figures"]:
        fid = fig["id"]
        h4 = fig["h4"]
        svg_path = MODULE / f"{fid}.svg"
        if not svg_path.exists():
            continue
        svg = svg_path.read_text(encoding="utf-8")
        if 'role="img"' not in svg[:200]:
            svg = svg.replace("<svg ", '<svg role="img" ', 1)
        # Replace sheet content after this h4 (concept or capstone figure)
        if fid == "m1-capstone":
            pat = rf'(<figure>\s*<h3>The capstone, in one picture</h3>\s*<div class="sheet">)(.*?)(</div>\s*<figcaption>)'
        else:
            esc = re.escape(h4)
            pat = rf'(<figure class="concept">\s*<h4>{esc}</h4>\s*<div class="sheet">)(.*?)(</div>\s*<figcaption>)'

        def repl(m: re.Match) -> str:
            return m.group(1) + svg + m.group(3)

        section, n = re.subn(pat, repl, section, count=1, flags=re.DOTALL)
        if n == 0 and fid != "m1-capstone":
            pat2 = rf'(<h4>{re.escape(h4)}</h4>\s*<div class="sheet">)(.*?)(</div>)'
            section, _ = re.subn(pat2, repl, section, count=1, flags=re.DOTALL)
    return section


def main() -> None:
    full = HTML_SRC.read_text(encoding="utf-8")
    m = re.search(r'(<section class="module" id="m1"[^>]*>.*?</section>)', full, re.DOTALL)
    if not m:
        raise SystemExit("m1 section not found")
    section = m.group(1)
    manifest = json.loads((MODULE / "manifest.json").read_text(encoding="utf-8"))
    section = inject_figures(section, manifest)

    # Minimal preview page with course CSS from full doc head
    head_m = re.search(r"(<style>.*?</style>)", full, re.DOTALL)
    style = head_m.group(1) if head_m else ""
    page = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>Module 1 preview — Agentic AI with Langflow</title>"
        + style
        + "</head><body><p><a href='../../../figtree/langflow/modules/index.html'>FigTree modules</a></p>"
        + section
        + "</body></html>"
    )
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
