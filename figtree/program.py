"""Addressable SVG programs.

The paper's central property is that every visual element corresponds to an addressable
statement of the program.  :func:`load_program` takes *any* SVG (hand drawn, exported from a
charting library, or produced by the generator), gives every element a stable id, resolves
inherited typography and colour, and computes absolute bounding boxes.  Everything downstream
(quality critic, edit scripts, refinement loop) works on this view.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional, Tuple

from figtree.geometry import path_to_points
from figtree.schemas import BBox
from figtree.svgmodel import SVG_NS, element_bbox, local, parse_svg, parse_translate

ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

SHAPE_TAGS = {"rect", "circle", "ellipse", "line", "polyline", "polygon", "path", "text", "image", "foreignObject", "use"}
_STYLE_PROP = re.compile(r"\s*([a-zA-Z-]+)\s*:\s*([^;]+)")
_COLOR_RE = re.compile(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b|rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)")


def style_props(el: ET.Element) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for k, v in _STYLE_PROP.findall(el.get("style", "") or ""):
        out[k.strip()] = v.strip()
    return out


def attr(el: ET.Element, name: str) -> Optional[str]:
    """Presentation attribute or the same property from ``style=``."""
    v = el.get(name)
    if v is not None:
        return v
    return style_props(el).get(name)


def parse_len(v: Optional[str], default: float) -> float:
    if v is None:
        return default
    m = re.match(r"\s*(-?\d+(?:\.\d+)?)\s*(px|pt|em|%)?", v)
    if not m:
        return default
    n = float(m.group(1))
    unit = m.group(2)
    if unit == "pt":
        return n * 4 / 3
    if unit == "em":
        return n * 16
    return n


def parse_color(v: Optional[str]) -> Optional[Tuple[int, int, int]]:
    if not v:
        return None
    v = v.strip()
    if v.lower() in ("none", "transparent"):
        return None
    m = _COLOR_RE.search(v)
    if not m:
        named = {"black": (0, 0, 0), "white": (255, 255, 255), "red": (255, 0, 0), "gray": (128, 128, 128), "grey": (128, 128, 128), "blue": (0, 0, 255), "green": (0, 128, 0)}
        return named.get(v.lower())
    if m.group(1):
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    return (int(m.group(2)), int(m.group(3)), int(m.group(4)))


def hex_color(rgb: Tuple[int, int, int]) -> str:
    return "#%02X%02X%02X" % rgb


def luminance(rgb: Tuple[int, int, int]) -> float:
    def ch(c: int) -> float:
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast_ratio(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def saturation(rgb: Tuple[int, int, int]) -> float:
    r, g, b = (c / 255 for c in rgb)
    mx, mn = max(r, g, b), min(r, g, b)
    return 0.0 if mx == 0 else (mx - mn) / mx


@dataclass
class ElementInfo:
    id: str
    tag: str
    el: ET.Element
    parent_id: Optional[str]
    depth: int
    offset: Tuple[int, int]
    bbox: Optional[BBox]
    fill: Optional[str]
    stroke: Optional[str]
    stroke_width: Optional[float]
    font_size: Optional[float]
    font_family: Optional[str]
    text: str = ""
    is_flow: bool = False
    points: List[Tuple[int, int]] = field(default_factory=list)


@dataclass
class Program:
    root: ET.Element
    width: int
    height: int
    elements: List[ElementInfo]
    assigned_ids: int = 0  # ids added during normalisation

    def by_id(self, eid: str) -> Optional[ElementInfo]:
        for e in self.elements:
            if e.id == eid:
                return e
        return None

    def element(self, eid: str) -> Optional[ET.Element]:
        info = self.by_id(eid)
        return info.el if info else None

    def parent_of(self, eid: str) -> Optional[ET.Element]:
        for parent in self.root.iter():
            for child in list(parent):
                if isinstance(child.tag, str) and child.get("id") == eid:
                    return parent
        return None

    def shapes(self) -> List[ElementInfo]:
        return [e for e in self.elements if e.tag in SHAPE_TAGS and e.bbox is not None and not self._in_defs(e)]

    def texts(self) -> List[ElementInfo]:
        return [e for e in self.elements if e.tag == "text" and not self._in_defs(e)]

    def flows(self) -> List[ElementInfo]:
        return [e for e in self.elements if e.is_flow]

    def _in_defs(self, e: ElementInfo) -> bool:
        return e.id in self._defs_ids

    @property
    def _defs_ids(self) -> set:
        ids = set()
        for d in self.root.iter():
            if isinstance(d.tag, str) and local(d.tag) in ("defs", "marker", "clipPath", "pattern", "symbol"):
                for sub in d.iter():
                    if isinstance(sub.tag, str) and sub.get("id"):
                        ids.add(sub.get("id"))
        return ids

    def content_bbox(self) -> Optional[BBox]:
        boxes = [e.bbox for e in self.shapes() if e.bbox is not None and not (e.tag == "rect" and e.bbox.x <= 0 and e.bbox.y <= 0 and e.bbox.w >= self.width and e.bbox.h >= self.height)]
        if not boxes:
            return None
        x1, y1 = min(b.x for b in boxes), min(b.y for b in boxes)
        x2, y2 = max(b.x2 for b in boxes), max(b.y2 for b in boxes)
        return BBox(x1, y1, x2 - x1, y2 - y1)

    def serialize(self) -> str:
        text = ET.tostring(self.root, encoding="unicode")
        return text if text.startswith("<svg") else text  # namespace already registered


def _canvas(root: ET.Element) -> Tuple[int, int]:
    """Canvas size in user units: the viewBox when present (geometry lives there), else width/height."""
    vb = root.get("viewBox")
    if vb:
        parts = [float(v) for v in re.split(r"[ ,]+", vb.strip()) if v]
        if len(parts) == 4 and parts[2] > 0 and parts[3] > 0:
            return int(round(parts[2])), int(round(parts[3]))
    return int(round(parse_len(root.get("width"), 0))), int(round(parse_len(root.get("height"), 0)))


_CMD = re.compile(r"([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)")


def path_extent_points(d: str) -> List[Tuple[float, float]]:
    """Every endpoint and control point of a path, absolute or relative commands alike.

    Curves are bounded by their control polygon, which is a safe (slightly generous) bbox.
    """
    pts: List[Tuple[float, float]] = []
    cx = cy = 0.0
    sx = sy = 0.0
    for cmd, args in _CMD.findall(d):
        nums = [float(n) for n in re.findall(r"-?\d*\.?\d+(?:e-?\d+)?", args)]
        rel = cmd.islower()
        c = cmd.upper()
        i = 0

        def take(n: int):
            nonlocal i
            vals = nums[i : i + n]
            i += n
            return vals

        if c == "Z":
            cx, cy = sx, sy
            continue
        while i < len(nums) or (c in "Z"):
            if c == "M":
                x, y = take(2)
                cx, cy = (cx + x, cy + y) if rel else (x, y)
                sx, sy = cx, cy
                pts.append((cx, cy))
                c = "L"  # subsequent pairs are implicit linetos
            elif c == "L" or c == "T":
                x, y = take(2)
                cx, cy = (cx + x, cy + y) if rel else (x, y)
                pts.append((cx, cy))
            elif c == "H":
                (x,) = take(1)
                cx = cx + x if rel else x
                pts.append((cx, cy))
            elif c == "V":
                (y,) = take(1)
                cy = cy + y if rel else y
                pts.append((cx, cy))
            elif c == "C":
                vals = take(6)
                for k in range(0, 6, 2):
                    px, py = (cx + vals[k], cy + vals[k + 1]) if rel else (vals[k], vals[k + 1])
                    pts.append((px, py))
                cx, cy = pts[-1]
            elif c in ("S", "Q"):
                vals = take(4)
                for k in range(0, 4, 2):
                    px, py = (cx + vals[k], cy + vals[k + 1]) if rel else (vals[k], vals[k + 1])
                    pts.append((px, py))
                cx, cy = pts[-1]
            elif c == "A":
                vals = take(7)
                ex, ey = (cx + vals[5], cy + vals[6]) if rel else (vals[5], vals[6])
                pts.append((ex, ey))  # arcs are bounded by their endpoints (radii ignored)
                cx, cy = ex, ey
            else:
                break
            if i >= len(nums):
                break
    return pts


def _shape_bbox(el: ET.Element, off: Tuple[int, int]) -> Optional[BBox]:
    tag = local(el.tag)
    ox, oy = off
    try:
        if tag in ("rect", "path", "line", "text"):
            bb = element_bbox(el, off)
            rot = re.search(r"rotate\(\s*(-?\d+(?:\.\d+)?)(?:[ ,]+(-?\d+(?:\.\d+)?)[ ,]+(-?\d+(?:\.\d+)?))?\s*\)", el.get("transform", "") or "")
            if bb is not None and tag == "text" and rot and abs(abs(float(rot.group(1))) - 90) < 1e-6:
                cx = int(float(rot.group(2))) + ox if rot.group(2) else bb.x + bb.w // 2
                cy = int(float(rot.group(3))) + oy if rot.group(3) else bb.y + bb.h // 2
                return BBox(cx - bb.h // 2, cy - bb.w // 2, bb.h, bb.w)
            return bb
        if tag == "circle":
            cx, cy, r = (parse_len(el.get(k), 0) for k in ("cx", "cy", "r"))
            return BBox(int(cx - r) + ox, int(cy - r) + oy, int(2 * r), int(2 * r))
        if tag == "ellipse":
            cx, cy, rx, ry = (parse_len(el.get(k), 0) for k in ("cx", "cy", "rx", "ry"))
            return BBox(int(cx - rx) + ox, int(cy - ry) + oy, int(2 * rx), int(2 * ry))
        if tag in ("polygon", "polyline"):
            nums = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", el.get("points", ""))]
            pts = list(zip(nums[0::2], nums[1::2]))
            if not pts:
                return None
            xs = [p[0] + ox for p in pts]
            ys = [p[1] + oy for p in pts]
            return BBox(int(min(xs)), int(min(ys)), int(max(xs) - min(xs)), int(max(ys) - min(ys)))
        if tag in ("image", "foreignObject", "use"):
            return BBox(int(parse_len(el.get("x"), 0)) + ox, int(parse_len(el.get("y"), 0)) + oy, int(parse_len(el.get("width"), 0)), int(parse_len(el.get("height"), 0)))
    except (ValueError, TypeError):
        return None
    return None


def load_program(svg_text: str) -> Program:
    root = parse_svg(svg_text)
    width, height = _canvas(root)
    elements: List[ElementInfo] = []
    existing = [int(m.group(1)) for el in root.iter() if isinstance(el.tag, str) and el.get("id") for m in [re.match(r"e(\d+)-", el.get("id"))] if m]
    counter = {"n": max(existing, default=0)}  # new ids continue the numbering
    assigned = {"n": 0}
    seen_ids: set = set()

    def ensure_id(el: ET.Element) -> str:
        eid = el.get("id")
        if not eid or eid in seen_ids:
            counter["n"] += 1
            eid = f"e{counter['n']}-{local(el.tag)}"
            el.set("id", eid)
            assigned["n"] += 1
        seen_ids.add(eid)
        return eid

    def walk(parent: ET.Element, parent_id: Optional[str], depth: int, off: Tuple[int, int], inherited: Dict[str, Optional[str]]) -> None:
        for el in list(parent):
            if not isinstance(el.tag, str):
                continue
            tag = local(el.tag)
            eid = ensure_id(el)
            inh = dict(inherited)
            for prop in ("fill", "stroke", "stroke-width", "font-size", "font-family"):
                v = attr(el, prop)
                if v is not None:
                    inh[prop] = v
            t = parse_translate(el.get("transform", "")) if el.get("transform") else (0, 0)
            own_off = (off[0] + t[0], off[1] + t[1])
            bbox = _shape_bbox(el, own_off) if tag in SHAPE_TAGS else None
            text = "".join(el.itertext()).strip() if tag == "text" else ""
            is_flow = tag in ("path", "line", "polyline") and bool(el.get("marker-end") or el.get("data-flow")) and el.get("data-role") != "block"
            pts: List[Tuple[int, int]] = []
            if tag == "path":
                pts = [(x + own_off[0], y + own_off[1]) for x, y in path_to_points(el.get("d", ""))]
            elif tag == "line":
                pts = [(int(parse_len(el.get("x1"), 0)) + own_off[0], int(parse_len(el.get("y1"), 0)) + own_off[1]), (int(parse_len(el.get("x2"), 0)) + own_off[0], int(parse_len(el.get("y2"), 0)) + own_off[1])]
            fs = inh.get("font-size")
            sw = inh.get("stroke-width")
            elements.append(
                ElementInfo(
                    id=eid, tag=tag, el=el, parent_id=parent_id, depth=depth, offset=own_off, bbox=bbox,
                    fill=inh.get("fill"), stroke=inh.get("stroke"),
                    stroke_width=parse_len(sw, 1.0) if sw is not None else None,
                    font_size=parse_len(fs, 16.0) if fs is not None else None,
                    font_family=inh.get("font-family"), text=text, is_flow=is_flow, points=pts,
                )
            )
            if tag in ("g", "svg", "a", "defs", "marker", "clipPath", "symbol", "pattern", "text"):
                walk(el, eid, depth + 1, own_off, inh)

    root_inh = {p: attr(root, p) for p in ("fill", "stroke", "stroke-width", "font-size", "font-family")}
    walk(root, None, 0, (0, 0), root_inh)
    return Program(root=root, width=width, height=height, elements=elements, assigned_ids=assigned["n"])


def normalize_svg(svg_text: str) -> Tuple[str, int]:
    """Return the SVG with every element addressable, and the number of ids assigned."""
    prog = load_program(svg_text)
    return prog.serialize(), prog.assigned_ids
