"""Regression tests for the checks folded in from the adversary reports.

Every implemented check must fire on its defect probe and stay silent on the clean controls; the
false-positive probes must stay clean; the geometry helpers behind the fixes are tested directly.
"""

from __future__ import annotations

import os

import pytest

from figtree.probes import evaluate, load_probes, seed_probes
from figtree.program import load_program, parse_transform, text_width
from figtree.quality import QualityCritic, parse_animation, parse_css, polygons_overlap, segment_inside_length, segments_cross
from figtree.rubric_spec import CHECKS, VETOES
from figtree.rubrics import RUBRICS
from figtree.schemas import BBox

PROBES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples", "figtree", "probes")
ALL = seed_probes() + load_probes(PROBES)
BY_ID = {p.id: p for p in ALL}

# check id -> (defect probe that must fire it, clean/false-positive probe that must stay silent)
FOLDED = {
    "flow.through_block": ("teaching.edge_hugging_arrow", "teaching.semantic_diagonal"),
    "flow.through_text": ("teaching.arrow_through_text", "teaching.use_icons_clean"),
    "flow.collinear_overlap": ("teaching.collinear_arrows", "defect.crossing"),
    "flow.reading_order": ("teaching.up_arrows_jog_right", "teaching.polyline_arrows"),
    "flow.semantic_direction": ("teaching.backwards_semantics", "teaching.use_icons_clean"),
    "text.overflow": ("teaching.wide_glyph_overflow", "teaching.narrow_glyph_fit"),
    "text.sentence_label": ("teaching.prose_transcription", "teaching.use_icons_clean"),
    "text.duplicate_labels": ("teaching.duplicate_labels", "teaching.use_icons_clean"),
    "text.outlined_glyphs": ("teaching.text_as_paths", "teaching.use_icons_clean"),
    "medium.embedded_title": ("methodology.embedded_title", "teaching.use_icons_clean"),
    "polish.invisible_elements": ("teaching.invisible_coverage", "teaching.use_icons_clean"),
    "polish.decoration": ("teaching.decorative_clipart", "teaching.use_icons_clean"),
    "topology.container_label_mismatch": ("teaching.misleading_grouping", "teaching.use_icons_clean"),
    "layout.legend_in_drawing": ("teaching.legend_inside_drawing", "teaching.use_icons_clean"),
    "chart.axis_units": ("data-figure.axis_labels_no_units", "data-figure.small_multiples"),
    "chart.bar_axis_zero": ("data-figure.truncated_axis", "data-figure.bars_not_to_scale"),
    "chart.bar_scale": ("data-figure.bars_not_to_scale", "data-figure.truncated_axis"),
    "chart.dual_axis": ("data-figure.dual_axis", "data-figure.heavy_gridlines"),
    "chart.pie": ("data-figure.pie_paths", "data-figure.small_multiples"),
    "chart.rainbow_categorical": ("data-figure.rainbow_palette", "data-figure.pseudo_3d_bars"),
    "chart.legend_swatch_colour": ("data-figure.legend_swatch_mismatch", "data-figure.dual_axis"),
    "chart.pseudo_3d": ("data-figure.pseudo_3d_bars", "data-figure.small_multiples"),
    "chart.gridline_weight": ("data-figure.heavy_gridlines", "data-figure.small_multiples"),
    "coverage.title": ("data-figure.three_word_title", "data-figure.small_multiples"),
    "tile.hierarchy": ("dashboard.key_number_smallest", "dashboard.clean_tile_grid"),
    "tile.status_colour": ("dashboard.status_colour_decoration", "dashboard.clean_tile_grid"),
    "tile.sparkline_reference": ("dashboard.sparkline_no_baseline", "dashboard.clean_tile_grid"),
    "tile.grid_uniform": ("dashboard.uneven_tiles", "dashboard.clean_tile_grid"),
    "polish.neon": ("dashboard.neon_border", "dashboard.clean_tile_grid"),
    "text.contrast": ("data-figure.label_on_path_bar_contrast", "data-figure.small_multiples"),
    "icon.min_feature_size": ("icon.stub-detail", "icon.viewbox24-size16"),
    "icon.solid_fill": ("icon.solid-currentcolor", "icon.polyline-polygon"),
    "icon.min_gap": ("icon.merge-at-16px", "icon.thirteen-elements"),
    "icon.ink_distribution": ("icon.corner-mass", "icon.marker-arrowhead"),
    "icon.subpath_count": ("icon.subpath-packing", "icon.viewbox24-size16"),
    "icon.invisible_shape": ("icon.invisible-coverage", "icon.viewbox24-size16"),
    "icon.crossing_density": ("icon.crossing-asterisk", "icon.detail-stroke-1-5"),
    "compactness.overflow": ("icon.stroke-clipped", "icon.scaled-group"),
    "motion.pulse_direction": ("teaching.motion-backwards-pulse", "teaching.animated-tokens-at-origin"),
    "motion.reveal_order": ("teaching.motion-reveal-reversed", "teaching.animated-tokens-at-origin"),
    "motion.control_tempo": ("teaching.motion-control-faster", "teaching.animated-tokens-at-origin"),
    "motion.reduced_motion": ("teaching.motion-no-reduced-motion", "teaching.animated-tokens-at-origin"),
    "motion.decorative": ("teaching.motion-decorative-pulse", "teaching.animated-tokens-at-origin"),
}


def fired(probe_id: str) -> set:
    p = BY_ID[probe_id]
    return {i.check_id for i in QualityCritic(p.rubric).review(p.svg).issues}


@pytest.mark.parametrize("check,pair", sorted(FOLDED.items()))
def test_folded_check_fires_on_defect_and_not_on_control(check, pair):
    defect, clean = pair
    assert check in {c.id for c in CHECKS}
    assert check in fired(defect), f"{check} silent on {defect}"
    assert check not in fired(clean), f"{check} fired on {clean}"


def test_every_false_positive_probe_is_clean():
    for p in ALL:
        if p.kind in ("false_positive", "clean"):
            wrong = set(p.expect_silent) & fired(p.id)
            assert not wrong, (p.id, wrong)


def test_full_probe_set_recall_and_precision():
    s = evaluate(ALL).summary()
    assert s["precision"] == 1.0, s
    assert s["recall"] >= 0.95, s
    # the only measurable miss left is the judge-only metaphor orientation
    missed = [r["id"] for r in evaluate(ALL).probe_results if r["missed"]]
    assert missed == ["icon.mirrored-magnifier"], missed


def test_new_checks_are_in_spec_and_vetoes_resolve():
    ids = {c.id for c in CHECKS}
    for check in FOLDED:
        assert check in ids
    for v in VETOES.values():
        assert set(v["checks"]) <= ids
    assert "chart.bar_axis_zero" in VETOES["misleading_data"]["checks"]
    assert "flow.through_text" in VETOES["occlusion"]["checks"]
    assert "medium.embedded_title" in VETOES["embedded_title_or_watermark"]["checks"]
    assert "text.sentence_label" in VETOES["textual_overload"]["checks"]


def test_icon_family_rules_run_inside_the_critic():
    from figtree.icons import standalone_icon
    from figtree.iconsmith import IconSpec, icon_structural_issues

    tiny = standalone_icon("t", '<circle cx="12" cy="12" r="2"/>')
    assert "icon.coverage" in {i.check_id for i in QualityCritic("icon").review(tiny).issues}
    assert any("vanish" in i.visual_description for i in icon_structural_issues(tiny, IconSpec("t", "dot")))
    edge = standalone_icon("e", '<path d="M0 0h24v24"/>')
    assert any("safe margin" in i.visual_description for i in icon_structural_issues(edge, IconSpec("e", "edge")))
    assert "icon.safe_margin" in {i.check_id for i in QualityCritic("icon").review(edge).issues}
    # the family rules are listed for the icon medium only
    from figtree.rubric_spec import spec_for

    assert any(c["id"] == "icon.min_gap" for c in spec_for("icon")["checks"])
    assert not any(c["id"] == "icon.min_gap" for c in spec_for("teaching")["checks"])


def test_seed_examples_do_not_regress():
    root = os.path.join(os.path.dirname(PROBES), "teaching", "output")
    floors = {("bar-chart.refined.svg", "data-figure"): 9.83, ("dashboard-tiles.refined.svg", "dashboard"): 9.7, ("process-icon.refined.svg", "icon"): 8.25,
              ("slide-pipeline.refined.svg", "slide"): 9.67, ("trajectory-chart.refined.svg", "data-figure"): 10.0, ("figtree-spec.teaching.svg", "teaching"): 8.67}
    for (name, rubric), floor in floors.items():
        svg = open(os.path.join(root, name), encoding="utf-8").read()
        assert QualityCritic(rubric).review(svg).overall >= floor, name
    design = os.path.join(os.path.dirname(PROBES), "design", "figtree-spec.teaching.svg")
    assert QualityCritic("teaching").review(open(design, encoding="utf-8").read()).overall >= 8.32


class TestGeometryBehindTheFixes:
    def test_segment_inside_length_and_halo(self):
        box = BBox(144, 24, 96, 32)
        assert segment_inside_length((120, 24), (264, 24), box, 0.0) == 0.0  # on the edge: not inside the open box
        assert segment_inside_length((120, 24), (264, 24), box, 4.0) > 90  # inside the halo
        assert segment_inside_length((120, 40), (264, 136), BBox(264, 24, 96, 32), 0.0) == 0.0  # diagonal ending at the corner
        assert segment_inside_length((24, 40), (144, 40), BBox(24, 24, 96, 32), 0.0) == pytest.approx(96)  # slicing through the source

    def test_proper_crossing_excludes_t_junctions(self):
        assert segments_cross((152, 32), (152, 104), (120, 96), (168, 96))
        assert not segments_cross((152, 32), (152, 96), (120, 96), (168, 96))  # touches at the endpoint

    def test_rotated_text_boxes_use_the_oriented_box(self):
        a = [(0, 0), (10, 0), (10, 2), (0, 2)]
        b = [(0, 5), (10, 5), (10, 7), (0, 7)]
        assert not polygons_overlap(a, b)
        assert polygons_overlap(a, [(5, -1), (6, -1), (6, 1), (5, 1)])

    def test_transforms_and_glyph_widths(self):
        m = parse_transform("rotate(-90)")
        x, y = m[0] * -150 + m[2] * 22 + m[4], m[1] * -150 + m[3] * 22 + m[5]
        assert (round(x), round(y)) == (22, 150)
        prog = load_program('<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" stroke="#333" fill="none"><g transform="scale(0.5)"><circle cx="21" cy="21" r="13"/></g></svg>')
        assert prog.shapes()[0].bbox == BBox(4, 4, 13, 13)
        assert 150 < text_width("WORKFLOW MANAGER", 14, "Times New Roman") < 160
        assert 68 < text_width("Initialisation", 14, "Times New Roman") < 74
        assert text_width("2020", 10, "Arial") > 20

    def test_tspans_without_text_coordinates(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100" viewBox="0 0 200 100"><text id="t" font-size="14" text-anchor="middle"><tspan x="72" y="40">Raw</tspan><tspan x="72" y="57">input</tspan></text></svg>'
        t = load_program(svg).texts()[0]
        assert t.bbox is not None and 55 <= t.bbox.x <= 60 and t.bbox.y2 >= 60

    def test_css_animation_parsing(self):
        entries = parse_animation("ft-travel 2.4s linear 2.10s infinite, ft-show .1s linear 2.10s forwards")
        assert [e.name for e in entries] == ["ft-travel", "ft-show"]
        assert entries[0].duration == 2.4 and entries[0].delay == 2.1 and entries[0].iterations == "infinite"
        parsed = parse_css("@keyframes ft-travel{from{offset-distance:100%}to{offset-distance:0%}} #p{offset-path:path('M1,2 H3')} @media (prefers-reduced-motion: reduce){*{animation:none!important}}")
        assert "ft-travel" in parsed["keyframes"] and parsed["reduced"] is not None and parsed["rules"][0][0] == "#p"


def test_rubric_thresholds_are_published():
    for name in RUBRICS:
        th = RUBRICS[name].to_dict()["thresholds"]
        assert "flow_halo" in th and "must_read_at" in th and "title_min_words" in th
