"""Structured SVG model.

Nodes keep a small structured drawing model (rects, texts, orthogonal paths, nested
groups, port comments) from which the editable SVG fragment is serialised.  The Critic
always inspects the serialised SVG source; the Worker repairs the model and re-serialises.
"""

from __future__ import annotations

import copy
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple

from figtree.geometry import Point, path_to_points, points_to_path
from figtree.schemas import BBox, GlobalStyle, Port

MARKER_ID = "figtree-arrow"
MARKER_W = 5      # tiny academic arrowhead: 5 x 3.5 px, filled border colour
MARKER_H = 3.5
DASH = "4 2"      # dashed pattern for skip / feedback connections

SVG_NS = "http://www.w3.org/2000/svg"


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def _num(v: float) -> str:
    if float(v).is_integer():
        return str(int(v))
    return f"{v:g}"


@dataclass
class RectEl:
    id: str
    x: int
    y: int
    w: int
    h: int
    fill: str
    stroke: str
    stroke_width: float
    role: str = "block"
    rx: int = 0
    extra: Dict[str, str] = field(default_factory=dict)

    def bbox(self) -> BBox:
        return BBox(self.x, self.y, self.w, self.h)

    def svg(self) -> str:
        attrs = (
            f'id="{_esc(self.id)}" x="{self.x}" y="{self.y}" width="{self.w}" height="{self.h}" '
            f'fill="{self.fill}" stroke="{self.stroke}" stroke-width="{_num(self.stroke_width)}" '
            f'data-role="{self.role}"'
        )
        if self.rx:
            attrs += f' rx="{self.rx}"'
        for k, v in self.extra.items():
            attrs += f' {k}="{_esc(v)}"'
        return f"<rect {attrs}/>"


@dataclass
class ShapeEl:
    """A non-rectangular block (cylinder, document, diamond, pill, actor) as one path."""

    id: str
    kind: str
    x: int
    y: int
    w: int
    h: int
    fill: str
    stroke: str
    stroke_width: float
    role: str = "block"
    extra: Dict[str, str] = field(default_factory=dict)

    def bbox(self) -> BBox:
        return BBox(self.x, self.y, self.w, self.h)

    def svg(self) -> str:
        from figtree.elements import shape_path

        d = shape_path(self.kind, self.w, self.h)
        attrs = (
            f'id="{_esc(self.id)}" d="{d}" fill="{self.fill}" stroke="{self.stroke}" '
            f'stroke-width="{_num(self.stroke_width)}" stroke-linejoin="round" data-role="{self.role}" data-kind="{self.kind}" '
            f'data-bbox="{self.x} {self.y} {self.w} {self.h}"'
        )
        if self.x or self.y:
            attrs += f' transform="translate({self.x},{self.y})"'
        for k, v in self.extra.items():
            attrs += f' {k}="{_esc(v)}"'
        return f"<path {attrs}/>"


@dataclass
class UseEl:
    """An icon placed from a ``<symbol>`` (``href="#icon-name"``)."""

    id: str
    href: str
    x: int
    y: int
    w: int = 16
    h: int = 16
    color: str = "#333333"

    def bbox(self) -> BBox:
        return BBox(self.x, self.y, self.w, self.h)

    def svg(self) -> str:
        return (
            f'<use id="{_esc(self.id)}" href="{_esc(self.href)}" x="{self.x}" y="{self.y}" width="{self.w}" height="{self.h}" '
            f'color="{self.color}" data-role="icon"/>'
        )


@dataclass
class TextEl:
    id: str
    x: int
    y: int
    text: str
    size: int
    kind: str  # label | annot
    font: str
    anchor: str = "middle"
    fill: str = "#333333"
    max_width: Optional[int] = None  # width of the block the text must fit in
    lines: List[str] = field(default_factory=list)  # multi-line (tspans)

    def est_width(self) -> int:
        longest = max([self.text] + self.lines, key=len) if (self.lines or self.text) else ""
        return int(round(len(longest) * self.size * 0.5))

    def bbox(self) -> BBox:
        w = self.est_width()
        n = max(1, len(self.lines) or 1)
        h = int(self.size * 1.2 * n)
        if self.anchor == "middle":
            x = self.x - w // 2
        elif self.anchor == "end":
            x = self.x - w
        else:
            x = self.x
        return BBox(x, self.y - h // 2, w, h)

    def svg(self) -> str:
        attrs = (
            f'id="{_esc(self.id)}" x="{self.x}" y="{self.y}" font-family="{_esc(self.font)}" '
            f'font-size="{self.size}" text-anchor="{self.anchor}" dominant-baseline="middle" '
            f'fill="{self.fill}" data-kind="{self.kind}"'
        )
        if self.max_width is not None:
            attrs += f' data-max-width="{self.max_width}"'
        if self.lines and len(self.lines) > 1:
            n = len(self.lines)
            lh = int(self.size * 1.2)
            start = self.y - (lh * (n - 1)) // 2
            spans = "".join(
                f'<tspan x="{self.x}" y="{start + i * lh}">{_esc(t)}</tspan>'
                for i, t in enumerate(self.lines)
            )
            return f"<text {attrs}>{spans}</text>"
        return f"<text {attrs}>{_esc(self.text)}</text>"


@dataclass
class PathEl:
    id: str
    points: List[Point]
    flow_type: str = "data"
    marker: bool = True
    stroke: str = "#333333"
    stroke_width: float = 1.2
    diagonal_flag: bool = False
    src_port: str = ""
    dst_port: str = ""
    label: str = ""

    def bbox(self) -> BBox:
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        return BBox(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))

    def svg(self) -> str:
        attrs = (
            f'id="{_esc(self.id)}" d="{points_to_path(self.points)}" fill="none" '
            f'stroke="{self.stroke}" stroke-width="{_num(self.stroke_width)}" '
            f'data-flow="{self.flow_type}"'
        )
        if self.flow_type in ("control", "conditional"):
            attrs += f' stroke-dasharray="{DASH}"'
        if self.marker:
            attrs += f' marker-end="url(#{MARKER_ID})"'
        if self.diagonal_flag:
            attrs += ' data-diagonal="semantic"'
        if self.src_port:
            attrs += f' data-from="{_esc(self.src_port)}"'
        if self.dst_port:
            attrs += f' data-to="{_esc(self.dst_port)}"'
        return f"<path {attrs}/>"


@dataclass
class GroupEl:
    """A placed child fragment: ``<g transform="translate(x,y)">``."""

    id: str
    x: int
    y: int
    fragment: "Fragment"
    label: str = ""

    def bbox(self) -> BBox:
        return BBox(self.x, self.y, self.fragment.w, self.fragment.h)

    def svg(self, indent: str = "") -> str:
        inner = self.fragment.svg(indent + "  ")
        return (
            f'{indent}<g id="{_esc(self.id)}" transform="translate({self.x},{self.y})" '
            f'data-bbox="{self.x} {self.y} {self.fragment.w} {self.fragment.h}" '
            f'data-label="{_esc(self.label)}">\n{inner}\n{indent}</g>'
        )


Element = Any  # RectEl | TextEl | PathEl | GroupEl


def port_comment(p: Port) -> str:
    """Port comment in the paper's convention: ``<!-- PORT:side x=.. y=.. -->`` plus id/type/component."""
    return (
        f'<!-- PORT:{p.side} x={p.rel_x} y={p.rel_y} id={p.id} type={p.type} '
        f'component="{_esc(p.component)}" -->'
    )


@dataclass
class Fragment:
    """The drawing model of one node, in the node's own frame (origin top-left)."""

    node_id: str
    w: int
    h: int
    elements: List[Element] = field(default_factory=list)
    ports: List[Port] = field(default_factory=list)

    # -- traversal ---------------------------------------------------------
    def rects(self) -> List[RectEl]:
        return [e for e in self.elements if isinstance(e, RectEl)]

    def texts(self) -> List[TextEl]:
        return [e for e in self.elements if isinstance(e, TextEl)]

    def paths(self) -> List[PathEl]:
        return [e for e in self.elements if isinstance(e, PathEl)]

    def groups(self) -> List[GroupEl]:
        return [e for e in self.elements if isinstance(e, GroupEl)]

    def find(self, element_id: str) -> Optional[Element]:
        for e in self.elements:
            if getattr(e, "id", None) == element_id:
                return e
            if isinstance(e, GroupEl):
                found = e.fragment.find(element_id)
                if found is not None:
                    return found
        return None

    def iter_all(self, offset: Point = (0, 0)) -> Iterator[Tuple[Element, Point]]:
        """Yield every element with the absolute offset of its frame."""
        for e in self.elements:
            yield e, offset
            if isinstance(e, GroupEl):
                yield from e.fragment.iter_all((offset[0] + e.x, offset[1] + e.y))

    def content_bbox(self) -> Optional[BBox]:
        boxes = [e.bbox() for e in self.elements]
        if not boxes:
            return None
        x1 = min(b.x for b in boxes)
        y1 = min(b.y for b in boxes)
        x2 = max(b.x2 for b in boxes)
        y2 = max(b.y2 for b in boxes)
        return BBox(x1, y1, x2 - x1, y2 - y1)

    # -- serialisation ----------------------------------------------------
    def svg(self, indent: str = "") -> str:
        lines = []
        for p in self.ports:
            lines.append(indent + port_comment(p))
        for e in self.elements:
            if isinstance(e, GroupEl):
                lines.append(e.svg(indent))
            else:
                lines.append(indent + e.svg())
        return "\n".join(lines)

    def clone(self) -> "Fragment":
        return copy.deepcopy(self)


def marker_defs(style: GlobalStyle) -> str:
    from figtree.styles import PRESETS

    pr = PRESETS.get(getattr(style, "preset", "paper"))
    w, h = (pr.marker_w, pr.marker_h) if pr else (MARKER_W, MARKER_H)
    return (
        f'<defs>\n  <marker id="{MARKER_ID}" markerWidth="{w}" markerHeight="{h:g}" refX="{w}" '
        f'refY="{h / 2:g}" orient="auto" markerUnits="userSpaceOnUse">\n'
        f'    <path d="M0,0 L{w},{h / 2:g} L0,{h:g} z" fill="{style.palette["border"]}"/>\n'
        f"  </marker>\n</defs>"
    )


def wrap_svg(fragment: Fragment, style: GlobalStyle, title: str = "") -> str:
    """Wrap a fragment as a complete standalone SVG document (white background first)."""
    from figtree.icons import symbol_defs

    w, h = fragment.w, fragment.h
    used = sorted({e.href[len("#icon-"):] for e, _ in fragment.iter_all() if isinstance(e, UseEl) and e.href.startswith("#icon-")})
    symbols = symbol_defs(used)
    head = (
        f'<svg xmlns="{SVG_NS}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'font-family="{_esc(style.font)}" data-figtree="1">'
    )
    parts = [head]
    if title:
        parts.append(f"  <title>{_esc(title)}</title>")
    parts.append(f'  <rect id="background" x="0" y="0" width="{w}" height="{h}" fill="#FFFFFF" data-role="background"/>')
    defs = marker_defs(style)
    if symbols:
        defs = defs.replace("</defs>", symbols + "\n</defs>")
    parts.append("  " + defs.replace("\n", "\n  "))
    parts.append(f'  <g id="{_esc(fragment.node_id)}" data-bbox="0 0 {w} {h}">')
    parts.append(fragment.svg("    "))
    parts.append("  </g>")
    parts.append("</svg>")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Parsing helpers used by the Critic and the editability proof
# ---------------------------------------------------------------------------

_PORT_RE = re.compile(
    r'PORT:(top|bottom|left|right)\s+x=(-?\d+)\s+y=(-?\d+)(?:\s+id=(\S+))?(?:\s+type=(\S+))?(?:\s+component="([^"]*)")?'
)


def parse_svg(svg_text: str) -> ET.Element:
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    return ET.fromstring(svg_text, parser=parser)


def local(tag: Any) -> str:
    if not isinstance(tag, str):
        return "comment"
    return tag.split("}")[-1]


def parse_translate(transform: str) -> Point:
    m = re.search(r"translate\(\s*(-?\d+(?:\.\d+)?)\s*[, ]\s*(-?\d+(?:\.\d+)?)\s*\)", transform or "")
    if not m:
        return (0, 0)
    return (int(float(m.group(1))), int(float(m.group(2))))


def iter_elements(root: ET.Element, offset: Point = (0, 0)) -> Iterator[Tuple[ET.Element, Point]]:
    """Iterate elements with their absolute frame offset (following translate transforms)."""
    for child in list(root):
        tag = local(child.tag)
        if tag == "comment":
            yield child, offset
            continue
        yield child, offset
        if tag in ("g", "svg"):
            off = offset
            if tag == "g":
                t = parse_translate(child.get("transform", ""))
                off = (offset[0] + t[0], offset[1] + t[1])
            yield from iter_elements(child, off)


def extract_ports(svg_text: str) -> List[Dict[str, Any]]:
    """Extract ports from comments with absolute coordinates."""
    root = parse_svg(svg_text)
    ports: List[Dict[str, Any]] = []
    for el, off in iter_elements(root):
        if local(el.tag) != "comment":
            continue
        m = _PORT_RE.search(el.text or "")
        if not m:
            continue
        side, x, y, pid, ptype, comp = m.groups()
        ports.append(
            {
                "id": pid or side,
                "side": side,
                "rel_x": int(x),
                "rel_y": int(y),
                "abs_x": int(x) + off[0],
                "abs_y": int(y) + off[1],
                "type": ptype or ("output" if side in ("right", "bottom") else "input"),
                "component": comp or "",
            }
        )
    return ports


def extract_bboxes(svg_text: str) -> Dict[str, BBox]:
    """Extract ``data-bbox`` groups with absolute coordinates."""
    root = parse_svg(svg_text)
    out: Dict[str, BBox] = {}
    for el, off in iter_elements(root):
        if local(el.tag) != "g":
            continue
        bb = el.get("data-bbox")
        if not bb:
            continue
        x, y, w, h = (int(float(v)) for v in bb.split())
        # the group's own translate is included in the stored bbox; use the parent offset
        gid = el.get("id", "")
        out[gid] = BBox(x + off[0], y + off[1], w, h)
    return out


def element_bbox(el: ET.Element, offset: Point) -> Optional[BBox]:
    tag = local(el.tag)
    ox, oy = offset
    try:
        if tag == "rect":
            return BBox(
                int(float(el.get("x", 0))) + ox,
                int(float(el.get("y", 0))) + oy,
                int(float(el.get("width", 0))),
                int(float(el.get("height", 0))),
            )
        if tag == "path":
            if el.get("data-bbox"):  # shaped block: trust the declared bbox (translate included)
                x, y, w, h = (int(float(v)) for v in el.get("data-bbox").split())
                return BBox(x + ox, y + oy, w, h)
            pts = path_to_points(el.get("d", ""))
            if not pts:
                return None
            xs = [p[0] + ox for p in pts]
            ys = [p[1] + oy for p in pts]
            return BBox(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
        if tag == "line":
            x1, y1, x2, y2 = (int(float(el.get(k, 0))) for k in ("x1", "y1", "x2", "y2"))
            return BBox(min(x1, x2) + ox, min(y1, y2) + oy, abs(x2 - x1), abs(y2 - y1))
        if tag == "text":
            size = int(float(el.get("font-size", 12)))
            text = "".join(el.itertext())
            lines = [t.text or "" for t in el.findall(f"{{{SVG_NS}}}tspan")] or [text]
            w = int(round(max(len(t) for t in lines) * size * 0.5))
            h = int(size * 1.2 * len(lines))
            x = int(float(el.get("x", 0))) + ox
            y = int(float(el.get("y", 0))) + oy
            anchor = el.get("text-anchor", "start")
            if anchor == "middle":
                x -= w // 2
            elif anchor == "end":
                x -= w
            return BBox(x, y - h // 2, w, h)
    except ValueError:
        return None
    return None
