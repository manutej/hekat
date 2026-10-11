"""Iterative refinement loop (the paper's iterative-editing evaluation, as a tool).

    round 0:  normalise ids -> render -> score
    round r:  edits = auto-fixes from the critic + external edit requests for this round
              apply (local, anchored) -> render -> score -> record trajectory point
    stop:     no edits left, score plateau, or round budget exhausted

External edit requests may come from a human (an ``edits.json`` with one script per round),
from a VLM (``figtree.agents.llm.ClaudeEditor`` turns a prose request into a script) or from
any callable ``request_fn(round_no, svg, report) -> list[EditOp]``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

from figtree.edits import EditOp, apply_edits
from figtree.editability import element_diff
from figtree.program import normalize_svg
from figtree.quality import QualityCritic, QualityReport
from figtree.render import render_png
from figtree.rubrics import Rubric, get_rubric

RequestSource = Union[None, Sequence[Sequence[EditOp]], Callable[[int, str, QualityReport], Optional[List[EditOp]]]]


@dataclass
class RoundRecord:
    round: int
    overall: float
    scores: Dict[str, float]
    issues: int
    critical: int
    edits_applied: int
    edits_failed: int
    diff_elements: int
    rendered: Optional[str] = None
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class RefineResult:
    svg: str
    initial: QualityReport
    final: QualityReport
    trajectory: List[RoundRecord] = field(default_factory=list)
    requests_remaining: List[Dict[str, Any]] = field(default_factory=list)
    stop_reason: str = ""
    ids_assigned: int = 0

    @property
    def improvement(self) -> float:
        return round(self.final.overall - self.initial.overall, 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rubric": self.final.rubric,
            "initial": self.initial.to_dict(),
            "final": self.final.to_dict(),
            "improvement": self.improvement,
            "trajectory": [r.to_dict() for r in self.trajectory],
            "requests_remaining": list(self.requests_remaining),
            "stop_reason": self.stop_reason,
            "ids_assigned": self.ids_assigned,
        }


class Refiner:
    def __init__(
        self,
        rubric: Union[Rubric, str] = "teaching",
        max_rounds: int = 8,
        plateau: int = 2,
        render: bool = True,
        render_dir: Optional[str] = None,
        critic: Optional[QualityCritic] = None,
    ) -> None:
        self.rubric = get_rubric(rubric) if isinstance(rubric, str) else rubric
        self.max_rounds = max_rounds
        self.plateau = plateau
        self.render = render
        self.render_dir = render_dir
        self.critic = critic or QualityCritic(self.rubric)

    @staticmethod
    def _canvas_unchanged(svg: str, op: EditOp) -> bool:
        import re

        w = re.search(r'<svg[^>]*\swidth="(\d+)', svg)
        h = re.search(r'<svg[^>]*\sheight="(\d+)', svg)
        return bool(w and h and int(w.group(1)) == int(op.get("width", -1)) and int(h.group(1)) == int(op.get("height", -1)))

    def _render(self, svg: str, name: str) -> Optional[str]:
        if not self.render:
            return None
        try:
            return render_png(svg, self.render_dir, name)
        except Exception:  # noqa: BLE001
            return None

    def run(
        self,
        svg_text: str,
        requests: RequestSource = None,
        source_text: Optional[str] = None,
        plan_terms: Optional[Sequence[str]] = None,
        auto: bool = True,
    ) -> RefineResult:
        svg, assigned = normalize_svg(svg_text)
        png = self._render(svg, "round0")
        report = self.critic.review(svg, source_text, plan_terms, png)
        initial = report
        trajectory = [RoundRecord(0, report.overall, report.scores, len(report.issues), sum(1 for i in report.issues if i.severity == "critical"), 0, 0, 0, png, "baseline")]
        best = report.overall
        stale = 0
        stop = "round budget exhausted"
        applied_keys: set = set()
        for rnd in range(1, self.max_rounds + 1):
            ops: List[EditOp] = []
            # external requests first (content decisions), then the critic's mechanical fixes;
            # element-anchored fixes are applied once, canvas-level ops recur while still requested
            external: Optional[List[EditOp]] = None
            if callable(requests):
                external = requests(rnd, svg, report)
            elif requests is not None and rnd - 1 < len(requests):
                external = list(requests[rnd - 1])
            if external:
                ops.extend(external)
            if auto:
                for op in report.auto_edits():
                    key = repr(sorted((k, str(v)) for k, v in op.items()))
                    if op.get("op") == "set_canvas" and self._canvas_unchanged(svg, op):
                        continue
                    if "id" in op and key in applied_keys:
                        continue
                    applied_keys.add(key)
                    ops.append(op)
            if not ops:
                stop = "no edits left"
                break
            result = apply_edits(svg, ops)
            diff = len(element_diff(svg, result.svg))
            svg = result.svg
            png = self._render(svg, f"round{rnd}")
            report = self.critic.review(svg, source_text, plan_terms, png)
            trajectory.append(
                RoundRecord(rnd, report.overall, report.scores, len(report.issues), sum(1 for i in report.issues if i.severity == "critical"),
                            len(result.applied), len(result.failed), diff, png,
                            "; ".join(f"{op.get('op')}:{op.get('id', op.get('parent_id', ''))}" for op in result.applied)[:200])
            )
            if report.overall > best + 1e-9:
                best = report.overall
                stale = 0
            else:
                stale += 1
                if stale >= self.plateau:
                    stop = f"score plateau after {self.plateau} rounds"
                    break
        else:
            pass
        remaining = [i.to_dict() for i in report.requests()]
        return RefineResult(svg, initial, report, trajectory, remaining, stop, assigned)
