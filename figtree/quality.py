"""Quality critic: rubric-scored, element-anchored review of any addressable SVG program.

Every signal is measurable from the program (and, when available, the rendered image), so a
score is reproducible and every issue carries a ``code_anchor``, a ``fix_instruction`` and,
when the fix is mechanical, an ``auto_edit`` that the refinement loop applies.  Scores use
the paper's 1-10 scale per dimension; the overall score is the weighted mean.

The checks are organised by medium: the diagram checks (flow, text, polish, topology) run for
every medium that allows them, ``_chart_checks`` for data figures, ``_tile_checks`` for
dashboard tiles, ``_icon_checks`` (the icon family rules, shared with IconSmith) for icons and
``_motion_checks`` whenever the document carries CSS animation.  Every issue is tagged with its
check id from ``figtree.rubric_spec.CHECKS`` so the probe harness can measure each check.
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from figtree.edits import EditOp
from figtree.geometry import is_orthogonal
from figtree.program import (
    ElementInfo,
    Program,
    contrast_ratio,
    hex_color,
    load_program,
    luminance,
    parse_color,
    parse_len,
    path_extent_points,
    path_subpaths,
    saturation,
)
from figtree.rubrics import DIMENSIONS, Rubric, get_rubric
from figtree.schemas import BBox

GREYS = {"#FFFFFF", "#000000", "#333333", "#666666", "#999999", "#CCCCCC", "#D5D5D5", "#F5F5F5", "#EEEEEE", "#DDDDDD"}
# axis-like vocabulary; the unit forms (parentheses, %, currency) are matched without word boundaries
AXIS_WORDS = re.compile(r"\b(?:axis|per|rate|count|score|accuracy|time|year|month|day|loss|error|epoch|step|latency|throughput)\b|\(.+\)|%|[$€£]", re.IGNORECASE)
UNIT_RE = re.compile(r"\(.+\)|%|[$€£]|\b(?:unitless|dimensionless|a\.u\.|arb\.)", re.IGNORECASE)
DIMENSIONLESS = re.compile(r"\b(?:epochs?|steps?|iterations?|count|number|index|rank|rounds?|trials?|samples?|n|quarter|year|month|day|date|week|weekday|hour|category|categories|class|label|group|region|model|configuration|variant|method)\b", re.IGNORECASE)
NUMERIC_RE = re.compile(r"^[+\-−]?[$€£]?\d[\d,]*(?:\.\d+)?\s?[%KMBk]?$")
TILE_VALUE_RE = re.compile(r"^[+\-−]?[$€£]?\d[\d,.]*\s?[%KMBk]?(?:\s?\d+[a-z]{1,2})?[a-z]{0,2}$")
SIGNED_DELTA_RE = re.compile(r"[+\-−▲▼↑↓]\s?\d")
STATUS_WORDS = re.compile(r"\b(?:up|down|healthy|critical|warning|ok|error|errors|failing|failed|target|goal|threshold|limit|budget|sla|above|below|vs\.?|versus|open|pending|need|needs|attention|overdue|late|due|alert|good|bad|on track|off track|behind|ahead)\b", re.IGNORECASE)
SPAN_CAPTION_RE = re.compile(r"\d+\s?(?:wk|w|weeks?|d|days?|mo|months?|h|hrs?|hours?|min|yrs?|years?|q)\b|\b(?:avg|average|trailing|rolling|last|baseline|dashed|median|target)\b", re.IGNORECASE)
FINDING_WORDS = re.compile(r"\b(?:rises?|rising|rose|falls?|falling|fell|grows?|growing|grew|drops?|dropped|leads?|leading|led|beats?|outperforms?|exceeds?|stays?|remains?|saturates?|reaches?|overtakes?|declines?|increases?|decreases?|improves?|doubles?|halves?|peaks?|dominates?|delivers?|wins?|lags?|trails?|matches?|holds?|converges?|diverges?|lifts?|flat|higher|lower|more|less|fewer|faster|slower|better|worse|most|least|above|below|than|vs\.?|versus|by|outpaces?|shrinks?|climbs?|plateaus?|sold|cost|costs|earns?|loses?|gains?|cuts?|halved|doubled|tripled)\b|\d", re.IGNORECASE)
SENTENCE_START = re.compile(r"^(?:the|a|an|if|then|otherwise|finally|when|while|after|before|and|but|so|because|first|next|lastly|once|thus|hence)\b", re.IGNORECASE)
EMBEDDED_TITLE = re.compile(r"^(?:Figure|Fig\.|Table|Algorithm)\s*\d", re.IGNORECASE)
SOURCE_WORDS = re.compile(r"\b(?:raw|input|inputs|source|sources|sensor|sensors)\b", re.IGNORECASE)
SINK_WORDS = re.compile(r"\b(?:report|reports|output|outputs|result|results|dashboard)\b", re.IGNORECASE)


@dataclass
class Issue:
    dimension: str
    severity: str  # critical | warning
    visual_description: str
    code_anchor: str
    fix_instruction: str
    penalty: float
    auto_edit: Optional[EditOp] = None
    check_id: Optional[str] = None  # from figtree.rubric_spec.classify

    def to_dict(self) -> Dict[str, object]:
        return {
            "check_id": self.check_id,
            "dimension": self.dimension,
            "severity": self.severity,
            "visual_description": self.visual_description,
            "code_anchor": self.code_anchor,
            "fix_instruction": self.fix_instruction,
            "penalty": self.penalty,
            "auto_edit": self.auto_edit,
        }


@dataclass
class QualityReport:
    rubric: str
    scores: Dict[str, Optional[float]]  # None = not assessed (no source / plan available)
    overall: float
    issues: List[Issue] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)

    def auto_edits(self) -> List[EditOp]:
        seen = set()
        out: List[EditOp] = []
        for i in self.issues:
            if i.auto_edit is not None:
                key = repr(sorted(i.auto_edit.items()))
                if key not in seen:
                    seen.add(key)
                    out.append(i.auto_edit)
        return out

    def requests(self) -> List[Issue]:
        """Issues that need a content decision (no mechanical fix): the edit requests for a human/VLM."""
        return [i for i in self.issues if i.auto_edit is None]

    def to_dict(self) -> Dict[str, object]:
        return {
            "rubric": self.rubric,
            "scores": dict(self.scores),
            "overall": self.overall,
            "issues": [i.to_dict() for i in self.issues],
            "tags": list(self.tags),
            "metrics": dict(self.metrics),
        }


# ---------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------

Point = Tuple[float, float]


def _segments(pts: Sequence[Point]):
    return [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]


def _seg_len(a: Point, b: Point) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def segment_inside_length(a: Point, b: Point, box: BBox, pad: float = 0.0) -> float:
    """Length of the part of segment a->b strictly inside ``box`` inflated by ``pad`` (Liang-Barsky)."""
    x1, y1, x2, y2 = box.x - pad, box.y - pad, box.x2 + pad, box.y2 + pad
    if x2 - x1 <= 0 or y2 - y1 <= 0:
        return 0.0
    dx, dy = b[0] - a[0], b[1] - a[1]
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, a[0] - x1), (dx, x2 - a[0]), (-dy, a[1] - y1), (dy, y2 - a[1])):
        if p == 0:
            if q <= 0:  # parallel and on/outside the open boundary
                return 0.0
            continue
        r = q / p
        if p < 0:
            if r > t1:
                return 0.0
            t0 = max(t0, r)
        else:
            if r < t0:
                return 0.0
            t1 = min(t1, r)
    if t1 <= t0:
        return 0.0
    return (t1 - t0) * math.hypot(dx, dy)


def _orient(a: Point, b: Point, c: Point) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def segments_cross(a: Point, b: Point, c: Point, d: Point) -> bool:
    """Proper crossing of two segments (touching at an endpoint or collinear overlap excluded)."""
    o1, o2, o3, o4 = _orient(a, b, c), _orient(a, b, d), _orient(c, d, a), _orient(c, d, b)
    if o1 == 0 or o2 == 0 or o3 == 0 or o4 == 0:
        return False
    return (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0)


def segment_intersection(a: Point, b: Point, c: Point, d: Point) -> Optional[Point]:
    if not segments_cross(a, b, c, d):
        return None
    den = (a[0] - b[0]) * (c[1] - d[1]) - (a[1] - b[1]) * (c[0] - d[0])
    if den == 0:
        return None
    t = ((a[0] - c[0]) * (c[1] - d[1]) - (a[1] - c[1]) * (c[0] - d[0])) / den
    return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))


def collinear_overlap(a: Point, b: Point, c: Point, d: Point) -> float:
    """Overlap length of two collinear axis-aligned segments (0 when not collinear)."""
    if a[1] == b[1] == c[1] == d[1]:
        return max(0.0, min(max(a[0], b[0]), max(c[0], d[0])) - max(min(a[0], b[0]), min(c[0], d[0])))
    if a[0] == b[0] == c[0] == d[0]:
        return max(0.0, min(max(a[1], b[1]), max(c[1], d[1])) - max(min(a[1], b[1]), min(c[1], d[1])))
    return 0.0


def _quad(e: ElementInfo) -> List[Point]:
    if e.corners:
        return list(e.corners)
    b = e.bbox
    return [(b.x, b.y), (b.x2, b.y), (b.x2, b.y2), (b.x, b.y2)]


def polygons_overlap(p: Sequence[Point], q: Sequence[Point]) -> bool:
    """Separating-axis test for two convex polygons (oriented text boxes)."""
    for poly in (p, q):
        for i in range(len(poly)):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % len(poly)]
            nx, ny = y1 - y2, x2 - x1
            pa = [nx * x + ny * y for x, y in p]
            qa = [nx * x + ny * y for x, y in q]
            if max(pa) <= min(qa) + 1e-6 or max(qa) <= min(pa) + 1e-6:
                return False
    return True


def texts_overlap(a: ElementInfo, b: ElementInfo) -> bool:
    if a.bbox is None or b.bbox is None:
        return False
    if not a.bbox.intersects(b.bbox):
        return False
    if a.corners is None and b.corners is None:
        return True
    return polygons_overlap(_quad(a), _quad(b))


def _on_boundary(p: Point, box: BBox, tol: float = 1.5) -> bool:
    x, y = p
    if not (box.x - tol <= x <= box.x2 + tol and box.y - tol <= y <= box.y2 + tol):
        return False
    return abs(x - box.x) <= tol or abs(x - box.x2) <= tol or abs(y - box.y) <= tol or abs(y - box.y2) <= tol


def _strictly_inside(p: Point, box: BBox, tol: float = 1.5) -> bool:
    x, y = p
    return box.x + tol < x < box.x2 - tol and box.y + tol < y < box.y2 - tol


def _touches(p: Point, box: BBox, tol: float = 2.0) -> bool:
    return box.x - tol <= p[0] <= box.x2 + tol and box.y - tol <= p[1] <= box.y2 + tol


def _stem(word: str) -> str:
    w = word.lower().strip(" :.,;()[]")
    for suf in ("ing", "ed", "ers", "er", "es", "s"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def _hue_class(c: Tuple[int, int, int]) -> str:
    r, g, b = c
    if r > g + 40 and r > b + 40:
        return "red"
    if g > r + 30 and g > b + 30:
        return "green"
    return ""


def _hue_bucket(c: Tuple[int, int, int]) -> int:
    r, g, b = (v / 255.0 for v in c)
    mx, mn = max(r, g, b), min(r, g, b)
    if mx - mn < 0.08:
        return -1
    if mx == r:
        h = ((g - b) / (mx - mn)) % 6
    elif mx == g:
        h = (b - r) / (mx - mn) + 2
    else:
        h = (r - g) / (mx - mn) + 4
    return int(h * 60 / 30) % 12  # 30-degree buckets


# ---------------------------------------------------------------------------
# CSS animation parsing (the motion layer)
# ---------------------------------------------------------------------------

_TIME_RE = re.compile(r"^(-?\d*\.?\d+)(ms|s)$")
_TIMING = {"linear", "ease", "ease-in", "ease-out", "ease-in-out", "step-start", "step-end"}
_DIRECTIONS = {"normal", "reverse", "alternate", "alternate-reverse"}
_FILLS = {"none", "forwards", "backwards", "both"}


@dataclass
class AnimEntry:
    name: str
    duration: float = 0.0
    delay: float = 0.0
    iterations: str = "1"
    direction: str = "normal"


def _parse_time(tok: str) -> Optional[float]:
    m = _TIME_RE.match(tok)
    if not m:
        return None
    v = float(m.group(1))
    return v / 1000.0 if m.group(2) == "ms" else v


def parse_animation(value: str) -> List[AnimEntry]:
    out: List[AnimEntry] = []
    for part in re.split(r",(?![^(]*\))", value):
        toks = [t for t in re.split(r"\s+", part.strip()) if t]
        if not toks:
            continue
        e = AnimEntry(name="")
        times: List[float] = []
        for t in toks:
            tv = _parse_time(t)
            tl = t.lower()
            if tv is not None:
                times.append(tv)
            elif tl in _TIMING or tl.startswith("cubic-bezier") or tl.startswith("steps("):
                continue
            elif tl in _DIRECTIONS:
                e.direction = tl
            elif tl in _FILLS:
                continue
            elif tl == "infinite" or re.fullmatch(r"\d*\.?\d+", tl):
                e.iterations = tl
            elif not e.name:
                e.name = t
        if times:
            e.duration = times[0]
        if len(times) > 1:
            e.delay = times[1]
        if e.name:
            out.append(e)
    return out


def _props(block: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for decl in re.split(r";(?![^(]*\))", block):
        if ":" in decl:
            k, v = decl.split(":", 1)
            out[k.strip().lower()] = v.strip().replace("!important", "").strip()
    return out


def _strip_block(css: str, start: int) -> Tuple[str, int]:
    """Return the text inside the brace block that opens at or after ``start`` and the end index."""
    i = css.find("{", start)
    depth = 0
    for j in range(i, len(css)):
        if css[j] == "{":
            depth += 1
        elif css[j] == "}":
            depth -= 1
            if depth == 0:
                return css[i + 1 : j], j + 1
    return css[i + 1 :], len(css)


def parse_css(css: str) -> Dict[str, object]:
    keyframes: Dict[str, List[Tuple[str, Dict[str, str]]]] = {}
    rules: List[Tuple[str, Dict[str, str]]] = []
    reduced: Optional[List[Tuple[str, Dict[str, str]]]] = None
    rest = []
    pos = 0
    for m in re.finditer(r"@(keyframes|media)\s*([^{]*)", css):
        if m.start() < pos:
            continue
        rest.append(css[pos : m.start()])
        body, end = _strip_block(css, m.end())
        pos = end
        if m.group(1) == "keyframes":
            frames = [(sel.strip().lower(), _props(blk)) for sel, blk in re.findall(r"([^{}]+)\{([^{}]*)\}", body)]
            keyframes[m.group(2).strip()] = frames
        elif "prefers-reduced-motion" in m.group(2) and "reduce" in m.group(2):
            reduced = [(sel.strip(), _props(blk)) for sel, blk in re.findall(r"([^{}]+)\{([^{}]*)\}", body)]
    rest.append(css[pos:])
    for sel, blk in re.findall(r"([^{}]+)\{([^{}]*)\}", "".join(rest)):
        rules.append((sel.strip(), _props(blk)))
    return {"keyframes": keyframes, "rules": rules, "reduced": reduced}


# ---------------------------------------------------------------------------
# the critic
# ---------------------------------------------------------------------------

DIAGRAM_MEDIA = ("paper", "teaching material", "presentation")


class QualityCritic:
    def __init__(self, rubric: Rubric | str = "methodology") -> None:
        self.rubric = get_rubric(rubric) if isinstance(rubric, str) else rubric

    # ------------------------------------------------------------------
    def review(self, svg_text: str, source_text: Optional[str] = None, plan_terms: Optional[Sequence[str]] = None, rendered_path: Optional[str] = None) -> QualityReport:
        R = self.rubric
        prog = load_program(svg_text)
        issues: List[Issue] = []
        metrics: Dict[str, float] = {}
        W, H = prog.width, prog.height
        shapes = prog.shapes()
        texts = prog.texts()
        flows = [] if R.medium == "icon" else prog.flows()  # an icon has no reading order: its markers are drawing
        blocks = [e for e in shapes if (e.tag in ("rect", "circle", "ellipse", "polygon") or e.role == "block") and e.bbox and not prog.is_background(e)]

        def add(dim: str, sev: str, desc: str, anchor: str, fix: str, penalty: float, edit: Optional[EditOp] = None, check: Optional[str] = None) -> None:
            issues.append(Issue(dim, sev, desc, anchor, fix, penalty, edit, check))

        if W <= 0 or H <= 0:
            add("medium_fit", "critical", "canvas has no width/height or viewBox", "svg", "declare width, height and viewBox", 6, check="medium.no_canvas")
            return self._finish(issues, metrics)

        # ---------------- compactness ----------------
        cb = prog.content_bbox()
        if cb is None:
            add("semantic_coverage", "critical", "no drawable content", "svg", "draw the content", 8, check="content.none")
            return self._finish(issues, metrics)
        margins = {"left": cb.x, "top": cb.y, "right": W - cb.x2, "bottom": H - cb.y2}
        metrics["fill_ratio"] = round((cb.w * cb.h) / float(W * H), 3)
        centred = abs(margins["left"] - margins["right"]) <= 8 and abs(margins["top"] - margins["bottom"]) <= 8
        for side, m in margins.items():
            side_len = W if side in ("left", "right") else H
            limit = max(R.margin + 8, R.max_margin_ratio * side_len)
            if R.fixed_canvas and centred:  # a centred figure may breathe on a fixed canvas (deck title and footer bands)
                limit = max(limit, R.max_centred_margin_ratio * side_len)
            if m > limit and R.medium != "icon":  # icons: the family coverage rule speaks instead
                edit = None
                if R.fixed_canvas:  # the canvas is the medium: centre the content instead of shrinking
                    fix = "centre the content on the canvas"
                    edit = None if centred else {"op": "center_content"}
                    if centred:
                        fix = "enlarge the content to fill the canvas"
                elif side in ("right", "bottom"):
                    # trailing blank bands are mechanical to remove; leading ones need the content moved
                    fix = "shrink the canvas to content + margin"
                    edit = {"op": "set_canvas", "width": cb.x2 + R.margin if side == "right" else W, "height": cb.y2 + R.margin if side == "bottom" else H}
                else:
                    fix = "move the content towards the edge and shrink the canvas"
                add("compactness", "warning", f"{side} margin is {m}px of blank canvas", "svg", fix, 1.0, edit, check="compactness.blank_margin")
            if m < 0:
                edit = None
                if R.fixed_canvas:
                    edit = None if centred else {"op": "center_content"}
                    fix = "centre the content, then shorten or shrink what still overflows" if edit else "shorten or shrink the overflowing content"
                elif side in ("right", "bottom"):
                    edit = {"op": "set_canvas", "width": max(W, cb.x2 + R.margin), "height": max(H, cb.y2 + R.margin)}
                    fix = "expand the canvas"
                else:
                    fix = "translate the content inside the canvas"
                add("compactness", "critical", f"content overflows the {side} edge by {-m}px", "svg", fix, 3.0, edit, check="compactness.overflow")
        aspect = W / float(H)
        metrics["aspect"] = round(aspect, 2)
        # a small figure's aspect is dictated by its content; the medium's range applies at page scale
        if not (R.aspect[0] <= aspect <= R.aspect[1]) and (max(W, H) >= 480 or R.require_square):
            axes = {self._dominant_axis(f.points) for f in flows if len(f.points) >= 2}
            tower = aspect < R.aspect[0] and axes == {"v"}
            banner = aspect > R.aspect[1] and axes == {"h"}
            if R.require_square:
                side_px = max(W, H)
                add("medium_fit", "critical", f"canvas aspect {aspect:.2f} is not square", "svg", "use a square viewBox", 3,
                    {"op": "set_canvas", "width": side_px, "height": side_px}, check="medium.square")
            elif not (tower or banner):  # a strictly vertical process is a tower by nature
                add("compactness", "warning", f"canvas aspect {aspect:.2f} outside the {R.medium} range {R.aspect[0]}-{R.aspect[1]} (banner or tower shape)", "svg",
                    "re-flow the layout into rows so the figure is closer to the medium's aspect", 1.5, check="compactness.aspect")
        # connector detours
        if flows:
            ratios = []
            for f in flows:
                if len(f.points) >= 2:
                    direct = abs(f.points[-1][0] - f.points[0][0]) + abs(f.points[-1][1] - f.points[0][1])
                    length = sum(abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in _segments(f.points))
                    if direct > 0:
                        ratios.append(length / direct)
                        if length / direct > 2.5 and length > 200:
                            add("compactness", "warning", f"connector {f.id} is {length}px long for a {direct}px displacement (long detour)", f.id,
                                "move the connected blocks closer or route a shorter loop", 0.8, check="compactness.detour")
            if ratios:
                metrics["mean_detour"] = round(sum(ratios) / len(ratios), 2)

        # ---------------- flow readability ----------------
        if flows:
            self._flow_checks(prog, R, flows, blocks, texts, add, metrics)
        elif len(blocks) > 2 and R.medium not in ("icon", "chart", "dashboard tile"):
            add("flow_readability", "warning", f"{len(blocks)} blocks but no connectors", "svg", "add arrows or spatial grouping that shows the relation between blocks", 1.0, check="flow.no_connectors")

        # ---------------- text quality ----------------
        self._text_checks(prog, R, shapes, texts, blocks, flows, add)

        # ---------------- visual polish / medium fit ----------------
        self._polish_checks(prog, R, shapes, texts, blocks, flows, add, metrics)

        if R.medium == "chart":
            self._chart_checks(prog, R, shapes, texts, add)
        if R.medium == "dashboard tile":
            self._tile_checks(prog, R, shapes, texts, add)
        if R.medium == "icon":
            for i in icon_family_issues(prog, R):
                issues.append(i)

        # ---------------- motion ----------------
        css = "".join(("".join(el.itertext()) or "") for el in prog.root.iter() if isinstance(el.tag, str) and el.tag.split("}")[-1] == "style")
        if "@keyframes" in css:
            self._motion_checks(prog, R, css, flows, blocks, add)

        # ---------------- topology ----------------
        groups = [e for e in prog.elements if e.tag == "g" and e.el.get("data-bbox")]
        if len(blocks) > 6 and not groups and R.medium in DIAGRAM_MEDIA:
            add("topology_accuracy", "warning", f"{len(blocks)} blocks without any grouping", "svg", "group related blocks into labelled containers", 1.0, check="topology.ungrouped")
        for g in groups:
            kids = [e for e in prog.elements if e.parent_id == g.id and e.tag in ("rect", "g", "text", "path")]

            def _container_has_block(k) -> bool:
                if k.tag in ("rect", "g"):
                    return True
                return k.tag == "path" and k.el.get("data-role") == "block"

            if not any(_container_has_block(k) for k in kids):
                add("topology_accuracy", "warning", f"empty container {g.id}", g.id, "remove the empty container", 0.5, {"op": "delete", "id": g.id}, check="topology.empty_container")
        if R.medium in DIAGRAM_MEDIA:
            self._container_checks(prog, blocks, texts, add)
            self._legend_checks(prog, shapes, texts, blocks, add)

        # ---------------- semantic coverage / hallucination ----------------
        if plan_terms:
            labels = " ".join(t.text.lower() for t in texts)
            covered = [p for p in plan_terms if p.lower() in labels]
            metrics["coverage"] = round(len(covered) / len(plan_terms), 2)
            missing = [p for p in plan_terms if p.lower() not in labels]
            if missing:
                add("semantic_coverage", "warning" if len(missing) < len(plan_terms) / 2 else "critical", f"{len(missing)} planned component(s) not labelled: {', '.join(missing[:5])}", "svg",
                    "add the missing components or justify their omission", 1.0 * len(missing), check="coverage.plan_terms")
        if source_text:
            src = source_text.lower()
            for t in texts:
                words = [w for w in re.findall(r"[A-Za-z][A-Za-z-]{3,}", t.text)]
                if words and not any(w.lower() in src for w in words):
                    add("hallucination_control", "warning", f"label {t.id} ({t.text[:30]!r}) has no basis in the source", t.id, "remove or rename to a term from the source", 1.0, check="hallucination.label_source")

        unassessed = []
        if not plan_terms and not R.require_axis_labels:
            unassessed.append("semantic_coverage")
        if not source_text:
            unassessed.append("hallucination_control")
        return self._finish(issues, metrics, unassessed)

    # ------------------------------------------------------------------
    @staticmethod
    def _dominant_axis(points: Sequence[Point]) -> str:
        dx, dy = points[-1][0] - points[0][0], points[-1][1] - points[0][1]
        return "h" if abs(dx) >= abs(dy) else "v"

    @staticmethod
    def _is_forward(points: Sequence[Point]) -> bool:
        dx, dy = points[-1][0] - points[0][0], points[-1][1] - points[0][1]
        return dx > 0 if abs(dx) >= abs(dy) else dy > 0

    @staticmethod
    def _is_data_flow(f: ElementInfo) -> bool:
        kind = (f.el.get("data-flow") or "data").lower()
        return kind == "data" and not f.el.get("stroke-dasharray")

    def _flow_checks(self, prog: Program, R: Rubric, flows: List[ElementInfo], blocks: List[ElementInfo], texts: List[ElementInfo], add, metrics: Dict[str, float]) -> None:
        obstacles = [b for b in blocks if b.bbox and b.role != "container"]
        crossings = 0
        collinear: List[Tuple[str, str, float]] = []
        segs = [(f, s) for f in flows for s in _segments(f.points)]
        reported = set()
        for i in range(len(segs)):
            for j in range(i + 1, len(segs)):
                fi, fj = segs[i][0], segs[j][0]
                if fi.id == fj.id:
                    continue
                if segments_cross(*segs[i][1], *segs[j][1]):
                    crossings += 1
                else:
                    ov = collinear_overlap(*segs[i][1], *segs[j][1])
                    shared_port = fi.points[0] == fj.points[0] or fi.points[-1] == fj.points[-1]  # fan-out / fan-in at one port is a merge, not two heads
                    if ov > 8 and not shared_port and (fi.id, fj.id) not in reported:
                        reported.add((fi.id, fj.id))
                        collinear.append((fi.id, fj.id, ov))
        metrics["crossings"] = crossings
        if crossings:
            add("flow_readability", "warning" if crossings < 3 else "critical", f"{crossings} arrow crossing(s)", flows[0].id, "re-order or re-route to remove crossings", 0.7 * crossings, check="flow.crossings")
        for a, b, ov in collinear:
            add("flow_readability", "critical", f"arrows {a} and {b} share a collinear shaft for {ov:.0f}px (two heads, ambiguous endpoints)", a,
                "offset one arrow by a grid step or merge them into one connector", 1.5, check="flow.collinear_overlap")
        halo = R.flow_halo
        for f in flows:
            if len(f.points) < 2:
                continue
            if not is_orthogonal(f.points) and f.el.get("data-diagonal") != "semantic":
                add("flow_readability", "warning", f"{f.id} uses diagonal routing", f.id, "re-route with horizontal and vertical segments", 0.5, check="flow.diagonal")
            start, end = f.points[0], f.points[-1]
            hit_ids = []
            for b in obstacles:
                box = b.bbox
                if _strictly_inside(start, box) or _strictly_inside(end, box):
                    continue  # an endpoint inside the box: the box hosts the arrow (a container-like block)
                if _on_boundary(start, box) or _on_boundary(end, box):
                    # a port: the shaft must leave the block outward, not slice through it
                    inside = sum(segment_inside_length(a, c, box, 0.0) for a, c in _segments(f.points))
                    if inside > 2.0:
                        hit_ids.append(b.id)
                    continue
                inside = sum(segment_inside_length(a, c, box, halo) for a, c in _segments(f.points))
                if inside > 1.0:
                    hit_ids.append(b.id)
            if hit_ids:
                add("flow_readability", "critical", f"{f.id} passes through a block ({', '.join(hit_ids[:3])})", f.id, "re-route around the block (keep a clear halo of %dpx)" % halo, 1.5, check="flow.through_block")
            struck = [t.id for t in texts if t.bbox and not (_touches(start, t.bbox) or _touches(end, t.bbox))
                      and sum(segment_inside_length(a, c, t.bbox, 0.0) for a, c in _segments(f.points)) > 2.0]
            if struck:
                add("flow_readability", "critical", f"{f.id} strikes through label(s) {', '.join(struck[:3])}", f.id, "move the label beside the shaft or re-route the arrow", 1.5, check="flow.through_text")
            if f.el.get("marker-end"):
                (x1, y1), (x2, y2) = f.points[-2], f.points[-1]
                if abs(x2 - x1) + abs(y2 - y1) < 20:
                    add("flow_readability", "warning", f"{f.id} arrow shaft shorter than 20px", f.id, "lengthen the final segment to at least 20px", 0.5, check="flow.short_shaft")
        # reading order: each arrow classified by its dominant axis and the sign on that axis
        routed = [f for f in flows if len(f.points) >= 2 and f.points[0] != f.points[-1]]
        if routed:
            forward = sum(1 for f in routed if self._is_forward(f.points))
            metrics["forward_ratio"] = round(forward / len(routed), 2)
            if forward / len(routed) < 0.6:
                add("flow_readability", "warning", "most arrows run right-to-left or bottom-to-top", routed[0].id, "re-order blocks so the main flow reads left-to-right / top-to-bottom", 1.0, check="flow.reading_order")
        # semantic direction: a sink with outgoing data and no incoming, a source with incoming and no outgoing
        label_of = self._block_labels(blocks, texts)
        if label_of:
            outgoing: Counter = Counter()
            incoming: Counter = Counter()
            for f in routed:
                if not self._is_data_flow(f):
                    continue
                src = self._block_at(f.points[0], blocks)
                dst = self._block_at(f.points[-1], blocks)
                if src is not None and dst is not None and src.id != dst.id:
                    outgoing[src.id] += 1
                    incoming[dst.id] += 1
            for b in blocks:
                lab = label_of.get(b.id, "")
                if SINK_WORDS.search(lab) and outgoing[b.id] and not incoming[b.id]:
                    add("flow_readability", "critical", f"block {b.id} ({lab[:24]!r}) reads as a sink but only emits data", b.id, "check the arrow direction against the method (judge request)", 2.0, check="flow.semantic_direction")
                elif SOURCE_WORDS.search(lab) and incoming[b.id] and not outgoing[b.id]:
                    add("flow_readability", "critical", f"block {b.id} ({lab[:24]!r}) reads as a source but only receives data", b.id, "check the arrow direction against the method (judge request)", 2.0, check="flow.semantic_direction")

    @staticmethod
    def _block_at(p: Point, blocks: List[ElementInfo]) -> Optional[ElementInfo]:
        hosts = [b for b in blocks if b.bbox and b.role != "container" and _touches(p, b.bbox)]
        if not hosts:
            return None
        return min(hosts, key=lambda b: b.bbox.w * b.bbox.h)

    @staticmethod
    def _block_labels(blocks: List[ElementInfo], texts: List[ElementInfo]) -> Dict[str, str]:
        out: Dict[str, List[str]] = defaultdict(list)
        for t in texts:
            if not t.text or t.bbox is None:
                continue
            host = QualityCritic._host_block(t, blocks)
            if host is not None:
                out[host.id].append(t.text)
        return {k: " ".join(v) for k, v in out.items()}

    # ------------------------------------------------------------------
    def _text_checks(self, prog: Program, R: Rubric, shapes: List[ElementInfo], texts: List[ElementInfo], blocks: List[ElementInfo], flows: List[ElementInfo], add) -> None:
        families: Counter = Counter()
        if not R.allow_text and texts:
            add("medium_fit", "critical", f"{len(texts)} text element(s) in an icon", texts[0].id, "remove text; icons must read without words", 3, check="medium.icon_text")
        tick_like = set(self._tick_labels(prog, shapes, texts)) if R.medium == "chart" else set()
        for t in texts:
            if not t.text:
                continue
            fs = t.font_size if t.font_size is not None else 16.0
            if R.min_font and fs < R.min_font:
                add("text_quality", "critical" if fs < R.min_font * 0.7 else "warning", f"{t.id} font size {fs:g}px below the {R.medium} minimum {R.min_font:g}px", t.id,
                    f"raise font size to at least {R.min_font:g}px", 1.0, {"op": "set_attr", "id": t.id, "attr": "font-size", "value": f"{R.min_font:g}"}, check="text.min_font")
            fam = (t.font_family or "").split(",")[0].strip().strip("'\"")
            if fam:
                families[fam] += 1
            words = len(t.text.split())
            if R.max_words_per_label and words > R.max_words_per_label and t.id not in tick_like:
                add("text_quality", "warning", f"{t.id} has {words} words (limit {R.max_words_per_label})", t.id, "shorten to a keyword label", 0.8, check="text.words_per_label")
            if R.medium != "icon" and EMBEDDED_TITLE.match(t.text) and R.medium in DIAGRAM_MEDIA:
                add("medium_fit", "critical", f"{t.id} embeds a figure title or caption ({t.text[:30]!r}) inside the drawing", t.id, "move the caption out of the figure; the document carries it", 2.0, check="medium.embedded_title")
            elif R.medium != "icon" and words >= 3 and (re.search(r"[.!?]$", t.text) or SENTENCE_START.match(t.text)):
                add("text_quality", "critical", f"{t.id} is a sentence, not a label ({t.text[:30]!r})", t.id, "replace prose with a 1-4 word keyword label", 1.5, check="text.sentence_label")
            # contrast against the shape behind the text
            col = parse_color(t.fill) or (0, 0, 0)
            bg = self._background_for(prog, t)
            host_fill = self._host_fill(prog, t)
            if host_fill and host_fill.lower().startswith("url("):
                add("text_quality", "warning", f"{t.id} sits on a gradient/pattern fill; contrast cannot be guaranteed", t.id, "give the host a flat fill", 1.0, check="text.gradient_host")
            elif bg is not None:
                cr = contrast_ratio(col, bg)
                if cr < R.min_contrast:
                    fix_col = "#333333" if contrast_ratio((0x33, 0x33, 0x33), bg) >= contrast_ratio((255, 255, 255), bg) else "#FFFFFF"
                    add("text_quality", "critical" if cr < 3 else "warning", f"{t.id} contrast {cr:.1f}:1 below {R.min_contrast}:1", t.id,
                        f"use {fix_col} text on {hex_color(bg)}", 1.2, {"op": "recolor", "id": t.id, "fill": fix_col}, check="text.contrast")
            # overflow of the enclosing block
            host = self._host_block(t, blocks)
            if host is not None and t.bbox is not None and t.corners is None and (t.bbox.x < host.bbox.x - 2 or t.bbox.x2 > host.bbox.x2 + 2):
                add("text_quality", "critical", f"{t.id} overflows its block {host.id} ({t.bbox.w}px in {host.bbox.w}px)", t.id, "widen the block or shorten the label", 1.5, check="text.overflow")
        # overlapping text
        tb = [t for t in texts if t.bbox and t.text]
        for i in range(len(tb)):
            for j in range(i + 1, len(tb)):
                if texts_overlap(tb[i], tb[j]):
                    add("text_quality", "critical", f"labels {tb[i].id} and {tb[j].id} overlap", tb[i].id, "move one label or shorten both", 1.5, check="text.overlap")
        if R.max_font_families and len(families) > R.max_font_families:
            main_family = families.most_common(1)[0][0]
            for t in texts:
                fam = (t.font_family or "").split(",")[0].strip().strip("'\"")
                if fam and fam != main_family and t.el.get("font-family"):
                    add("visual_polish", "warning", f"{t.id} uses {fam}; the figure's family is {main_family}", t.id, f"set font-family to {main_family}", 0.5,
                        {"op": "set_attr", "id": t.id, "attr": "font-family", "value": main_family}, check="polish.font_families")
            add("visual_polish", "warning", f"{len(families)} font families in one figure: {', '.join(families)}", texts[0].id, f"use one font family ({main_family})", 0.5, check="polish.font_families")
        # labels drawn as path glyphs (not addressable text) and duplicate block labels
        if R.allow_text and R.medium in DIAGRAM_MEDIA:
            hosted: Dict[str, List[str]] = defaultdict(list)
            for t in texts:
                h = self._host_block(t, blocks)
                if h is not None and t.text:
                    hosted[h.id].append(t.text.strip().lower())
            small = [s for s in shapes if s.tag in ("path", "polyline") and s.bbox and s.role != "block" and not s.is_flow and s.bbox.w <= 12 and s.bbox.h <= 12]
            for b in blocks:
                if b.role == "container" or b.id in hosted or b.bbox is None:
                    continue
                glyphs = [s for s in small if b.bbox.contains_point(*s.centre, strict=False)]
                if len(glyphs) >= 2:
                    height = max(s.bbox.h for s in glyphs)
                    add("text_quality", "critical", f"label of {b.id} is drawn as {len(glyphs)} path glyphs, not addressable text", glyphs[0].id, "replace the glyph paths with a <text> element", 1.5, check="text.outlined_glyphs")
                    if R.min_font and height < R.min_font:
                        add("text_quality", "critical", f"{glyphs[0].id} font size {height:g}px below the {R.medium} minimum {R.min_font:g}px (glyph cluster height)", glyphs[0].id,
                            f"set the label as text at {R.min_font:g}px", 1.0, check="text.min_font")
            seen: Dict[str, List[str]] = defaultdict(list)
            for bid, labs in hosted.items():
                seen[" ".join(labs)].append(bid)
            for lab, ids in seen.items():
                if len(ids) > 1 and lab:
                    add("text_quality", "warning", f"blocks {', '.join(ids)} carry the same label {lab[:24]!r}", ids[0], "disambiguate the labels (or merge the blocks if they are one component)", 1.0, check="text.duplicate_labels")

    # ------------------------------------------------------------------
    def _polish_checks(self, prog: Program, R: Rubric, shapes: List[ElementInfo], texts: List[ElementInfo], blocks: List[ElementInfo], flows: List[ElementInfo], add, metrics: Dict[str, float]) -> None:
        W, H = prog.width, prog.height
        palette: Counter = Counter()
        strokes: Counter = Counter()
        neon = []
        for s in shapes:
            if s.tag == "text":
                continue
            c = parse_color(s.fill)
            if c is not None and hex_color(c) not in GREYS and saturation(c) > 0.05:
                palette[hex_color(c)] += 1
                if saturation(c) > 0.9 and max(c) > 240:
                    neon.append((s, "fill"))
            sc = parse_color(s.stroke)
            if sc is not None and hex_color(sc) not in GREYS and saturation(sc) > 0.9 and max(sc) > 240:
                neon.append((s, "stroke"))
            if s.stroke and s.stroke.lower() != "none" and s.stroke_width is not None:
                strokes[round(s.stroke_width, 1)] += 1
            fill = (s.fill or "").lower()
            if fill.startswith("url("):
                add("visual_polish", "warning", f"{s.id} uses a gradient or pattern fill", s.id, "replace with a flat fill", 1.0, {"op": "recolor", "id": s.id, "fill": "#7BA3C9"}, check="polish.gradient_fill")
            if s.el.get("filter") or "filter:" in (s.el.get("style") or ""):
                add("visual_polish", "warning", f"{s.id} uses a filter effect", s.id, "remove shadows and filters", 1.0, {"op": "set_attr", "id": s.id, "attr": "filter", "value": "none"}, check="polish.filter")
            if s.tag == "rect" and s.el.get("rx") and s.bbox:
                rx_raw = s.el.get("rx")
                rx = parse_len(rx_raw, 0.0)
                if rx_raw.strip().endswith("%"):
                    rx = rx / 100.0 * s.bbox.w
                pill = rx >= min(s.bbox.w, s.bbox.h) / 2.0 - 0.5  # a stadium (toggle track, pill) is a shape, not decoration
                if rx > R.max_corner_radius and not (pill and R.medium == "icon"):
                    add("visual_polish", "warning", f"{s.id} corner radius {rx_raw} looks clip-art like", s.id, f"use rx <= {R.max_corner_radius}", 0.5, {"op": "set_attr", "id": s.id, "attr": "rx", "value": str(R.max_corner_radius)}, check="polish.corner_radius")
        metrics["palette_size"] = len(palette)
        if len(palette) > R.max_palette:
            add("visual_polish", "warning", f"{len(palette)} accent colours (limit {R.max_palette}): {', '.join(palette)}", "svg", "reduce to a small semantic palette", 1.0 * (len(palette) - R.max_palette), check="polish.palette_size")
        for s, which in neon:
            colour = s.fill if which == "fill" else s.stroke
            add("visual_polish", "warning", f"{s.id} uses a neon {which} colour {colour}", s.id, "use a muted tone from the palette", 0.8, {"op": "recolor", "id": s.id, which: "#7BA3C9"}, check="polish.neon")
        if len(strokes) > R.max_stroke_widths:
            if R.max_stroke_widths == 1:
                common = strokes.most_common(1)[0][0]
                for s2 in shapes:
                    if s2.stroke and s2.stroke.lower() != "none" and s2.stroke_width is not None and round(s2.stroke_width, 1) != common and s2.tag != "text":
                        add("visual_polish", "warning", f"{s2.id} stroke width {s2.stroke_width:g} differs from the icon's {common:g}", s2.id, f"set stroke-width to {common:g}", 0.5,
                            {"op": "set_attr", "id": s2.id, "attr": "stroke-width", "value": f"{common:g}"}, check="polish.stroke_widths")
            else:
                add("visual_polish", "warning", f"{len(strokes)} different stroke widths: {sorted(strokes)}", "svg", "use one stroke width for lines and one for borders", 1.0, check="polish.stroke_widths")
        for s in shapes:
            if prog.is_background(s):
                c = parse_color(s.fill)
                if c is not None and max(c) < 60:
                    add("medium_fit", "critical", "black background", s.id, "use a white background", 3, {"op": "recolor", "id": s.id, "fill": "#FFFFFF"}, check="medium.black_background")
        hidden = [h for h in prog.hidden_shapes() if not prog.is_background(h)]
        if hidden:
            sev = "critical" if R.medium == "icon" else "warning"
            check = "icon.invisible_shape" if R.medium == "icon" else "polish.invisible_elements"
            add("visual_polish", sev, f"{len(hidden)} invisible element(s) ({', '.join(h.id for h in hidden[:3])}): no fill and no stroke, opacity 0, hidden, or background-coloured", hidden[0].id,
                "delete invisible elements; they stretch the content box without drawing", 1.0 * len(hidden), {"op": "delete", "id": hidden[0].id}, check=check)
        if R.max_elements is not None and len(shapes) > R.max_elements:
            add("medium_fit", "warning", f"{len(shapes)} elements; an icon should have at most {R.max_elements}", "svg", "simplify the icon", 1.0 * (len(shapes) - R.max_elements) / 2, check="medium.icon_elements")
        # decorative clusters: overlapping circles/ellipses that host no label and carry no arrow (clouds, clip art)
        if R.medium in DIAGRAM_MEDIA:
            ends = [p for f in flows for p in (f.points[0], f.points[-1]) if f.points]
            rounds = [s for s in shapes if s.tag in ("circle", "ellipse") and s.bbox and not any(t.bbox and s.bbox.contains_point(*t.centre, strict=False) for t in texts)
                      and not any(_touches(p, s.bbox) for p in ends)]
            cluster = [(a, b) for i, a in enumerate(rounds) for b in rounds[i + 1 :] if a.bbox.intersects(b.bbox)]
            if cluster:
                ids = sorted({x.id for pair in cluster for x in pair})
                add("visual_polish", "critical", f"decorative cluster of {len(ids)} overlapping ellipses ({', '.join(ids[:3])}) with no label or connector (clip art)", ids[0],
                    "remove decoration; every shape must be a labelled component", 2.0, check="polish.decoration")

    # ------------------------------------------------------------------
    def _container_checks(self, prog: Program, blocks: List[ElementInfo], texts: List[ElementInfo], add) -> None:
        containers = [b for b in blocks if b.role == "container" and b.bbox]
        labels = self._block_labels([b for b in blocks if b.role != "container"], texts)
        for c in containers:
            parent = prog.by_id(c.parent_id) if c.parent_id else None
            title = (parent.el.get("data-label") if parent is not None else None) or ""
            if not title:
                inside = [t for t in texts if t.bbox and c.bbox.contains_point(*t.centre, strict=False) and self._host_block(t, blocks) in (None, c)]
                if inside:
                    title = min(inside, key=lambda t: t.bbox.y).text
            if not title:
                continue
            stems = {_stem(w) for w in re.findall(r"[A-Za-z]+", title) if len(w) > 3}
            if not stems:
                continue
            children = [b for b in blocks if b.role != "container" and b.id != c.id and b.bbox and c.bbox.contains_point(*b.centre, strict=False)]
            outside = [b for b in blocks if b.role != "container" and b.bbox and not c.bbox.contains_point(*b.centre, strict=False)]
            child_hit = any(stems & {_stem(w) for w in re.findall(r"[A-Za-z]+", labels.get(b.id, ""))} for b in children)
            out_hit = [b for b in outside if stems & {_stem(w) for w in re.findall(r"[A-Za-z]+", labels.get(b.id, ""))}]
            if out_hit and not child_hit:
                add("topology_accuracy", "critical", f"container {c.id} is titled {title[:24]!r} but the matching block {out_hit[0].id} sits outside it", c.id,
                    "move the block into its container or retitle the container (judge request)", 2.0, check="topology.container_label_mismatch")

    def _legend_checks(self, prog: Program, shapes: List[ElementInfo], texts: List[ElementInfo], blocks: List[ElementInfo], add) -> None:
        legends = []
        for r in blocks:
            if r.tag != "rect" or r.bbox is None or r.role == "container":
                continue
            if r.role == "legend":
                legends.append(r)
                continue
            swatches = [s for s in shapes if s.tag == "line" and s.bbox and s.bbox.w <= 40 and s.bbox.h <= 2 and r.bbox.contains_point(*s.centre, strict=False)]
            labs = [t for t in texts if t.bbox and r.bbox.contains_point(*t.centre, strict=False)]
            if len(swatches) >= 2 and len(labs) >= 2:
                legends.append(r)
        if not legends:
            return
        others = [b for b in blocks if b.bbox and b.role in ("block", "") and b not in legends and b.tag == "rect"]
        if len(others) < 2:
            return
        x1, y1 = min(b.bbox.x for b in others), min(b.bbox.y for b in others)
        x2, y2 = max(b.bbox.x2 for b in others), max(b.bbox.y2 for b in others)
        for lg in legends:
            b = lg.bbox
            if b.x >= x1 - 2 and b.x2 <= x2 + 2 and b.y >= y1 - 2 and b.y2 <= y2 + 2:
                add("topology_accuracy", "warning", f"legend {lg.id} sits inside the block grid and reads as a stage", lg.id, "move the legend to a margin below or beside the drawing", 1.0, check="layout.legend_in_drawing")

    # ------------------------------------------------------------------
    @staticmethod
    def _axis_lines(shapes: List[ElementInfo], W: int, H: int):
        horiz, vert = [], []
        for s in shapes:
            if s.tag not in ("line", "path", "polyline") or len(s.points) != 2 or not s.stroke or s.stroke.lower() == "none":
                continue
            (x1, y1), (x2, y2) = s.points
            if abs(y1 - y2) <= 1 and abs(x2 - x1) >= 0.2 * W:
                horiz.append((float(y1), float(min(x1, x2)), float(max(x1, x2)), s))
            elif abs(x1 - x2) <= 1 and abs(y2 - y1) >= 0.2 * H:
                vert.append((float(x1), float(min(y1, y2)), float(max(y1, y2)), s))
        return horiz, vert

    def _tick_labels(self, prog: Program, shapes: List[ElementInfo], texts: List[ElementInfo]) -> List[str]:
        """Ids of tick / category labels: end-anchored next to a vertical axis or centred just below a horizontal one."""
        horiz, vert = self._axis_lines(shapes, prog.width, prog.height)
        out = []
        for t in texts:
            if t.bbox is None:
                continue
            anchor = t.el.get("text-anchor") or "start"
            cx, cy = t.centre
            if t.el.get("data-role") in ("tick", "category", "tick-label"):
                out.append(t.id)
                continue
            if anchor == "end" and any(abs(t.bbox.x2 - x) <= 20 and y1 - 8 <= cy <= y2 + 8 for x, y1, y2, _ in vert):
                out.append(t.id)
            elif any(x1 - 4 <= cx <= x2 + 4 and y <= t.bbox.y + 2 <= y + 30 for y, x1, x2, _ in horiz):
                out.append(t.id)
        return out

    def _chart_checks(self, prog: Program, R: Rubric, shapes: List[ElementInfo], texts: List[ElementInfo], add) -> None:
        W, H = prog.width, prog.height
        horiz, vert = self._axis_lines(shapes, W, H)
        numeric = {t.id: float(re.sub(r"[^\d.\-]", "", t.text.replace("−", "-")) or 0) for t in texts if t.text and NUMERIC_RE.match(t.text.strip())}
        # the x axis: the lowest long horizontal line; the y axis: the leftmost long vertical line
        x_axis = max(horiz, key=lambda h: h[0]) if horiz else None
        y_axis = min(vert, key=lambda v: v[0]) if vert else None
        pies = self._pie_slices(shapes)
        if pies:
            add("semantic_coverage", "critical", f"pie chart of {len(pies)} slices ({pies[0].id}, ...)", pies[0].id, "redraw as a sorted bar chart; angles are read worse than lengths", 2.0, check="chart.pie")

        def ticks_left(x: float, y1: float, y2: float) -> List[ElementInfo]:
            return [t for t in texts if t.id in numeric and t.bbox and (t.el.get("text-anchor") == "end" or t.bbox.x2 <= x + 2) and abs(t.bbox.x2 - x) <= 16 and y1 - 8 <= t.centre[1] <= y2 + 8]

        def ticks_right(x: float, y1: float, y2: float) -> List[ElementInfo]:
            return [t for t in texts if t.id in numeric and t.bbox and t.bbox.x >= x - 2 and abs(t.bbox.x - x) <= 16 and y1 - 8 <= t.centre[1] <= y2 + 8]

        def ticks_below(y: float, x1: float, x2: float) -> List[ElementInfo]:
            return [t for t in texts if t.bbox and x1 - 8 <= t.centre[0] <= x2 + 8 and y - 2 <= t.bbox.y <= y + 30]

        y_ticks = ticks_left(*y_axis[:3]) if y_axis else []
        x_tick_texts = ticks_below(*x_axis[:3]) if x_axis else []
        x_ticks = [t for t in x_tick_texts if t.id in numeric]
        # axis labels: rotated text or data-role on the left/right; the lowest centred text under the plot
        x_label = y_labels = None
        xl_cands, yl_cands = [], []
        for t in texts:
            if not t.text or t.bbox is None or t.id in numeric or t.id in {x.id for x in x_tick_texts} or t.id in {y.id for y in y_ticks}:
                continue
            rotated = t.corners is not None or "rotate" in (t.el.get("transform") or "")
            role = t.el.get("data-role") in ("axis-label", "x-label", "y-label")
            if y_axis and rotated and t.bbox.x2 <= y_axis[0] + 4 and t.bbox.y <= y_axis[2] and t.bbox.y2 >= y_axis[1]:
                yl_cands.append(t)
            elif y_axis and not rotated and t.bbox.y2 <= y_axis[1] + 6 and abs(t.bbox.x - y_axis[0]) <= 40 and not AXIS_WORDS.search(t.text) is None:
                yl_cands.append(t)  # unrotated y label sitting above the axis
            elif rotated and vert and t.bbox.x >= max(v[0] for v in vert) - 4:
                yl_cands.append(t)
            elif x_axis and t.centre[1] > x_axis[0] + 12 and x_axis[1] - 40 <= t.centre[0] <= x_axis[2] + 40 and t.font_size and t.font_size >= 9:
                xl_cands.append(t)
            elif role:
                (yl_cands if rotated else xl_cands).append(t)
        if xl_cands:
            x_label = max(xl_cands, key=lambda t: t.centre[1])
        y_labels = yl_cands
        found = ([x_label] if x_label else []) + y_labels
        if R.require_axis_labels:
            fallback = [t for t in texts if t.text and (AXIS_WORDS.search(t.text) or t.el.get("data-role") in ("axis-label", "x-label", "y-label") or "rotate" in (t.el.get("transform") or ""))]
            if len(found) < 2 and len(fallback) < 2 and not pies:
                add("semantic_coverage", "critical", "axis label(s) with units are missing", "svg", "add x and y axis labels with units (insert <text data-role=\"axis-label\">)", 2.5, check="coverage.axis_labels")
            titled = [t for t in texts if t.text and t.bbox and t.font_size]
            if titled:
                top = max(titled, key=lambda t: (t.font_size, -t.bbox.y))
                words = len(top.text.split())
                if words < 3 or (words < R.title_min_words and not FINDING_WORDS.search(top.text)):
                    add("semantic_coverage", "warning", f"the most prominent text ({top.text[:30]!r}) does not state the finding", top.id, "make the title a one-line statement of what the data shows (a verb or comparison, e.g. 'X rises with Y')", 1.0, check="coverage.title")
        # units on the label of every numeric axis
        if len(x_ticks) >= 2 and x_label is not None and not UNIT_RE.search(x_label.text) and not DIMENSIONLESS.search(x_label.text):
            add("semantic_coverage", "critical", f"x-axis label {x_label.text[:24]!r} carries no unit although its ticks are numeric", x_label.id, "append the unit in parentheses, e.g. 'Time (s)'", 1.5, check="chart.axis_units")
        if len(y_ticks) >= 2:
            for yl in y_labels[:1]:
                if not UNIT_RE.search(yl.text) and not DIMENSIONLESS.search(yl.text):
                    add("semantic_coverage", "critical", f"y-axis label {yl.text[:24]!r} carries no unit although its ticks are numeric", yl.id, "append the unit in parentheses, e.g. 'Loss (nats)'", 1.5, check="chart.axis_units")
        # dual axis: two vertical axes on opposite sides of the plot each carrying numeric ticks
        if y_axis:
            right = [v for v in vert if v[0] - y_axis[0] >= 0.4 * W and len(ticks_right(*v[:3])) >= 2]
            right_labels = [t for t in y_labels if t.bbox and t.bbox.x >= y_axis[0] + 0.4 * W]
            if len(y_ticks) >= 2 and (right or right_labels):
                anchor = right[0][3].id if right else right_labels[0].id
                add("semantic_coverage", "critical", f"dual y axis ({y_axis[3].id} and {anchor}): the two scales make the series look related", anchor, "split into two panels or index both series to a common unit", 2.5, check="chart.dual_axis")
        # bars standing on the x axis / starting at the y axis
        swatches = self._swatches(shapes, texts)
        swatch_ids = {s.id for s in swatches}
        bars: List[ElementInfo] = []
        hbars: List[ElementInfo] = []
        if x_axis:
            y0, ax1, ax2, _ = x_axis
            for s in shapes:
                if s.bbox is None or s.id in swatch_ids or prog.is_background(s) or parse_color(s.fill) is None:
                    continue
                rectish = s.tag == "rect" or (s.tag in ("path", "polygon") and self._is_axis_rect(s.points))
                if rectish and abs(s.bbox.y2 - y0) <= 2 and s.bbox.h >= 2 and s.bbox.w >= 3 and ax1 - 2 <= s.bbox.x and s.bbox.x2 <= ax2 + 2 and s.bbox.w < 0.6 * (ax2 - ax1):
                    bars.append(s)
        if y_axis:
            x0, ay1, ay2, _ = y_axis
            for s in shapes:
                if s.bbox is None or s.id in swatch_ids or prog.is_background(s) or parse_color(s.fill) is None or s in bars:
                    continue
                rectish = s.tag == "rect" or (s.tag in ("path", "polygon") and self._is_axis_rect(s.points))
                if rectish and abs(s.bbox.x - x0) <= 2 and s.bbox.w >= 2 and s.bbox.h >= 3 and ay1 - 2 <= s.bbox.y and s.bbox.y2 <= ay2 + 2 and s.bbox.h < 0.6 * (ay2 - ay1):
                    hbars.append(s)
        if len(bars) >= 2 and len(y_ticks) >= 2 and x_axis:
            lowest = max(y_ticks, key=lambda t: t.centre[1])
            if abs(lowest.centre[1] - x_axis[0]) <= 10 and numeric[lowest.id] != 0:
                add("semantic_coverage", "critical", f"bars stand on an axis whose lowest tick reads {lowest.text!r}, not 0 (truncated axis exaggerates differences)", lowest.id, "start the bar axis at zero or switch to a dot plot", 2.5, check="chart.bar_axis_zero")
        if len(hbars) >= 2 and len(x_ticks) >= 2 and y_axis:
            leftmost = min(x_ticks, key=lambda t: t.centre[0])
            if abs(leftmost.centre[0] - y_axis[0]) <= 10 and numeric[leftmost.id] != 0:
                add("semantic_coverage", "critical", f"bars start at an axis whose first tick reads {leftmost.text!r}, not 0 (truncated axis exaggerates differences)", leftmost.id, "start the bar axis at zero or switch to a dot plot", 2.5, check="chart.bar_axis_zero")
        # bar heights vs the tick scale and their own value labels
        if len(bars) >= 2 and len(y_ticks) >= 2:
            lo, hi = min(y_ticks, key=lambda t: numeric[t.id]), max(y_ticks, key=lambda t: numeric[t.id])
            if numeric[hi.id] != numeric[lo.id] and hi.centre[1] != lo.centre[1]:
                slope = (numeric[hi.id] - numeric[lo.id]) / (hi.centre[1] - lo.centre[1])
                span = abs(numeric[hi.id] - numeric[lo.id])
                bad = []
                for b in bars:
                    labels = [t for t in texts if t.id in numeric and t.bbox and b.bbox.x - 2 <= t.centre[0] <= b.bbox.x2 + 2 and (b.bbox.y - 24 <= t.bbox.y2 <= b.bbox.y + 4 or b.bbox.contains_point(*t.centre))]
                    if not labels:
                        continue
                    implied = numeric[lo.id] + (b.bbox.y - lo.centre[1]) * slope
                    if abs(implied - numeric[labels[0].id]) > R.bar_scale_tolerance * span:
                        bad.append((b.id, implied, numeric[labels[0].id]))
                if bad:
                    b0 = bad[0]
                    add("semantic_coverage", "critical", f"{len(bad)} bar(s) not to scale: {b0[0]} reads {b0[1]:.0f} on the tick scale but is labelled {b0[2]:g}", b0[0], "redraw bar heights from the data", 3.0, check="chart.bar_scale")
        # one series, many hues
        if not swatches:
            series_bars = bars or hbars
            hues = {_hue_bucket(parse_color(b.fill)) for b in series_bars if parse_color(b.fill) is not None} - {-1}
            if len(series_bars) >= 3 and len(hues) > 2:
                add("visual_polish", "warning", f"single series coloured with {len(hues)} hues (rainbow categorical palette encodes nothing)", series_bars[0].id, "use one colour, or colour only the bar the title is about", 1.0, check="chart.rainbow_categorical")
        # legend swatches must match a series colour
        if swatches:
            series_colours = set()
            for s in shapes:
                if s.id in swatch_ids or prog.is_background(s) or s.tag == "text":
                    continue
                fc = parse_color(s.fill)
                if fc is not None and s.tag in ("rect", "path", "polygon", "circle", "ellipse") and not (s.tag == "rect" and s.bbox and s.bbox.w <= 16 and s.bbox.h <= 16):
                    series_colours.add(fc)
                sc = parse_color(s.stroke)
                if sc is not None and s.tag in ("polyline", "path", "line") and len(s.points) >= 2:
                    series_colours.add(sc)
            mism = [s for s in swatches if parse_color(s.fill) is not None and parse_color(s.fill) not in series_colours]
            if mism:
                add("semantic_coverage", "critical", f"legend swatch {mism[0].id} ({hex_color(parse_color(mism[0].fill))}) matches no series colour", mism[0].id, "recolour the swatch to the series it names", 2.0, check="chart.legend_swatch_colour")
        # pseudo-3D: polygons sharing an edge with a rect and carrying slanted edges
        rect_corners = set()
        for s in shapes:
            if s.tag == "rect" and s.bbox and not prog.is_background(s):
                b = s.bbox
                rect_corners.update({(b.x, b.y), (b.x2, b.y), (b.x2, b.y2), (b.x, b.y2)})
        faces = []
        for s in shapes:
            if s.tag != "polygon" or len(s.points) < 4:
                continue
            shared = sum(1 for p in s.points if p in rect_corners)
            slanted = any(a[0] != b[0] and a[1] != b[1] for a, b in _segments(s.points))
            if shared >= 2 and slanted:
                faces.append(s)
        if faces:
            add("visual_polish", "critical", f"{len(faces)} pseudo-3D face(s) ({faces[0].id}, ...) on the bars: the value edge is ambiguous", faces[0].id, "draw flat bars", 2.0, check="chart.pseudo_3d")
        # gridlines heavier or darker than the series marks
        if x_axis and y_axis:
            y0, ax1, ax2, xs = x_axis
            x0, ay1, ay2, ys = y_axis
            grid = [h[3] for h in horiz if h[0] < y0 - 1 and h[2] - h[1] >= 0.5 * (ax2 - ax1)]
            grid += [v[3] for v in vert if v[0] > x0 + 1 and v[2] - v[1] >= 0.5 * (ay2 - ay1) and not any(v[3].id == r[3].id for r in vert if len(ticks_right(*r[:3])) >= 2)]
            series = [s for s in shapes if s.tag in ("polyline", "path") and len(s.points) >= 3 and s.stroke and s.stroke.lower() != "none" and (s.fill or "none").lower() == "none"]
            if grid and series:
                gw = max(g.stroke_width or 1.0 for g in grid)
                sw = min(s.stroke_width or 1.0 for s in series)
                glum = min(luminance(parse_color(g.stroke) or (0, 0, 0)) for g in grid)
                slum = max(luminance(parse_color(s.stroke) or (0, 0, 0)) for s in series)
                if gw > sw or glum < slum:
                    add("visual_polish", "critical", f"gridlines ({grid[0].id}, ...) are heavier or darker than the series marks ({gw:g}px vs {sw:g}px)", grid[0].id, "draw gridlines thinner and lighter than every data mark (e.g. 0.5px #DDDDDD)", 1.5, check="chart.gridline_weight")

    @staticmethod
    def _is_axis_rect(points: Sequence[Point]) -> bool:
        pts = list(points)
        if len(pts) >= 2 and pts[0] == pts[-1]:
            pts = pts[:-1]
        if len(pts) != 4:
            return False
        return all(a[0] == b[0] or a[1] == b[1] for a, b in _segments(pts + [pts[0]]))

    @staticmethod
    def _pie_slices(shapes: List[ElementInfo]) -> List[ElementInfo]:
        starts: Dict[Tuple[int, int], List[ElementInfo]] = defaultdict(list)
        for s in shapes:
            if s.tag != "path" or parse_color(s.fill) is None:
                continue
            d = s.el.get("d", "")
            if not re.search(r"[Aa]", d):
                continue
            pts = path_extent_points(d, controls=False)
            if pts:
                starts[(int(round(pts[0][0])), int(round(pts[0][1])))].append(s)
        for group in starts.values():
            if len(group) >= 3:
                return group
        return []

    @staticmethod
    def _swatches(shapes: List[ElementInfo], texts: List[ElementInfo]) -> List[ElementInfo]:
        out = []
        for s in shapes:
            if s.tag == "rect" and s.bbox and s.bbox.w <= 16 and s.bbox.h <= 16 and parse_color(s.fill) is not None:
                if any(t.bbox and 0 <= t.bbox.x - s.bbox.x2 <= 12 and t.bbox.y < s.bbox.y2 and t.bbox.y2 > s.bbox.y for t in texts):
                    out.append(s)
        return out

    # ------------------------------------------------------------------
    def _tile_checks(self, prog: Program, R: Rubric, shapes: List[ElementInfo], texts: List[ElementInfo], add) -> None:
        tiles = [s for s in shapes if s.tag == "rect" and s.bbox and not prog.is_background(s) and s.bbox.w >= 80 and s.bbox.h >= 48
                 and any(t.bbox and s.bbox.contains_point(*t.centre, strict=False) for t in texts)]
        tiles = [t for t in tiles if not any(o is not t and o.bbox.contains_point(*t.centre, strict=False) and o.bbox.w * o.bbox.h > t.bbox.w * t.bbox.h and o.bbox.w >= 80 for o in tiles)] or tiles
        for tile in tiles:
            inside = [t for t in texts if t.bbox and t.text and tile.bbox.contains_point(*t.centre, strict=False)]
            values = [t for t in inside if TILE_VALUE_RE.match(t.text.strip())]
            others = [t for t in inside if t not in values]
            if values and others:
                vmax = max(t.font_size or 16 for t in values)
                omax = max(t.font_size or 16 for t in others)
                if vmax < omax:
                    v = max(values, key=lambda t: t.font_size or 16)
                    add("medium_fit", "critical", f"tile {tile.id}: the key number {v.text!r} ({vmax:g}px) is smaller than its label ({omax:g}px)", v.id, "make the number the largest text in the tile (label < number > note)", 2.0, check="tile.hierarchy")
            all_text = " ".join(t.text for t in inside)
            paired = bool(SIGNED_DELTA_RE.search(all_text) or STATUS_WORDS.search(all_text))
            coloured = []
            for t in inside:
                c = parse_color(t.fill)
                if c is not None and _hue_class(c):
                    coloured.append((t, _hue_class(c)))
            for s in shapes:
                if s.tag == "rect" and s.bbox and s is not tile and tile.bbox.contains_point(*s.centre, strict=False) and (s.bbox.h <= 8 or s.bbox.w <= 8):
                    c = parse_color(s.fill)
                    if c is not None and _hue_class(c):
                        coloured.append((s, _hue_class(c)))
            sc = parse_color(tile.stroke)
            if sc is not None and _hue_class(sc):
                coloured.append((tile, _hue_class(sc)))
            if coloured and not paired:
                e, hue = coloured[0]
                add("medium_fit", "critical", f"tile {tile.id}: {hue} on {e.id} without a signed delta, threshold or status word (status colour as decoration)", e.id, "use red/green only on a signed change or a stated threshold", 1.5, check="tile.status_colour")
            sparks = [s for s in shapes if s.tag in ("polyline", "path") and len(s.points) >= 4 and (s.fill or "none").lower() == "none" and s.bbox and tile.bbox.contains_point(*s.centre, strict=False)]
            for sp in sparks:
                ref = any(s.tag == "line" and s.bbox and tile.bbox.contains_point(*s.centre, strict=False) and s.bbox.h <= 2 and s.bbox.x < sp.bbox.x2 and s.bbox.x2 > sp.bbox.x for s in shapes)
                ends = sum(1 for t in inside if _touches(sp.points[0], t.bbox, 12) or _touches(sp.points[-1], t.bbox, 12))
                caption = any(SPAN_CAPTION_RE.search(t.text) for t in inside)
                if not (ref or ends >= 2 or caption):
                    add("medium_fit", "warning", f"sparkline {sp.id} has no baseline, end values or span caption", sp.id, "add a dashed reference line or label the span and end values", 1.0, check="tile.sparkline_reference")
        rows: Dict[int, List[ElementInfo]] = defaultdict(list)
        for t in tiles:
            key = next((k for k in rows if abs(k - t.bbox.y) <= 4), t.bbox.y)
            rows[key].append(t)
        for row in rows.values():
            if len(row) < 2:
                continue
            row.sort(key=lambda t: t.bbox.x)
            widths = [t.bbox.w for t in row]
            gutters = [row[i + 1].bbox.x - row[i].bbox.x2 for i in range(len(row) - 1)]
            styles = {((t.fill or "").lower(), (t.stroke or "").lower(), round(t.stroke_width or 0, 1)) for t in row}
            if max(widths) - min(widths) > R.tile_width_tolerance or (len(gutters) > 1 and max(gutters) - min(gutters) > R.tile_gutter_tolerance) or len(styles) > 1:
                add("visual_polish", "warning", f"tiles in one row differ in width ({', '.join(str(w) for w in widths)}) or gutter ({', '.join(str(g) for g in gutters)}) or style", row[0].id, "give tiles in a row the same width, gutter, fill and border", 1.0, check="tile.grid_uniform")

    # ------------------------------------------------------------------
    def _motion_checks(self, prog: Program, R: Rubric, css: str, flows: List[ElementInfo], blocks: List[ElementInfo], add) -> None:
        parsed = parse_css(css)
        keyframes: Dict[str, List[Tuple[str, Dict[str, str]]]] = parsed["keyframes"]  # type: ignore[assignment]
        rules: List[Tuple[str, Dict[str, str]]] = parsed["rules"]  # type: ignore[assignment]
        reduced = parsed["reduced"]
        by_id: Dict[str, Dict[str, str]] = {}
        anims: Dict[str, List[AnimEntry]] = {}
        for sel, props in rules:
            for part in sel.split(","):
                part = part.strip()
                if part.startswith("#") and re.fullmatch(r"#[\w.:-]+", part):
                    eid = part[1:]
                    by_id.setdefault(eid, {}).update(props)
                    if "animation" in props:
                        anims.setdefault(eid, []).extend(parse_animation(props["animation"]))
                    elif "animation-name" in props:
                        anims.setdefault(eid, []).append(AnimEntry(props["animation-name"], _parse_time(props.get("animation-duration", "0s")) or 0.0, _parse_time(props.get("animation-delay", "0s")) or 0.0, props.get("animation-iteration-count", "1"), props.get("animation-direction", "normal")))
        if not anims:
            return

        def frame_values(name: str, prop: str) -> List[Tuple[float, float]]:
            out = []
            for sel, props in keyframes.get(name, []):
                if prop not in props:
                    continue
                for key in sel.split(","):
                    key = key.strip()
                    pct = 0.0 if key == "from" else 100.0 if key == "to" else float(key.rstrip("%") or 0)
                    out.append((pct, float(re.sub(r"[^\d.\-]", "", props[prop]) or 0)))
            return sorted(out)

        def animated_props(name: str) -> set:
            return {p for _, props in keyframes.get(name, []) for p in props}

        if reduced is None:
            add("medium_fit", "critical", "no @media (prefers-reduced-motion: reduce) block: reduced-motion users never see the final state", "svg",
                "add a reduced-motion block that disables animation and shows the final state", 2.0, check="motion.reduced_motion")
        else:
            kills = any("none" in (props.get("animation", "") + props.get("animation-name", "")) for _, props in reduced)
            hides = any("display" in props and props["display"] == "none" and "pulse" in sel for sel, props in reduced) or not any(e.role == "pulse" for e in prog.elements)
            if not (kills and hides):
                add("medium_fit", "critical", "the reduced-motion block does not stop the animation and hide the tokens", "svg", "set animation: none and display: none on tokens under prefers-reduced-motion", 2.0, check="motion.reduced_motion")
        flow_paths = {f.id: f.points for f in flows if f.points}
        rev_paths = {f.id: list(reversed(f.points)) for f in flows if f.points}
        tokens = []  # (id, flow or None, entry, points)
        decorative = []
        for eid, props in by_id.items():
            el = prog.by_id(eid)
            if el is None:
                continue
            entries = anims.get(eid, [])
            op = props.get("offset-path", "")
            m = re.search(r"path\(\s*['\"]([^'\"]+)['\"]\s*\)", op)
            if m:
                pts = [(int(round(x)), int(round(y))) for x, y in path_extent_points(m.group(1), controls=False)]
                match = next((fid for fid, fp in flow_paths.items() if fp == pts), None)
                reverse = next((fid for fid, fp in rev_paths.items() if fp == pts), None)
                travel = next((e for e in entries if "offset-distance" in animated_props(e.name)), None)
                if travel is not None:
                    vals = frame_values(travel.name, "offset-distance")
                    backwards = len(vals) >= 2 and vals[-1][1] < vals[0][1]
                    if backwards or travel.direction in ("reverse", "alternate-reverse") or (reverse and not match):
                        add("flow_readability", "critical", f"token {eid} travels from the arrowhead back to the tail", eid, "animate offset-distance from 0% to 100% along the flow's own path", 2.0, check="motion.pulse_direction")
                    if travel.direction == "alternate":
                        add("flow_readability", "critical", f"token {eid} alternates direction along its path", eid, "use animation-direction: normal", 2.0, check="motion.pulse_direction")
                if not match and not reverse:
                    decorative.append(f"{eid} rides a path that is no flow")
                tokens.append((eid, match or reverse, travel, pts))
            if el.role != "pulse":
                for e in entries:
                    if e.iterations == "infinite" or e.direction in ("alternate", "alternate-reverse"):
                        decorative.append(f"{eid} animates forever ({e.name})")
                    extra = animated_props(e.name) - {"opacity", "stroke-dashoffset", "offset-distance", "offset-rotate"}
                    if extra:
                        decorative.append(f"{eid} animates {', '.join(sorted(extra))}")
        if decorative:
            add("visual_polish", "warning", f"decorative motion: {'; '.join(decorative[:3])}", "svg", "animate only reveals, draw-ons and tokens along data/control flows", 1.0 * len(decorative), check="motion.decorative")
        # control tokens: slower (longer period) and dimmer than data tokens
        data_tokens, control_tokens = [], []
        for eid, fid, travel, pts in tokens:
            if fid is None or travel is None:
                continue
            f = prog.by_id(fid)
            tok = prog.by_id(eid)
            fill = parse_color(tok.fill if tok else None) or (0, 0, 0)
            (control_tokens if f is not None and not self._is_data_flow(f) else data_tokens).append((eid, travel.duration, luminance(fill)))
        if data_tokens and control_tokens:
            dmax = max(d for _, d, _ in data_tokens)
            dlum = max(l for _, _, l in data_tokens)
            for eid, dur, lum in control_tokens:
                if dur < dmax or lum <= dlum:
                    add("flow_readability", "warning", f"control token {eid} is faster or as dark as the data tokens ({dur:g}s vs {dmax:g}s)", eid, "give control tokens a longer period and a lighter fill", 1.0, check="motion.control_tempo")
                    break
        # reveal order: a target must not appear before its source
        delays: Dict[str, float] = {}
        for eid, entries in anims.items():
            for e in entries:
                vals = frame_values(e.name, "opacity")
                if vals and vals[-1][1] >= 1 and (vals[0][1] < 1 or len(vals) == 1):
                    delays[eid] = e.delay
        if delays:
            def reveal_delay(b: ElementInfo) -> Optional[float]:
                cur: Optional[ElementInfo] = b
                while cur is not None:
                    if cur.id in delays:
                        return delays[cur.id]
                    cur = prog.by_id(cur.parent_id) if cur.parent_id else None
                return None

            for f in flows:
                if len(f.points) < 2 or not self._is_data_flow(f):
                    continue
                src = self._block_at(f.points[0], blocks)
                dst = self._block_at(f.points[-1], blocks)
                if src is None or dst is None:
                    continue
                ds, dd = reveal_delay(src), reveal_delay(dst)
                if ds is not None and dd is not None and dd + 1e-6 < ds:
                    add("flow_readability", "warning", f"{dst.id} is revealed at {dd:g}s before its source {src.id} at {ds:g}s", dst.id, "order reveal delays along the flow (source before target)", 1.0, check="motion.reveal_order")
                    break

    # ------------------------------------------------------------------
    @staticmethod
    def _host_block(t: ElementInfo, blocks: List[ElementInfo]) -> Optional[ElementInfo]:
        if t.bbox is None:
            return None
        cx, cy = t.centre
        hosts = [b for b in blocks if b.bbox and b.bbox.contains_point(cx, cy, strict=False) and b.role != "container"]
        if not hosts:
            return None
        return min(hosts, key=lambda b: b.bbox.w * b.bbox.h)

    @staticmethod
    def _host_fill(prog: Program, t: ElementInfo) -> Optional[str]:
        if t.bbox is None:
            return None
        cx, cy = t.centre
        hosts = [b for b in prog.shapes() if b.tag in ("rect", "circle", "ellipse", "polygon", "path") and b.bbox and b.bbox.contains_point(cx, cy, strict=False) and b.fill and b.fill.lower() != "none" and b.id != t.id]
        if not hosts:
            return None
        return min(hosts, key=lambda b: b.bbox.w * b.bbox.h).fill

    def _background_for(self, prog: Program, t: ElementInfo) -> Optional[Tuple[int, int, int]]:
        if t.bbox is None:
            return (255, 255, 255)
        cx, cy = t.centre
        hosts = [b for b in prog.shapes() if b.tag in ("rect", "circle", "ellipse", "polygon", "path") and b.bbox and b.bbox.contains_point(cx, cy, strict=False) and parse_color(b.fill) is not None and b.id != t.id]
        if not hosts:
            return (255, 255, 255)
        host = min(hosts, key=lambda b: b.bbox.w * b.bbox.h)
        return parse_color(host.fill)

    def _finish(self, issues: List[Issue], metrics: Dict[str, float], unassessed: Optional[List[str]] = None) -> QualityReport:
        """Scores follow the paper's anchors: a dimension with any critical defect is at most 5
        ("average / mediocre"), each further defect subtracts its penalty, floor 1.  Dimensions
        without evidence (no source text / plan) are reported as None and excluded."""
        from figtree.rubric_spec import classify

        for i in issues:
            if i.check_id is None:
                i.check_id = classify(i.visual_description)
        unassessed = unassessed or []
        scores: Dict[str, Optional[float]] = {d: 10.0 for d in DIMENSIONS}
        for d in DIMENSIONS:
            dim_issues = [i for i in issues if i.dimension == d]
            if any(i.severity == "critical" for i in dim_issues):
                scores[d] = 5.0
                for i in dim_issues:
                    scores[d] = max(1.0, scores[d] - (i.penalty if i.severity == "warning" else max(0.0, i.penalty - 2.0)))
            else:
                for i in dim_issues:
                    scores[d] = max(1.0, scores[d] - i.penalty)
        for d in unassessed:
            if not any(i.dimension == d for i in issues):
                scores[d] = None
        weights = self.rubric.weights
        for d in DIMENSIONS:  # a dimension the medium does not use is not assessed
            if weights.get(d, 1.0) == 0 and not any(i.dimension == d for i in issues):
                scores[d] = None
        # veto-class defects also count against medium fit (a chart with a gradient is not a chart
        # for publication, whatever its other dimensions say)
        from figtree.rubric_spec import VETOES

        fired = {i.check_id for i in issues if i.check_id}
        vetoed = [name for name, v in VETOES.items() if any(c in fired for c in v["checks"])]
        if vetoed and scores["medium_fit"] is not None:
            scores["medium_fit"] = max(1.0, min(scores["medium_fit"], 7.0) - 1.0 * (len(vetoed) - 1))
            metrics["vetoes"] = len(vetoed)
            self._vetoed = vetoed
        assessed = [d for d in DIMENSIONS if scores[d] is not None and weights.get(d, 1.0) > 0]
        overall = sum(scores[d] * weights.get(d, 1.0) for d in assessed) / sum(weights.get(d, 1.0) for d in assessed)
        tags = sorted({i.dimension for i in issues if i.severity == "critical"}) + [f"veto:{v}" for v in getattr(self, "_vetoed", [])]
        self._vetoed = []
        return QualityReport(self.rubric.name, {k: (round(v, 2) if v is not None else None) for k, v in scores.items()}, round(overall, 2), issues, tags, metrics)


# ---------------------------------------------------------------------------
# icon family rules (shared with IconSmith)
# ---------------------------------------------------------------------------

def _stroke_segments(prog: Program, shapes: List[ElementInfo]) -> List[Tuple[str, Point, Point]]:
    """Straight stroke segments of an icon (paths, lines, polylines, rect edges), tagged by element id."""
    segs: List[Tuple[str, Point, Point]] = []
    for s in shapes:
        if s.tag == "text" or not s.stroke or s.stroke.lower() == "none":
            continue
        if s.tag == "path":
            for sub in re.split(r"(?=[Mm])", s.el.get("d", "")):
                if not sub.strip():
                    continue
                pts = path_extent_points(sub, controls=False)
                # relative subpaths after a split lose their start point; use the full path in that case
                if sub[0] == "m" and sub is not None:
                    pts = path_extent_points(s.el.get("d", ""), controls=False)
                    segs.extend((s.id, a, b) for a, b in _segments(pts) if a != b)
                    break
                segs.extend((s.id, a, b) for a, b in _segments(pts) if a != b)
        elif s.tag in ("line", "polyline", "polygon"):
            segs.extend((s.id, a, b) for a, b in _segments(s.points) if a != b)
        elif s.tag == "rect" and s.bbox and s.corners is None:
            b = s.bbox
            segs.extend((s.id, a, c) for a, c in _segments([(b.x, b.y), (b.x2, b.y), (b.x2, b.y2), (b.x, b.y2), (b.x, b.y)]))
    if any(s.matrix != (1.0, 0.0, 0.0, 1.0, 0.0, 0.0) and s.tag == "path" for s in shapes):
        from figtree.program import mat_apply

        fixed = []
        for sid, a, b in segs:
            s = prog.by_id(sid)
            if s is not None and s.tag == "path":
                a, b = mat_apply(s.matrix, *a), mat_apply(s.matrix, *b)
            fixed.append((sid, a, b))
        segs = fixed
    return segs


def icon_family_issues(prog: Program, R: Rubric) -> List[Issue]:
    """Family rules beyond the generic icon rubric: safe margin, coverage, stroke count, fills, feature size, gaps, crossings, ink balance."""
    issues: List[Issue] = []
    W, H = prog.width, prog.height
    if W <= 0 or H <= 0:
        return issues
    scale = W / 24.0
    dev = R.must_read_at / float(W)  # device px per user unit at the must-read size
    shapes = [s for s in prog.shapes() if s.tag != "text"]
    if not shapes:
        return issues
    ext = prog.content_extent()
    if ext is not None:
        x1, y1, x2, y2 = ext
        safe = R.icon_safe_margin * scale
        if x1 < safe - 1 or y1 < safe - 1 or x2 > W - safe + 1 or y2 > H - safe + 1:
            issues.append(Issue("compactness", "warning", f"strokes enter the {R.icon_safe_margin:g}px safe margin", "svg", f"keep all strokes inside {R.icon_safe_margin:g}..{24 - R.icon_safe_margin:g} of the 24 grid", 1.0, check_id="icon.safe_margin"))
        w, h = x2 - x1, y2 - y1
        coverage = (w * h) / float(W * H)
        if coverage < R.min_coverage and max(w, h) < 0.7 * W:  # a flat metaphor (minus, toggle, trend) is judged by its long side
            issues.append(Issue("compactness", "warning", f"icon covers {coverage:.0%} of the grid; it will vanish at {R.must_read_at}px", "svg", "enlarge the metaphor to fill ~70% of the grid", 1.5, check_id="icon.coverage"))
    strokes = 0
    for s in shapes:
        strokes += path_subpaths(s.el.get("d", "")) if s.tag == "path" else 1
    if strokes > R.max_strokes:
        issues.append(Issue("medium_fit", "warning", f"{strokes} strokes (subpaths); family limit is {R.max_strokes}", "svg", "merge or drop strokes", 1.0, check_id="icon.subpath_count"))
    solid = [s for s in shapes if (s.fill or "none").lower() not in ("none", "transparent") and s.bbox and max(s.bbox.w, s.bbox.h) > 3 * scale]
    if solid:
        issues.append(Issue("visual_polish", "warning", f"solid fill on {solid[0].id} in an outline family", solid[0].id, "use fill=none (dots up to 3px may stay filled)", 0.8, check_id="icon.solid_fill"))
    # minimum feature size: every stroke extent must survive at the must-read size
    tiny = []
    for s in shapes:
        if s.tag == "path":
            subs = [sub for sub in re.split(r"(?=[M])", s.el.get("d", "")) if sub.strip()] if "m" not in s.el.get("d", "") else [s.el.get("d", "")]
            for sub in subs:
                pts = path_extent_points(sub, controls=False)
                if not pts:
                    continue
                extent = max(max(p[0] for p in pts) - min(p[0] for p in pts), max(p[1] for p in pts) - min(p[1] for p in pts))
                if 0.05 * scale < extent < R.min_feature_px / dev:
                    tiny.append(s.id)
        elif s.tag in ("line", "polyline", "circle", "ellipse", "rect") and s.bbox:
            extent = max(s.bbox.w, s.bbox.h)
            if 0.05 * scale < extent < R.min_feature_px / dev:
                tiny.append(s.id)
    if tiny:
        issues.append(Issue("medium_fit", "warning", f"{len(tiny)} stroke(s) shorter than {R.min_feature_px:g} device px at {R.must_read_at}px ({', '.join(tiny[:3])}): sub-pixel detail smudges", tiny[0], "drop the detail or enlarge it to at least 2 grid units", 1.0, check_id="icon.min_feature_size"))
    segs = _stroke_segments(prog, shapes)
    # minimum gap between parallel strokes
    sw = max([(s.stroke_width or 1.0) for s in shapes if s.stroke and s.stroke.lower() != "none"] or [2.0])
    merged = []
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            (ia, a1, a2), (ib, b1, b2) = segs[i], segs[j]
            if a1[1] == a2[1] and b1[1] == b2[1]:  # both horizontal
                overlap = min(max(a1[0], a2[0]), max(b1[0], b2[0])) - max(min(a1[0], a2[0]), min(b1[0], b2[0]))
                gap = abs(a1[1] - b1[1]) - sw
            elif a1[0] == a2[0] and b1[0] == b2[0]:  # both vertical
                overlap = min(max(a1[1], a2[1]), max(b1[1], b2[1])) - max(min(a1[1], a2[1]), min(b1[1], b2[1]))
                gap = abs(a1[0] - b1[0]) - sw
            else:
                continue
            if overlap > 0.5 * scale and 0 < abs(gap + sw) and gap * dev < R.min_gap_px and (ia != ib or abs(gap + sw) > 0):
                if abs(gap + sw) < 1e-6:
                    continue  # the same line twice
                merged.append((ia, ib, gap))
    if merged:
        ia, ib, gap = merged[0]
        issues.append(Issue("medium_fit", "warning", f"parallel strokes {ia} and {ib} are {max(gap, 0):.1f}px apart ({gap * dev:.1f} device px at {R.must_read_at}px): they fuse", ia, f"space parallel strokes at least {R.min_gap_px / dev:.1f} grid units apart (centre to centre minus the stroke width)", 1.0, check_id="icon.min_gap"))
    # crossing density: more than two strokes through one 2px cell
    cells: Dict[Tuple[int, int], set] = defaultdict(set)
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            (ia, a1, a2), (ib, b1, b2) = segs[i], segs[j]
            if ia == ib:
                continue
            p = segment_intersection(a1, a2, b1, b2)
            if p is not None:
                key = (int(p[0] // (2 * scale)), int(p[1] // (2 * scale)))
                cells[key].update({ia, ib})
    dense = [(k, v) for k, v in cells.items() if len(v) > 2]
    if dense:
        k, v = max(dense, key=lambda kv: len(kv[1]))
        issues.append(Issue("medium_fit", "warning", f"{len(v)} strokes cross in one 2px cell near ({k[0] * 2 * scale:g},{k[1] * 2 * scale:g}): a blob at {R.must_read_at}px", sorted(v)[0], "spread the crossings or drop a stroke", 1.0, check_id="icon.crossing_density"))
    # ink distribution: the ink centroid should sit near the centre of the content box
    if ext is not None:
        total = 0.0
        sx = sy = 0.0
        for sid, a, b in segs:
            L = _seg_len(a, b)
            total += L
            sx += L * (a[0] + b[0]) / 2.0
            sy += L * (a[1] + b[1]) / 2.0
        for s in prog.shapes():
            if s.tag in ("circle", "ellipse") and s.bbox:
                L = math.pi * (s.bbox.w + s.bbox.h) / 2.0
            elif s.tag == "text" and s.bbox:
                L = float(s.bbox.w)  # a (forbidden) label still carries ink
            else:
                continue
            total += L
            sx += L * s.centre[0]
            sy += L * s.centre[1]
        if total > 0:
            cx, cy = sx / total, sy / total
            mx, my = (ext[0] + ext[2]) / 2.0, (ext[1] + ext[3]) / 2.0
            off = math.hypot(cx - mx, cy - my)
            if off > R.max_ink_offset * scale:
                issues.append(Issue("visual_polish", "warning", f"ink centroid sits {off / scale:.1f} grid units off the centre of the icon's box: the meaning is crowded into one corner", "svg", "balance the metaphor across the grid or drop the empty frame lines", 1.0, check_id="icon.ink_distribution"))
    return issues
