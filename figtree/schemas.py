"""Data schemas for the FigTree generator (section 2 of the specification).

Every schema is a plain dataclass with ``to_dict``/``from_dict`` so that the
same objects round-trip through JSON for the LLM-backed agents and through the
sheaf storage.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

FLOW_TYPES = ("data", "control", "conditional", "parallel")
PORT_SIDES = ("top", "bottom", "left", "right")
SEVERITIES = ("critical", "warning")

DEFAULT_PALETTE: Dict[str, str] = {
    "attention": "#F4A460",
    "processing": "#7BA3C9",
    "residual": "#FFF3CD",
    "input": "#D5D5D5",
    "container": "#F5F5F5",
    "border": "#333333",
}


def _pt_range(spec: str, default: tuple[int, int]) -> tuple[int, int]:
    m = re.match(r"\s*(\d+)\s*-\s*(\d+)\s*pt", spec or "")
    if not m:
        return default
    return int(m.group(1)), int(m.group(2))


@dataclass
class GlobalStyle:
    """Style invariants.  These are the conserved quantities checked at Merge."""

    palette: Dict[str, str] = field(default_factory=lambda: dict(DEFAULT_PALETTE))
    font: str = "Times New Roman"
    font_size_label: str = "11-13pt"
    font_size_annot: str = "9-11pt"
    stroke_main: float = 1.2
    stroke_border: float = 1.4
    grid: int = 8
    min_arrow: int = 20
    padding: int = 24

    # -- derived helpers -------------------------------------------------
    @property
    def label_range(self) -> tuple[int, int]:
        return _pt_range(self.font_size_label, (11, 13))

    @property
    def annot_range(self) -> tuple[int, int]:
        return _pt_range(self.font_size_annot, (9, 11))

    @property
    def label_size(self) -> int:
        lo, hi = self.label_range
        return (lo + hi) // 2

    @property
    def annot_size(self) -> int:
        lo, hi = self.annot_range
        return (lo + hi) // 2

    def invariant_key(self) -> tuple:
        """Hashable view of the conserved quantities."""
        return (
            tuple(sorted(self.palette.items())),
            self.font,
            self.font_size_label,
            self.font_size_annot,
            self.stroke_main,
            self.stroke_border,
            self.grid,
            self.min_arrow,
            self.padding,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "palette": dict(self.palette),
            "font": self.font,
            "font_size_label": self.font_size_label,
            "font_size_annot": self.font_size_annot,
            "stroke_main": self.stroke_main,
            "stroke_border": self.stroke_border,
            "grid": self.grid,
            "min_arrow": self.min_arrow,
            "padding": self.padding,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "GlobalStyle":
        d = d or {}
        palette = dict(DEFAULT_PALETTE)
        palette.update({k: str(v) for k, v in (d.get("palette") or {}).items()})
        return cls(
            palette=palette,
            font=str(d.get("font", "Times New Roman")),
            font_size_label=str(d.get("font_size_label", "11-13pt")),
            font_size_annot=str(d.get("font_size_annot", "9-11pt")),
            stroke_main=float(d.get("stroke_main", 1.2)),
            stroke_border=float(d.get("stroke_border", 1.4)),
            grid=int(d.get("grid", 8)),
            min_arrow=int(d.get("min_arrow", 20)),
            padding=int(d.get("padding", 24)),
        )


@dataclass
class Component:
    name: str
    evidence_span: str

    def to_dict(self) -> Dict[str, str]:
        return {"name": self.name, "evidence_span": self.evidence_span}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Component":
        return cls(name=str(d["name"]).strip(), evidence_span=str(d.get("evidence_span", "")))


@dataclass
class Flow:
    src: str
    dst: str
    type: str = "data"
    evidence_span: str = ""

    def __post_init__(self) -> None:
        if self.type not in FLOW_TYPES:
            raise ValueError(f"unknown flow type {self.type!r}")

    def to_dict(self) -> Dict[str, str]:
        return {"from": self.src, "to": self.dst, "type": self.type, "evidence_span": self.evidence_span}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Flow":
        return cls(
            src=str(d["from"]).strip(),
            dst=str(d["to"]).strip(),
            type=str(d.get("type", "data")),
            evidence_span=str(d.get("evidence_span", "")),
        )


@dataclass
class ContentPlan:
    claim: str = ""
    components: List[Component] = field(default_factory=list)
    flows: List[Flow] = field(default_factory=list)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    notation: List[str] = field(default_factory=list)

    def component_names(self) -> List[str]:
        return [c.name for c in self.components]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim": self.claim,
            "components": [c.to_dict() for c in self.components],
            "flows": [f.to_dict() for f in self.flows],
            "inputs": list(self.inputs),
            "outputs": list(self.outputs),
            "notation": list(self.notation),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ContentPlan":
        return cls(
            claim=str(d.get("claim", "")),
            components=[Component.from_dict(c) for c in d.get("components", [])],
            flows=[Flow.from_dict(f) for f in d.get("flows", [])],
            inputs=[str(x) for x in d.get("inputs", [])],
            outputs=[str(x) for x in d.get("outputs", [])],
            notation=[str(x) for x in d.get("notation", [])],
        )


@dataclass
class Port:
    id: str
    side: str
    rel_x: int
    rel_y: int
    type: str  # input | output
    abs_x: int = 0
    abs_y: int = 0
    component: str = ""  # component the port belongs to (leaf ports)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "side": self.side,
            "rel_x": self.rel_x,
            "rel_y": self.rel_y,
            "abs_x": self.abs_x,
            "abs_y": self.abs_y,
            "type": self.type,
            "component": self.component,
        }


@dataclass
class ResidualDefect:
    severity: str
    visual_description: str
    code_anchor: str
    fix_instruction: str
    round_introduced: int = 0

    def __post_init__(self) -> None:
        if self.severity not in SEVERITIES:
            self.severity = "warning"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "visual_description": self.visual_description,
            "code_anchor": self.code_anchor,
            "fix_instruction": self.fix_instruction,
            "round_introduced": self.round_introduced,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ResidualDefect":
        return cls(
            severity=str(d.get("severity", "warning")),
            visual_description=str(d.get("visual_description", "")),
            code_anchor=str(d.get("code_anchor", "")),
            fix_instruction=str(d.get("fix_instruction", "")),
            round_introduced=int(d.get("round_introduced", 0) or 0),
        )


@dataclass
class BBox:
    x: int
    y: int
    w: int
    h: int

    @property
    def x2(self) -> int:
        return self.x + self.w

    @property
    def y2(self) -> int:
        return self.y + self.h

    def intersects(self, other: "BBox") -> bool:
        return not (
            self.x2 <= other.x or other.x2 <= self.x or self.y2 <= other.y or other.y2 <= self.y
        )

    def contains_point(self, x: float, y: float, strict: bool = True) -> bool:
        if strict:
            return self.x < x < self.x2 and self.y < y < self.y2
        return self.x <= x <= self.x2 and self.y <= y <= self.y2

    def to_dict(self) -> Dict[str, int]:
        return {"x": self.x, "y": self.y, "w": self.w, "h": self.h}


@dataclass
class Node:
    id: str
    parent_id: Optional[str]
    description: str
    depth: int
    style: GlobalStyle
    components: List[str] = field(default_factory=list)
    flows: List[Flow] = field(default_factory=list)  # flows internal to this node
    canvas: Dict[str, int] = field(default_factory=lambda: {"w": 0, "h": 0})
    ports: List[Port] = field(default_factory=list)
    children: List["Node"] = field(default_factory=list)
    svg_fragment: Optional[str] = None
    bbox: Optional[BBox] = None
    residuals: List[ResidualDefect] = field(default_factory=list)
    marked_leaf: bool = False
    layout: str = "horizontal"
    # position inside the parent frame (set by Merge)
    offset: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0})
    # structured drawing model (see figtree.svgmodel); the SVG fragment is derived from it
    model: Any = None

    def is_leaf(self) -> bool:
        return not self.children

    def port(self, pid: str) -> Optional[Port]:
        for p in self.ports:
            if p.id == pid:
                return p
        return None

    def walk(self):
        yield self
        for c in self.children:
            yield from c.walk()

    def critical_count(self) -> int:
        return sum(1 for r in self.residuals if r.severity == "critical")

    def to_dict(self, include_svg: bool = False) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "id": self.id,
            "parent_id": self.parent_id,
            "description": self.description,
            "canvas": dict(self.canvas),
            "ports": [p.to_dict() for p in self.ports],
            "depth": self.depth,
            "style": self.style.to_dict(),
            "children": [c.to_dict(include_svg) for c in self.children],
            "bbox": self.bbox.to_dict() if self.bbox else None,
            "residuals": [r.to_dict() for r in self.residuals],
            "components": list(self.components),
            "layout": self.layout,
            "offset": dict(self.offset),
        }
        d["svg_fragment"] = self.svg_fragment if include_svg else None
        return d


@dataclass
class SheafGraph:
    """Sheaf storage: nodes are stalks, residual defects and style invariants are sections.

    ``restriction`` records, for each parent->child edge, whether the style section of the
    child restricts to the parent's (the Noether-style conservation check).
    """

    stalks: Dict[str, Node] = field(default_factory=dict)
    sections: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    edges: List[tuple[str, str]] = field(default_factory=list)
    restriction: Dict[str, bool] = field(default_factory=dict)

    def store(self, node: Node) -> None:
        self.stalks[node.id] = node
        self.sections[node.id] = {
            "residuals": [r.to_dict() for r in node.residuals],
            "style": node.style.invariant_key(),
        }
        for c in node.children:
            edge = (node.id, c.id)
            if edge not in self.edges:
                self.edges.append(edge)
            self.restriction[f"{node.id}->{c.id}"] = c.style.invariant_key() == node.style.invariant_key()

    def conserved(self) -> bool:
        return all(self.restriction.values())

    def all_residuals(self) -> List[ResidualDefect]:
        out: List[ResidualDefect] = []
        for node in self.stalks.values():
            out.extend(node.residuals)
        return out

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stalks": {k: v.to_dict() for k, v in self.stalks.items()},
            "sections": {
                k: {"residuals": v["residuals"], "style_invariant": repr(v["style"])}
                for k, v in self.sections.items()
            },
            "edges": [list(e) for e in self.edges],
            "restriction": dict(self.restriction),
            "conserved": self.conserved(),
        }
