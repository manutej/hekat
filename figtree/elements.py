"""Element vocabulary for leaf blocks.

A methodology figure is more than labelled rectangles: data stores are cylinders, documents
have a folded corner, decisions are diamonds, start/end states are pills, people are actors.
Each kind is drawn as a single ``<path>`` (or ``<rect>``) carrying ``data-role="block"`` so the
critic, the quality rubric and the ports treat it exactly like a rectangle of the same bbox.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

KINDS = ("block", "store", "document", "decision", "terminal", "actor", "process")

_KIND_KEYWORDS: List[Tuple[Tuple[str, ...], str]] = [
    (("database", "store", "memory", "cache", "sheaf", "repository", "corpus", "table"), "store"),
    (("document", "paper", "source text", "spec", "report", "file", "skill.md", "manuscript"), "document"),
    (("decision", "check", "gate", "condition", "if ", "branch", "converge"), "decision"),
    (("user", "human", "author", "reader", "student", "reviewer", "teacher"), "actor"),
    (("input", "output", "start", "end", "final"), "terminal"),
]
_WORD = {k: re.compile(rf"(?<![a-z]){re.escape(k.strip())}(?![a-z])") for keys, _ in _KIND_KEYWORDS for k in keys}


def kind_for(component: str, explicit: str = "") -> str:
    if explicit in KINDS:
        return explicit
    n = component.lower()
    for keys, kind in _KIND_KEYWORDS:
        if any(_WORD[k].search(n) for k in keys):
            return kind
    return "block"


def shape_path(kind: str, w: int, h: int) -> str:
    """Path data (origin top-left) for a block of ``kind`` filling a ``w`` x ``h`` bbox."""
    if kind == "store":  # cylinder: top ellipse, body, bottom arc
        ry = max(4, h // 6)
        return (
            f"M0,{ry} A{w / 2:g},{ry} 0 0 1 {w},{ry} V{h - ry} A{w / 2:g},{ry} 0 0 1 0,{h - ry} Z "
            f"M0,{ry} A{w / 2:g},{ry} 0 0 0 {w},{ry}"
        )
    if kind == "document":  # folded corner top-right, wavy bottom
        c = 8
        return f"M0,0 H{w - c} L{w},{c} V{h} H0 Z M{w - c},0 V{c} H{w}"
    if kind == "decision":  # diamond
        return f"M{w / 2:g},0 L{w},{h / 2:g} L{w / 2:g},{h} L0,{h / 2:g} Z"
    if kind == "terminal":  # pill
        r = h / 2
        return f"M{r:g},0 H{w - r:g} A{r:g},{r:g} 0 0 1 {w - r:g},{h} H{r:g} A{r:g},{r:g} 0 0 1 {r:g},0 Z"
    if kind == "actor":  # head + shoulders inside the bbox (no label inside; label sits under)
        hr = min(w, h) / 5
        cx = w / 2
        return (
            f"M{cx - hr:g},{hr + 2:g} A{hr:g},{hr:g} 0 1 1 {cx + hr:g},{hr + 2:g} A{hr:g},{hr:g} 0 1 1 {cx - hr:g},{hr + 2:g} "
            f"M{cx - 2.4 * hr:g},{h} V{h - 1.6 * hr:g} A{2.4 * hr:g},{2 * hr:g} 0 0 1 {cx + 2.4 * hr:g},{h - 1.6 * hr:g} V{h}"
        )
    if kind == "process":  # rectangle with double side bars
        return f"M0,0 H{w} V{h} H0 Z M6,0 V{h} M{w - 6},0 V{h}"
    return f"M0,0 H{w} V{h} H0 Z"


def text_inset(kind: str) -> Tuple[int, int]:
    """Extra horizontal padding (left, right) a kind needs around its label."""
    return {"decision": (16, 16), "terminal": (8, 8), "document": (4, 12), "store": (4, 4), "process": (8, 8)}.get(kind, (0, 0))
