"""Machine-readable rubric specifications.

A rubric spec is the contract between the meta-prompt and the evaluators: for each medium it
lists the eight dimensions with their 1-10 anchors, the *checks* (what is measured, by which
signal, with which severity, whether a mechanical fix exists), the *veto rules* (defects that
disqualify a figure whatever else it does well, after PaperBananaBench), and the *judge
questions* an image-space evaluator answers.  ``classify`` maps a critic issue to its check id,
so probes (``figtree.probes``) can measure every check's recall and precision.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from figtree.rubrics import DIMENSIONS, RUBRICS, Rubric

ANCHORS: Dict[str, Dict[str, str]] = {
    "semantic_coverage": {"1-2": "wrong topic or generic; almost no source-specific content", "3-4": "domain recognisable, most key components missing", "5-6": "main idea present, important mechanisms omitted or distorted", "7-8": "most concepts and relationships present, minor omissions", "9-10": "complete, source-specific coverage of stages and relationships"},
    "hallucination_control": {"1-2": "mostly fabricated", "3-4": "major unsupported components alter the method", "5-6": "core idea recognisable, several invented details", "7-8": "minor embellishments or one wrong label", "9-10": "every important element is source-grounded"},
    "topology_accuracy": {"1-2": "no coherent topology", "3-4": "severe structural mismatch", "5-6": "recognisable organisation with grouping errors", "7-8": "mostly correct, minor grouping or proportion issues", "9-10": "precise, publication-grade topology"},
    "flow_readability": {"1-2": "flow unreadable; arrows missing, chaotic or misleading", "3-4": "major confusion from wrong arrows, crossings, overlaps, order", "5-6": "flow inferable but routing or spacing slows reading", "7-8": "clear flow with minor arrow or spacing imperfections", "9-10": "very clear, economical flow, no ambiguity"},
    "text_quality": {"1-2": "illegible, garbled or mostly missing text", "3-4": "severe text errors or glyph deformation", "5-6": "readable with noticeable spelling, placement or blur defects", "7-8": "mostly correct and clean, minor local defects", "9-10": "accurate, sharp, well placed, typographically consistent"},
    "visual_polish": {"1-2": "visually broken or unprofessional", "3-4": "messy composition, harsh or inconsistent styling", "5-6": "acceptable but visibly rough or unbalanced", "7-8": "polished with minor imperfections", "9-10": "highly polished and balanced"},
    "medium_fit": {"1-2": "unsuitable for the medium", "3-4": "amateurish or wrong register for the medium", "5-6": "borderline; substantial cleanup needed", "7-8": "suitable with minor editing", "9-10": "fully aligned with the medium's conventions"},
    "compactness": {"1-2": "content occupies a small fraction of the canvas", "3-4": "large blank margins or gaps; stretched connectors", "5-6": "usable but uneven density or oversized spacing", "7-8": "compact, mostly even, minor wasted space", "9-10": "economical, evenly distributed, no wasted area"},
}


@dataclass
class Check:
    id: str
    dimension: str
    severity: str  # critical | warning
    description: str
    signal: str  # what is measured
    mechanical: bool  # has an auto edit
    media: List[str] = field(default_factory=lambda: ["*"])
    pattern: str = ""  # regex over visual_description that identifies this check

    def to_dict(self) -> Dict[str, object]:
        return {"id": self.id, "dimension": self.dimension, "severity": self.severity, "description": self.description, "signal": self.signal, "mechanical": self.mechanical, "media": list(self.media)}


DIAGRAM_MEDIA = ["paper", "teaching material", "presentation", "course narrative"]

CHECKS: List[Check] = [
    Check("compactness.blank_margin", "compactness", "warning", "a blank band wider than the medium's margin on any side", "content bbox vs canvas", True, pattern=r"margin is \d+px of blank canvas"),
    Check("compactness.overflow", "compactness", "critical", "content outside the canvas", "content bbox vs canvas", True, pattern=r"overflows the (left|top|right|bottom) edge"),
    Check("compactness.aspect", "compactness", "warning", "canvas aspect outside the medium's range (banner or tower)", "width/height", False, pattern=r"canvas aspect .* outside"),
    Check("compactness.detour", "compactness", "warning", "a connector far longer than its displacement", "path length / Manhattan distance", False, pattern=r"long detour"),
    Check("flow.crossings", "flow_readability", "warning", "arrow crossings", "orthogonal segment intersections", False, pattern=r"arrow crossing"),
    Check("flow.diagonal", "flow_readability", "warning", "diagonal routing without a semantic flag", "segment orientation", False, pattern=r"diagonal routing"),
    Check("flow.through_block", "flow_readability", "critical", "an arrow passing through a block", "segment vs block interiors", False, pattern=r"passes through a block"),
    Check("flow.short_shaft", "flow_readability", "warning", "a marker-ended arrow with a shaft under 20px", "final segment length", False, pattern=r"shaft shorter than 20px"),
    Check("flow.reading_order", "flow_readability", "warning", "most arrows run against reading order", "share of right/down arrows", False, pattern=r"right-to-left or bottom-to-top"),
    Check("flow.no_connectors", "flow_readability", "warning", "several blocks and no connectors", "block and flow counts", False, ["paper", "teaching material", "presentation"], pattern=r"blocks but no connectors"),
    Check("text.min_font", "text_quality", "warning", "font below the medium's minimum", "resolved font-size", True, pattern=r"font size .* below the .* minimum"),
    Check("text.words_per_label", "text_quality", "warning", "a label longer than the medium allows", "word count", False, pattern=r"has \d+ words \(limit"),
    Check("text.contrast", "text_quality", "critical", "text/background contrast below the threshold", "WCAG ratio vs host fill", True, pattern=r"contrast [\d.]+:1 below"),
    Check("text.gradient_host", "text_quality", "warning", "text over a gradient or pattern fill", "host fill is url()", False, pattern=r"sits on a gradient/pattern fill"),
    Check("text.overflow", "text_quality", "critical", "a label wider than its block", "estimated text width vs host block", False, pattern=r"overflows its block"),
    Check("text.overlap", "text_quality", "critical", "two labels overlapping", "text bbox intersection", False, pattern=r"labels .* overlap"),
    Check("polish.font_families", "visual_polish", "warning", "more font families than allowed", "distinct font-family values", True, pattern=r"font families in one figure|uses .*; the figure's family is"),
    Check("polish.palette_size", "visual_polish", "warning", "more accent colours than allowed", "distinct saturated fills", False, pattern=r"accent colours \(limit"),
    Check("polish.neon", "visual_polish", "warning", "a neon fill or stroke", "saturation > 0.9 and max channel > 240", True, pattern=r"uses a neon"),
    Check("polish.gradient_fill", "visual_polish", "warning", "a gradient or pattern fill", "fill url()", True, pattern=r"uses a gradient or pattern fill"),
    Check("polish.filter", "visual_polish", "warning", "a filter effect", "filter attribute", True, pattern=r"uses a filter effect"),
    Check("polish.corner_radius", "visual_polish", "warning", "oversized corner radius", "rx", True, pattern=r"corner radius"),
    Check("polish.stroke_widths", "visual_polish", "warning", "more stroke widths than allowed", "distinct stroke-width values", False, pattern=r"different stroke widths|stroke width .* differs from"),
    Check("medium.black_background", "medium_fit", "critical", "black background", "full-canvas rect fill", True, pattern=r"black background"),
    Check("medium.icon_text", "medium_fit", "critical", "text inside an icon", "text elements", False, ["icon"], pattern=r"text element\(s\) in an icon"),
    Check("medium.icon_elements", "medium_fit", "warning", "too many elements for an icon", "shape count", False, ["icon"], pattern=r"elements; an icon should have"),
    Check("medium.square", "medium_fit", "critical", "non-square icon canvas", "aspect", True, ["icon"], pattern=r"is not square"),
    Check("coverage.axis_labels", "semantic_coverage", "critical", "missing axis labels with units", "axis-like or rotated text", False, ["chart"], pattern=r"axis label\(s\) with units are missing"),
    Check("coverage.title", "semantic_coverage", "warning", "the most prominent text does not state the finding", "largest text word count", False, ["chart"], pattern=r"does not state the finding"),
    Check("coverage.plan_terms", "semantic_coverage", "warning", "planned components not labelled", "plan terms vs labels", False, pattern=r"planned component\(s\) not labelled"),
    Check("hallucination.label_source", "hallucination_control", "warning", "a label with no basis in the source", "label words vs source text", False, pattern=r"has no basis in the source"),
    Check("topology.ungrouped", "topology_accuracy", "warning", "many blocks without grouping", "block count vs containers", False, ["paper", "teaching material", "presentation"], pattern=r"blocks without any grouping"),
    Check("topology.empty_container", "topology_accuracy", "warning", "an empty container", "container children", True, pattern=r"empty container"),
    Check("narrative.canvas_height", "medium_fit", "warning", "canvas shorter than course narrative minimum", "viewBox height vs rubric", False, ["course narrative"], pattern=r"canvas height .* below course-narrative minimum"),
    Check("narrative.annot_density", "semantic_coverage", "warning", "too few annotation lines for a course figure", "data-kind=annot count", False, ["course narrative"], pattern=r"only \d+ annotation line"),
    Check("narrative.panel_support", "semantic_coverage", "warning", "large panels without supporting annotation text", "panel blocks vs annot", False, ["course narrative"], pattern=r"large panels but fewer than 2 annotation"),
    Check("narrative.section_title", "medium_fit", "warning", "multi-panel layout without a section title", "title text or font-weight", False, ["course narrative"], pattern=r"no section title"),
    Check("narrative.example_panels", "visual_polish", "warning", "multi-column layout without example panels or annotations", "nested white rects vs annot", False, ["course narrative"], pattern=r"without nested example panels"),
    Check("content.none", "semantic_coverage", "critical", "nothing drawn", "shape count", False, pattern=r"no drawable content"),
    Check("medium.no_canvas", "medium_fit", "critical", "no canvas size", "width/height/viewBox", False, pattern=r"canvas has no width"),
    # --- folded in from the adversary reports (diagram) ---
    Check("flow.collinear_overlap", "flow_readability", "critical", "two arrows sharing a collinear shaft (two heads, ambiguous endpoints)", "collinear segment overlap > 8px", False, pattern=r"share a collinear shaft"),
    Check("flow.through_text", "flow_readability", "critical", "an arrow striking through a label", "segment vs text bbox interior", False, pattern=r"strikes through label"),
    Check("flow.semantic_direction", "flow_readability", "critical", "a sink that only emits or a source that only receives data (judge request)", "role lexicon vs arrow endpoints", False, DIAGRAM_MEDIA, pattern=r"reads as a (sink|source) but only"),
    Check("text.sentence_label", "text_quality", "critical", "a label that is a sentence (trailing full stop or sentence opener)", "label text", False, pattern=r"is a sentence, not a label"),
    Check("text.duplicate_labels", "text_quality", "warning", "two blocks with the same label", "case-folded hosted labels", False, DIAGRAM_MEDIA, pattern=r"carry the same label"),
    Check("text.outlined_glyphs", "text_quality", "critical", "a block label drawn as path glyphs, not addressable text", "small stroked paths inside a block with no text", False, DIAGRAM_MEDIA, pattern=r"drawn as \d+ path glyphs"),
    Check("medium.embedded_title", "medium_fit", "critical", "a figure caption or title inside the drawing", "text matching 'Figure N' / 'Table N'", False, DIAGRAM_MEDIA, pattern=r"embeds a figure title"),
    Check("polish.invisible_elements", "visual_polish", "warning", "elements that draw nothing but stretch the content box", "opacity 0, display none, no fill and no stroke, background-coloured", True, pattern=r"invisible element\(s\)"),
    Check("polish.decoration", "visual_polish", "critical", "overlapping ellipses with no label or connector (clip art)", "unlabelled round shapes that intersect", False, DIAGRAM_MEDIA, pattern=r"decorative cluster"),
    Check("topology.container_label_mismatch", "topology_accuracy", "critical", "a container whose title names a block outside it (judge request)", "container title stem vs child/outside labels", False, DIAGRAM_MEDIA, pattern=r"but the matching block .* sits outside"),
    Check("layout.legend_in_drawing", "topology_accuracy", "warning", "a legend inside the block grid", "legend bbox inside the union of blocks", False, DIAGRAM_MEDIA, pattern=r"legend .* sits inside the block grid"),
    # --- charts ---
    Check("chart.axis_units", "semantic_coverage", "critical", "the label of a numeric axis without a unit", "parenthesised unit / % / currency on the axis label", False, ["chart"], pattern=r"axis label .* carries no unit"),
    Check("chart.bar_axis_zero", "semantic_coverage", "critical", "bars on an axis that does not start at zero", "lowest numeric tick at the bar baseline", False, ["chart"], pattern=r"lowest tick reads|first tick reads"),
    Check("chart.bar_scale", "semantic_coverage", "critical", "bar heights that contradict the tick scale or their value labels", "linear fit of tick labels vs bar tops", False, ["chart"], pattern=r"not to scale"),
    Check("chart.dual_axis", "semantic_coverage", "critical", "two y axes on opposite sides of the plot", "two vertical axis lines with ticks, or two rotated labels", False, ["chart"], pattern=r"dual y axis"),
    Check("chart.pie", "semantic_coverage", "critical", "a pie chart", "three or more filled arc paths sharing one start point", False, ["chart"], pattern=r"pie chart of"),
    Check("chart.rainbow_categorical", "visual_polish", "warning", "one series coloured with many hues", "distinct hues on bars with no legend", False, ["chart"], pattern=r"rainbow categorical"),
    Check("chart.legend_swatch_colour", "semantic_coverage", "critical", "a legend swatch that matches no series colour", "swatch fill vs series fills/strokes", False, ["chart"], pattern=r"legend swatch .* matches no series"),
    Check("chart.pseudo_3d", "visual_polish", "critical", "pseudo-3D faces on bars", "polygon sharing an edge with a rect and carrying slanted edges", False, ["chart"], pattern=r"pseudo-3D face"),
    Check("chart.gridline_weight", "visual_polish", "critical", "gridlines heavier or darker than the series marks", "gridline stroke width / luminance vs series", False, ["chart"], pattern=r"gridlines .* heavier or darker"),
    # --- dashboard tiles ---
    Check("tile.hierarchy", "medium_fit", "critical", "the key number is not the largest text in its tile", "font sizes of numeric vs other texts per tile", False, ["dashboard tile"], pattern=r"key number .* is smaller than its label"),
    Check("tile.status_colour", "medium_fit", "critical", "red/green without a signed delta, threshold or status word", "hue class of value text / stripe / border vs tile text", False, ["dashboard tile"], pattern=r"status colour as decoration"),
    Check("tile.sparkline_reference", "medium_fit", "warning", "a sparkline without baseline, end values or span caption", "line / end labels / caption inside the tile", False, ["dashboard tile"], pattern=r"sparkline .* has no baseline"),
    Check("tile.grid_uniform", "visual_polish", "warning", "tiles in one row with different widths, gutters or styles", "tile rects grouped by row", False, ["dashboard tile"], pattern=r"tiles in one row differ"),
    # --- icon family (shared with IconSmith) ---
    Check("icon.safe_margin", "compactness", "warning", "strokes inside the safe margin", "content extent vs 2-unit margin", False, ["icon"], pattern=r"safe margin"),
    Check("icon.coverage", "compactness", "warning", "the icon covers too little of the grid", "content box area (flat metaphors by their long side)", False, ["icon"], pattern=r"icon covers .* of the grid"),
    Check("icon.subpath_count", "medium_fit", "warning", "more strokes (subpaths) than the family allows", "M commands across paths plus other shapes", False, ["icon"], pattern=r"strokes \(subpaths\)"),
    Check("icon.solid_fill", "visual_polish", "warning", "a solid fill in an outline family", "resolved fill not none on a shape larger than a dot", False, ["icon"], pattern=r"solid fill on"),
    Check("icon.invisible_shape", "visual_polish", "critical", "an invisible shape that stretches the content box", "no fill and no stroke, opacity 0, hidden", True, ["icon"], pattern=r"invisible element\(s\)"),
    Check("icon.min_feature_size", "medium_fit", "warning", "a stroke that is sub-pixel at the must-read size", "stroke extent x (must_read_at / grid)", False, ["icon"], pattern=r"shorter than .* device px"),
    Check("icon.min_gap", "medium_fit", "warning", "parallel strokes that fuse at the must-read size", "centre distance minus stroke width in device px", False, ["icon"], pattern=r"parallel strokes .* fuse"),
    Check("icon.crossing_density", "medium_fit", "warning", "more than two strokes through one 2px cell", "pairwise segment intersections bucketed", False, ["icon"], pattern=r"strokes cross in one 2px cell"),
    Check("icon.ink_distribution", "visual_polish", "warning", "ink crowded into one corner of the content box", "length-weighted ink centroid vs content box centre", False, ["icon"], pattern=r"ink centroid"),
    # --- motion (any medium with CSS animation) ---
    Check("motion.pulse_direction", "flow_readability", "critical", "a token travelling from arrowhead to tail", "offset-distance keyframes, animation-direction, path vs reversed flow", False, pattern=r"travels from the arrowhead|alternates direction"),
    Check("motion.reveal_order", "flow_readability", "warning", "a target revealed before its source", "reveal delays along data flows", False, pattern=r"is revealed at .* before its source"),
    Check("motion.control_tempo", "flow_readability", "warning", "a control token faster or as dark as data tokens", "travel duration and fill luminance per token", False, pattern=r"control token .* is faster or as dark"),
    Check("motion.reduced_motion", "medium_fit", "critical", "no (or an incomplete) prefers-reduced-motion block", "@media (prefers-reduced-motion: reduce) rules", False, pattern=r"reduced-motion"),
    Check("motion.decorative", "visual_polish", "warning", "motion that encodes nothing", "paths that are no flow, infinite/alternate on non-tokens, animated properties beyond opacity/dashoffset", False, pattern=r"decorative motion"),
]

# Veto rules (after PaperBananaBench): disqualifying whatever else is good.  A veto maps to the
# checks that detect it; a veto with no measurable check is a judge question only.
VETOES: Dict[str, Dict[str, object]] = {
    "textual_overload": {"description": "full sentences or more than 15 words in a box; literal copying of the source", "checks": ["text.words_per_label", "text.sentence_label"]},
    "occlusion": {"description": "overlapping elements or labels", "checks": ["text.overlap", "flow.through_block", "flow.through_text", "flow.collinear_overlap"]},
    "chaotic_routing": {"description": "crossings and detours that defeat reading order", "checks": ["flow.crossings", "compactness.detour", "flow.reading_order"]},
    "illegible_type": {"description": "fonts below the medium's minimum or low contrast", "checks": ["text.min_font", "text.contrast", "text.outlined_glyphs"]},
    "black_background": {"description": "dark page background", "checks": ["medium.black_background"]},
    "neon_or_gradient": {"description": "jarring colour, gradients, filters", "checks": ["polish.neon", "polish.gradient_fill", "polish.filter"]},
    "hallucination": {"description": "elements with no basis in the source", "checks": ["hallucination.label_source"]},
    "embedded_title_or_watermark": {"description": "figure title or watermark inside the drawing (paper figures)", "checks": ["medium.embedded_title"]},
    "clip_art": {"description": "decorative, cartoonish or photorealistic elements", "checks": ["polish.corner_radius", "polish.decoration"]},
    "misleading_data": {"description": "a chart that misstates the data: truncated bar axis, bars not to scale, dual axis, legend that names the wrong series", "checks": ["chart.bar_axis_zero", "chart.bar_scale", "chart.dual_axis", "chart.legend_swatch_colour"]},
    "motion_misleads": {"description": "animation that runs against the flow or is lost to reduced-motion users", "checks": ["motion.pulse_direction", "motion.reduced_motion"]},
}

JUDGE_QUESTIONS: Dict[str, str] = {
    "semantic_coverage": "Does the figure show the components and stages the source names, and the relationships between them?",
    "hallucination_control": "Is every visible element justified by the source? Flag invented modules, labels, branches or decoration.",
    "topology_accuracy": "Do grouping, hierarchy and containment match the structure of the method?",
    "flow_readability": "Can a cold reader follow the flow: arrow direction, endpoints, crossings, reading order, spacing?",
    "text_quality": "Are labels correct, legible at the intended size, well placed, consistent in font, not overflowing?",
    "visual_polish": "Is the palette restrained, strokes consistent, whitespace balanced, contrast adequate, no artifacts?",
    "medium_fit": "Does the figure follow the conventions of its medium (paper, teaching, slide, chart, tile, icon)?",
    "compactness": "Is the canvas used economically: margins, spacing, connector length, density balance?",
}


def spec_for(rubric: Rubric | str) -> Dict[str, object]:
    r = RUBRICS[rubric] if isinstance(rubric, str) else rubric
    checks = [c for c in CHECKS if "*" in c.media or r.medium in c.media]
    return {
        "name": r.name,
        "medium": r.medium,
        "description": r.description,
        "thresholds": r.to_dict()["thresholds"],
        "dimensions": {d: {"question": DIMENSIONS[d], "anchors": ANCHORS[d], "judge": JUDGE_QUESTIONS[d], "weight": r.weights.get(d, 1.0)} for d in DIMENSIONS},
        "checks": [c.to_dict() for c in checks],
        "vetoes": VETOES,
        "scoring": "10 per dimension; a critical defect caps the dimension at 5; each further defect subtracts its penalty; floor 1; dimensions without evidence are not assessed; overall = weighted mean of assessed dimensions",
    }


def classify(description: str) -> Optional[str]:
    for c in CHECKS:
        if c.pattern and re.search(c.pattern, description):
            return c.id
    return None


def all_specs() -> Dict[str, Dict[str, object]]:
    return {name: spec_for(name) for name in RUBRICS}


def write_specs(directory: str) -> List[str]:
    import os

    os.makedirs(directory, exist_ok=True)
    out = []
    for name, spec in all_specs().items():
        path = os.path.join(directory, f"{name}.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(spec, fh, indent=2)
        out.append(path)
    return out
