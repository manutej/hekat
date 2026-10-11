"""Edit scripts: anchored, local edits to an addressable SVG program.

An edit request (from a human, a critic rule, or a VLM) is a list of operations, each anchored
to an element id.  Applying a script never regenerates the figure: only the addressed elements
change, which is what keeps the editability property measurable (``element_diff``).

Operations::

    {"op": "set_attr",   "id": "e3-text", "attr": "font-size", "value": "14"}
    {"op": "set_text",   "id": "e3-text", "text": "Accuracy (%)"}
    {"op": "translate",  "id": "e9-g",    "dx": 8, "dy": 0}
    {"op": "recolor",    "id": "e4-rect", "fill": "#7BA3C9"}          # stroke optional
    {"op": "delete",     "id": "e5-path"}
    {"op": "insert",     "parent_id": "root-or-group-id", "svg": "<text ...>..</text>"}
    {"op": "scale_font", "min": 14}                                    # all texts below min
    {"op": "set_canvas", "width": 960, "height": 540}
    {"op": "center_content"}                                           # translate all top-level content to the canvas centre
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from figtree.program import Program, attr, load_program, parse_len, style_props
from figtree.svgmodel import SVG_NS, local

EditOp = Dict[str, Any]


@dataclass
class EditResult:
    svg: str
    applied: List[EditOp] = field(default_factory=list)
    failed: List[Tuple[EditOp, str]] = field(default_factory=list)


def _set_prop(el: ET.Element, name: str, value: str) -> None:
    """Set a presentation attribute, removing a conflicting ``style`` property."""
    props = style_props(el)
    if name in props:
        del props[name]
        if props:
            el.set("style", ";".join(f"{k}:{v}" for k, v in props.items()))
        else:
            el.attrib.pop("style", None)
    el.set(name, str(value))


def _apply_one(prog: Program, op: EditOp) -> None:
    kind = op.get("op")
    if kind == "set_attr":
        el = prog.element(op["id"])
        if el is None:
            raise KeyError(op["id"])
        _set_prop(el, op["attr"], str(op["value"]))
    elif kind == "set_text":
        el = prog.element(op["id"])
        if el is None:
            raise KeyError(op["id"])
        spans = [c for c in el if isinstance(c.tag, str) and local(c.tag) == "tspan"]
        if spans:
            spans[0].text = str(op["text"])
            for extra in spans[1:]:
                el.remove(extra)
        else:
            el.text = str(op["text"])
    elif kind == "translate":
        el = prog.element(op["id"])
        if el is None:
            raise KeyError(op["id"])
        dx, dy = int(op.get("dx", 0)), int(op.get("dy", 0))
        tag = local(el.tag)
        if tag in ("rect", "text", "image", "use", "foreignObject") and el.get("x") is not None:
            el.set("x", str(int(parse_len(el.get("x"), 0)) + dx))
            el.set("y", str(int(parse_len(el.get("y"), 0)) + dy))
        elif tag in ("circle", "ellipse"):
            el.set("cx", str(int(parse_len(el.get("cx"), 0)) + dx))
            el.set("cy", str(int(parse_len(el.get("cy"), 0)) + dy))
        else:
            m = re.search(r"translate\(\s*(-?\d+(?:\.\d+)?)[ ,]\s*(-?\d+(?:\.\d+)?)\s*\)", el.get("transform", "") or "")
            tx, ty = (float(m.group(1)), float(m.group(2))) if m else (0.0, 0.0)
            rest = re.sub(r"translate\([^)]*\)", "", el.get("transform", "") or "").strip()
            el.set("transform", f"translate({int(tx + dx)},{int(ty + dy)}) {rest}".strip())
    elif kind == "recolor":
        el = prog.element(op["id"])
        if el is None:
            raise KeyError(op["id"])
        if "fill" in op:
            _set_prop(el, "fill", op["fill"])
        if "stroke" in op:
            _set_prop(el, "stroke", op["stroke"])
    elif kind == "delete":
        parent = prog.parent_of(op["id"])
        el = prog.element(op["id"])
        if parent is None or el is None:
            raise KeyError(op["id"])
        parent.remove(el)
    elif kind == "insert":
        parent = prog.element(op["parent_id"]) if op.get("parent_id") else prog.root
        if parent is None:
            raise KeyError(op.get("parent_id"))
        snippet = op["svg"]
        if "xmlns" not in snippet:
            snippet = re.sub(r"^<(\w+)", rf'<\1 xmlns="{SVG_NS}"', snippet.strip(), count=1)
        new = ET.fromstring(snippet)
        parent.append(new)
    elif kind == "scale_font":
        minimum = float(op["min"])
        for info in prog.texts():
            if info.font_size is not None and info.font_size < minimum:
                _set_prop(info.el, "font-size", f"{minimum:g}")
            elif info.font_size is None:
                _set_prop(info.el, "font-size", f"{minimum:g}")
    elif kind == "center_content":
        cb = prog.content_bbox()
        if cb is None:
            raise ValueError("no content to centre")
        dx = int(round((prog.width - cb.w) / 2 - cb.x))
        dy = int(round((prog.height - cb.h) / 2 - cb.y))
        for child in list(prog.root):
            if not isinstance(child.tag, str):
                continue
            tag = local(child.tag)
            if tag in ("defs", "title", "desc", "metadata", "style"):
                continue
            if tag == "rect" and parse_len(child.get("width"), 0) >= prog.width and parse_len(child.get("height"), 0) >= prog.height:
                continue  # background
            cid = child.get("id")
            if cid:
                _apply_one(prog, {"op": "translate", "id": cid, "dx": dx, "dy": dy})
    elif kind == "set_canvas":
        w, h = int(op["width"]), int(op["height"])
        prog.root.set("width", str(w))
        prog.root.set("height", str(h))
        prog.root.set("viewBox", f"0 0 {w} {h}")
        bg = prog.element("background")
        if bg is not None:
            bg.set("width", str(w))
            bg.set("height", str(h))
    else:
        raise ValueError(f"unknown op {kind!r}")


def apply_edits(svg_text: str, ops: List[EditOp]) -> EditResult:
    """Apply ``ops`` in order on an addressable program; failures are collected, not raised."""
    prog = load_program(svg_text)
    result = EditResult(svg=svg_text)
    for op in ops:
        try:
            _apply_one(prog, op)
            result.applied.append(op)
            prog = load_program(prog.serialize())  # refresh inventory (ids are stable)
        except Exception as exc:  # noqa: BLE001
            result.failed.append((op, f"{type(exc).__name__}: {exc}"))
    result.svg = prog.serialize()
    return result
