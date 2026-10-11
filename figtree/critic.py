"""Structural Critic agent (dual-space review, code side).

The checklist follows the specification.  When a renderer is available the rendered PNG is
checked for basic sanity (non-blank, expected dimensions); otherwise the ``no-vision``
residual flag is raised and only structural rules apply.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Set

from figtree.geometry import is_orthogonal, on_grid, path_hits_boxes, path_to_points, final_segment_length
from figtree.memory import VerificationMemory
from figtree.schemas import BBox, GlobalStyle, ResidualDefect
from figtree.svgmodel import (
    SVG_NS,
    element_bbox,
    extract_ports,
    iter_elements,
    local,
    parse_svg,
)

_URL_REF = re.compile(r"url\(#([^)]+)\)")


class StructuralCritic:
    def __init__(self, memory: Optional[VerificationMemory] = None, max_chars: int = 5000) -> None:
        self.memory = memory or VerificationMemory()
        self.max_chars = max_chars  # mirrors the prompt budget; structural rules see the full source

    def _fix(self, condition: str, default: str) -> str:
        return self.memory.repair_for(condition) or default

    # ------------------------------------------------------------------
    def review(
        self,
        svg_text: str,
        style: GlobalStyle,
        rendered_path: Optional[str] = None,
        round_no: int = 0,
        padded: bool = True,
    ) -> List[ResidualDefect]:
        """Review ``svg_text``.  ``padded`` is False for leaf fragments, whose canvas is the block itself."""
        defects: List[ResidualDefect] = []

        def add(sev: str, desc: str, anchor: str, fix: str) -> None:
            defects.append(ResidualDefect(sev, desc, anchor, fix, round_no))

        try:
            root = parse_svg(svg_text)
        except Exception as exc:  # noqa: BLE001
            add("critical", f"SVG parse failure: {exc}", "svg", "roll back to last valid fragment")
            return defects

        W = int(float(root.get("width", 0)))
        H = int(float(root.get("height", 0)))
        canvas = BBox(0, 0, W, H)
        grid, pad = style.grid, style.padding
        palette_values = {v.upper() for v in style.palette.values()} | {"#FFFFFF", "NONE"}

        # white background first
        first = next((c for c in root if local(c.tag) not in ("comment", "title")), None)
        if first is None or local(first.tag) != "rect" or first.get("fill", "").upper() != "#FFFFFF":
            add("warning", "white background rect is not the first element", "background", "insert white background rect first")

        # markers
        marker_ids: Set[str] = {el.get("id") for el in root.iter() if local(el.tag) == "marker" and el.get("id")}
        for el, _ in iter_elements(root):
            tag = local(el.tag)
            if tag in ("linearGradient", "radialGradient", "filter"):
                add("warning", f"{tag} present; only flat fills are allowed", el.get("id", tag), self._fix("gradient present", "replace with flat fill from palette"))

        ports = extract_ports(svg_text)
        port_by_id: Dict[str, dict] = {}
        for p in ports:
            if p["id"] in port_by_id and (port_by_id[p["id"]]["abs_x"], port_by_id[p["id"]]["abs_y"]) != (p["abs_x"], p["abs_y"]):
                add("warning", f"port id collision: {p['id']}", p["id"], self._fix("port collision", "prefix with node id"))
            port_by_id.setdefault(p["id"], p)
        port_points = {(p["abs_x"], p["abs_y"]) for p in ports}

        block_boxes: List[tuple] = []  # (id, bbox)
        group_boxes: Dict[str, List[tuple]] = {}  # parent id -> [(id, bbox)]
        content: List[BBox] = []
        text_count = 0

        for el, off in iter_elements(root):
            tag = local(el.tag)
            eid = el.get("id", tag) if tag != "comment" else "comment"
            if tag == "comment":
                continue
            if tag in ("defs", "marker", "title", "tspan", "svg"):
                continue
            if tag == "g":
                bb = el.get("data-bbox")
                if bb:
                    x, y, w, h = (int(float(v)) for v in bb.split())
                    for v in (x, y, w, h):
                        if not on_grid(v, grid):
                            add("warning", f"group {eid} not on {grid}px grid", eid, self._fix("ungrid coordinate", "ceil snap to multiple of 8"))
                            break
                continue
            if tag == "rect" and el.get("data-role") == "background":
                continue
            # fills / strokes
            fill = (el.get("fill") or "").upper()
            if tag == "use":
                fill = ""
            if _URL_REF.search(fill) or _URL_REF.search((el.get("stroke") or "")):
                add("warning", f"{eid} uses a paint server (gradient/pattern)", eid, self._fix("gradient present", "replace with flat fill from palette"))
            elif tag == "rect" and fill and fill not in palette_values:
                add("warning", f"{eid} fill {fill} is not in the palette", eid, "replace with flat fill from palette")
            if el.get("filter") or el.get("style"):
                add("warning", f"{eid} uses filter/style attributes", eid, "remove filters and inline styles")

            bbox = element_bbox(el, off)
            if bbox is not None:
                # a node's own container (spanning its canvas) and its title are frame chrome, not content
                is_chrome = (
                    tag == "rect" and el.get("data-role") == "container" and bbox.x == 0 and bbox.y == 0 and bbox.w == W and bbox.h == H
                ) or (tag == "text" and el.get("data-kind") == "annot" and el.get("id", "").endswith(".title"))
                if not is_chrome:
                    content.append(bbox)
                if not (bbox.x >= 0 and bbox.y >= 0 and bbox.x2 <= W and bbox.y2 <= H):
                    add("critical", f"{eid} overflows the canvas", eid, "expand canvas with padding and re-snap")

            if tag == "rect":
                coords = [el.get(k, "0") for k in ("x", "y", "width", "height")]
                if any(not on_grid(float(c), grid) for c in coords):
                    add("warning", f"{eid} not on {grid}px grid", eid, self._fix("ungrid coordinate", "ceil snap to multiple of 8"))
                sw = float(el.get("stroke-width", style.stroke_main))
                if abs(sw - style.stroke_main) > 1e-6 and abs(sw - style.stroke_border) > 1e-6:
                    add("warning", f"{eid} stroke width {sw} is not a style stroke", eid, "set stroke width to stroke_main or stroke_border")
                if el.get("data-role") == "block" and bbox is not None:
                    block_boxes.append((eid, bbox))
            elif tag == "text":
                text_count += 1
                size = float(el.get("font-size", 0))
                kind = el.get("data-kind", "label")
                lo, hi = style.label_range if kind == "label" else style.annot_range
                if not (lo <= size <= hi):
                    add("critical", f"{eid} font size {size:g}pt outside {lo}-{hi}pt", eid, f"set font size to {(lo + hi) // 2}")
                fam = el.get("font-family") or root.get("font-family") or ""
                if style.font.lower() not in fam.lower():
                    add("critical", f"{eid} font family {fam!r} is not {style.font}", eid, f"set font family to {style.font}")
                if any(not on_grid(float(el.get(k, "0")), grid) for k in ("x", "y")):
                    add("warning", f"{eid} not on {grid}px grid", eid, self._fix("ungrid coordinate", "ceil snap to multiple of 8"))
                mw = el.get("data-max-width")
                if mw and bbox is not None and bbox.w > int(mw) - 8:
                    add("critical", f"{eid} text overflows its block", eid, self._fix("text overflow", "reduce font or expand block"))
            elif tag == "path" and el.get("data-role") == "block":
                if bbox is not None:
                    block_boxes.append((eid, bbox))
                    if any(not on_grid(v, grid) for v in (bbox.x, bbox.y, bbox.w, bbox.h)):
                        add("warning", f"{eid} not on {grid}px grid", eid, self._fix("ungrid coordinate", "ceil snap to multiple of 8"))
            elif tag == "use":
                pass  # icons: library symbols, validated by the icon rubric
            elif tag in ("path", "line", "polyline"):
                if tag == "path":
                    pts = path_to_points(el.get("d", ""))
                elif tag == "line":
                    pts = [(int(float(el.get("x1", 0))), int(float(el.get("y1", 0)))), (int(float(el.get("x2", 0))), int(float(el.get("y2", 0))))]
                else:
                    pts = []
                if pts and not is_orthogonal(pts) and el.get("data-diagonal") != "semantic":
                    add("warning", f"{eid} has a diagonal segment without a semantic flag", eid, self._fix("diagonal without flag", "reroute to right-angle"))
                if any(not on_grid(x, grid) or not on_grid(y, grid) for x, y in pts):
                    add("warning", f"{eid} not on {grid}px grid", eid, self._fix("ungrid coordinate", "ceil snap to multiple of 8"))
                marker = el.get("marker-end", "")
                if marker:
                    m = _URL_REF.search(marker)
                    if not m or m.group(1) not in marker_ids:
                        add("critical", f"{eid} references an undefined marker", eid, "define the arrow marker in <defs>")
                    if final_segment_length(pts) < style.min_arrow:
                        add("warning", f"{eid} arrow shaft is {final_segment_length(pts)}px (< {style.min_arrow})", eid, self._fix("arrow length < 20", "shift target by ceil_to_grid(20-dist), recompute ports"))
                    # endpoints on ports
                    abs_pts = [(x + off[0], y + off[1]) for x, y in pts]
                    src_id, dst_id = el.get("data-from"), el.get("data-to")
                    if src_id and dst_id:
                        sp, dp = port_by_id.get(src_id), port_by_id.get(dst_id)
                        if sp is None or dp is None:
                            add("critical", f"{eid} refers to unknown ports", eid, "re-extract ports and reroute")
                        elif abs_pts[0] != (sp["abs_x"], sp["abs_y"]) or abs_pts[-1] != (dp["abs_x"], dp["abs_y"]):
                            add("critical", f"{eid} does not start/end at its ports", eid, "reroute between the declared ports")
                    elif ports and (abs_pts[0] not in port_points or abs_pts[-1] not in port_points):
                        add("warning", f"{eid} endpoints are not on declared ports", eid, "route between declared ports")
                    sw = float(el.get("stroke-width", style.stroke_main))
                    if abs(sw - style.stroke_main) > 1e-6:
                        add("warning", f"{eid} stroke width {sw} differs from stroke_main", eid, "set stroke width to stroke_main")
                    el.set("data-_abs", " ".join(f"{x},{y}" for x, y in abs_pts))
            elif tag in ("polygon",):
                add("warning", f"{eid} standalone polygon (triangle) outside marker", eid, "use a marker-ended path instead")

        # arrows through blocks
        for el, off in iter_elements(root):
            if local(el.tag) != "path" or not el.get("marker-end"):
                continue
            eid = el.get("id", "path")
            abs_pts = [tuple(int(v) for v in p.split(",")) for p in (el.get("data-_abs") or "").split()] if el.get("data-_abs") else []
            if not abs_pts:
                continue
            endpoints = {abs_pts[0], abs_pts[-1]}
            boxes = [b for bid, b in block_boxes if not any(b.contains_point(x, y, strict=False) for x, y in endpoints)]
            if path_hits_boxes(abs_pts, boxes):
                add("critical", f"{eid} clips through a block", eid, "reroute around the block (over-the-top detour)")

        # overlaps between blocks
        for i in range(len(block_boxes)):
            for j in range(i + 1, len(block_boxes)):
                a, b = block_boxes[i], block_boxes[j]
                if a[1].intersects(b[1]):
                    add("critical", f"blocks {a[0]} and {b[0]} overlap", a[0], self._fix("overlap after merge", "expand canvas or re-layout children"))

        if not block_boxes:
            add("critical", "no content blocks drawn", "svg", "draw the node content")
        if text_count == 0:
            add("critical", "no labels present", "svg", "add labels")

        # padding / empty space (merged canvases only; a leaf canvas is the block itself)
        if content and padded:
            x1 = min(b.x for b in content)
            y1 = min(b.y for b in content)
            x2 = max(b.x2 for b in content)
            y2 = max(b.y2 for b in content)
            if x1 < pad or y1 < pad or W - x2 < pad or H - y2 < pad:
                add("warning", f"content is closer than {pad}px to the canvas edge", "svg", "expand canvas with padding")
            if (W - x2) > pad + 2 * grid or (H - y2) > pad + 2 * grid or x1 > pad + 2 * grid or y1 > pad + 2 * grid:
                add("warning", "excessive empty space around content", "svg", "shrink canvas to content + padding")

        if rendered_path is None:
            add("warning", "no renderer available; structural review only", "no-vision", "install cairosvg or rsvg-convert for image review")
        else:
            defects.extend(self._review_image(rendered_path, W, H, round_no))
        return defects

    # ------------------------------------------------------------------
    @staticmethod
    def _review_image(path: str, W: int, H: int, round_no: int) -> List[ResidualDefect]:
        out: List[ResidualDefect] = []
        try:
            import struct
            import zlib

            with open(path, "rb") as fh:
                data = fh.read()
            if data[:8] != b"\x89PNG\r\n\x1a\n":
                raise ValueError("not a PNG")
            w, h = struct.unpack(">II", data[16:24])
            if (w, h) != (W, H):
                out.append(ResidualDefect("warning", f"rendered size {w}x{h} differs from canvas {W}x{H}", "render", "re-render at canvas size", round_no))
            # blank-image check: prefer Pillow when present, else inspect the raw IDAT stream
            try:
                from PIL import Image

                with Image.open(path) as im:
                    extrema = im.convert("L").getextrema()
                if extrema[0] == extrema[1]:
                    out.append(ResidualDefect("critical", "rendered image is blank", "render", "check that content is drawn inside the canvas", round_no))
                return out
            except ImportError:
                pass
            idat = b"".join(
                data[i + 8 : i + 8 + struct.unpack(">I", data[i : i + 4])[0]]
                for i in _png_chunks(data)
                if data[i + 4 : i + 8] == b"IDAT"
            )
            raw = zlib.decompress(idat)
            if raw and all(b in (0, 255) for b in raw[: min(len(raw), 2_000_000)]):
                out.append(ResidualDefect("critical", "rendered image is blank", "render", "check that content is drawn inside the canvas", round_no))
        except Exception as exc:  # noqa: BLE001
            out.append(ResidualDefect("warning", f"could not inspect render: {exc}", "no-vision", "structural rules only", round_no))
        return out


def _png_chunks(data: bytes):
    i = 8
    while i + 8 <= len(data):
        import struct

        length = struct.unpack(">I", data[i : i + 4])[0]
        yield i
        i += 12 + length
