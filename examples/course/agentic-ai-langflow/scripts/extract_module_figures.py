#!/usr/bin/env python3
"""Extract Module 1 figures and pedagogy from the course companion HTML."""

from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "Agentic_AI_with_Langflow.html"
MODULE_DIR = ROOT / "module-01"
GOLD_DIR = MODULE_DIR / "gold"
WORKSPACE = Path(__file__).resolve().parents[4]
META_DIR = WORKSPACE / "docs/course/agentic-ai-langflow/module-01/_meta"

FIGURE_MAP = [
    ("m1a", "Script or agent?", "concept"),
    ("m1b", "The four parts, with real contents", "concept"),
    ("m1c", "Where the key lives", "concept"),
    ("m1d", "One question, four beats", "concept"),
    ("m1e", "What a good answer looks like", "concept"),
    ("m1-capstone", "The capstone, in one picture", "capstone"),
]


def extract_svg_block(text: str, start: int) -> tuple[str, int]:
    """Return SVG starting at first <svg after start, and end index."""
    i = text.find("<svg", start)
    if i < 0:
        return "", start
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
                return text[i:j], j
            continue
        j += 1
    return "", start


def tag_inner(html: str, tag: str, attr: str, value: str) -> str:
    pat = rf"<{tag}[^>]*{attr}=[\"']{re.escape(value)}[\"'][^>]*>(.*?)</{tag}>"
    m = re.search(pat, html, re.DOTALL | re.IGNORECASE)
    return unescape(m.group(1).strip()) if m else ""


def figcaption_after(sheet_end: int, section: str) -> str:
    m = re.search(r"<figcaption>(.*?)</figcaption>", section[sheet_end : sheet_end + 800], re.DOTALL)
    return unescape(m.group(1).strip()) if m else ""


def title_desc(svg: str) -> tuple[str, str]:
    title = ""
    desc = ""
    m = re.search(r"<title[^>]*id=[\"']([^\"']+)[\"'][^>]*>(.*?)</title>", svg, re.DOTALL)
    if m:
        title = unescape(re.sub(r"\s+", " ", m.group(2)).strip())
    m = re.search(r"<desc[^>]*id=[\"'][^\"']+[\"'][^>]*>(.*?)</desc>", svg, re.DOTALL)
    if m:
        desc = unescape(re.sub(r"\s+", " ", m.group(1)).strip())
    if not title:
        m = re.search(r"<title[^>]*>(.*?)</title>", svg, re.DOTALL)
        if m:
            title = unescape(re.sub(r"\s+", " ", m.group(1)).strip())
    return title, desc


def reading_lists(section: str) -> list[str]:
    out: list[str] = []
    for block in re.finditer(r'<ol class="reading">(.*?)</ol>', section, re.DOTALL):
        for li in re.finditer(r"<li>\s*<span>(.*?)</span>", block.group(1), re.DOTALL):
            out.append(unescape(re.sub(r"\s+", " ", li.group(1)).strip()))
    return out


def labs(section: str) -> list[dict]:
    labs_out: list[dict] = []
    for art in re.finditer(
        r'<article class="lab">(.*?)</article>', section, re.DOTALL
    ):
        chunk = art.group(1)
        h4 = re.search(r"<h4>(.*?)</h4>", chunk, re.DOTALL)
        p = re.search(r"<p>(.*?)</p>", chunk, re.DOTALL)
        lid = re.search(r'<span class="id">(.*?)</span>', chunk)
        chip = re.search(r'<span class="chip ([^"]+)"', chunk)
        labs_out.append(
            {
                "id": lid.group(1).strip() if lid else "",
                "chip": chip.group(1).strip() if chip else "",
                "title": unescape(h4.group(1).strip()) if h4 else "",
                "description": unescape(re.sub(r"\s+", " ", p.group(1)).strip()) if p else "",
            }
        )
    return labs_out


def glossary(section: str) -> list[dict]:
    items: list[dict] = []
    for div in re.finditer(r"<div><dt>(.*?)</dt><dd>(.*?)</dd></div>", section, re.DOTALL):
        items.append({"term": unescape(div.group(1).strip()), "definition": unescape(div.group(2).strip())})
    return items


def main() -> int:
    text = HTML_PATH.read_text(encoding="utf-8")
    m = re.search(r'<section class="module" id="m1"[^>]*>(.*?)</section>', text, re.DOTALL)
    if not m:
        print("module m1 not found", file=sys.stderr)
        return 1
    section = m.group(1)

    figures: list[dict] = []
    search_from = 0
    for fig_id, h4_match, kind in FIGURE_MAP:
        h4_pos = section.find(f"<h4>{h4_match}</h4>", search_from)
        if h4_pos < 0:
            h4_pos = section.find(h4_match, search_from)
        if h4_pos < 0:
            print(f"warning: h4 not found for {fig_id}", file=sys.stderr)
            continue
        sheet_pos = section.find('<div class="sheet">', h4_pos)
        svg, svg_end = extract_svg_block(section, sheet_pos)
        if not svg:
            print(f"warning: no svg for {fig_id}", file=sys.stderr)
            continue
        cap = figcaption_after(svg_end, section)
        title, desc = title_desc(svg)
        gold_path = GOLD_DIR / f"{fig_id}.svg"
        gold_path.write_text(svg if svg.endswith("\n") else svg + "\n", encoding="utf-8")
        figures.append(
            {
                "id": fig_id,
                "kind": kind,
                "h4": h4_match,
                "title": title,
                "desc": desc,
                "figcaption": cap,
                "gold_svg": str(gold_path.relative_to(ROOT)),
                "reading_nearby": reading_lists(section[h4_pos : h4_pos + 12000])[:8],
            }
        )
        search_from = svg_end

    manifest = {
        "module": "m1",
        "title": "Introduction to Agentic AI",
        "source_html": str(HTML_PATH.relative_to(ROOT)),
        "figures": figures,
    }
    MODULE_DIR.mkdir(parents=True, exist_ok=True)
    (MODULE_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    META_DIR.mkdir(parents=True, exist_ok=True)
    pedagogy = {
        "labs": labs(section),
        "glossary": glossary(section),
        "module_intro": unescape(
            re.sub(
                r"\s+",
                " ",
                re.search(
                    r'<p class="tag">.*?</p><p>(.*?)</p>',
                    section,
                    re.DOTALL,
                ).group(1),
            )
        )
        if re.search(r'<p class="tag">.*?</p><p>(.*?)</p>', section, re.DOTALL)
        else "",
    }
    (META_DIR / "pedagogy.json").write_text(json.dumps(pedagogy, indent=2) + "\n", encoding="utf-8")

    checklist = re.search(r"<details><summary>Instructor checklist</summary><ol>(.*?)</ol>", section, re.DOTALL)
    if checklist:
        items = [unescape(re.sub(r"\s+", " ", li.group(1)).strip()) for li in re.finditer(r"<li>(.*?)</li>", checklist.group(1), re.DOTALL)]
        (META_DIR / "INSTRUCTOR-CHECKLIST.md").write_text(
            "# Instructor checklist (Module 1)\n\n" + "\n".join(f"- {x}" for x in items) + "\n",
            encoding="utf-8",
        )

    print(f"extracted {len(figures)} figures -> {MODULE_DIR / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
