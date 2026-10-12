# Diagram gotchas: what the measurable critic misses

Every row below is a probe in `examples/figtree/probes/` that the critic (`figtree score`)
scored 9.0-10.0 or flagged wrongly when the adversary wrote it (`ADVERSARY-diagram.md` and
the diagram half of `ADVERSARY-icon-motion.md`). The **status** column is the critic at HEAD
(2026-10-12, computed with `figtree.probes.evaluate`); re-run `python -m figtree eval` before
quoting. Most proposals became checks (`flow.collinear_overlap`, `flow.through_text`,
`flow.semantic_direction`, `text.sentence_label`, `text.duplicate_labels`,
`text.outlined_glyphs`, `medium.embedded_title`, `polish.invisible_elements`,
`polish.decoration`, `topology.container_label_mismatch`, `layout.legend_in_drawing`, a 4 px
flow halo, a glyph-width table, full transform parsing). A check fires on the probe it was
written for, not on every variant, and the semantic rows are lexicon proxies: keep reading the
`Look for` column as the checklist for your own eyes on the rendered PNG.
Severity is the adversary's: veto = disqualifying, critical = a reader is misled or cannot
read, warning = polish.

Prevention status for every row that became a worker rule is in `docs/FAILURE-MODES.md`.

## Check this by eye: arrows

| Look for | Why the critic is silent | Probe | Severity | Status at HEAD |
|---|---|---|---|---|
| An arrow drawn **along a block's border** or whose head lands on a block's corner, so one line touches three boxes | `flow.through_block` tests the strict interior; grazing an edge is not "through" | `teaching.edge_hugging_arrow` | veto (occlusion) | fires `flow.through_block` (8.67) |
| An arrow that **starts on the far side of its source** and slices through it | a block touched by an endpoint is dropped from the obstacles | `teaching.arrow_exits_through_source` | veto (occlusion) | fires `flow.semantic_direction`, `flow.through_block`, `flow.through_text` (8.67) |
| **Two arrows sharing a shaft** (an H with two heads); endpoints ambiguous | counted as one `flow.crossings` warning, -0.7, figure scores 9.38 | `teaching.collinear_arrows` | critical (under-penalised) | fires `flow.collinear_overlap` (8.67) |
| An arrow **struck through an annotation** | text bboxes are not flow obstacles | `teaching.arrow_through_text` | critical | fires `flow.through_text` (8.67) |
| **Backwards semantics with forward arrows**: Report -> Analysis -> Raw data, all heads pointing right | `forward_ratio` counts geometry only | `teaching.backwards_semantics` | critical (judge) | fires `flow.semantic_direction` (9.17) |
| Bottom-up columns where each arrow jogs 8 px right before climbing 24 px | an arrow counts as forward if it goes right **or** down; classify by dominant axis yourself | `teaching.up_arrows_jog_right` | warning | fires `flow.reading_order` (9.33) |
| Arrows drawn as `<polyline>` (draw.io, Inkscape exports) | polyline points are never parsed: through-block, crossings, diagonal, short-shaft and detour are blind, and reading order counts them as backward | `teaching.polyline_arrows` | critical miss + false warning | fires `flow.through_block`, `flow.through_text` (8.67) |
| A snake or ring layout | about half the arrows run against reading order by construction; `flow.reading_order` fires at 0.5 < 0.6. Decide whether the layout is right, not the rule | (noted in ADVERSARY-diagram) | warning (false) | rule unchanged |
| A fan-in **diagonal marked `data-diagonal="semantic"`** flagged as through-block | the segment/box test returns true for every diagonal against every box; a real intersection test is missing | `teaching.semantic_diagonal` | critical false positive | silent (10.00) |

## Check this by eye: text

| Look for | Why the critic is silent | Probe | Severity | Status at HEAD |
|---|---|---|---|---|
| **Wide labels** (caps, 14 px, 16 characters) spilling past a 112 px block | width is estimated at 0.5 em per character; caps run 0.65-0.72 em | `teaching.wide_glyph_overflow` | critical | fires `text.overflow` (9.17) |
| A label whose **font-size is inherited** from a `<g font-size="24">` and overflows | the bbox is computed at the 12 px default although the min-font check resolves inheritance | `teaching.overflow_inherited_font` | critical miss | fires `text.overflow` (9.17) |
| Narrow labels ("Initialisation", 71 px real) flagged as overflow in an 88 px block | same estimator, other direction | `teaching.narrow_glyph_fit` | false positive | silent (10.00) |
| **Labels drawn as paths** (outlined glyphs, 8 px tall): no `<text>` exists | every text check passes vacuously | `teaching.text_as_paths` | critical | fires `text.min_font`, `text.outlined_glyphs` (8.67) |
| **Full sentences in boxes** chained boustrophedon, <= 8 words each | the word limit is per label; a label ending in "." is not detected | `teaching.prose_transcription` | veto (textual overload) | fires `text.sentence_label` (8.67) |
| **Duplicate labels** ("Filter" twice): the same component or two? | not measured | `teaching.duplicate_labels` | warning | fires `text.duplicate_labels` (9.67) |
| Two-line labels whose x/y live only on the `<tspan>`s (editor export) flagged as overlap/overflow | `<text>` without x/y is placed at 0,0 | `teaching.tspan_no_text_y` | critical false positive | silent (10.00) |
| A rotated label at an angle other than +-90 degrees | bbox is only rotated for +-90; expect false overlaps | `data-figure.rotated_ticks_45` | false positive | silent (10.00) |
| `rotate(-90)` without a centre, `x="-150"` (d3/matplotlib export) flagged as overflow | the un-centred rotation is not mapped | `data-figure.rotated_ylabel_export` | false positive | silent (10.00) |

## Check this by eye: topology, composition, decoration

| Look for | Why the critic is silent | Probe | Severity | Status at HEAD |
|---|---|---|---|---|
| A **container whose title contradicts its contents** ("Training" holds Deploy and Monitor; Train sits outside) | container labels are not matched to children | `teaching.misleading_grouping` | critical (judge) | fires `topology.container_label_mismatch` (9.17) |
| A **legend placed inside the drawing** at grid level, reading as a fourth stage | legends are not recognised | `teaching.legend_inside_drawing` | warning | fires `layout.legend_in_drawing` (9.83) |
| **Invisible elements that stretch the content bbox** (white-on-white rect, opacity-0 text) to fake 24 px margins | the bbox counts invisible elements | `teaching.invisible_coverage` | warning (compactness 1-2 by anchor) | fires `compactness.blank_margin`, `polish.invisible_elements` (9.00) |
| **Clip-art**: overlapping grey ellipses as a "cloud" with no label and no connector | only `rx` is a clip-art signal | `teaching.decorative_clipart` | veto | fires `polish.decoration` (8.67) |
| `Figure 2: Overview of ...` **caption inside the canvas** (paper figures) | the `embedded_title_or_watermark` veto has no check | `methodology.embedded_title` | veto | fires `medium.embedded_title` (9.17) |
| A six-step **vertical process at page scale** flagged as a tower | aspect rule ignores that every flow is vertical | `teaching.narrow_tower` | warning (false) | silent (10.00) |
| A slide with **symmetric 96 px title/footer bands** asked to "enlarge the content" | fixed canvas tolerates no band wider than 15 %; centred bands are not exempt | `slide.breathing_room` | warning (false) | silent (10.00) |
| A figure with **no source**: tidy geometry, wrong semantics, score 10.0 | coverage and hallucination are `n/a` without `--source`; the judge-only vetoes never cap `medium_fit` | all gaming probes | - | by design |

## Check this by eye: after `animate`

| Look for | Why | Probe | Status at HEAD |
|---|---|---|---|
| Overflow reported on an animated figure that scored 10.0 before | pulse tokens are `<circle r="3.5">` with no cx/cy: bbox at -3,-3. Four or more tokens also count as blocks for `topology.ungrouped` | `teaching.animated-tokens-at-origin` | silent (10.00) |

## Critic defects the adversaries filed (not probes)

- `rx="50%"` on a rect raised `ValueError` and aborted the whole review; verify before relying on percentage radii.
- Polyline flows had no points (fixed at HEAD: `teaching.polyline_arrows` fires).
- The 0.5 em width estimate was wrong both ways (measured caps 0.65-0.72 em, narrow lower-case
  0.36-0.45 em); at HEAD `wide_glyph_overflow` fires and `narrow_glyph_fit` is silent, so the
  estimate is per-glyph now. Still check wide caps by eye at the medium's size.
- Transforms: only `translate()` was applied; at HEAD `figtree/program.py` parses the full
  transform list (translate, scale, rotate with or without centre, matrix, skew), which fixed
  `rotated_ylabel_export`, `scaled-group` and `tspan_no_text_y`.

## What to do with a finding

Anchor it to an id and write the fix as an edit-script op, exactly as the critic would:
`{"op": "translate", "id": "f1", ...}` for a re-route is usually wrong (paths are `d` strings),
so re-routes are `set_attr d` with a new orthogonal path, and block moves are `translate` on the
leaf group followed by `set_attr d` on every arrow that touched it. If the finding recurs across
figures, write it as a probe (`.claude/skills/svg-eval`) so it becomes a regression test.
