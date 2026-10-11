"""Quality critic: rubric-scored, element-anchored review of any addressable SVG program.

Every signal is measurable from the program (and, when available, the rendered image), so a
score is reproducible and every issue carries a ``code_anchor``, a ``fix_instruction`` and,
when the fix is mechanical, an ``auto_edit`` that the refinement loop applies.  Scores use
the paper's 1-10 scale per dimension; the overall score is the weighted mean.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from figtree.edits import EditOp
from figtree.geometry import is_orthogonal, path_hits_boxes
from figtree.program import (
    ElementInfo,
    Program,
    contrast_ratio,
    hex_color,
    load_program,
    parse_color,
    saturation,
)
from figtree.rubrics import DIMENSIONS, Rubric, get_rubric
from figtree.schemas import BBox

GREYS = {"#FFFFFF", "#000000", "#333333", "#666666", "#999999", "#CCCCCC", "#D5D5D5", "#F5F5F5", "#EEEEEE", "#DDDDDD"}
AXIS_WORDS = re.compile(r"\b(?:axis|%|\(.*\)|per|rate|count|score|accuracy|time|year|month|day|loss|error|\$|€|£)\b", re.IGNORECASE)


@dataclass
class Issue:
    dimension: str
    severity: str  # critical | warning
    visual_description: str
    code_anchor: str
    fix_instruction: str
    penalty: float
    auto_edit: Optional[EditOp] = None

    def to_dict(self) -> Dict[str, object]:
        return {
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


def _segments(pts: Sequence[Tuple[int, int]]):
    return [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]


def _cross(a, b) -> bool:
    """Proper crossing of an H and a V segment (shared endpoints excluded)."""
    (ax1, ay1), (ax2, ay2) = a
    (bx1, by1), (bx2, by2) = b
    if ay1 == ay2 and bx1 == bx2:
        return min(ax1, ax2) < bx1 < max(ax1, ax2) and min(by1, by2) < ay1 < max(by1, by2)
    if ax1 == ax2 and by1 == by2:
        return min(bx1, bx2) < ax1 < max(bx1, bx2) and min(ay1, ay2) < by1 < max(ay1, ay2)
    return False


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
        flows = prog.flows()
        blocks = [e for e in shapes if (e.tag in ("rect", "circle", "ellipse", "polygon") or e.el.get("data-role") == "block") and e.bbox and not (e.tag == "rect" and e.bbox.w >= W and e.bbox.h >= H)]

        def add(dim: str, sev: str, desc: str, anchor: str, fix: str, penalty: float, edit: Optional[EditOp] = None) -> None:
            issues.append(Issue(dim, sev, desc, anchor, fix, penalty, edit))

        if W <= 0 or H <= 0:
            add("medium_fit", "critical", "canvas has no width/height or viewBox", "svg", "declare width, height and viewBox", 6)
            return self._finish(issues, metrics)

        # ---------------- compactness ----------------
        cb = prog.content_bbox()
        if cb is None:
            add("semantic_coverage", "critical", "no drawable content", "svg", "draw the content", 8)
            return self._finish(issues, metrics)
        margins = {"left": cb.x, "top": cb.y, "right": W - cb.x2, "bottom": H - cb.y2}
        metrics["fill_ratio"] = round((cb.w * cb.h) / float(W * H), 3)
        centred = abs(margins["left"] - margins["right"]) <= 8 and abs(margins["top"] - margins["bottom"]) <= 8
        for side, m in margins.items():
            limit = max(R.margin + 8, R.max_margin_ratio * (W if side in ("left", "right") else H))
            if m > limit:
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
                add("compactness", "warning", f"{side} margin is {m}px of blank canvas", "svg", fix, 1.0, edit)
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
                add("compactness", "critical", f"content overflows the {side} edge by {-m}px", "svg", fix, 3.0, edit)
        aspect = W / float(H)
        metrics["aspect"] = round(aspect, 2)
        if not (R.aspect[0] <= aspect <= R.aspect[1]):
            if R.require_square:
                side_px = max(W, H)
                add("medium_fit", "critical", f"canvas aspect {aspect:.2f} is not square", "svg", "use a square viewBox", 3,
                    {"op": "set_canvas", "width": side_px, "height": side_px})
            else:
                add("compactness", "warning", f"canvas aspect {aspect:.2f} outside the {R.medium} range {R.aspect[0]}-{R.aspect[1]} (banner or tower shape)", "svg",
                    "re-flow the layout into rows so the figure is closer to the medium's aspect", 1.5)
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
                                "move the connected blocks closer or route a shorter loop", 0.8)
            if ratios:
                metrics["mean_detour"] = round(sum(ratios) / len(ratios), 2)

        # ---------------- flow readability ----------------
        if flows:
            block_boxes = [b.bbox for b in blocks if b.bbox]
            crossings = 0
            segs = [(f, s) for f in flows for s in _segments(f.points)]
            for i in range(len(segs)):
                for j in range(i + 1, len(segs)):
                    if segs[i][0].id != segs[j][0].id and _cross(segs[i][1], segs[j][1]):
                        crossings += 1
            metrics["crossings"] = crossings
            if crossings:
                add("flow_readability", "warning" if crossings < 3 else "critical", f"{crossings} arrow crossing(s)", flows[0].id, "re-order or re-route to remove crossings", 0.7 * crossings)
            for f in flows:
                if not f.points:
                    continue
                if not is_orthogonal(f.points) and f.el.get("data-diagonal") != "semantic":
                    add("flow_readability", "warning", f"{f.id} uses diagonal routing", f.id, "re-route with horizontal and vertical segments", 0.5)
                ends = {f.points[0], f.points[-1]}
                obstacles = [bx for bx in block_boxes if not any(bx.contains_point(x, y, strict=False) for x, y in ends)]
                if path_hits_boxes(f.points, obstacles):
                    add("flow_readability", "critical", f"{f.id} passes through a block", f.id, "re-route around the block", 1.5)
                if f.el.get("marker-end") and len(f.points) >= 2:
                    (x1, y1), (x2, y2) = f.points[-2], f.points[-1]
                    if abs(x2 - x1) + abs(y2 - y1) < 20:
                        add("flow_readability", "warning", f"{f.id} arrow shaft shorter than 20px", f.id, "lengthen the final segment to at least 20px", 0.5)
            # reading order: fraction of arrows pointing right or down
            forward = sum(1 for f in flows if len(f.points) >= 2 and (f.points[-1][0] > f.points[0][0] or f.points[-1][1] > f.points[0][1]))
            metrics["forward_ratio"] = round(forward / len(flows), 2)
            if forward / len(flows) < 0.6:
                add("flow_readability", "warning", "most arrows run right-to-left or bottom-to-top", flows[0].id, "re-order blocks so the main flow reads left-to-right / top-to-bottom", 1.0)
        elif len(blocks) > 2 and R.medium not in ("icon", "chart", "dashboard tile"):
            add("flow_readability", "warning", f"{len(blocks)} blocks but no connectors", "svg", "add arrows or spatial grouping that shows the relation between blocks", 1.0)

        # ---------------- text quality ----------------
        families = Counter()
        if not R.allow_text and texts:
            add("medium_fit", "critical", f"{len(texts)} text element(s) in an icon", texts[0].id, "remove text; icons must read without words", 3)
        for t in texts:
            if not t.text:
                continue
            fs = t.font_size if t.font_size is not None else 16.0
            if R.min_font and fs < R.min_font:
                add("text_quality", "critical" if fs < R.min_font * 0.7 else "warning", f"{t.id} font size {fs:g}px below the {R.medium} minimum {R.min_font:g}px", t.id,
                    f"raise font size to at least {R.min_font:g}px", 1.0, {"op": "set_attr", "id": t.id, "attr": "font-size", "value": f"{R.min_font:g}"})
            fam = (t.font_family or "").split(",")[0].strip().strip("'\"")
            if fam:
                families[fam] += 1
            words = len(t.text.split())
            if R.max_words_per_label and words > R.max_words_per_label:
                add("text_quality", "warning", f"{t.id} has {words} words (limit {R.max_words_per_label})", t.id, "shorten to a keyword label", 0.8)
            # contrast against the shape behind the text
            col = parse_color(t.fill) or (0, 0, 0)
            bg = self._background_for(prog, t, blocks)
            host_fill = self._host_fill(prog, t)
            if host_fill and host_fill.lower().startswith("url("):
                add("text_quality", "warning", f"{t.id} sits on a gradient/pattern fill; contrast cannot be guaranteed", t.id, "give the host a flat fill", 1.0)
            elif bg is not None:
                cr = contrast_ratio(col, bg)
                if cr < R.min_contrast:
                    fix_col = "#333333" if contrast_ratio((0x33, 0x33, 0x33), bg) >= contrast_ratio((255, 255, 255), bg) else "#FFFFFF"
                    add("text_quality", "critical" if cr < 3 else "warning", f"{t.id} contrast {cr:.1f}:1 below {R.min_contrast}:1", t.id,
                        f"use {fix_col} text on {hex_color(bg)}", 1.2, {"op": "recolor", "id": t.id, "fill": fix_col})
            # overflow of the enclosing block
            host = self._host_block(t, blocks)
            if host is not None and t.bbox is not None and (t.bbox.x < host.bbox.x - 2 or t.bbox.x2 > host.bbox.x2 + 2):
                add("text_quality", "critical", f"{t.id} overflows its block {host.id}", t.id, "widen the block or shorten the label", 1.5)
        # overlapping text
        tb = [t for t in texts if t.bbox and t.text]
        for i in range(len(tb)):
            for j in range(i + 1, len(tb)):
                if tb[i].bbox.intersects(tb[j].bbox):
                    add("text_quality", "critical", f"labels {tb[i].id} and {tb[j].id} overlap", tb[i].id, "move one label or shorten both", 1.5)
        if R.max_font_families and len(families) > R.max_font_families:
            main_family = families.most_common(1)[0][0]
            for t in texts:
                fam = (t.font_family or "").split(",")[0].strip().strip("'\"")
                if fam and fam != main_family and t.el.get("font-family"):
                    add("visual_polish", "warning", f"{t.id} uses {fam}; the figure's family is {main_family}", t.id, f"set font-family to {main_family}", 0.5,
                        {"op": "set_attr", "id": t.id, "attr": "font-family", "value": main_family})
            add("visual_polish", "warning", f"{len(families)} font families in one figure: {', '.join(families)}", texts[0].id, f"use one font family ({main_family})", 0.5)

        # ---------------- visual polish / medium fit ----------------
        palette = Counter()
        strokes = Counter()
        neon = []
        for s in shapes:
            if s.tag == "text":
                continue
            c = parse_color(s.fill)
            if c is not None and hex_color(c) not in GREYS and saturation(c) > 0.05:
                palette[hex_color(c)] += 1
                if saturation(c) > 0.9 and max(c) > 240:
                    neon.append((s, "fill"))
            sc = parse_color(s.stroke) if s.tag in ("path", "line", "polyline") else None
            if sc is not None and hex_color(sc) not in GREYS and saturation(sc) > 0.9 and max(sc) > 240:
                neon.append((s, "stroke"))
            if s.stroke and s.stroke.lower() != "none" and s.stroke_width is not None and s.tag != "text":
                strokes[round(s.stroke_width, 1)] += 1
            fill = (s.fill or "").lower()
            if fill.startswith("url("):
                add("visual_polish", "warning", f"{s.id} uses a gradient or pattern fill", s.id, "replace with a flat fill", 1.0, {"op": "recolor", "id": s.id, "fill": "#7BA3C9"})
            if s.el.get("filter") or "filter:" in (s.el.get("style") or ""):
                add("visual_polish", "warning", f"{s.id} uses a filter effect", s.id, "remove shadows and filters", 1.0, {"op": "set_attr", "id": s.id, "attr": "filter", "value": "none"})
            if s.tag == "rect" and s.el.get("rx") and float(s.el.get("rx")) > R.max_corner_radius:
                add("visual_polish", "warning", f"{s.id} corner radius {s.el.get('rx')} looks clip-art like", s.id, f"use rx <= {R.max_corner_radius}", 0.5, {"op": "set_attr", "id": s.id, "attr": "rx", "value": str(R.max_corner_radius)})
        metrics["palette_size"] = len(palette)
        if len(palette) > R.max_palette:
            add("visual_polish", "warning", f"{len(palette)} accent colours (limit {R.max_palette}): {', '.join(palette)}", "svg", "reduce to a small semantic palette", 1.0 * (len(palette) - R.max_palette))
        for s, which in neon:
            colour = s.fill if which == "fill" else s.stroke
            add("visual_polish", "warning", f"{s.id} uses a neon {which} colour {colour}", s.id, "use a muted tone from the palette", 0.8, {"op": "recolor", "id": s.id, which: "#7BA3C9"})
        if len(strokes) > R.max_stroke_widths:
            if R.max_stroke_widths == 1:
                common = strokes.most_common(1)[0][0]
                for s2 in shapes:
                    if s2.stroke and s2.stroke.lower() != "none" and s2.stroke_width is not None and round(s2.stroke_width, 1) != common and s2.tag != "text":
                        add("visual_polish", "warning", f"{s2.id} stroke width {s2.stroke_width:g} differs from the icon's {common:g}", s2.id, f"set stroke-width to {common:g}", 0.5,
                            {"op": "set_attr", "id": s2.id, "attr": "stroke-width", "value": f"{common:g}"})
            else:
                add("visual_polish", "warning", f"{len(strokes)} different stroke widths: {sorted(strokes)}", "svg", "use one stroke width for lines and one for borders", 1.0)
        bg = prog.element("background")
        for s in shapes:
            if s.tag == "rect" and s.bbox and s.bbox.w >= W and s.bbox.h >= H:
                c = parse_color(s.fill)
                if c is not None and max(c) < 60:
                    add("medium_fit", "critical", "black background", s.id, "use a white background", 3, {"op": "recolor", "id": s.id, "fill": "#FFFFFF"})
        if R.max_elements is not None and len(shapes) > R.max_elements:
            add("medium_fit", "warning", f"{len(shapes)} elements; an icon should have at most {R.max_elements}", "svg", "simplify the icon", 1.0 * (len(shapes) - R.max_elements) / 2)
        if R.require_axis_labels:
            axis_like = [t for t in texts if t.text and (AXIS_WORDS.search(t.text) or t.el.get("data-role") in ("axis-label", "x-label", "y-label"))]
            rotated = [t for t in texts if "rotate" in (t.el.get("transform") or "")]
            if len(axis_like) + len(rotated) < 2:
                add("semantic_coverage", "critical", "axis label(s) with units are missing", "svg", "add x and y axis labels with units (insert <text data-role=\"axis-label\">)", 2.5)
            titled = [t for t in texts if t.text and t.bbox and t.font_size]
            if titled:
                top = max(titled, key=lambda t: (t.font_size, -t.bbox.y))
                if len(top.text.split()) < 3:
                    add("semantic_coverage", "warning", f"the most prominent text ({top.text[:30]!r}) does not state the finding", top.id, "make the title a one-line statement of what the data shows", 1.0)

        # ---------------- topology ----------------
        groups = [e for e in prog.elements if e.tag == "g" and e.el.get("data-bbox")]
        if len(blocks) > 6 and not groups and R.medium in ("paper", "teaching material", "presentation"):
            add("topology_accuracy", "warning", f"{len(blocks)} blocks without any grouping", "svg", "group related blocks into labelled containers", 1.0)
        for g in groups:
            kids = [e for e in prog.elements if e.parent_id == g.id and e.tag in ("rect", "g", "text")]
            if not any(k.tag in ("rect", "g") for k in kids):
                add("topology_accuracy", "warning", f"empty container {g.id}", g.id, "remove the empty container", 0.5, {"op": "delete", "id": g.id})

        # ---------------- semantic coverage / hallucination ----------------
        if plan_terms:
            labels = " ".join(t.text.lower() for t in texts)
            covered = [p for p in plan_terms if p.lower() in labels]
            metrics["coverage"] = round(len(covered) / len(plan_terms), 2)
            missing = [p for p in plan_terms if p.lower() not in labels]
            if missing:
                add("semantic_coverage", "warning" if len(missing) < len(plan_terms) / 2 else "critical", f"{len(missing)} planned component(s) not labelled: {', '.join(missing[:5])}", "svg",
                    "add the missing components or justify their omission", 1.0 * len(missing))
        if source_text:
            src = source_text.lower()
            for t in texts:
                words = [w for w in re.findall(r"[A-Za-z][A-Za-z-]{3,}", t.text)]
                if words and not any(w.lower() in src for w in words):
                    add("hallucination_control", "warning", f"label {t.id} ({t.text[:30]!r}) has no basis in the source", t.id, "remove or rename to a term from the source", 1.0)

        unassessed = []
        if not plan_terms and not R.require_axis_labels:
            unassessed.append("semantic_coverage")
        if not source_text:
            unassessed.append("hallucination_control")
        return self._finish(issues, metrics, unassessed)

    # ------------------------------------------------------------------
    @staticmethod
    def _host_block(t: ElementInfo, blocks: List[ElementInfo]) -> Optional[ElementInfo]:
        if t.bbox is None:
            return None
        cx, cy = t.bbox.x + t.bbox.w // 2, t.bbox.y + t.bbox.h // 2
        hosts = [b for b in blocks if b.bbox and b.bbox.contains_point(cx, cy, strict=False) and b.el.get("data-role") != "container"]
        if not hosts:
            return None
        return min(hosts, key=lambda b: b.bbox.w * b.bbox.h)

    @staticmethod
    def _host_fill(prog: Program, t: ElementInfo) -> Optional[str]:
        if t.bbox is None:
            return None
        cx, cy = t.bbox.x + t.bbox.w // 2, t.bbox.y + t.bbox.h // 2
        hosts = [b for b in prog.shapes() if b.tag in ("rect", "circle", "ellipse", "polygon", "path") and b.bbox and b.bbox.contains_point(cx, cy, strict=False) and b.fill and b.fill.lower() != "none" and b.id != t.id]
        if not hosts:
            return None
        return min(hosts, key=lambda b: b.bbox.w * b.bbox.h).fill

    def _background_for(self, prog: Program, t: ElementInfo, blocks: List[ElementInfo]) -> Optional[Tuple[int, int, int]]:
        if t.bbox is None:
            return (255, 255, 255)
        cx, cy = t.bbox.x + t.bbox.w // 2, t.bbox.y + t.bbox.h // 2
        hosts = [b for b in prog.shapes() if b.tag in ("rect", "circle", "ellipse", "polygon") and b.bbox and b.bbox.contains_point(cx, cy, strict=False) and parse_color(b.fill) is not None]
        if not hosts:
            return (255, 255, 255)
        host = min(hosts, key=lambda b: b.bbox.w * b.bbox.h)
        return parse_color(host.fill)

    def _finish(self, issues: List[Issue], metrics: Dict[str, float], unassessed: Optional[List[str]] = None) -> QualityReport:
        """Scores follow the paper's anchors: a dimension with any critical defect is at most 5
        ("average / mediocre"), each further defect subtracts its penalty, floor 1.  Dimensions
        without evidence (no source text / plan) are reported as None and excluded."""
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
        assessed = [d for d in DIMENSIONS if scores[d] is not None]
        overall = sum(scores[d] * weights.get(d, 1.0) for d in assessed) / sum(weights.get(d, 1.0) for d in assessed)
        tags = sorted({i.dimension for i in issues if i.severity == "critical"})
        return QualityReport(self.rubric.name, {k: (round(v, 2) if v is not None else None) for k, v in scores.items()}, round(overall, 2), issues, tags, metrics)
