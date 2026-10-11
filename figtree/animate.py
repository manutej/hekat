"""Animation layer: make a generated figure come to life.

Three techniques from the SVG animation canon, applied only where they carry meaning:

* **reveal**  - blocks fade/slide in by tree depth and reading order (the figure builds itself
  the way the recursion builds it);
* **draw**    - connectors draw themselves (stroke-dasharray / stroke-dashoffset) after the
  blocks they join exist;
* **pulse**   - a small token travels along each flow path (CSS motion path), so a reader sees
  *what moves where*; dashed control edges get a slower, dimmer token.

The CSS is deterministic (fixed delays per element, derived from the program) and guarded by
``prefers-reduced-motion``.  ``animate_svg`` returns the SVG with an internal ``<style>`` for
standalone files, or the SVG plus a separate stylesheet for pages that inline the figure.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from figtree.geometry import points_to_path
from figtree.program import load_program


@dataclass
class Timeline:
    step: float = 0.35  # seconds between successive block reveals
    draw: float = 0.6  # seconds a connector takes to draw
    pulse: float = 2.4  # seconds for one token trip
    total: float = 0.0


def _order(prog) -> List[Tuple[str, int]]:
    """Reveal order: leaf blocks by (y row, x), so the figure builds left-to-right, top-down."""
    blocks = [e for e in prog.shapes() if e.el.get("data-role") == "block" and e.bbox]
    blocks.sort(key=lambda e: (e.bbox.y // 64, e.bbox.x))
    return [(e.id, i) for i, e in enumerate(blocks)]


def animate_svg(svg_text: str, modes: Tuple[str, ...] = ("reveal", "draw", "pulse"), timeline: Optional[Timeline] = None, inline_style: bool = True) -> Tuple[str, str]:
    """Return ``(svg, css)``.  With ``inline_style`` the CSS is also embedded in the SVG."""
    tl = timeline or Timeline()
    prog = load_program(svg_text)
    order = dict(_order(prog))
    css: List[str] = []
    svg = prog.serialize()
    n_blocks = len(order)
    blocks_done = tl.step * max(n_blocks, 1)

    # map each leaf group (the <g> holding block + label) to its block index
    group_delay: Dict[str, float] = {}
    for e in prog.elements:
        if e.el.get("data-role") == "block" and e.id in order:
            group_delay[e.parent_id or e.id] = order[e.id] * tl.step

    if "reveal" in modes:
        # opacity only: a CSS transform would replace the group's own SVG translate()
        css.append("@keyframes ft-reveal{from{opacity:0}to{opacity:1}}")
        for gid, delay in group_delay.items():
            css.append(f"#{_css_id(gid)}{{opacity:0;animation:ft-reveal .5s ease-out {delay:.2f}s forwards}}")

    flows = [e for e in prog.flows() if e.points]
    shafts: List[str] = []
    if "draw" in modes:
        # a marker-less copy of each connector draws itself; the real connector (with its
        # arrowhead) appears the moment the shaft is complete, so no standalone triangles
        css.append("@keyframes ft-draw{to{stroke-dashoffset:0}}")
        css.append("@keyframes ft-appear{to{opacity:1}}")
        for i, f in enumerate(flows):
            length = sum(abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in zip(f.points, f.points[1:])) or 1
            delay = blocks_done + i * 0.15
            sid = f"ft-shaft-{i}"
            dash = f' stroke-dasharray="{f.el.get("stroke-dasharray")}"' if f.el.get("stroke-dasharray") else ""
            shafts.append(
                f'<path id="{sid}" d="{points_to_path(f.points)}" fill="none" stroke="{f.stroke or "#333333"}" '
                f'stroke-width="{f.stroke_width or 1.2:g}" data-role="anim-shaft"/>'
            )
            css.append(
                f"#{sid}{{stroke-dasharray:{length};stroke-dashoffset:{length};"
                f"animation:ft-draw {tl.draw}s ease-in-out {delay:.2f}s forwards}}"
            )
            css.append(f"#{_css_id(f.id)}{{opacity:0;animation:ft-appear .01s linear {delay + tl.draw:.2f}s forwards}}")
    pulses: List[str] = []
    if "pulse" in modes and flows:
        css.append("@keyframes ft-travel{from{offset-distance:0%}to{offset-distance:100%}}")
        start = blocks_done + len(flows) * 0.15 + tl.draw
        for i, f in enumerate(flows):
            is_control = f.el.get("data-flow") in ("control", "conditional")
            dur = tl.pulse * (1.6 if is_control else 1.0)
            pid = f"ft-pulse-{i}"
            fill = "#333333" if not is_control else "#999999"
            pulses.append(f'<circle id="{pid}" r="3" fill="{fill}" data-role="pulse"/>')
            css.append(
                f"#{pid}{{offset-path:path('{points_to_path(f.points)}');offset-rotate:0deg;opacity:0;"
                f"animation:ft-travel {dur:.1f}s linear {start + i * 0.4:.2f}s infinite, ft-show .1s linear {start + i * 0.4:.2f}s forwards}}"
            )
        css.append("@keyframes ft-show{to{opacity:1}}")
        tl.total = start + tl.pulse
    else:
        tl.total = blocks_done + len(flows) * 0.15 + tl.draw

    css.append("@media (prefers-reduced-motion: reduce){[id^=ft-pulse],[id^=ft-shaft]{display:none}*{animation:none!important;opacity:1!important;stroke-dashoffset:0!important}}")
    stylesheet = "\n".join(css)

    extra = shafts + pulses
    if extra:
        svg = svg.replace("</svg>", "  " + "\n  ".join(extra) + "\n</svg>")
    if inline_style:
        style_block = f"<style>\n{stylesheet}\n</style>"
        svg = re.sub(r"(<svg[^>]*>)", lambda m: m.group(1) + "\n" + style_block, svg, count=1)
    return svg, stylesheet


def _css_id(eid: str) -> str:
    """Escape characters that are not valid unescaped in a CSS id selector."""
    return re.sub(r"([.:\[\]#])", r"\\\1", eid)
