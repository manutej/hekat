"""Concept page: one self-contained HTML page for a concept space built from spec docs.

    python -m figtree page --title "Agentic workflows in Langflow" --specs DIR --digest OUT/digest.json \\
        [--icons-dir DIR --sheet sheet.svg] [--animated FIG.animated.svg] [--overview 00-overview] -o page.html

Inputs are what the pipeline already produced: the spec docs (intro sentences, steps, gaps),
the digest run (one scored SVG per spec), the icon family sheet, and an animated figure.  The
page inlines every SVG (ids namespaced per figure so twelve figures can share one document),
needs no network, and renders in light and dark themes with the figures on white sheets.
"""

from __future__ import annotations

import html
import json
import os
import re
from typing import Any, Dict, List, Optional, Sequence

from figtree.specs import parse_spec

_ID_ATTR = re.compile(r'\b(id|href|xlink:href)="(#?)([^"]+)"')
_URL_REF = re.compile(r"url\(#([^)]+)\)")
_SVG_OPEN = re.compile(r"<svg\b[^>]*>", re.S)
_XML_DECL = re.compile(r"<\?xml[^>]*\?>\s*")


def namespace_svg(svg: str, prefix: str) -> str:
    """Prefix every id and reference so several inline SVGs coexist in one HTML document."""
    svg = _XML_DECL.sub("", svg)
    svg = _ID_ATTR.sub(lambda m: f'{m.group(1)}="{m.group(2)}{prefix}{m.group(3)}"', svg)
    svg = _URL_REF.sub(lambda m: f"url(#{prefix}{m.group(1)})", svg)
    # animation keyframe/class names stay global; only ids are namespaced
    m = _SVG_OPEN.search(svg)
    if m and "width=" in m.group(0):
        head = re.sub(r'\s(width|height)="[^"]*"', "", m.group(0))
        head = head.replace("<svg", '<svg style="width:100%;height:auto;display:block"', 1)
        svg = svg[: m.start()] + head + svg[m.end():]
    return svg


def _read(p: str) -> str:
    with open(p, encoding="utf-8") as fh:
        return fh.read()


CSS = """
:root{--bg:#F6F5F1;--fg:#1F2328;--muted:#5C6470;--rule:#D9D6CE;--accent:#2F5F8F;--sheet:#FFFFFF;--sheet-edge:#E2DFD7;--good:#1B7F5A;--warn:#B5651D;
--display:Georgia,"Times New Roman",serif;--body:"IBM Plex Sans","Helvetica Neue",Arial,sans-serif;--mono:ui-monospace,Menlo,Consolas,monospace}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#15181C;--fg:#E8E6E0;--muted:#A6ADB8;--rule:#2C323A;--accent:#8AB4E0;--sheet-edge:#2C323A}}
:root[data-theme="dark"]{--bg:#15181C;--fg:#E8E6E0;--muted:#A6ADB8;--rule:#2C323A;--accent:#8AB4E0;--sheet-edge:#2C323A}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--body);font-size:16px;line-height:1.55;padding:32px clamp(16px,4vw,56px) 64px}
main{max-width:1040px;margin:0 auto}h1,h2,h3{font-family:var(--display);font-weight:600;margin:0;text-wrap:balance}
h1{font-size:clamp(2rem,5vw,3.2rem);line-height:1.05}h2{font-size:1.6rem;margin:56px 0 12px;padding-top:24px;border-top:1px solid var(--rule)}h3{font-size:1.15rem;margin:24px 0 8px}
p{max-width:70ch;margin:8px 0}.eyebrow{font-family:var(--mono);font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 8px}
.lede{font-size:1.1rem}.toc{display:flex;flex-wrap:wrap;gap:6px 18px;margin:20px 0;font-size:.92rem}.toc a{color:var(--accent);text-decoration:none}
.sheet{background:var(--sheet);border:1px solid var(--sheet-edge);border-radius:8px;padding:16px;margin:12px 0}.sheet svg{max-width:100%}
.fig{margin:12px 0 24px}.cap{font-size:.92rem;color:var(--muted);margin:8px 0 0}.cap b{color:var(--fg)}
.score{display:inline-block;font-family:var(--mono);font-size:.78rem;padding:2px 8px;border-radius:999px;border:1px solid var(--rule);margin-left:8px}
.score.good{color:var(--good);border-color:var(--good)}.score.warn{color:var(--warn);border-color:var(--warn)}
.steps{max-width:70ch;padding-left:1.4em}.steps li{margin:4px 0}.gaps{font-size:.92rem;color:var(--muted);max-width:70ch}
.icons{display:grid;grid-template-columns:repeat(auto-fill,minmax(96px,1fr));gap:12px}.icons .sheet{text-align:center;padding:10px}
.icons svg{width:40px;height:40px;color:var(--fg)}.icons .name{font-family:var(--mono);font-size:.74rem;color:var(--muted);display:block;margin-top:6px}
.stats{display:flex;flex-wrap:wrap;gap:16px 40px;margin:20px 0 0;padding:0}.stats div{display:flex;flex-direction:column}.stats dt{font-size:.78rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.stats dd{margin:0;font-family:var(--display);font-size:1.9rem;font-variant-numeric:tabular-nums}
details{margin:8px 0}summary{cursor:pointer;color:var(--accent)}pre{font-family:var(--mono);font-size:.8rem;white-space:pre-wrap;background:var(--sheet);color:#1F2328;padding:12px;border-radius:6px;border:1px solid var(--sheet-edge)}
footer{margin-top:56px;padding-top:16px;border-top:1px solid var(--rule);font-size:.88rem;color:var(--muted)}
@media (prefers-reduced-motion: reduce){svg *{animation:none!important}}
"""


def build_page(title: str, specs_dir: str, digest_path: str, out: str, icons_dir: Optional[str] = None,
               sheet: Optional[str] = None, animated: Optional[str] = None, overview_id: str = "00-overview",
               description: str = "", source_note: str = "") -> str:
    digest = json.load(open(digest_path, encoding="utf-8")) if os.path.exists(digest_path) else {}
    rows: List[Dict[str, Any]] = digest.get("units") or digest.get("rows") or (digest if isinstance(digest, list) else [])
    by_source: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        key = os.path.splitext(os.path.basename(str(r.get("source") or r.get("id") or "")))[0]
        by_source.setdefault(key, r)
        by_source.setdefault(str(r.get("id")), r)
    spec_files = sorted(f for f in os.listdir(specs_dir) if f.endswith(".md") and not f.startswith("_") and f.upper() != f)
    specs = []
    for f in spec_files:
        sid = f[:-3]
        s = parse_spec(_read(os.path.join(specs_dir, f)))
        intro = next((l.strip() for l in _read(os.path.join(specs_dir, f)).splitlines()[1:] if l.strip() and not l.startswith("#")), "")
        r = by_source.get(sid) or next((v for k, v in by_source.items() if k.startswith(sid)), {})
        specs.append({"id": sid, "title": s["title"] or sid, "intro": intro, "steps": s["steps"], "gaps": s["gaps"], "components": s["components"], "flows": s["flows"], "svg": r.get("svg"), "overall": r.get("overall")})
    overview = next((s for s in specs if s["id"] == overview_id), None)
    sections = [s for s in specs if s is not overview]

    def fig(s: Dict[str, Any], prefix: str, anim_css: str = "") -> str:
        if not s.get("svg") or not os.path.exists(s["svg"]):
            return '<p class="cap">No figure was generated for this spec.</p>'
        svg = namespace_svg(_read(s["svg"]), prefix)
        sc = s.get("overall")
        badge = f'<span class="score {"good" if (sc or 0) >= 8 else "warn"}">{sc:.2f} / 10</span>' if isinstance(sc, (int, float)) else ""
        style = f"<style>{anim_css}</style>" if anim_css else ""
        return f'<figure class="fig"><div class="sheet">{style}{svg}</div><figcaption class="cap"><b>{html.escape(s["title"])}</b>{badge} {html.escape(s["intro"])}</figcaption></figure>'

    parts = [f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(title)}</title><meta name="description" content="{html.escape(description)}"><style>{CSS}</style></head><body><main>']
    parts.append(f'<p class="eyebrow">Concept space</p><h1>{html.escape(title)}</h1>')
    if description:
        parts.append(f'<p class="lede">{html.escape(description)}</p>')
    n_fig = sum(1 for s in specs if s.get("svg"))
    scored = [s["overall"] for s in specs if isinstance(s.get("overall"), (int, float))]
    parts.append('<dl class="stats">' + f'<div><dt>workflows</dt><dd>{len(sections)}</dd></div><div><dt>figures</dt><dd>{n_fig}</dd></div>'
                 + (f'<div><dt>mean score</dt><dd>{sum(scored) / len(scored):.2f}</dd></div>' if scored else "")
                 + (f'<div><dt>components</dt><dd>{sum(len(s["components"]) for s in specs)}</dd></div>') + "</dl>")
    parts.append('<nav class="toc">' + "".join(f'<a href="#{html.escape(s["id"])}">{html.escape(s["title"])}</a>' for s in ([overview] if overview else []) + sections) + (' <a href="#icons">Icons</a>' if sheet or icons_dir else "") + "</nav>")
    if overview:
        anim_css = ""
        svg_path = overview["svg"]
        if animated and os.path.exists(animated):
            svg_path = animated
            css_sibling = animated.replace(".animated.svg", ".animation.css")
            txt = _read(animated)
            if "<style>" not in txt and os.path.exists(css_sibling):
                anim_css = _read(css_sibling)
        parts.append(f'<section id="{html.escape(overview["id"])}"><h2>How the workflows coordinate</h2><p>{html.escape(overview["intro"])}</p>')
        parts.append(fig({**overview, "svg": svg_path}, "ov-", anim_css))
        if overview["steps"]:
            parts.append('<h3>Read the workflows in this order</h3><ol class="steps">' + "".join(f"<li>{html.escape(st)}</li>" for st in overview["steps"]) + "</ol>")
        parts.append("</section>")
    for i, s in enumerate(sections, 1):
        parts.append(f'<section id="{html.escape(s["id"])}"><h2>{i} · {html.escape(s["title"])}</h2><p>{html.escape(s["intro"])}</p>')
        parts.append(fig(s, f"f{i}-"))
        if s["steps"]:
            parts.append('<h3>Steps</h3><ol class="steps">' + "".join(f"<li>{html.escape(st)}</li>" for st in s["steps"]) + "</ol>")
        if s["gaps"]:
            parts.append('<p class="gaps"><b>Not in the documentation:</b> ' + " ".join(html.escape(g.lstrip("-* ")) for g in s["gaps"]) + "</p>")
        parts.append("</section>")
    if sheet or icons_dir:
        parts.append('<section id="icons"><h2>Icon family for this concept space</h2><p>Each concept that appears across the figures has a 24-grid monoline icon, drawn with the icon-smith loop and checked at 16, 24 and 48 px.</p>')
        if icons_dir and os.path.isdir(icons_dir):
            cards = []
            for f in sorted(os.listdir(icons_dir)):
                if f.endswith(".svg") and f != "sheet.svg":
                    cards.append(f'<div class="sheet">{namespace_svg(_read(os.path.join(icons_dir, f)), "ic-" + f[:-4] + "-")}<span class="name">{html.escape(f[:-4])}</span></div>')
            parts.append('<div class="icons">' + "".join(cards) + "</div>")
        if sheet and os.path.exists(sheet):
            parts.append(f'<details><summary>Contact sheet with scores</summary><div class="sheet">{namespace_svg(_read(sheet), "sheet-")}</div></details>')
        parts.append("</section>")
    parts.append(f'<footer><p>{html.escape(source_note) if source_note else "Figures are generated from spec documents whose every component and flow carries a verbatim quote of the source documentation; what the documentation does not state is listed, not drawn."}</p></footer></main></body></html>')
    page = "\n".join(parts)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(page)
    return out


def main(argv: Sequence[str]) -> int:
    import argparse

    ap = argparse.ArgumentParser(prog="figtree page", description="build the concept page from specs, a digest run, icons and an animated figure")
    ap.add_argument("--title", required=True)
    ap.add_argument("--specs", required=True, help="directory of spec docs")
    ap.add_argument("--digest", required=True, help="digest.json written by figtree digest / the digest workflow")
    ap.add_argument("--icons-dir", default=None)
    ap.add_argument("--sheet", default=None)
    ap.add_argument("--animated", default=None, help="animated SVG of the overview figure")
    ap.add_argument("--overview", default="00-overview")
    ap.add_argument("--description", default="")
    ap.add_argument("--source-note", default="")
    ap.add_argument("-o", "--output", required=True)
    a = ap.parse_args(list(argv))
    out = build_page(a.title, a.specs, a.digest, a.output, a.icons_dir, a.sheet, a.animated, a.overview, a.description, a.source_note)
    print(f"wrote {out} ({os.path.getsize(out) // 1024} KB)")
    return 0
