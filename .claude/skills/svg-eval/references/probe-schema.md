# Probe schema and harness

Implementation: `figtree/probes.py` (`Probe`, `seed_probes`, `load_probes`, `evaluate`),
driven by `python -m figtree eval`.

## Files

```
examples/figtree/probes/<rubric>/<slug>.svg     the figure (standalone, house style, ids on every element)
examples/figtree/probes/<rubric>/<slug>.json    the verdict
```

`load_probes(dir)` walks `**/*.json` and pairs each with the `.svg` of the same stem; a JSON
without an SVG is skipped. The directory name is the default `source`.

## JSON fields

```json
{
  "id": "teaching.edge_hugging_arrow",         // "<rubric>.<slug>"; authoritative over the file name
  "rubric": "teaching",                        // methodology | teaching | slide | data-figure | dashboard | icon
  "kind": "gaming",                            // defect | clean | gaming | false_positive (default defect)
  "expect_fire": ["flow.through_block"],       // check ids that must fire (proposed.* allowed)
  "expect_silent": [],                         // check ids that must not fire
  "rationale": "Arrow f1 is drawn along y=24, Parser's top border ... segment_hits_box tests the strict interior.",
  "source": "adversary-diagram"                // who wrote it; seeds are "seed"
}
```

Check ids are the `id` fields of `figtree/rubric_spec.py:CHECKS` (73 at HEAD; regenerate this list
from `python -m figtree eval --specs DIR`):

```
compactness.blank_margin  compactness.overflow  compactness.aspect  compactness.detour
flow.crossings  flow.diagonal  flow.through_block  flow.short_shaft  flow.reading_order  flow.no_connectors  flow.collinear_overlap  flow.through_text  flow.semantic_direction
text.min_font  text.words_per_label  text.contrast  text.gradient_host  text.overflow  text.overlap  text.sentence_label  text.duplicate_labels  text.outlined_glyphs
polish.font_families  polish.palette_size  polish.neon  polish.gradient_fill  polish.filter  polish.corner_radius  polish.stroke_widths  polish.invisible_elements  polish.decoration
medium.black_background  medium.icon_text  medium.icon_elements  medium.square  medium.no_canvas  medium.embedded_title
coverage.axis_labels  coverage.title  coverage.plan_terms
hallucination.label_source
topology.ungrouped  topology.empty_container  topology.container_label_mismatch
content.none
layout.legend_in_drawing
chart.axis_units  chart.bar_axis_zero  chart.bar_scale  chart.dual_axis  chart.pie  chart.rainbow_categorical  chart.legend_swatch_colour  chart.pseudo_3d  chart.gridline_weight
tile.hierarchy  tile.status_colour  tile.sparkline_reference  tile.grid_uniform
icon.safe_margin  icon.coverage  icon.subpath_count  icon.solid_fill  icon.invisible_shape  icon.min_feature_size  icon.min_gap  icon.crossing_density  icon.ink_distribution
motion.pulse_direction  motion.reveal_order  motion.control_tempo  motion.reduced_motion  motion.decorative
```

`classify(description)` maps a critic message to its check id by regex (`Check.pattern`); a
message that matches no pattern has `check_id = None` and counts for no check. A `proposed.*`
id never fires, so it is always a miss: that is how gaming probes record their demand.

## How a probe is scored

```python
report = QualityCritic(p.rubric).review(p.svg)           # no source text: coverage/hallucination n/a
fired  = {i.check_id for i in report.issues if i.check_id}
missed = [c for c in p.expect_fire if c not in fired]     # -> per_check[c].fn
wrong  = [c for c in p.expect_silent if c in fired]       # -> per_check[c].fp
passed = not missed and not wrong
if p.kind == "gaming": passed = report.overall >= 9.0     # fooled by definition; recorded for the judge
```

`per_check` accumulates tp/fn/fp/tn per check id; `summary()` gives probes, expected fires,
caught, missed, false positives, recall, precision and the failing probe ids; `eval` exits 1
while any probe fails. `--report` writes `{summary, per_check, probes[...]}`, which the showcase
reads.

## Seed probes (`seed_probes()`)

Built from three helpers: `block(i, x, y, w=96, h=32, fill="#7BA3C9", label, size=12, font,
text_fill, extra)`, `arrow(i, d, flow="data")` (marker-ended, dashed when not data) and
`doc(body, w=320, h=96)` (Times, white background, `#a` marker). The clean diagram is two
compliant blocks and one arrow with 24 px margins. One defect probe per teaching check (min
font, contrast, gradient, neon fill, neon stroke, overflow, overlap, two fonts, through block,
crossing, diagonal, short shaft, reading order, blank margin, canvas overflow, black background,
corner radius, long label, palette, no connectors), a chart triple (clean, no axis labels, title
not a finding), an icon quad (clean, text, not square, stroke widths) and a slide pair (clean,
small font). Use the same helpers' conventions when you hand-write a probe so the only
difference between probe and control is the defect.

## Writing a good probe

- One defect per defect probe; the control for it is the clean probe of the same medium.
- House style, ids on everything, `data-role="block"` on blocks, `data-flow` on arrows,
  `data-kind="label"` on labels, white `background` rect first.
- Render it (`figtree refine --rounds 0 --render-dir r/` or the headless command in
  `svg-animation/references/capture-frames.md`) and look before filing; measure real glyph widths
  with a metric-compatible font (Liberation Serif for Times) when the claim is about width.
- Name the probe for what the reader sees (`edge_hugging_arrow`), not for the check.
- In `rationale`, say which function and branch is blind and what the proposed signal is; the
  table in `ADVERSARY-*.md` is built from these.
- Severity in the table: veto (misleads about the data or the method), critical (a reader
  misreads or cannot read), warning (polish), and mark false positives as what they are.
