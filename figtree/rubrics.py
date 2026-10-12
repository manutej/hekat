"""Rubric profiles for the iterative refinement loop.

The ``methodology`` profile carries the paper's eight fine-grained diagnostic dimensions
(semantic coverage, hallucination control, topology accuracy, flow readability, text & glyph
quality, visual polish, academic style, compactness) with their 1-10 anchors.  The other
profiles reuse the same dimensions with medium-specific thresholds for teaching diagrams,
slides, data figures, dashboard tiles and icons.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

DIMENSIONS: Dict[str, str] = {
    "semantic_coverage": "Does the figure cover the concepts that matter in the source?",
    "hallucination_control": "Are all visible elements justified by the source?",
    "topology_accuracy": "Does grouping, hierarchy and containment reflect the intended structure?",
    "flow_readability": "Can a reader follow the flow: arrow direction, endpoints, crossings, reading order?",
    "text_quality": "Label correctness, font consistency, legibility, placement, overflow.",
    "visual_polish": "Restrained palette, consistent strokes, balanced whitespace, contrast, no artifacts.",
    "medium_fit": "Does the figure follow the conventions of its medium (paper, slide, dashboard, icon)?",
    "compactness": "Economical use of the canvas: margins, spacing, connector length, density balance.",
}

ANCHORS: Dict[str, str] = {
    "1-2": "completely broken",
    "3-4": "severe problems",
    "5-6": "average / mediocre",
    "7-8": "good with minor defects",
    "9-10": "near-perfect",
}


@dataclass
class Rubric:
    name: str
    medium: str
    description: str
    min_font: float  # px, user units
    min_contrast: float  # WCAG ratio for text over its background
    max_palette: int  # distinct fill colours (excluding white/black/greys)
    max_words_per_label: int
    aspect: Tuple[float, float]  # (min, max) width/height
    margin: int  # expected outer margin in px
    max_margin_ratio: float  # largest acceptable blank band as a fraction of the canvas side
    max_stroke_widths: int
    max_font_families: int
    max_elements: Optional[int] = None  # icons
    allow_text: bool = True
    require_axis_labels: bool = False
    require_square: bool = False
    max_corner_radius: int = 8
    fixed_canvas: bool = False  # slides, tiles and icons keep their canvas; content is centred instead
    max_centred_margin_ratio: float = 0.34  # fixed canvas: a centred figure may leave symmetric bands up to this fraction
    flow_halo: float = 4.0  # px of clear space an arrow must keep from any block it does not connect
    title_min_words: int = 5  # charts: a title shorter than this must carry a verb or comparison
    bar_scale_tolerance: float = 0.05  # charts: bar height vs value label, as a fraction of the tick range
    tile_width_tolerance: int = 4  # dashboard: tiles in one row share a width within this many px
    tile_gutter_tolerance: int = 2  # dashboard: gutters in one row agree within this many px
    must_read_at: int = 16  # icons: the device size at which every feature must survive
    max_strokes: int = 12  # icons: strokes (subpaths) per icon
    icon_safe_margin: float = 2.0  # icons: grid units kept clear on every side
    min_coverage: float = 0.4  # icons: share of the grid the content box must cover (flat metaphors judged by their long side)
    min_feature_px: float = 1.5  # icons: smallest stroke extent in device px at must_read_at
    min_gap_px: float = 1.0  # icons: smallest clear gap between parallel strokes in device px at must_read_at
    max_ink_offset: float = 3.0  # icons: grid units the ink centroid may sit off the centre of the content box
    weights: Dict[str, float] = field(default_factory=lambda: {k: 1.0 for k in DIMENSIONS})
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "medium": self.medium,
            "description": self.description,
            "thresholds": {
                "min_font": self.min_font,
                "min_contrast": self.min_contrast,
                "max_palette": self.max_palette,
                "max_words_per_label": self.max_words_per_label,
                "aspect": list(self.aspect),
                "margin": self.margin,
                "max_elements": self.max_elements,
                "allow_text": self.allow_text,
                "require_axis_labels": self.require_axis_labels,
                "require_square": self.require_square,
                "fixed_canvas": self.fixed_canvas,
                "max_centred_margin_ratio": self.max_centred_margin_ratio,
                "flow_halo": self.flow_halo,
                "title_min_words": self.title_min_words,
                "bar_scale_tolerance": self.bar_scale_tolerance,
                "tile_width_tolerance": self.tile_width_tolerance,
                "tile_gutter_tolerance": self.tile_gutter_tolerance,
                "must_read_at": self.must_read_at,
                "max_strokes": self.max_strokes,
                "icon_safe_margin": self.icon_safe_margin,
                "min_coverage": self.min_coverage,
                "min_feature_px": self.min_feature_px,
                "min_gap_px": self.min_gap_px,
                "max_ink_offset": self.max_ink_offset,
            },
            "dimensions": dict(DIMENSIONS),
            "anchors": dict(ANCHORS),
            "weights": dict(self.weights),
        }


RUBRICS: Dict[str, Rubric] = {
    "methodology": Rubric(
        name="methodology",
        medium="paper",
        description="Academic methodology figure (NeurIPS/ICLR conventions, the paper's eight diagnostic dimensions).",
        min_font=9, min_contrast=4.5, max_palette=6, max_words_per_label=15, aspect=(1.2, 4.0), margin=24,
        max_margin_ratio=0.12, max_stroke_widths=3, max_font_families=1,
        notes=["flat fills, 1.0-1.5px strokes, Times New Roman, dashed lines only for feedback"],
    ),
    "teaching": Rubric(
        name="teaching",
        medium="teaching material",
        description="Teaching diagram: one idea per figure, large labels, strong reading order, few colours.",
        min_font=14, min_contrast=4.5, max_palette=5, max_words_per_label=8, aspect=(1.0, 2.4), margin=24,
        max_margin_ratio=0.12, max_stroke_widths=2, max_font_families=1,
        notes=["prefer left-to-right or top-to-bottom reading order", "at most ~12 labelled elements"],
    ),
    "slide": Rubric(
        name="slide",
        medium="presentation",
        description="Presentation figure: 16:9 canvas, fonts readable from the back of the room, very few colours.",
        min_font=18, min_contrast=4.5, max_palette=4, max_words_per_label=6, aspect=(1.6, 1.9), margin=32,
        max_margin_ratio=0.15, max_stroke_widths=2, max_font_families=1, fixed_canvas=True,
    ),
    "data-figure": Rubric(
        name="data-figure",
        medium="chart",
        description="Data figure: labelled axes with units, zero-based bars to scale, one y axis, no pie, no 3D or gradients, legend swatches that match the series, a title that states the finding.",
        min_font=10, min_contrast=4.5, max_palette=6, max_words_per_label=8, aspect=(1.0, 2.2), margin=16,
        max_margin_ratio=0.15, max_stroke_widths=3, max_font_families=1, require_axis_labels=True,
        weights={**{k: 1.0 for k in DIMENSIONS}, "topology_accuracy": 0.5, "flow_readability": 0.5},
        notes=["direct labelling beats a legend", "title states the finding"],
    ),
    "dashboard": Rubric(
        name="dashboard",
        medium="dashboard tile",
        description="Dashboard tile: one title, one key number (the largest text) or trend with a reference, uniform tiles, red/green only on a signed change, no decoration.",
        min_font=12, min_contrast=4.5, max_palette=4, max_words_per_label=6, aspect=(0.8, 2.0), margin=16,
        max_margin_ratio=0.2, max_stroke_widths=2, max_font_families=1, fixed_canvas=True,
        weights={**{k: 1.0 for k in DIMENSIONS}, "topology_accuracy": 0.5, "flow_readability": 0.5},
    ),
    "icon": Rubric(
        name="icon",
        medium="icon",
        description="Icon: square viewBox, a dozen strokes at most, one stroke width, no text, no fills, recognisable at 16px.",
        min_font=0, min_contrast=3.0, max_palette=2, max_words_per_label=0, aspect=(1.0, 1.0), margin=2,
        max_margin_ratio=0.25, max_stroke_widths=1, max_font_families=0, max_elements=12, allow_text=False,
        require_square=True, max_corner_radius=4, fixed_canvas=True,
        weights={**{k: 1.0 for k in DIMENSIONS}, "semantic_coverage": 0.0, "hallucination_control": 0.0, "topology_accuracy": 0.0, "flow_readability": 0.0},
    ),
}


def get_rubric(name: str) -> Rubric:
    try:
        return RUBRICS[name]
    except KeyError:
        raise KeyError(f"unknown rubric {name!r}; choose from {sorted(RUBRICS)}") from None
