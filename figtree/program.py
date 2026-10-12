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

from figtree.schemas import BBox
from figtree.svgmodel import SVG_NS, local, parse_svg

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


# ---------------------------------------------------------------------------
# Transforms (2x3 affine, SVG convention: x' = a*x + c*y + e, y' = b*x + d*y + f)
# ---------------------------------------------------------------------------

Matrix = Tuple[float, float, float, float, float, float]
IDENTITY: Matrix = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
_TRANSFORM_RE = re.compile(r"(matrix|translate|scale|rotate|skewX|skewY)\s*\(([^)]*)\)")


def mat_mul(m: Matrix, n: Matrix) -> Matrix:
    """``m`` then ``n`` applied to a point is ``mat_mul(m, n)`` (n is applied first)."""
    a1, b1, c1, d1, e1, f1 = m
    a2, b2, c2, d2, e2, f2 = n
    return (a1 * a2 + c1 * b2, b1 * a2 + d1 * b2, a1 * c2 + c1 * d2, b1 * c2 + d1 * d2, a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1)


def mat_apply(m: Matrix, x: float, y: float) -> Tuple[float, float]:
    a, b, c, d, e, f = m
    return (a * x + c * y + e, b * x + d * y + f)


def parse_transform(transform: Optional[str]) -> Matrix:
    """Full ``transform`` list: translate, scale, rotate (with or without a centre), matrix, skew."""
    import math

    m = IDENTITY
    for name, args in _TRANSFORM_RE.findall(transform or ""):
        nums = [float(v) for v in re.findall(r"-?\d*\.?\d+(?:e-?\d+)?", args)]
        t: Matrix = IDENTITY
        if name == "translate" and nums:
            t = (1, 0, 0, 1, nums[0], nums[1] if len(nums) > 1 else 0.0)
        elif name == "scale" and nums:
            t = (nums[0], 0, 0, nums[1] if len(nums) > 1 else nums[0], 0, 0)
        elif name == "rotate" and nums:
            r = math.radians(nums[0])
            rot: Matrix = (math.cos(r), math.sin(r), -math.sin(r), math.cos(r), 0, 0)
            if len(nums) >= 3:
                cx, cy = nums[1], nums[2]
                t = mat_mul(mat_mul((1, 0, 0, 1, cx, cy), rot), (1, 0, 0, 1, -cx, -cy))
            else:
                t = rot
        elif name == "matrix" and len(nums) >= 6:
            t = tuple(nums[:6])  # type: ignore[assignment]
        elif name == "skewX" and nums:
            t = (1, 0, math.tan(math.radians(nums[0])), 1, 0, 0)
        elif name == "skewY" and nums:
            t = (1, math.tan(math.radians(nums[0])), 0, 1, 0, 0)
        m = mat_mul(m, t)
    return m


def is_axis_aligned(m: Matrix) -> bool:
    return abs(m[1]) < 1e-9 and abs(m[2]) < 1e-9


Extent = Tuple[float, float, float, float]  # x1, y1, x2, y2 (floats)


def transform_extent(m: Matrix, ext: Extent) -> Tuple[Extent, Optional[List[Tuple[float, float]]]]:
    """Axis-aligned extent of a transformed box, plus its corners when the box is rotated/skewed."""
    x1, y1, x2, y2 = ext
    corners = [mat_apply(m, x, y) for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2))]
    xs = [p[0] for p in corners]
    ys = [p[1] for p in corners]
    return (min(xs), min(ys), max(xs), max(ys)), (None if is_axis_aligned(m) else corners)


def extent_to_bbox(ext: Extent) -> BBox:
    import math

    x1, y1, x2, y2 = ext
    X1, Y1 = int(math.floor(x1 + 1e-6)), int(math.floor(y1 + 1e-6))
    X2, Y2 = int(math.ceil(x2 - 1e-6)), int(math.ceil(y2 - 1e-6))
    return BBox(X1, Y1, max(0, X2 - X1), max(0, Y2 - Y1))


# ---------------------------------------------------------------------------
# Glyph metrics (advance widths in 1/1000 em) for the two font classes the critic meets:
# a Times-class serif (the house font) and an Arial/Helvetica-class sans (chart exports).
# ---------------------------------------------------------------------------

def _table(spec: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for item in spec.split():
        ch, w = item[:-4], item[-4:]
        if ch == "sp":
            ch = " "
        out[ch] = int(w)
    return out


GLYPH_SERIF = _table(
    "sp0250 a0444 b0500 c0444 d0500 e0444 f0333 g0500 h0500 i0278 j0278 k0500 l0278 m0778 n0500 o0500 p0500 q0500 r0333 s0389 t0278 u0500 v0500 w0722 x0500 y0500 z0444 "
    "A0722 B0667 C0667 D0722 E0611 F0556 G0722 H0722 I0333 J0389 K0722 L0611 M0889 N0722 O0722 P0556 Q0722 R0667 S0556 T0611 U0722 V0722 W0944 X0722 Y0722 Z0611 "
    "00500 10500 20500 30500 40500 50500 60500 70500 80500 90500 .0250 ,0250 :0278 ;0278 -0333 (0333 )0333 [0333 ]0333 %0833 $0500 +0564 =0564 /0278 '0180 \"0408 &0778 *0500 !0333 ?0444 @0921 _0500 <0564 >0564 °0400 –0500 —1000 ‘0333 ’0333 “0444 ”0444 €0500 £0500"
)
GLYPH_SANS = _table(
    "sp0278 a0556 b0556 c0500 d0556 e0556 f0278 g0556 h0556 i0222 j0222 k0500 l0222 m0833 n0556 o0556 p0556 q0556 r0333 s0500 t0278 u0556 v0500 w0722 x0500 y0500 z0500 "
    "A0667 B0667 C0722 D0722 E0667 F0611 G0778 H0722 I0278 J0500 K0667 L0556 M0833 N0722 O0778 P0667 Q0778 R0722 S0667 T0611 U0722 V0667 W0944 X0667 Y0667 Z0611 "
    "00556 10556 20556 30556 40556 50556 60556 70556 80556 90556 .0278 ,0278 :0278 ;0278 -0333 (0333 )0333 [0278 ]0278 %0889 $0556 +0584 =0584 /0278 '0191 \"0355 &0667 *0389 !0278 ?0556 @1015 _0556 <0584 >0584 °0400 –0556 —1000 ‘0222 ’0222 “0333 ”0333 €0556 £0556"
)
_SERIF_HINT = re.compile(r"times|georgia|garamond|serif|liberation serif|cambria|palatino|book", re.IGNORECASE)
_SANS_HINT = re.compile(r"sans|arial|helvetica|verdana|plex|inter|roboto|segoe|calibri|tahoma", re.IGNORECASE)


def glyph_table(font_family: Optional[str]) -> Dict[str, int]:
    fam = (font_family or "").split(",")[0]
    if _SANS_HINT.search(fam):
        return GLYPH_SANS
    if _SERIF_HINT.search(fam):
        return GLYPH_SERIF
    return GLYPH_SANS


def text_width(text: str, size: float, font_family: Optional[str] = None, bold: bool = False) -> float:
    """Advance width of ``text`` in user units from the per-glyph table of the font class."""
    tab = glyph_table(font_family)
    default = 500 if tab is GLYPH_SERIF else 556
    total = sum(tab.get(ch, default) for ch in text)
    return total / 1000.0 * size * (1.07 if bold else 1.0)


def is_bold(el: ET.Element, inh: Optional[Dict[str, Optional[str]]] = None) -> bool:
    w = attr(el, "font-weight") or (inh or {}).get("font-weight") or ""
    return w.lower() in ("bold", "bolder") or (w.isdigit() and int(w) >= 600)


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
    corners: Optional[List[Tuple[float, float]]] = None  # oriented box when rotated/skewed
    ink: Optional[Extent] = None  # stroke-inclusive float extent on the canvas
    visible: bool = True
    matrix: Matrix = IDENTITY
    role: str = ""  # data-role

    @property
    def centre(self) -> Tuple[float, float]:
        if self.bbox is None:
            return (0.0, 0.0)
        return (self.bbox.x + self.bbox.w / 2.0, self.bbox.y + self.bbox.h / 2.0)


ANIMATION_ROLES = ("pulse", "anim-shaft")


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
        """Visible drawable elements outside <defs>, animation overlays excluded."""
        return [e for e in self.elements if e.tag in SHAPE_TAGS and e.bbox is not None and e.visible and e.role not in ANIMATION_ROLES and not self._in_defs(e)]

    def hidden_shapes(self) -> List[ElementInfo]:
        """Drawable elements that render nothing (opacity 0, display none, no fill and no stroke, background-coloured)."""
        return [e for e in self.elements if e.tag in SHAPE_TAGS and not e.visible and e.role not in ANIMATION_ROLES and not self._in_defs(e)]

    def texts(self) -> List[ElementInfo]:
        return [e for e in self.elements if e.tag == "text" and e.visible and not self._in_defs(e)]

    def flows(self) -> List[ElementInfo]:
        return [e for e in self.elements if e.is_flow and e.visible]

    def background_color(self) -> Tuple[int, int, int]:
        for e in self.elements:
            if self.is_background(e):
                return parse_color(e.fill) or (255, 255, 255)
        return (255, 255, 255)

    def is_background(self, e: ElementInfo) -> bool:
        return (e.tag == "rect" and e.bbox is not None and e.corners is None and parse_color(e.fill) is not None
                and e.bbox.x <= 0 and e.bbox.y <= 0 and e.bbox.w >= self.width and e.bbox.h >= self.height)

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

    def content_extent(self) -> Optional[Extent]:
        """Stroke-inclusive extent of the visible content (background rect and animation overlays excluded)."""
        exts = [e.ink or (e.bbox.x, e.bbox.y, e.bbox.x2, e.bbox.y2) for e in self.shapes() if e.bbox is not None and not self.is_background(e)]
        if not exts:
            return None
        return (min(x[0] for x in exts), min(x[1] for x in exts), max(x[2] for x in exts), max(x[3] for x in exts))

    def content_bbox(self) -> Optional[BBox]:
        ext = self.content_extent()
        return None if ext is None else extent_to_bbox(ext)

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


def path_extent_points(d: str, controls: bool = True) -> List[Tuple[float, float]]:
    """Every endpoint (and, with ``controls``, every control point) of a path, absolute or relative.

    Curves are bounded by their control polygon, which is a safe (slightly generous) bbox.
    Without ``controls`` the result is the vertex list a flow check needs (curve endpoints only).
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
            if pts and pts[-1] != (sx, sy) and not controls:
                pts.append((sx, sy))
            continue
        while i < len(nums):
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
                if len(vals) < 6:
                    break
                for k in range(0, 6, 2):
                    px, py = (cx + vals[k], cy + vals[k + 1]) if rel else (vals[k], vals[k + 1])
                    if controls or k == 4:
                        pts.append((px, py))
                cx, cy = (cx + vals[4], cy + vals[5]) if rel else (vals[4], vals[5])
            elif c in ("S", "Q"):
                vals = take(4)
                if len(vals) < 4:
                    break
                for k in range(0, 4, 2):
                    px, py = (cx + vals[k], cy + vals[k + 1]) if rel else (vals[k], vals[k + 1])
                    if controls or k == 2:
                        pts.append((px, py))
                cx, cy = (cx + vals[2], cy + vals[3]) if rel else (vals[2], vals[3])
            elif c == "A":
                vals = take(7)
                if len(vals) < 7:
                    break
                ex, ey = (cx + vals[5], cy + vals[6]) if rel else (vals[5], vals[6])
                if controls:  # sample the arc itself (SVG F.6.5 endpoint -> centre conversion)
                    pts.extend(arc_points(cx, cy, vals[0], vals[1], vals[2], vals[3], vals[4], ex, ey))
                pts.append((ex, ey))
                cx, cy = ex, ey
            else:
                break
    return pts


def arc_points(x1: float, y1: float, rx: float, ry: float, phi: float, fa: float, fs: float, x2: float, y2: float, n: int = 12) -> List[Tuple[float, float]]:
    """Points along an SVG elliptical arc (endpoint parametrisation, SVG 1.1 F.6.5)."""
    import math

    rx, ry = abs(rx), abs(ry)
    if rx == 0 or ry == 0 or (x1 == x2 and y1 == y2):
        return [(x2, y2)]
    p = math.radians(phi)
    cp, sp = math.cos(p), math.sin(p)
    dx, dy = (x1 - x2) / 2.0, (y1 - y2) / 2.0
    x1p = cp * dx + sp * dy
    y1p = -sp * dx + cp * dy
    lam = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    coef = 0.0 if den == 0 else math.sqrt(max(0.0, num / den))
    if (fa != 0) == (fs != 0):
        coef = -coef
    cxp, cyp = coef * rx * y1p / ry, -coef * ry * x1p / rx
    cx = cp * cxp - sp * cyp + (x1 + x2) / 2.0
    cy = sp * cxp + cp * cyp + (y1 + y2) / 2.0

    def ang(ux: float, uy: float, vx: float, vy: float) -> float:
        d = math.hypot(ux, uy) * math.hypot(vx, vy)
        if d == 0:
            return 0.0
        a = math.acos(max(-1.0, min(1.0, (ux * vx + uy * vy) / d)))
        return -a if ux * vy - uy * vx < 0 else a

    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if fs == 0 and dt > 0:
        dt -= 2 * math.pi
    elif fs != 0 and dt < 0:
        dt += 2 * math.pi
    out = []
    for k in range(1, n):
        t = t1 + dt * k / n
        ex, ey = rx * math.cos(t), ry * math.sin(t)
        out.append((cp * ex - sp * ey + cx, sp * ex + cp * ey + cy))
    return out


def path_subpaths(d: str) -> int:
    """Number of subpaths (``M``/``m`` commands) in a path: the stroke count an icon family sees."""
    return len(re.findall(r"[Mm]", d or ""))


def _text_local_extent(el: ET.Element, inh: Dict[str, Optional[str]]) -> Optional[Extent]:
    """Local extent of a text element from the glyph table, honouring tspans with their own x/y."""
    size = parse_len(inh.get("font-size"), 16.0) if inh.get("font-size") is not None else 16.0
    family = inh.get("font-family")
    bold = is_bold(el, inh)
    spans = [t for t in el.findall(f"{{{SVG_NS}}}tspan")]
    baseline = (attr(el, "dominant-baseline") or inh.get("dominant-baseline") or "").lower()
    shift = 0.0 if baseline in ("middle", "central") else -0.3 * size
    anchor = attr(el, "text-anchor") or inh.get("text-anchor") or "start"
    lh = size * 1.2

    def box(x: float, y: float, w: float) -> Extent:
        if anchor == "middle":
            x -= w / 2.0
        elif anchor == "end":
            x -= w
        yc = y + shift
        return (x, yc - lh / 2.0, x + w, yc + lh / 2.0)

    tx, ty = el.get("x"), el.get("y")
    lines = [("".join(t.itertext()) or "") for t in spans] if spans else ["".join(el.itertext()) or ""]
    if spans and (tx is None or ty is None):  # editor export: coordinates live on the tspans
        first = spans[0]
        tx = tx if tx is not None else first.get("x")
        ty = ty if ty is not None else first.get("y")
    x0 = parse_len(tx, 0.0) if tx is not None else 0.0
    y0 = parse_len(ty, 0.0) if ty is not None else 0.0
    exts: List[Extent] = []
    if spans and any(t.get("y") is not None for t in spans):
        for i, (t, line) in enumerate(zip(spans, lines)):
            x = parse_len(t.get("x"), x0) if t.get("x") is not None else x0
            y = parse_len(t.get("y"), y0 + i * lh) if t.get("y") is not None else (y0 + i * lh)
            exts.append(box(x, y, text_width(line, size, family, bold)))
    else:
        n = max(1, len(lines))
        w = max(text_width(line, size, family, bold) for line in lines)
        h = lh * n
        yc = y0 + shift
        x = x0 - (w / 2.0 if anchor == "middle" else w if anchor == "end" else 0.0)
        exts.append((x, yc - h / 2.0, x + w, yc + h / 2.0))
    return (min(e[0] for e in exts), min(e[1] for e in exts), max(e[2] for e in exts), max(e[3] for e in exts))


def _local_extent(el: ET.Element, inh: Dict[str, Optional[str]]) -> Optional[Extent]:
    tag = local(el.tag)
    try:
        if tag == "rect":
            x, y = parse_len(el.get("x"), 0.0), parse_len(el.get("y"), 0.0)
            w, h = parse_len(el.get("width"), 0.0), parse_len(el.get("height"), 0.0)
            return (x, y, x + w, y + h)
        if tag == "circle":
            cx, cy, r = (parse_len(el.get(k), 0.0) for k in ("cx", "cy", "r"))
            return (cx - r, cy - r, cx + r, cy + r)
        if tag == "ellipse":
            cx, cy, rx, ry = (parse_len(el.get(k), 0.0) for k in ("cx", "cy", "rx", "ry"))
            return (cx - rx, cy - ry, cx + rx, cy + ry)
        if tag == "line":
            x1, y1, x2, y2 = (parse_len(el.get(k), 0.0) for k in ("x1", "y1", "x2", "y2"))
            return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        if tag in ("polygon", "polyline"):
            pts = polyline_points(el.get("points", ""))
            if not pts:
                return None
            return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))
        if tag == "path":
            pts = path_extent_points(el.get("d", ""))
            if not pts:
                return None
            return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))
        if tag == "text":
            return _text_local_extent(el, inh)
        if tag in ("image", "foreignObject", "use"):
            x, y = parse_len(el.get("x"), 0.0), parse_len(el.get("y"), 0.0)
            return (x, y, x + parse_len(el.get("width"), 0.0), y + parse_len(el.get("height"), 0.0))
    except (ValueError, TypeError):
        return None
    return None


def polyline_points(points: str) -> List[Tuple[float, float]]:
    nums = [float(n) for n in re.findall(r"-?\d*\.?\d+(?:e-?\d+)?", points or "")]
    return list(zip(nums[0::2], nums[1::2]))


def _is_visible(tag: str, el: ET.Element, inh: Dict[str, Optional[str]], background: Tuple[int, int, int]) -> bool:
    if (inh.get("display") or "").strip().lower() == "none" or (inh.get("visibility") or "").strip().lower() in ("hidden", "collapse"):
        return False
    try:
        if inh.get("opacity") is not None and float(inh["opacity"]) <= 0.0:
            return False
    except ValueError:
        pass
    if tag in ("text", "image", "foreignObject", "use"):
        return True
    fill = (inh.get("fill") or "").strip().lower()
    stroke = (inh.get("stroke") or "").strip().lower()
    fill_none = fill in ("none", "transparent")
    stroke_none = stroke in ("", "none", "transparent")
    if fill_none and stroke_none:
        return False
    if not fill_none and stroke_none and fill:
        c = parse_color(fill)
        if c is not None and c == background and tag in ("rect", "circle", "ellipse", "polygon", "path"):
            return False  # background-coloured shape with no outline: invisible on the page
    return True


def load_program(svg_text: str) -> Program:
    root = parse_svg(svg_text)
    width, height = _canvas(root)
    elements: List[ElementInfo] = []
    existing = [int(m.group(1)) for el in root.iter() if isinstance(el.tag, str) and el.get("id") for m in [re.match(r"e(\d+)-", el.get("id"))] if m]
    counter = {"n": max(existing, default=0)}  # new ids continue the numbering
    assigned = {"n": 0}
    seen_ids: set = set()
    background = (255, 255, 255)
    for el in root:
        if isinstance(el.tag, str) and local(el.tag) == "rect":
            try:
                if parse_len(el.get("width"), 0) >= width and parse_len(el.get("height"), 0) >= height and parse_len(el.get("x"), 0) <= 0 and parse_len(el.get("y"), 0) <= 0:
                    c = parse_color(attr(el, "fill"))
                    if c is not None:
                        background = c
                        break
            except ValueError:
                pass

    def ensure_id(el: ET.Element) -> str:
        eid = el.get("id")
        if not eid or eid in seen_ids:
            counter["n"] += 1
            eid = f"e{counter['n']}-{local(el.tag)}"
            el.set("id", eid)
            assigned["n"] += 1
        seen_ids.add(eid)
        return eid

    INHERITED = ("fill", "stroke", "stroke-width", "font-size", "font-family", "font-weight", "text-anchor", "dominant-baseline", "display", "visibility")

    def walk(parent: ET.Element, parent_id: Optional[str], depth: int, matrix: Matrix, inherited: Dict[str, Optional[str]]) -> None:
        for el in list(parent):
            if not isinstance(el.tag, str):
                continue
            tag = local(el.tag)
            eid = ensure_id(el)
            inh = dict(inherited)
            for prop in INHERITED:
                v = attr(el, prop)
                if v is not None:
                    inh[prop] = v
            op = attr(el, "opacity")
            if op is not None:
                try:
                    inh["opacity"] = str(float(op) * float(inherited.get("opacity") or 1.0))
                except ValueError:
                    pass
            own_m = mat_mul(matrix, parse_transform(el.get("transform"))) if el.get("transform") else matrix
            own_off = (int(round(own_m[4])), int(round(own_m[5])))
            bbox: Optional[BBox] = None
            corners = None
            ink: Optional[Extent] = None
            sw = inh.get("stroke-width")
            stroke_w = parse_len(sw, 1.0) if sw is not None else None
            if tag in SHAPE_TAGS:
                if tag == "path" and el.get("data-bbox"):  # shaped block: trust the declared bbox (translate included)
                    try:
                        x, y, w, h = (float(v) for v in el.get("data-bbox").split())
                        ext, corners = transform_extent(matrix, (x, y, x + w, y + h))
                    except ValueError:
                        ext = None
                else:
                    loc = _local_extent(el, inh)
                    ext, corners = (transform_extent(own_m, loc) if loc is not None else (None, None))
                if ext is not None:
                    bbox = extent_to_bbox(ext)
                    stroke = (inh.get("stroke") or "").strip().lower()
                    pad = 0.0
                    if tag != "text" and stroke not in ("", "none", "transparent"):
                        scale = max(abs(own_m[0]), abs(own_m[3]), abs(own_m[1]), abs(own_m[2]))
                        pad = (stroke_w if stroke_w is not None else 1.0) * scale / 2.0
                    ink = (ext[0] - pad, ext[1] - pad, ext[2] + pad, ext[3] + pad)
            text = "".join(el.itertext()).strip() if tag == "text" else ""
            role = el.get("data-role") or ""
            is_flow = tag in ("path", "line", "polyline") and bool(el.get("marker-end") or el.get("data-flow")) and role not in ("block", "anim-shaft")
            pts: List[Tuple[int, int]] = []
            raw: List[Tuple[float, float]] = []
            if tag == "path":
                raw = path_extent_points(el.get("d", ""), controls=False)
            elif tag == "line":
                raw = [(parse_len(el.get("x1"), 0.0), parse_len(el.get("y1"), 0.0)), (parse_len(el.get("x2"), 0.0), parse_len(el.get("y2"), 0.0))]
            elif tag in ("polyline", "polygon"):
                raw = polyline_points(el.get("points", ""))
                if tag == "polygon" and raw and raw[0] != raw[-1]:
                    raw.append(raw[0])
            if raw:
                pts = [(int(round(x)), int(round(y))) for x, y in (mat_apply(own_m, px, py) for px, py in raw)]
            fs = inh.get("font-size")
            visible = _is_visible(tag, el, inh, background) if tag in SHAPE_TAGS else True
            if not visible and tag == "rect" and bbox is not None and corners is None and bbox.x <= 0 and bbox.y <= 0 and bbox.w >= width and bbox.h >= height and (inh.get("display") or "").lower() != "none":
                visible = True  # the page background itself
            elements.append(
                ElementInfo(
                    id=eid, tag=tag, el=el, parent_id=parent_id, depth=depth, offset=own_off, bbox=bbox,
                    fill=inh.get("fill"), stroke=inh.get("stroke"),
                    stroke_width=stroke_w,
                    font_size=parse_len(fs, 16.0) if fs is not None else None,
                    font_family=inh.get("font-family"), text=text, is_flow=is_flow, points=pts,
                    corners=corners, ink=ink, visible=visible, matrix=own_m, role=role,
                )
            )
            if tag in ("g", "svg", "a", "defs", "marker", "clipPath", "symbol", "pattern", "text"):
                walk(el, eid, depth + 1, own_m, inh)

    root_inh = {p: attr(root, p) for p in INHERITED}
    walk(root, None, 0, IDENTITY, root_inh)
    return Program(root=root, width=width, height=height, elements=elements, assigned_ids=assigned["n"])


def normalize_svg(svg_text: str) -> Tuple[str, int]:
    """Return the SVG with every element addressable, and the number of ids assigned."""
    prog = load_program(svg_text)
    return prog.serialize(), prog.assigned_ids
