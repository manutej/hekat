# Chart and tile gotchas: what fooled the critic

Source: `examples/figtree/probes/ADVERSARY-chart.md` (26 probes under `data-figure/` and
`dashboard/`) and `examples/figtree/teaching/NOTES-dashboard-chart.md`. "Scored 10.0" means
`figtree score` found nothing when the adversary ran. The **status** column is the critic at
HEAD (2026-10-12, computed with `figtree.probes.evaluate`; re-run `python -m figtree eval`
before quoting): the proposals became the `chart.*` and `tile.*` checks and every gaming probe
now fires one; the library-export false positives are silent. A check fires on the probe it
was written for, not on every form of the lie, so read each `Look for` row as an eye check on
the rendered PNG.

## Data encoding (unmeasured when the adversary ran; `chart.*` / `tile.*` checks since)

| Look for | What the critic did | Probe | Severity | Status at HEAD |
|---|---|---|---|---|
| **Two y axes** (left $M, right %) whose lines cross only because of the scales | 10.0: both axes have labelled units | `data-figure.dual_axis` | veto | fires `chart.dual_axis` (8.58) |
| **Bars on an axis that starts above zero** (90 %): a 1.3-point spread looks 3x | 10.0 | `data-figure.truncated_axis` | veto | fires `chart.bar_axis_zero` (8.58) |
| **Bar heights that contradict their value labels** or the tick scale ("87" shorter than "42") | 10.0 | `data-figure.bars_not_to_scale` | veto | fires `chart.bar_scale` (8.50) |
| **A pie** built from arc paths | 10.0; `path_to_points` ignored `A` commands, so the bbox was wrong too | `data-figure.pie_paths` | high | fires `chart.pie` (9.17) |
| **Pseudo-3D bars** (skewed top and side faces) | 10.0: flat fills, no gradient | `data-figure.pseudo_3d_bars` | high | fires `chart.pseudo_3d` (9.17) |
| **Legend swatches in colours no series uses** | 10.0: nothing related swatches to marks | `data-figure.legend_swatch_mismatch` | high | fires `chart.legend_swatch_colour` (8.67) |
| **Axis labels without units** ("Time", "Loss") | 10.0: the check tested for axis-like words, not units | `data-figure.axis_labels_no_units` | high | fires `chart.axis_units` (9.17) |
| **A topic title** of three words ("Quarterly Sales Overview") | 10.0: `coverage.title` fired only under 3 words | `data-figure.three_word_title` | medium | fires `coverage.title` (9.83) |
| **Six hues on one series** | 10.0: exactly six fills satisfied `polish.palette_size` | `data-figure.rainbow_palette` | medium | fires `chart.rainbow_categorical` (9.83) |
| **Gridlines heavier and darker than the data line** (2 px #333 over 0.75 px pale blue) | 10.0: three stroke widths is the limit, nothing neon | `data-figure.heavy_gridlines` | high | fires `chart.gridline_weight` (9.17) |
| A sparkline **without baseline, end values or span caption** | 10.0 | `dashboard.sparkline_no_baseline` | medium | fires `tile.sparkline_reference` (9.80) |

## Typography and colour inside a tile

| Look for | What the critic did | Probe | Severity | Status at HEAD |
|---|---|---|---|---|
| **Key number smaller than its label** (12 px number, 36 px label, 24 px note) | 10.0: every font cleared 12 px | `dashboard.key_number_smallest` | high | fires `tile.hierarchy` (9.00) |
| **Red/green on neutral metrics** with no delta, sign or threshold | 10.0 | `dashboard.status_colour_decoration` | high | fires `tile.status_colour` (9.00) |
| **Uneven tiles** (150 / 280 / 146 px, 12 and 20 px gutters) or borders on some tiles only | 10.0: tile geometry was not measured | `dashboard.uneven_tiles` | medium | fires `tile.grid_uniform` (9.80) |
| **Neon tile border** (`#00FF66` 3 px stroke on a rect) | `polish.neon` missed: the stroke branch inspected path/line/polyline only | `dashboard.neon_border` | medium | fires `polish.neon` (9.24) |
| **Neon polyline stroke** on a line series | the fill branch recoloured the markers, the line stayed neon (auto-only pass of trajectory-chart, NOTES) | - | high | not a probe |
| **Text on a gradient** tile checked against the canvas (1.3:1 at the dark end reported fine) | `parse_color` returned None for `url(#)`; only the gradient ban caught it. The critic refuses to certify contrast on gradient hosts now (`text.gradient_host`, NOTES) | - | high | not a probe |
| **Value labels inside `<path>` bars** (d3/Vega form) at 1.5:1 | `text.contrast` missed: only rect/circle/ellipse/polygon hosts | `data-figure.label_on_path_bar_contrast` | high | fires `text.contrast` (8.67) |
| Label and note at the **same size** in a tile | no hierarchy rule (NOTES) | - | medium | not a probe |

## False positives (the chart is right; do not "fix" the chart)

| Look for | Why it fired | Probe | What to do | Status at HEAD |
|---|---|---|---|---|
| y label exported as `transform="rotate(-90)" x="-150" y="22"` | un-centred rotation treated x=-150 as a canvas coordinate: `compactness.overflow` 157 px | `data-figure.rotated_ylabel_export` | full transform parsing landed; the centred form still keeps `translate` edits predictable | silent (10.00) |
| `Latency (ms)` horizontal above the y axis, no `data-role` | the `(unit)` regex alternative was wrapped in `\b` and never matched: `coverage.axis_labels` | `data-figure.units_in_parens_unrotated` | add `data-role="axis-label"` and rotate the y label; the new `chart.axis_units` fires on the unrotated form | fires `chart.axis_units` (9.17) |
| Eight region names at -45 degrees, 48 px pitch | bbox rotated only for +-90: nine false `text.overlap` pairs | `data-figure.rotated_ticks_45` | rotated boxes are real now; horizontal bars still read better | silent (10.00) |
| Nine-word category names on horizontal bars | tick labels counted as box labels for `text.words_per_label` | `data-figure.horizontal_bars_long_labels` | tag ticks `data-role="tick"` (exempt) | silent (10.00) |
| Twelve four-digit years at 10 px on an 18 px pitch | correctly caught; note the old 0.5 em estimate (20 px for "2020") vs Arial's 22 px | `data-figure.tick_labels_overlap` | use >= 24 px pitch or thin the ticks | fires `text.overlap` (8.67) |

## Refinement traps (from the bundled trajectories)

- Mechanical font raises (9 -> 12 px) make long tile labels overflow and collide in the same
  round: criticals went 3 -> 6 while the overall rose. Shorten in the same script.
- An 11 px legend that grows 3 px past the right edge is "fixed" by `set_canvas` to 578 x 325,
  silently breaking a 560 x 320 spec. Translate the legend left in the same round instead.
- The auto recolour is a fixed `#7BA3C9`, nearly the `#4C72B0` series blue: two of four series
  became indistinguishable. Choose the replacement from the unused palette in the next round.
- `coverage.title` reads the largest text, ties to the topmost. Keep the title the largest text
  (and `data-role="title"`); a legend entry larger than the title is what it will judge.

## Eval numbers

```
# adversary run                                                        HEAD 2026-10-12
figtree eval --rubric data-figure   21 probes, recall 0.25, precision 0.5, missed 12, fp 4   ->  21 probes, recall 1.0, precision 1.0, missed 0, fp 0
figtree eval --rubric dashboard      8 probes, recall 0.286, precision 1.0, missed 5, fp 0   ->  8 probes, recall 1.0, precision 1.0, missed 0, fp 0
```
The probe JSONs now expect the real check ids; re-run `python -m figtree eval` before quoting.
