"""Tighten teaching SVGs when refine cannot auto-fix leading blank margins."""

from __future__ import annotations

import re
from typing import List

from figtree.edits import EditOp, apply_edits
from figtree.program import load_program, parse_len
from figtree.rubrics import RUBRICS
from figtree.svgmodel import local


def _fit_canvas(svg_text: str, margin: int) -> str:
    """Expand canvas so content bbox (+ margin) is fully visible; nudge if needed."""
    prog = load_program(svg_text)
    cb = prog.content_bbox()
    if cb is None:
        return svg_text
    ops: List[EditOp] = []
    dx = dy = 0
    if cb.x < margin:
        dx = margin - cb.x
    if cb.y < margin:
        dy = margin - cb.y
    if dx or dy:
        for child in list(prog.root):
            if not isinstance(child.tag, str):
                continue
            tag = local(child.tag)
            if tag in ("defs", "title", "desc", "metadata", "style"):
                continue
            if tag == "rect" and parse_len(child.get("width"), 0) >= prog.width and parse_len(
                child.get("height"), 0
            ) >= prog.height:
                continue
            cid = child.get("id")
            if cid:
                ops.append({"op": "translate", "id": cid, "dx": dx, "dy": dy})
        svg_text = apply_edits(svg_text, ops).svg
        prog = load_program(svg_text)
        cb = prog.content_bbox()
        if cb is None:
            return svg_text
    w = max(prog.width, cb.x2 + margin)
    h = max(prog.height, cb.y2 + margin)
    if w != prog.width or h != prog.height:
        svg_text = apply_edits(svg_text, [{"op": "set_canvas", "width": int(w), "height": int(h)}]).svg
    return svg_text


def trim_teaching_canvas(svg_text: str, *, rubric: str = "teaching") -> str:
    """Translate content to ``margin`` inset and size canvas to fit all content."""
    margin = int(RUBRICS[rubric].margin)
    prog = load_program(svg_text)
    cb = prog.content_bbox()
    if cb is None:
        return svg_text
    dx = margin - cb.x
    dy = margin - cb.y
    w = cb.w + 2 * margin
    h = cb.h + 2 * margin
    ops: List[EditOp] = []
    for child in list(prog.root):
        if not isinstance(child.tag, str):
            continue
        tag = local(child.tag)
        if tag in ("defs", "title", "desc", "metadata", "style"):
            continue
        if tag == "rect" and parse_len(child.get("width"), 0) >= prog.width and parse_len(
            child.get("height"), 0
        ) >= prog.height:
            continue
        cid = child.get("id")
        if cid and (dx or dy):
            ops.append({"op": "translate", "id": cid, "dx": dx, "dy": dy})
    ops.append({"op": "set_canvas", "width": w, "height": h})
    out = apply_edits(svg_text, ops).svg
    return _fit_canvas(out, margin)


def components_in_svg(svg_text: str) -> set[str]:
    return set(re.findall(r'data-component="([^"]+)"', svg_text))


def needs_leading_margin_trim(issues: list) -> bool:
    for issue in issues:
        if issue.get("check_id") != "compactness.blank_margin":
            continue
        if issue.get("auto_edit") is None and issue.get("visual_description", "").startswith(
            ("left margin", "top margin")
        ):
            return True
    return False
