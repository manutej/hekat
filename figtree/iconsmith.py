"""Icon smith: the generate -> critique -> refine loop applied to custom icon design.

An :class:`IconSpec` names the concept, its metaphor and the constraints of the family
(24-grid, 2px stroke, round joins, no text, at most a dozen strokes).  A draughtsman
(rule-based composition of primitives, or a Claude-backed one) proposes an icon program; the
icon rubric scores it; mechanical fixes are applied; what remains is handed back as
requests.  Accepted icons join the library as ``<symbol>`` definitions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from figtree.icons import ICONS, ICON_VIEWBOX, standalone_icon
from figtree.program import load_program
from figtree.quality import Issue, QualityCritic, icon_family_issues
from figtree.refine import Refiner
from figtree.rubrics import get_rubric


@dataclass
class IconSpec:
    name: str
    concept: str
    metaphor: str = ""  # the visual idea, e.g. "a document with a magnifier"
    family: str = "figtree"  # 24 grid, 2px stroke, round caps/joins, currentColor
    must_read_at: int = 16  # px
    max_strokes: int = 12
    base: Optional[str] = None  # library icon to adapt, when the metaphor is close to one

    def prompt(self) -> str:
        return (
            f"Design the icon '{self.name}' meaning: {self.concept}. Metaphor: {self.metaphor or 'choose a literal, recognisable object'}. "
            f"Family: {ICON_VIEWBOX} grid, stroke-width 2, stroke=currentColor, fill=none, round caps and joins, "
            f"no text, at most {self.max_strokes} strokes, must read at {self.must_read_at}px, 2px safe margin, "
            f"consistent with these library icons: {', '.join(sorted(ICONS))}. Output only the inner SVG elements."
        )


_PRIMITIVES: Dict[str, str] = {
    "page": '<path d="M6 3h8l5 5v13H6z"/><path d="M14 3v5h5"/>',
    "lens": '<circle cx="15" cy="15" r="4.5"/><path d="M18.3 18.3L22 22"/>',
    "lines": '<path d="M9 12h6M9 16h6"/>',
    "box": '<rect x="4" y="6" width="16" height="12" rx="1"/>',
    "arrow": '<path d="M4 12h12"/><path d="M12 8l4 4-4 4"/>',
    "arrows-cycle": '<path d="M4 12a8 8 0 0 1 13.7-5.7L20 8"/><path d="M20 4v4h-4"/><path d="M20 12a8 8 0 0 1-13.7 5.7L4 16"/><path d="M4 20v-4h4"/>',
    "node": '<circle cx="12" cy="12" r="3"/>',
    "branches": '<path d="M12 9V5M12 15l-6 4M12 15l6 4"/>',
    "tick": '<path d="M7 12.5l3 3 7-7"/>',
    "pencil": '<path d="M4 20l4-1 11-11-3-3L5 16z"/><path d="M13 8l3 3"/>',
    "spark": '<path d="M12 4v3M12 17v3M4 12h3M17 12h3M6.3 6.3l2.2 2.2M15.5 15.5l2.2 2.2M6.3 17.7l2.2-2.2M15.5 8.5l2.2-2.2"/>',
    "frame": '<rect x="3" y="4" width="18" height="16" rx="1"/>',
    "wave": '<path d="M3 15c3-6 6-6 9 0s6 6 9 0"/>',
}

_METAPHOR_WORDS: List[tuple] = [
    (("document", "paper", "text", "page", "spec"), "page"),
    (("search", "find", "ground", "inspect", "look"), "lens"),
    (("list", "lines", "content"), "lines"),
    (("box", "block", "module", "component"), "box"),
    (("flow", "arrow", "next", "pipeline"), "arrow"),
    (("loop", "cycle", "iterate", "repeat", "refine"), "arrows-cycle"),
    (("node", "point", "centre", "center"), "node"),
    (("tree", "branch", "split", "decompose"), "branches"),
    (("check", "done", "accept", "verify"), "tick"),
    (("edit", "write", "draw", "pencil"), "pencil"),
    (("spark", "idea", "render", "light"), "spark"),
    (("frame", "canvas", "image", "figure"), "frame"),
    (("wave", "signal", "animate", "motion"), "wave"),
]


def compose_icon(spec: IconSpec) -> str:
    """Rule-based draughtsman: compose up to three primitives named by the metaphor."""
    if spec.base and spec.base in ICONS:
        return ICONS[spec.base]
    words = f"{spec.concept} {spec.metaphor}".lower()
    chosen: List[str] = []
    for keys, prim in _METAPHOR_WORDS:
        if any(k in words for k in keys) and prim not in chosen:
            chosen.append(prim)
        if len(chosen) == 3:
            break
    if not chosen:
        chosen = ["box", "arrow"]
    # a lens or tick composes as an overlay in the bottom-right corner over a page/box
    return "".join(_PRIMITIVES[p] for p in chosen)


@dataclass
class IconResult:
    spec: IconSpec
    inner: str
    svg: str
    score: float
    issues: List[Dict[str, Any]] = field(default_factory=list)
    trajectory: List[Dict[str, Any]] = field(default_factory=list)
    accepted: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.spec.name, "concept": self.spec.concept, "score": self.score, "accepted": self.accepted, "issues": self.issues, "trajectory": self.trajectory, "inner": self.inner}


def icon_structural_issues(svg: str, spec: IconSpec) -> List[Issue]:
    """Family rules beyond the generic icon rubric (safe margin, coverage, stroke count, fills, feature
    size, gaps, crossings, ink balance).  They live in ``figtree.quality.icon_family_issues`` and run
    inside ``QualityCritic`` for the icon rubric, so ``figtree eval`` measures them; this wrapper keeps
    the spec's own limits (``max_strokes``, ``must_read_at``) for callers that score an icon directly."""
    from dataclasses import replace

    rubric = replace(get_rubric("icon"), max_strokes=spec.max_strokes, must_read_at=spec.must_read_at)
    return icon_family_issues(load_program(svg), rubric)


class IconSmith:
    def __init__(self, draughtsman=None, rounds: int = 3, accept_at: float = 9.0) -> None:
        self.draughtsman = draughtsman or compose_icon
        self.rounds = rounds
        self.accept_at = accept_at
        self.critic = QualityCritic("icon")

    def score(self, inner: str, spec: IconSpec) -> tuple:
        from dataclasses import replace

        svg = standalone_icon(spec.name, inner, size=48)
        # the family rules run inside the critic (icon rubric) with the spec's own limits
        critic = QualityCritic(replace(self.critic.rubric, max_strokes=spec.max_strokes, must_read_at=spec.must_read_at))
        report = critic.review(svg)
        return svg, report

    def design(self, spec: IconSpec, requests: Optional[Sequence[Sequence[Dict[str, Any]]]] = None) -> IconResult:
        inner = self.draughtsman(spec)
        svg, report = self.score(inner, spec)
        trajectory = [{"round": 0, "score": report.overall, "issues": len(report.issues)}]
        # mechanical refinement rounds on the standalone icon document
        ref = Refiner("icon", max_rounds=self.rounds, render=False)
        res = ref.run(svg, requests)
        final_svg = res.svg
        inner_final = _inner_of(final_svg)
        _, final_report = self.score(inner_final, spec)
        for r in res.trajectory[1:]:
            trajectory.append({"round": r.round, "score": r.overall, "issues": r.issues, "edits": r.edits_applied})
        issues = [i.to_dict() for i in final_report.issues]
        return IconResult(spec, inner_final, final_svg, final_report.overall, issues, trajectory, final_report.overall >= self.accept_at)


def _inner_of(svg: str) -> str:
    m = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S)
    body = m.group(1) if m else svg
    body = re.sub(r"\s+xmlns(:\w+)?=\"[^\"]*\"", "", body)
    return body.strip()


def sheet(results: Sequence[IconResult], cols: int = 6, cell: int = 72) -> str:
    """Contact sheet of icons with names and scores (an editable SVG, same rules as any figure)."""
    rows = (len(results) + cols - 1) // cols
    w, h = cols * cell + 24, rows * (cell + 24) + 24
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="Times New Roman">',
           f'<rect id="background" width="{w}" height="{h}" fill="#FFFFFF"/>', "<defs>"]
    for r in results:
        out.append(f'<symbol id="icon-{r.spec.name}" viewBox="{ICON_VIEWBOX}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{r.inner}</symbol>')
    out.append("</defs>")
    for i, r in enumerate(results):
        x = 24 + (i % cols) * cell
        y = 24 + (i // cols) * (cell + 24)
        out.append(f'<g id="cell-{r.spec.name}" transform="translate({x},{y})" color="#333333">')
        out.append(f'<use href="#icon-{r.spec.name}" x="12" y="0" width="48" height="48"/>')
        out.append(f'<text x="36" y="64" font-size="11" text-anchor="middle" fill="#333333" data-kind="label">{r.spec.name}</text>')
        out.append(f'<text x="36" y="80" font-size="9" text-anchor="middle" fill="#666666" data-kind="annot">{r.score:.1f}</text>')
        out.append("</g>")
    out.append("</svg>")
    return "\n".join(out)
