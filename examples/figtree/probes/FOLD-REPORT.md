# Fold report: adversary findings folded into the measurable critic

Source reports: `ADVERSARY-diagram.md`, `ADVERSARY-chart.md`, `ADVERSARY-icon-motion.md`.
Every `proposed.*` id that became a real check was renamed in its probe's `.json` (same
meaning, `kind` changed from `gaming` to `defect`, a `folded` note added). Numbers below are
`python -m figtree eval --rubric R` before and after; the full run is in `../eval/eval.json`
and the published specs in `../rubrics/*.json`.

## Before / after

| rubric | probes | recall before | precision before | recall after | precision after |
|---|---|---|---|---|---|
| methodology | 1 | 0.00 | n/a | 1.00 | 1.00 |
| teaching | 52 -> 53 | 0.54 | 0.77 | 1.00 | 1.00 |
| slide | 4 | 1.00 | 0.67 | 1.00 | 1.00 |
| data-figure | 21 | 0.25 | 0.50 | 1.00 | 1.00 |
| dashboard | 8 | 0.29 | 1.00 | 1.00 | 1.00 |
| icon | 23 | 0.31 | 0.50 | 0.94 | 1.00 |
| **all** | 109 -> 110 | **0.43** | **0.68** | **0.99** | **1.00** |

(teaching gains one seed probe, `defect.collinear`; the seed `defect.crossing` is now a true X.)

Seed figures (must not regress): `design/figtree-spec.teaching.svg` 8.32 -> 9.05;
`output/figtree-spec.teaching.svg` 8.67 -> 8.67; `bar-chart.refined` 9.83 -> 9.83;
`dashboard-tiles.refined` 9.70 -> 9.70; `process-icon.refined` 8.25 -> 8.50;
`slide-pipeline.refined` 9.67 -> 9.67; `trajectory-chart.refined` 10.0 -> 10.0.
Tests: 133 -> 197 (`tests/test_figtree_adversary.py`: one fire/silent pair per folded check,
all false-positive and clean probes, the seed floors, and the geometry behind the fixes).

## False positives fixed (rule changed, never the figure)

- `program.py`: full `transform` lists (translate, scale, rotate with/without centre, matrix,
  skew) applied to every bbox; rotated text keeps an oriented box and `text.overlap` uses a
  separating-axis test (`rotated_ticks_45`, `rotated_ylabel_export`, `scaled-group`,
  `rotated-into-margin`).
- Per-glyph width tables (Times class and Arial class, bold +7%) with the resolved
  (inherited, `style=`) font size replace the 0.5 em estimate (`narrow_glyph_fit`,
  `wide_glyph_overflow`, `overflow_inherited_font`, `tick_labels_overlap`).
- `<text>` without x/y takes them from its tspans; per-tspan boxes are unioned (`tspan_no_text_y`).
- Relative path commands, arcs (sampled), curves, `polyline`/`polygon` points and
  stroke-inclusive floor/ceil extents (`relative-path-commands`, `polyline_arrows`,
  `stroke-clipped`, `label_on_path_bar_contrast`).
- Animation overlays (`data-role=pulse|anim-shaft`) and invisible elements are no shapes
  (`animated-tokens-at-origin`); `flow.*` never runs for icons (`marker-arrowhead`).
- `compactness.aspect` skipped for a strictly vertical tower / horizontal banner
  (`narrow_tower`); fixed canvases tolerate centred bands up to 34% (`slide.breathing_room`);
  icons use the family coverage rule instead of blank margins.
- Pill rects (`rx >= min(w,h)/2`) are shapes, not clip art, in icons; `rx="50%"` no longer
  aborts the review (`pill-toggle`).
- `AXIS_WORDS` matches `(unit)`, `%`, currency without word boundaries; an unrotated y label
  above the axis counts (`units_in_parens_unrotated`); tick/category labels next to an axis
  are exempt from the word limit (`horizontal_bars_long_labels`).
- `polish.neon` and `text.contrast` look at every shape tag, including rect strokes and
  path/polygon hosts (`neon_border`, `label_on_path_bar_contrast`).

## Implemented checks (all `mechanical=True` in `rubric_spec.CHECKS`; rubric thresholds in `rubrics.py`)

- diagram: `flow.through_block` (halo `flow_halo`=4px, port rule: a shaft may not slice its own
  block), `flow.through_text`, `flow.collinear_overlap` (split from `flow.crossings`, fan-in/
  fan-out at one port exempt), `flow.reading_order` by dominant axis, `flow.semantic_direction`,
  `text.sentence_label`, `text.duplicate_labels`, `text.outlined_glyphs` (+ `text.min_font` on
  the glyph height), `medium.embedded_title`, `polish.invisible_elements`, `polish.decoration`,
  `topology.container_label_mismatch`, `layout.legend_in_drawing`.
- chart: `chart.axis_units` (numeric axes only), `chart.bar_axis_zero`, `chart.bar_scale`
  (`bar_scale_tolerance`), `chart.dual_axis`, `chart.pie`, `chart.rainbow_categorical`,
  `chart.legend_swatch_colour`, `chart.pseudo_3d`, `chart.gridline_weight`; `coverage.title`
  tightened (`title_min_words`=5 or a verb/comparison).
- dashboard: `tile.hierarchy`, `tile.status_colour`, `tile.sparkline_reference`,
  `tile.grid_uniform` (`tile_width_tolerance`, `tile_gutter_tolerance`).
- icon (family rules now inside `QualityCritic`, `IconSmith.score` and
  `icon_structural_issues` delegate to `quality.icon_family_issues`): `icon.safe_margin`,
  `icon.coverage` (flat metaphors judged by the long side), `icon.subpath_count`,
  `icon.solid_fill`, `icon.invisible_shape`, `icon.min_feature_size`, `icon.min_gap`,
  `icon.crossing_density`, `icon.ink_distribution` (`must_read_at`, `max_strokes`,
  `icon_safe_margin`, `min_coverage`, `min_feature_px`, `min_gap_px`, `max_ink_offset`).
- motion (CSS parsed from `<style>`): `motion.pulse_direction`, `motion.reveal_order`,
  `motion.control_tempo` (control period >= data period and lighter fill),
  `motion.reduced_motion`, `motion.decorative`.
- vetoes: `occlusion` += through_text, collinear_overlap; `textual_overload` += sentence_label;
  `illegible_type` += outlined_glyphs; `embedded_title_or_watermark` = embedded_title;
  `clip_art` += decoration; new `misleading_data` (bar_axis_zero, bar_scale, dual_axis,
  legend_swatch_colour) and `motion_misleads` (pulse_direction, reduced_motion).

## Gaming-only (judge is the only defence)

- `icon.mirrored-magnifier` (`proposed.icon.metaphor_orientation`): chirality of a metaphor
  needs the brief or a library reference; no measurable proxy without one.
- `flow.semantic_direction` and `topology.container_label_mismatch` are lexical proxies that
  raise a judge request; they catch the probes, not every wrong arrow or grouping.
- Rendered-frame motion checks (token position at t, reduced-motion frame equality) remain
  unimplemented; the CSS checks cover the five motion probes statically.
- Scores still saturate at 10 without a source or plan (`semantic_coverage`,
  `hallucination_control` unassessed); a tidy, wrong figure needs the judge.
