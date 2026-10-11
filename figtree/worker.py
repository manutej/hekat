"""Worker agent: Merge (placement, parent-owned arrows, min-arrow spacing) and local repair."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from figtree.generator import _layers, fill_for
from figtree.geometry import (
    Point,
    ceil_to_grid,
    final_segment_length,
    is_orthogonal,
    on_grid,
    path_hits_boxes,
    route,
    terminal_direction,
)
from figtree.schemas import BBox, Flow, GlobalStyle, Node, Port, ResidualDefect
from figtree.svgmodel import Fragment, GroupEl, PathEl, RectEl, TextEl


class RepairError(Exception):
    """Raised when a repair leaves the fragment in an invalid state (triggers rollback)."""


@dataclass
class Worker:
    gap_h: int = 24  # compact; the MIN_ARROW_DISTANCE spacing pass widens it where an arrow needs it
    gap_v: int = 16
    detour: int = 24
    spacing_iterations: int = 5
    events: List[str] = field(default_factory=list)

    # ==================================================================
    # Merge
    # ==================================================================
    def merge(self, node: Node, children: Sequence[Node]) -> Fragment:
        style = node.style
        grid = style.grid
        child_of: Dict[str, Node] = {}
        for c in children:
            for comp in c.components:
                child_of[comp] = c
        # parent-owned flows: endpoints in different children
        owned: List[Tuple[Flow, Node, Node]] = []
        for f in node.flows:
            a, b = child_of.get(f.src), child_of.get(f.dst)
            if a is None or b is None:
                node.residuals.append(
                    ResidualDefect("warning", f"flow {f.src} -> {f.dst} has no drawable endpoint at {node.id}", node.id, "none")
                )
                continue
            if a.id != b.id:
                owned.append((f, a, b))

        # column layout: layers of children by inter-child flows
        child_ids = [c.id for c in children]
        pseudo = [Flow(a.id, b.id, f.type, "") for f, a, b in owned]
        layers = _layers(child_ids, pseudo) if owned else [[cid] for cid in child_ids]
        if not owned:
            layers = [child_ids]  # no flows -> single vertical stack (parallel block)
            node.layout = "vertical"
        else:
            node.layout = "horizontal"
        by_id = {c.id: c for c in children}
        columns: List[List[Node]] = [[by_id[cid] for cid in layer] for layer in layers]
        column_of: Dict[str, int] = {c.id: i for i, col in enumerate(columns) for c in col}

        titled = node.depth >= 1
        origin_y = style.padding + (16 if titled else 0)
        self._place(columns, style.padding, origin_y, grid)

        fragment = self._assemble(node, children, columns, column_of, owned, titled)
        return fragment

    # ------------------------------------------------------------------
    def _place(self, columns: List[List[Node]], x0: int, y0: int, grid: int) -> None:
        col_heights = [sum(c.canvas["h"] for c in col) + self.gap_v * (len(col) - 1) for col in columns]
        max_h = max(col_heights) if col_heights else 0
        x = x0
        for col, ch in zip(columns, col_heights):
            col_w = max(c.canvas["w"] for c in col)
            y = y0 + ceil_to_grid((max_h - ch) / 2, grid)
            for c in col:
                c.offset = {"x": x + ceil_to_grid((col_w - c.canvas["w"]) / 2, grid), "y": y}
                y += c.canvas["h"] + self.gap_v
            x += col_w + self.gap_h

    def _export_ports(self, node: Node, children: Sequence[Node]) -> List[Port]:
        ports: List[Port] = []
        seen: Dict[str, int] = {}
        for c in children:
            for p in c.ports:
                pid = p.id
                if pid in seen:  # collision: prefix with the owning node id
                    pid = f"{c.id}.{p.id}"
                    self.events.append(f"port collision at {node.id}: {p.id} -> {pid}")
                seen[pid] = 1
                ports.append(
                    Port(
                        id=pid,
                        side=p.side,
                        rel_x=c.offset["x"] + p.rel_x,
                        rel_y=c.offset["y"] + p.rel_y,
                        type=p.type,
                        component=p.component,
                    )
                )
        return ports

    @staticmethod
    def _leaf_port(child: Node, component: str, side: str) -> Optional[Port]:
        for p in child.ports:
            if p.component == component and p.side == side:
                return p
        return None

    def _route_all(
        self,
        node: Node,
        children: Sequence[Node],
        column_of: Dict[str, int],
        owned: List[Tuple[Flow, Node, Node]],
    ) -> List[PathEl]:
        boxes = {c.id: BBox(c.offset["x"], c.offset["y"], c.canvas["w"], c.canvas["h"]) for c in children}
        all_boxes = list(boxes.values())
        # leaf blocks of every child, in this node's frame, keyed by component
        leaf_blocks: Dict[str, BBox] = {}
        for c in children:
            for el, off in c.model.iter_all((c.offset["x"], c.offset["y"])):
                if isinstance(el, RectEl) and el.role == "block":
                    leaf_blocks[el.extra.get("data-component", el.id)] = BBox(el.x + off[0], el.y + off[1], el.w, el.h)
        min_top = min(b.y for b in all_boxes)
        max_bottom = max(b.y2 for b in all_boxes)
        paths: List[PathEl] = []
        over = under = 0

        def port_pt(child: Node, port: Port) -> Point:
            return (child.offset["x"] + port.rel_x, child.offset["y"] + port.rel_y)

        for i, (f, a, b) in enumerate(owned):
            fwd = column_of[a.id] < column_of[b.id]
            obstacles = [bx for comp, bx in leaf_blocks.items() if comp not in (f.src, f.dst)]
            sp = self._leaf_port(a, f.src, "right")
            dp = self._leaf_port(b, f.dst, "left")
            if sp is None or dp is None:
                node.residuals.append(ResidualDefect("warning", f"missing port for {f.src} -> {f.dst}", node.id, "none"))
                continue
            s, d = port_pt(a, sp), port_pt(b, dp)
            pts: Optional[List[Point]] = None
            if fwd:
                direct = route(s, d, "right", "left", node.style.grid)
                if not path_hits_boxes(direct, obstacles):
                    pts = direct
            if pts is None:
                # Detour candidates, first collision-free wins:
                #  1. gap bus: exit right into the inter-column gap, run along a horizontal bus
                #     above (forward) / below (backward) every block, re-enter from the left;
                #  2. gap bus entering the target from its top/bottom port;
                #  3. top/bottom exit and entry (over-the-top / under-the-bottom bracket);
                #  4. candidate 1 regardless (the critic will flag the clip as a residual).
                gx1 = boxes[a.id].x2 + 8
                # entry lane: just right of the column preceding the target, so that shifting the
                # target (spacing pass) lengthens the final segment instead of moving the lane
                prev_cols = [bx for cid, bx in boxes.items() if column_of[cid] == column_of[b.id] - 1]
                gx2 = (max(bx.x2 for bx in prev_cols) + 8) if prev_cols else boxes[b.id].x - self.detour
                if fwd:
                    over += 1
                    y = min_top - self.detour - 8 * (over - 1)
                    vside = "top"
                else:
                    under += 1
                    y = max_bottom + self.detour + 8 * (under - 1)
                    vside = "bottom"
                sp_v = self._leaf_port(a, f.src, vside)
                dp_v = self._leaf_port(b, f.dst, vside)
                s_v, d_v = port_pt(a, sp_v), port_pt(b, dp_v)
                candidates = [
                    ([s, (gx1, s[1]), (gx1, y), (gx2, y), (gx2, d[1]), d], sp, dp),
                    ([s, (gx1, s[1]), (gx1, y), (d_v[0], y), d_v], sp, dp_v),
                    ([s_v, (s_v[0], y), (d_v[0], y), d_v], sp_v, dp_v),
                ]
                chosen = next((c for c in candidates if not path_hits_boxes(c[0], obstacles)), candidates[0])
                pts, sp, dp = chosen
            paths.append(
                PathEl(
                    id=f"{node.id}.arrow{i}",
                    points=pts,
                    flow_type=f.type,
                    stroke=node.style.palette["border"],
                    stroke_width=node.style.stroke_main,
                    src_port=sp.id,
                    dst_port=dp.id,
                )
            )
        return paths

    def _assemble(
        self,
        node: Node,
        children: Sequence[Node],
        columns: List[List[Node]],
        column_of: Dict[str, int],
        owned: List[Tuple[Flow, Node, Node]],
        titled: bool,
    ) -> Fragment:
        style = node.style
        grid = style.grid
        paths = self._route_all(node, children, column_of, owned)

        # spacing algorithm: terminates in <= spacing_iterations
        for _ in range(self.spacing_iterations):
            short = [p for p in paths if p.marker and final_segment_length(p.points) < style.min_arrow]
            if not short:
                break
            p = short[0]
            dist = final_segment_length(p.points)
            shift = ceil_to_grid(style.min_arrow - dist, grid)
            dx, dy = terminal_direction(p.points)
            target = next(c for c in children if any(q.id == p.dst_port for q in c.ports))
            if dx:
                movers = [c for c in children if column_of[c.id] >= column_of[target.id]]
                for c in movers:
                    c.offset["x"] += shift * dx
            else:
                movers = [c for c in children if c.offset["y"] >= target.offset["y"]] if dy > 0 else [target]
                for c in movers:
                    c.offset["y"] += shift * dy
            self.events.append(f"spacing shift at {node.id}: {p.id} by {shift}")
            paths = self._route_all(node, children, column_of, owned)
        else:
            still = [p for p in paths if p.marker and final_segment_length(p.points) < style.min_arrow]
            for p in still:
                node.residuals.append(
                    ResidualDefect("warning", f"{p.id} arrow shaft still < {style.min_arrow}px after {self.spacing_iterations} shifts", p.id, "shift target by ceil_to_grid(20-dist), recompute ports")
                )

        # normalise: shift everything so the content starts at the padding
        boxes = [BBox(c.offset["x"], c.offset["y"], c.canvas["w"], c.canvas["h"]) for c in children]
        for p in paths:
            boxes.append(p.bbox())
        min_x = min(b.x for b in boxes)
        min_y = min(b.y for b in boxes)
        origin_y = style.padding + (16 if titled else 0)
        shift_x = style.padding - min_x
        shift_y = origin_y - min_y
        if shift_x or shift_y:
            for c in children:
                c.offset["x"] += shift_x
                c.offset["y"] += shift_y
            for p in paths:
                p.points = [(x + shift_x, y + shift_y) for x, y in p.points]
            boxes = [BBox(b.x + shift_x, b.y + shift_y, b.w, b.h) for b in boxes]
        max_x = max(b.x2 for b in boxes)
        max_y = max(b.y2 for b in boxes)
        w = ceil_to_grid(max_x + style.padding, grid)
        h = ceil_to_grid(max_y + style.padding, grid)

        elements: List = []
        if titled:
            elements.append(
                RectEl(
                    id=f"{node.id}.container",
                    x=0,
                    y=0,
                    w=w,
                    h=h,
                    fill=style.palette["container"],
                    stroke=style.palette["border"],
                    stroke_width=style.stroke_border,
                    role="container",
                    rx=4,
                    extra={"stroke-dasharray": "4 2"},
                )
            )
            title = node.description
            max_chars = max(4, (w - 16) * 2 // style.annot_size)
            if len(title) > max_chars:
                title = title[: max_chars - 1].rstrip() + "…"
            elements.append(
                TextEl(
                    id=f"{node.id}.title",
                    x=8,
                    y=16,
                    text=title,
                    size=style.annot_size,
                    kind="annot",
                    font=style.font,
                    anchor="start",
                    max_width=w,
                )
            )
        for c in children:
            elements.append(GroupEl(id=c.id, x=c.offset["x"], y=c.offset["y"], fragment=c.model, label=c.description))
        elements.extend(paths)
        ports = self._export_ports(node, children)
        return Fragment(node_id=node.id, w=w, h=h, elements=elements, ports=ports)

    # ==================================================================
    # Local repair
    # ==================================================================
    def local_repair(self, node: Node, defects: Sequence[ResidualDefect]) -> List[ResidualDefect]:
        """Apply only the listed fix instructions to the anchored elements.

        Returns the defects that could not be repaired locally.
        """
        frag: Fragment = node.model
        style = node.style
        unresolved: List[ResidualDefect] = []
        relayout = False
        for d in defects:
            fix = d.fix_instruction.lower()
            el = frag.find(d.code_anchor)
            # dispatch in priority order: the most specific instruction wins
            if "expand block" in fix or "text overflow" in fix:
                if isinstance(el, TextEl):
                    self._expand_block_for_text(frag, el, style)
                else:
                    unresolved.append(d)
            elif "expand canvas" in fix or "shrink canvas" in fix or "padding" in fix:
                self._fit_canvas(frag, style, titled=node.depth >= 1 and not node.is_leaf())
            elif "flat fill" in fix or "gradient" in fix:
                if isinstance(el, RectEl):
                    el.fill = fill_for(el.extra.get("data-component", el.id), style.palette) if el.role == "block" else style.palette["container"]
                else:
                    for r in frag.rects():
                        if r.fill.startswith("url(") or r.fill.upper() not in {v.upper() for v in style.palette.values()}:
                            r.fill = fill_for(r.extra.get("data-component", r.id), style.palette) if r.role == "block" else style.palette["container"]
            elif "right-angle" in fix or "diagonal" in fix:
                if isinstance(el, PathEl) and not is_orthogonal(el.points) and not el.diagonal_flag:
                    if not el.src_port and not el.dst_port and not el.marker:
                        frag.elements.remove(el)  # decorative diagonal: not a flow, remove
                    else:
                        el.points = self._orthogonalise(el.points)
                else:
                    unresolved.append(d)
            elif "shift target" in fix or "re-layout" in fix or "reroute" in fix or "overlap" in fix:
                relayout = True
            elif "prefix" in fix:
                self._prefix_ports(frag, node.id)
            elif "marker" in fix or "background" in fix:
                pass  # provided by the document wrapper
            elif "font" in fix:
                for t in frag.texts():
                    t.font = style.font
                    t.size = style.label_size if t.kind == "label" else style.annot_size
            elif "snap" in fix or "grid" in fix:
                self._snap_fragment(frag, style.grid)
            else:
                unresolved.append(d)
        if relayout:
            if node.children:
                node.model = self.merge(node, node.children)
                frag = node.model
            else:
                unresolved.extend(d for d in defects if "shift" in d.fix_instruction or "layout" in d.fix_instruction)
        self._snap_fragment(frag, style.grid)
        self._fit_canvas(frag, style, titled=node.depth >= 1 and not node.is_leaf())
        self.refresh_ports(node)
        self.validate(node)
        return unresolved

    # ------------------------------------------------------------------
    @staticmethod
    def _orthogonalise(points: List[Point]) -> List[Point]:
        out: List[Point] = [points[0]]
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            if x1 != x2 and y1 != y2:
                out.append((x2, y1))
            out.append((x2, y2))
        return out

    @staticmethod
    def _snap_fragment(frag: Fragment, grid: int) -> None:
        for e in frag.elements:
            if isinstance(e, RectEl):
                e.x, e.y = ceil_to_grid(e.x, grid), ceil_to_grid(e.y, grid)
                e.w, e.h = ceil_to_grid(e.w, grid), ceil_to_grid(e.h, grid)
            elif isinstance(e, TextEl):
                e.x, e.y = ceil_to_grid(e.x, grid), ceil_to_grid(e.y, grid)
            elif isinstance(e, PathEl):
                e.points = [(ceil_to_grid(x, grid), ceil_to_grid(y, grid)) for x, y in e.points]
            elif isinstance(e, GroupEl):
                e.x, e.y = ceil_to_grid(e.x, grid), ceil_to_grid(e.y, grid)
        for p in frag.ports:
            p.rel_x, p.rel_y = ceil_to_grid(p.rel_x, grid), ceil_to_grid(p.rel_y, grid)
        frag.w, frag.h = ceil_to_grid(frag.w, grid), ceil_to_grid(frag.h, grid)

    @staticmethod
    def _expand_block_for_text(frag: Fragment, text: TextEl, style: GlobalStyle) -> None:
        need = ceil_to_grid(text.est_width() + 32, 2 * style.grid)
        block = next((r for r in frag.rects() if r.role == "block"), None)
        if block is None:
            return
        if block.w < need:
            block.w = need
        text.x = block.x + block.w // 2
        text.max_width = block.w
        frag.w = max(frag.w, block.x + block.w)
        for p in frag.ports:
            if p.side == "right":
                p.rel_x = block.x + block.w
            elif p.side in ("top", "bottom"):
                p.rel_x = block.x + block.w // 2

    @staticmethod
    def _prefix_ports(frag: Fragment, node_id: str) -> None:
        seen: Dict[str, int] = {}
        for p in frag.ports:
            if p.id in seen:
                p.id = f"{node_id}.{p.id}"
            seen[p.id] = 1

    @staticmethod
    def _fit_canvas(frag: Fragment, style: GlobalStyle, titled: bool) -> None:
        content = [e.bbox() for e in frag.elements if not (isinstance(e, RectEl) and e.role == "container")]
        if not content:
            return
        max_x = max(b.x2 for b in content)
        max_y = max(b.y2 for b in content)
        leaf = any(isinstance(e, RectEl) and e.role == "block" for e in frag.elements) and not frag.groups()
        if leaf:
            frag.w = ceil_to_grid(max_x, style.grid)
            frag.h = ceil_to_grid(max_y, style.grid)
        else:
            frag.w = ceil_to_grid(max_x + style.padding, style.grid)
            frag.h = ceil_to_grid(max_y + style.padding, style.grid)
        for e in frag.elements:
            if isinstance(e, RectEl) and e.role == "container":
                e.w, e.h = frag.w, frag.h

    # ------------------------------------------------------------------
    def refresh_ports(self, node: Node) -> None:
        """Re-extract ports and bbox from the model after a change."""
        frag: Fragment = node.model
        if node.children:
            for c in node.children:
                g = next((g for g in frag.groups() if g.id == c.id), None)
                if g is not None:
                    c.offset = {"x": g.x, "y": g.y}
            frag.ports = self._export_ports(node, node.children)
        node.ports = frag.ports
        node.canvas = {"w": frag.w, "h": frag.h}
        node.bbox = BBox(0, 0, frag.w, frag.h)

    @staticmethod
    def validate(node: Node) -> None:
        """Raise :class:`RepairError` on overlaps or port collisions."""
        frag: Fragment = node.model
        groups = frag.groups()
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                if groups[i].bbox().intersects(groups[j].bbox()):
                    raise RepairError(f"children {groups[i].id} and {groups[j].id} overlap")
        ids = [p.id for p in frag.ports]
        if len(ids) != len(set(ids)):
            raise RepairError("port id collision")
        for e in frag.elements:
            b = e.bbox()
            if b.x < 0 or b.y < 0 or b.x2 > frag.w or b.y2 > frag.h:
                raise RepairError(f"{getattr(e, 'id', '?')} outside canvas")
