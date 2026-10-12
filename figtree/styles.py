"""Design presets: named GlobalStyle records for different media.

``paper`` is the specification's academic register (Times, flat fills, dashed containers,
tiny arrowheads).  ``teaching`` is an editorial register for teaching material and slides:
a sans face, softer tinted fills with a dark ink border, solid light containers, larger
labels and arrowheads, more air between blocks.  A preset is a complete style record, so the
critic's typography, palette and stroke checks follow it automatically.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from figtree.schemas import GlobalStyle


@dataclass
class Preset:
    style: GlobalStyle
    container_fill: str
    container_stroke: str
    container_dash: str  # "" for solid
    container_rx: int
    block_rx: int
    marker_w: int
    marker_h: float
    gap_h: int
    gap_v: int
    row_gap: int
    icon_color: str
    label_color: str
    title_color: str


PRESETS: Dict[str, Preset] = {
    "paper": Preset(
        style=GlobalStyle(),
        container_fill="#F5F5F5", container_stroke="#333333", container_dash="4 2", container_rx=4, block_rx=4,
        marker_w=5, marker_h=3.5, gap_h=24, gap_v=16, row_gap=48, icon_color="#333333", label_color="#333333", title_color="#333333",
    ),
    "teaching": Preset(
        style=GlobalStyle(
            palette={"attention": "#F3C9A4", "processing": "#C9DCF0", "residual": "#F6EFD2", "input": "#E6E8EC", "container": "#F8F9FB", "border": "#2B3A4A"},
            font="IBM Plex Sans, Helvetica Neue, Arial, sans-serif",
            font_size_label="14-16pt", font_size_annot="11-13pt",
            stroke_main=1.4, stroke_border=1.0, grid=8, min_arrow=24, padding=32, preset="teaching",
        ),
        container_fill="#F8F9FB", container_stroke="#D5DBE4", container_dash="", container_rx=10, block_rx=6,
        marker_w=8, marker_h=6, gap_h=40, gap_v=24, row_gap=64, icon_color="#2B3A4A", label_color="#1C2630", title_color="#5B6B7C",
    ),
    "slide": Preset(
        style=GlobalStyle(
            palette={"attention": "#F3C9A4", "processing": "#C9DCF0", "residual": "#F6EFD2", "input": "#E6E8EC", "container": "#F8F9FB", "border": "#2B3A4A"},
            font="IBM Plex Sans, Helvetica Neue, Arial, sans-serif",
            font_size_label="18-20pt", font_size_annot="13-15pt",
            stroke_main=1.6, stroke_border=1.2, grid=8, min_arrow=28, padding=40, preset="slide",
        ),
        container_fill="#F8F9FB", container_stroke="#D5DBE4", container_dash="", container_rx=12, block_rx=8,
        marker_w=10, marker_h=7, gap_h=56, gap_v=32, row_gap=80, icon_color="#2B3A4A", label_color="#1C2630", title_color="#5B6B7C",
    ),
    "course-narrative": Preset(
        style=GlobalStyle(
            palette={"attention": "#F3C9A4", "processing": "#C9DCF0", "residual": "#F6EFD2", "input": "#E6E8EC", "container": "#F8F9FB", "border": "#2B3A4A"},
            font="IBM Plex Sans, Helvetica Neue, Arial, sans-serif",
            font_size_label="15-16pt", font_size_annot="11.5-13pt",
            stroke_main=1.4, stroke_border=1.0, grid=8, min_arrow=24, padding=32, preset="course-narrative",
        ),
        container_fill="#F8F9FB", container_stroke="#D5DBE4", container_dash="", container_rx=8, block_rx=8,
        marker_w=8, marker_h=6, gap_h=48, gap_v=32, row_gap=72, icon_color="#2B3A4A", label_color="#1C2630", title_color="#5B6B7C",
    ),
}


def get_preset(name: str) -> Preset:
    try:
        return PRESETS[name]
    except KeyError:
        raise KeyError(f"unknown style preset {name!r}; choose from {sorted(PRESETS)}") from None
