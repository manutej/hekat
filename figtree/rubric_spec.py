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
    Check("content.none", "semantic_coverage", "critical", "nothing drawn", "shape count", False, pattern=r"no drawable content"),
]

# Veto rules (after PaperBananaBench): disqualifying whatever else is good.  A veto maps to the
# checks that detect it; a veto with no measurable check is a judge question only.
VETOES: Dict[str, Dict[str, object]] = {
    "textual_overload": {"description": "full sentences or more than 15 words in a box; literal copying of the source", "checks": ["text.words_per_label"]},
    "occlusion": {"description": "overlapping elements or labels", "checks": ["text.overlap", "flow.through_block"]},
    "chaotic_routing": {"description": "crossings and detours that defeat reading order", "checks": ["flow.crossings", "compactness.detour", "flow.reading_order"]},
    "illegible_type": {"description": "fonts below the medium's minimum or low contrast", "checks": ["text.min_font", "text.contrast"]},
    "black_background": {"description": "dark page background", "checks": ["medium.black_background"]},
    "neon_or_gradient": {"description": "jarring colour, gradients, filters", "checks": ["polish.neon", "polish.gradient_fill", "polish.filter"]},
    "hallucination": {"description": "elements with no basis in the source", "checks": ["hallucination.label_source"]},
    "embedded_title_or_watermark": {"description": "figure title or watermark inside the drawing (paper figures)", "checks": []},
    "clip_art": {"description": "decorative, cartoonish or photorealistic elements", "checks": ["polish.corner_radius"]},
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
