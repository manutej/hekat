"""Orchestrator (section 4 of the specification).

    root = Grounder(SourceText)
    final = build(root)

``build`` draws atomic nodes, decomposes the others into 2-4 children, merges, runs the
critic loop (<= 3 rounds), forces re-decomposition when more than 3 critical residuals
remain, validates the style/port invariants and stores every node as a sheaf stalk.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from figtree.critic import StructuralCritic
from figtree.editability import EditabilityProof, apply_local_edit, prove_editability
from figtree.generator import RuleBasedGenerator, is_atomic
from figtree.grounder import GrounderOutput, RuleBasedGrounder, check_faithfulness
from figtree.ingest import to_noun_phrase
from figtree.memory import VerificationMemory
from figtree.render import render_png
from figtree.schemas import BBox, ContentPlan, GlobalStyle, Node, ResidualDefect, SheafGraph
from figtree.svgmodel import Fragment, wrap_svg
from figtree.worker import RepairError, Worker


@dataclass
class Limits:
    max_nodes: int = 32
    max_depth: int = 8
    max_critic_rounds: int = 3
    max_schema_retries: int = 2
    spacing_iterations: int = 5


@dataclass
class FigTreeResult:
    final_svg: str
    residual_defects: List[ResidualDefect]
    layout_tree: SheafGraph
    editability_proof: EditabilityProof
    content_plan: ContentPlan
    global_style: GlobalStyle
    root: Node
    faithfulness_failures: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    node_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "residual_defects": [r.to_dict() for r in self.residual_defects],
            "layout_tree": self.layout_tree.to_dict(),
            "editability_proof": self.editability_proof.to_dict(),
            "content_plan": self.content_plan.to_dict(),
            "global_style": self.global_style.to_dict(),
            "faithfulness_failures": list(self.faithfulness_failures),
            "events": list(self.events),
            "node_count": self.node_count,
        }


class FigTree:
    """The recursive figure generator."""

    def __init__(
        self,
        grounder: Optional[Any] = None,
        generator: Optional[Any] = None,
        critic: Optional[Any] = None,
        worker: Optional[Worker] = None,
        memory: Optional[VerificationMemory] = None,
        limits: Optional[Limits] = None,
        render: bool = True,
        render_dir: Optional[str] = None,
    ) -> None:
        self.limits = limits or Limits()
        self.memory = memory or VerificationMemory()
        self.grounder = grounder or RuleBasedGrounder()
        self.generator = generator or RuleBasedGenerator(max_depth=self.limits.max_depth)
        self.critic = critic or StructuralCritic(self.memory)
        self.worker = worker or Worker(spacing_iterations=self.limits.spacing_iterations)
        self.render = render
        self.render_dir = render_dir
        self.sheaf = SheafGraph()
        self.style_override: Optional[GlobalStyle] = None  # a design preset replaces the grounder's style
        self.events: List[str] = []
        self._counter = 0
        self._node_count = 0
        self._cap_hit = False
        self._source = ""

    # ------------------------------------------------------------------
    def _next_id(self) -> str:
        self._counter += 1
        return f"n{self._counter}"

    def _log(self, msg: str) -> None:
        self.events.append(msg)

    # ------------------------------------------------------------------
    def run(self, source_text: str, edit: Optional[Dict[str, Any]] = None) -> FigTreeResult:
        self._source = source_text
        grounded = self._ground_with_retry(source_text)
        # explicit kind/icon hints from the source (spec format) reach the generator's leaf drawing
        self.generator.hints = {c.name: {'kind': c.kind, 'icon': c.icon} for c in grounded.content_plan.components if c.kind or c.icon}
        plan, style = grounded.content_plan, grounded.global_style
        if self.style_override is not None:
            style = self.style_override
        faith = check_faithfulness(plan, source_text)
        root = Node(
            id=self._next_id(),
            parent_id=None,
            description=to_noun_phrase(plan.claim or "methodology"),
            depth=0,
            style=style,
            components=plan.component_names(),
            flows=list(plan.flows),
        )
        root.residuals.extend(grounded.residuals)
        self._node_count = 1
        if not root.components:
            root.marked_leaf = True
            root.components = [plan.claim[:40] or "source"]
            root.residuals.append(
                ResidualDefect("critical", "no components grounded in the source", "content_plan", "none; nothing invented")
            )
        final_root = self.build(root)
        final_svg = wrap_svg(final_root.model, style, title=plan.claim)
        proof = prove_editability(final_svg, edit or self._default_edit(plan))
        residuals = _dedupe_global(self.sheaf.all_residuals())
        return FigTreeResult(
            final_svg=final_svg,
            residual_defects=residuals,
            layout_tree=self.sheaf,
            editability_proof=proof,
            content_plan=plan,
            global_style=style,
            root=final_root,
            faithfulness_failures=faith,
            events=self.events + self.worker.events,
            node_count=self._node_count,
        )

    @staticmethod
    def _default_edit(plan: ContentPlan) -> Dict[str, Any]:
        names = plan.component_names()
        if "Critic" in names and "Generator" in names:
            return {"op": "add_dashed_arrow", "from": "Critic", "to": "Generator"}
        if names:
            return {"op": "recolor", "component": names[0], "fill": "#F4A460"}
        return {"op": "recolor", "component": "", "fill": "#F4A460"}

    def _ground_with_retry(self, source_text: str) -> GrounderOutput:
        last_exc: Optional[Exception] = None
        for attempt in range(self.limits.max_schema_retries + 1):
            try:
                out = self.grounder.ground(source_text)
                if not isinstance(out, GrounderOutput):
                    raise TypeError("grounder returned an unexpected object")
                return out
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                self._log(f"grounder attempt {attempt + 1} failed: {exc}")
        # fall back to an empty plan with a parse_error residual
        return GrounderOutput(
            ContentPlan(),
            GlobalStyle(),
            [ResidualDefect("critical", f"parse_error: {last_exc}", "grounder", "retry with schema prompt")],
        )

    # ------------------------------------------------------------------
    def build(self, node: Node, depth: int = 0) -> Node:
        node.depth = depth
        cap_reached = self._node_count >= self.limits.max_nodes
        if cap_reached and not self._cap_hit:
            self._cap_hit = True
            self._log(f"node cap {self.limits.max_nodes} hit at {node.id}; forcing Draw")
        if depth >= self.limits.max_depth or cap_reached or is_atomic(node, self.limits.max_depth):
            node.model = self.generator.draw(node)
            self._after_fragment(node)
            self.critic_loop(node)
            self._validate_svg(node)
            self.sheaf.store(node)
            return node

        children = self._decompose(node)
        if len(children) < 2:  # could not split further: draw
            node.marked_leaf = True
            return self.build(node, depth)
        node.children = children
        for c in children:
            self.build(c, depth + 1)
        node.model = self.worker.merge(node, children)
        self._after_fragment(node)
        self.critic_loop(node)
        if node.critical_count() > 3:
            self._log(f"{node.id}: {node.critical_count()} critical residuals; forcing re-Decompose")
            node.children = []
            node.residuals = [r for r in node.residuals if r.severity != "critical"]
            children = self._decompose(node, force=True)
            if len(children) >= 2:
                node.children = children
                for c in children:
                    self.build(c, depth + 1)
                node.model = self.worker.merge(node, children)
                self._after_fragment(node)
                self.critic_loop(node)
        self._validate_invariants(node)
        self.sheaf.store(node)
        return node

    def _decompose(self, node: Node, force: bool = False) -> List[Node]:
        children = self.generator.decompose(node, self._next_id)
        if force:
            # alternative split: halve the component list into two children
            comps = list(node.components)
            half = (len(comps) + 1) // 2
            children = []
            for group in (comps[:half], comps[half:]):
                if not group:
                    continue
                gset = set(group)
                children.append(
                    Node(
                        id=self._next_id(),
                        parent_id=node.id,
                        description=to_noun_phrase(", ".join(group)),
                        depth=node.depth + 1,
                        style=node.style,
                        components=list(group),
                        flows=[f for f in node.flows if f.src in gset and f.dst in gset],
                    )
                )
        if not 2 <= len(children) <= 4:
            self._log(f"{node.id}: decomposition produced {len(children)} children; forcing Draw")
            return []
        if self._node_count + len(children) > self.limits.max_nodes:
            self._log(f"node cap {self.limits.max_nodes} would be exceeded at {node.id}; forcing Draw")
            self._cap_hit = True
            return []
        for c in children:
            c.description = to_noun_phrase(c.description)
        self._node_count += len(children)
        return children

    # ------------------------------------------------------------------
    def _after_fragment(self, node: Node) -> None:
        frag: Fragment = node.model
        node.ports = frag.ports
        node.canvas = {"w": frag.w, "h": frag.h}
        node.bbox = BBox(0, 0, frag.w, frag.h)
        node.svg_fragment = frag.svg()

    def _validate_svg(self, node: Node) -> None:
        try:
            from figtree.svgmodel import parse_svg

            parse_svg(wrap_svg(node.model, node.style))
        except Exception as exc:  # noqa: BLE001
            node.residuals.append(ResidualDefect("critical", f"SVG parse failure: {exc}", node.id, "roll back"))

    def critic_loop(self, node: Node) -> None:
        """render -> Critic -> Worker repair -> re-validate invariants, at most ``max_critic_rounds``."""
        last_valid = node.model.clone()
        previous: set = set()
        for rnd in range(1, self.limits.max_critic_rounds + 1):
            svg = wrap_svg(node.model, node.style)
            png = render_png(svg, self.render_dir, node.id) if self.render else None
            defects = self.critic.review(svg, node.style, png, rnd, padded=not node.is_leaf())
            actionable = [d for d in defects if d.code_anchor != "no-vision"]
            no_vision = [d for d in defects if d.code_anchor == "no-vision"]
            if not actionable:
                for d in no_vision:
                    if not any(r.code_anchor == "no-vision" for r in node.residuals):
                        node.residuals.append(d)
                self._after_fragment(node)
                return
            self._log(f"{node.id} round {rnd}: {len(actionable)} defect(s)")
            signature = {(d.code_anchor, d.visual_description) for d in actionable}
            if signature == previous:  # no progress: stop early, keep as residuals
                self._log(f"{node.id}: repair made no progress; recording residuals")
                node.residuals.extend(d for d in actionable if not any(r.code_anchor == d.code_anchor and r.visual_description == d.visual_description for r in node.residuals))
                self._after_fragment(node)
                return
            previous = signature
            try:
                unresolved = self.worker.local_repair(node, actionable)
            except RepairError as exc:
                node.model = last_valid.clone()
                self.worker.refresh_ports(node)
                node.residuals.append(ResidualDefect("critical", f"repair broke the fragment: {exc}; rolled back", node.id, "manual review", rnd))
                self._after_fragment(node)
                return
            last_valid = node.model.clone()
            self._after_fragment(node)
            if unresolved and rnd == self.limits.max_critic_rounds:
                node.residuals.extend(unresolved)
        # final review after the last round
        svg = wrap_svg(node.model, node.style)
        defects = self.critic.review(svg, node.style, None, self.limits.max_critic_rounds + 1, padded=not node.is_leaf())
        for d in defects:
            if d.code_anchor == "no-vision":
                if not any(r.code_anchor == "no-vision" for r in node.residuals):
                    node.residuals.append(d)
            elif not any(r.code_anchor == d.code_anchor and r.visual_description == d.visual_description for r in node.residuals):
                node.residuals.append(d)
        self._after_fragment(node)

    def _validate_invariants(self, node: Node) -> None:
        """Style conserved and ports consistent across the parent/child boundary."""
        for c in node.children:
            if c.style.invariant_key() != node.style.invariant_key():
                node.residuals.append(ResidualDefect("critical", f"style invariant broken at {c.id}", c.id, "restore GlobalStyle"))
            for p in c.ports:
                expected = (c.offset["x"] + p.rel_x, c.offset["y"] + p.rel_y)
                if not any((q.rel_x, q.rel_y) == expected and q.side == p.side for q in node.ports):
                    node.residuals.append(ResidualDefect("critical", f"port {c.id}.{p.id} not re-exported by {node.id}", node.id, "re-extract ports"))
                    break


def _dedupe_global(residuals: List[ResidualDefect]) -> List[ResidualDefect]:
    """Per-node sections stay in the sheaf; the global list collapses repeated global flags."""
    out: List[ResidualDefect] = []
    seen: set = set()
    for r in residuals:
        key = (r.severity, r.code_anchor, r.visual_description)
        if r.code_anchor in ("no-vision", "ingest") and key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def assign_absolute_ports(root: Node, offset: tuple = (0, 0)) -> None:
    """Fill ``abs_x``/``abs_y`` for every port in the tree (root canvas frame)."""
    for p in root.ports:
        p.abs_x = offset[0] + p.rel_x
        p.abs_y = offset[1] + p.rel_y
    for c in root.children:
        assign_absolute_ports(c, (offset[0] + c.offset["x"], offset[1] + c.offset["y"]))
