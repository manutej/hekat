# Adversarial probes: `data-figure` and `dashboard`

Twenty-six probes that try to break the measurable critic (`figtree/quality.py`) on charts
and dashboard tiles: 14 *gaming* cases (bad chart or tile, critic scores 10), 4
*false positives* (good chart, critic flags it), 6 *defects* (4 caught, 2 missed) and 2
*clean* controls. Files: `data-figure/<slug>.svg` + `.json`, `dashboard/<slug>.svg` + `.json`
(`source: adversary-chart`). Scores below are `python -m figtree score FILE --rubric ...`.

Severity: **veto** = the chart misleads the reader about the data; **high** = a reader will
misread or cannot read a value; **medium** = polish or convention; **low** = cosmetic.

## Table

| id | kind | what it shows | what the critic did | proposed check / rule change | severity |
|---|---|---|---|---|---|
| `data-figure.dual_axis` | gaming | Revenue ($M) on a left axis and churn (%) on a right axis; the lines "cross" only because of the two scale choices | 10.00, nothing fired: both axes have labelled units, so `coverage.axis_labels` is satisfied | `proposed.dual_axis`: two vertical axis lines (or two rotated axis labels) on opposite sides of the plot area | veto |
| `data-figure.truncated_axis` | gaming | Bar chart with the y axis starting at 90 %; a 1.3-point spread looks like a 3x difference | 10.00, nothing fired | `proposed.bar_axis_zero`: for bars standing on the x axis line the lowest y tick label must read 0 | veto |
| `data-figure.bars_not_to_scale` | gaming | Bars whose heights contradict their own value labels and the tick scale (the "87" bar is shorter than the "42" bar) | 10.00, nothing fired | `proposed.bar_scale`: fit the y ticks to their positions (linear), then check each bar height against its value label or against monotone ordering | veto |
| `data-figure.pie_paths` | gaming | A four-slice pie built from arc paths; "per" and "count" in the subtitle/footnote satisfy `AXIS_WORDS` | 10.00, nothing fired; `path_to_points` ignores `A` commands so the pie's bbox is only its M/L points | `proposed.pie_chart`: three or more filled paths with an `A` command sharing one `M` point; the canon asks for a sorted bar chart | high |
| `data-figure.rainbow_palette` | gaming | One series, six bars, six hues that encode nothing | 10.00: exactly six saturated fills, so `polish.palette_size` (limit 6) stays silent | `proposed.rainbow_categorical`: single-series chart (no legend) whose bars carry more than two hues | medium |
| `data-figure.legend_swatch_mismatch` | gaming | Lines are blue and orange; the legend swatches are green and purple | 10.00: four muted fills, no check relates swatches to series | `proposed.legend_swatch_colour`: every legend swatch fill must equal the stroke/fill of some series mark | high |
| `data-figure.axis_labels_no_units` | gaming | Axis labels "Time" and "Loss" with no unit on either | 10.00: the check named "missing axis labels *with units*" only tests for axis-like words | `proposed.axis_units`: an axis label must contain a parenthesised unit, a `%`, or an explicit unitless marker | high |
| `data-figure.three_word_title` | gaming | Title "Quarterly Sales Overview", a topic rather than a finding | 10.00: `coverage.title` fires only below three words | `proposed.title_is_finding` (tighten `coverage.title`): require a verb or comparative (rises, falls, leads, by N %) or at least five words | medium |
| `data-figure.pseudo_3d_bars` | gaming | Each bar has a skewed top and side face (3D effect); the value edge is ambiguous | 10.00: three flat fills, no gradient, no filter; the rubric text forbids 3D but nothing measures it | `proposed.pseudo_3d`: a polygon sharing an edge with a rect and having non-axis-aligned edges | high |
| `data-figure.heavy_gridlines` | gaming | 2 px `#333333` gridlines over a 0.75 px pale-blue data line | 10.00: three stroke widths (limit 3), nothing neon | `proposed.gridline_weight`: a line spanning the plot area must be thinner and lighter than every series mark | high |
| `data-figure.rotated_ylabel_export` | false_positive | Correct y label written as d3/matplotlib export it: `transform="rotate(-90)" x="-150" y="22"` | 8.83, `compactness.overflow` critical: "content overflows the left edge by 157px" (and top by 14px); the rotation branch only handles `rotate(a cx cy)` and takes x=-150 as a canvas coordinate | Map (x, y) through the rotation when `rotate()` has no centre | high (any library export of a y label is rejected) |
| `data-figure.units_in_parens_unrotated` | false_positive | "Latency (ms)" and "Throughput (req/s)", the y label horizontal above the axis, no `data-role` | 9.08, `coverage.axis_labels` critical: `AXIS_WORDS` wraps `(.*)`, `%`, `$` in `\b`, which never matches after a space or at the end of a string, so neither label counts and nothing is rotated | Detect a parenthesised unit or trailing `%` without word boundaries; accept an unrotated text whose bbox sits just above the y axis | high |
| `data-figure.rotated_ticks_45` | false_positive | Eight long region names rotated -45 degrees at a 48 px pitch (rendered, they do not touch) | 8.67, `text.overlap` critical, nine pairs: the bbox is only rotated for +-90 degrees, so each label keeps its full horizontal width (up to 99 px) | Rotate the text bbox for any angle (or shrink its horizontal extent by cos(angle)) | high |
| `data-figure.horizontal_bars_long_labels` | false_positive | Horizontal bar chart of survey items; four category names run to nine words | 8.97, `text.words_per_label` x4: category labels are treated like box labels | Exempt tick/category labels (text end-anchored on the y axis, or `data-role="tick"`) from the word limit, or raise the chart limit | medium |
| `data-figure.small_multiples` | clean | 2x2 panel with one finding title, shared axis labels with units, one-word panel titles | 10.00, nothing fired (panel titles under three words do not trip `coverage.title`, hosted panel text is not reported as overflow) | regression guard | - |
| `data-figure.tick_labels_overlap` | defect | Twelve four-digit years at 10 px on an 18 px pitch | 8.67, `text.overlap` x11 caught. Note: the 0.5 em estimate gives 20 px for "2020"; Arial digits make it 22 px, so a 21-22 px pitch collides on screen yet passes | Use per-class glyph widths (digits 0.56 em, caps 0.67 em) in the estimate | medium |
| `data-figure.seven_series_palette` | defect | Seven series in seven muted colours | 9.83, `polish.palette_size` caught (7 > 6) | - | medium |
| `data-figure.label_on_path_bar_contrast` | defect | Bars drawn as `<path>` (d3/Vega form) in navy with `#4A4A4A` value labels inside them (1.5:1) | 10.00, `text.contrast` **missed**: `_background_for` only considers rect/circle/ellipse/polygon hosts, so the labels are checked against the white canvas (7.5:1) | Include filled paths and polygons as contrast hosts, as `_host_fill` already does for the gradient check | high |
| `dashboard.key_number_smallest` | gaming | Tile whose key number is 12 px while the label is 36 px and the footnote 24 px | 10.00, nothing fired: every font clears the 12 px minimum | `proposed.tile_hierarchy`: inside a tile the numeric value must be the largest text (title < number > note; NOTES-dashboard-chart raised this) | high |
| `dashboard.status_colour_decoration` | gaming | Three neutral metrics painted red / green / red (value and top stripe) with no delta, sign or threshold | 10.00: two accent fills, high contrast | `proposed.status_colour_semantics`: red/green on a value or stripe must pair with a signed delta, a threshold or a status word in the same tile | high |
| `dashboard.sparkline_no_baseline` | gaming | Sparkline with no baseline, no end values, no span caption | 10.00, nothing fired | `proposed.sparkline_reference`: a polyline inside a tile needs a reference line or labelled end points or a span caption | medium |
| `dashboard.uneven_tiles` | gaming | Tiles 150 / 280 / 146 px wide with 12 and 20 px gutters | 10.00: tile geometry is not measured (already noted in NOTES-dashboard-chart) | `proposed.tile_grid_uniform`: tiles in one row share width within 4 px, gutters within 2 px, and the same border/fill treatment | medium |
| `dashboard.clean_tile_grid` | clean | 2x2 grid, equal tiles, label < number > delta, red/green only on signed deltas, sparkline with dashed reference and span caption | 10.00, nothing fired | regression guard | - |
| `dashboard.neon_border` | defect | 3 px `#00FF66` tile border as a "healthy" indicator | 10.00, `polish.neon` **missed**: the stroke branch only inspects path/line/polyline, so rect and circle strokes in neon pass | Check stroke colour on every shape tag | medium |
| `dashboard.grey_delta_contrast` | defect | `#9A9A9A` delta on a `#F7F7F7` tile (2.6:1) | 8.40, `text.contrast` caught with a mechanical recolor | - | high |
| `dashboard.label_seven_words` | defect | Seven-word tile title on a six-word limit | 9.24, `text.words_per_label` caught | - | low |

## Patterns across the probes

1. **The data-figure rubric measures typography and colour, not the data encoding.** All ten
   data-figure gaming probes score 10.00 and six of them (dual axis, truncated axis, bars
   not to scale, legend mismatch, missing units, 3D) misstate the data. The rubric
   description promises "labelled axes with units ... no 3D or gradients"; only the gradient
   half is measured. The cheapest high-value additions are `proposed.axis_units`,
   `proposed.bar_axis_zero` and `proposed.legend_swatch_colour`, all computable from ids and
   attributes already present.
2. **`AXIS_WORDS` is the single weakest regex.** The alternatives `%`, `$`, `€`, `£` and
   `\(.*\)` are wrapped in `\b` and never match in practice; the words that do match
   (`time`, `loss`, `score`, `count`, `per`) let unit-less labels, pie subtitles and
   footnotes pass. One false positive (`units_in_parens_unrotated`) and two gaming probes
   (`axis_labels_no_units`, `pie_paths`) hinge on it.
3. **Text geometry is the source of every false positive.** `rotate(-90)` without a centre,
   rotation by any angle other than +-90, and the 0.5 em glyph estimate each produce a
   critical issue on a correct chart (`compactness.overflow`, `text.overlap`), each of which
   caps a dimension at 5 and would push the refiner to "fix" a correct label.
4. **Host detection ignores paths.** Any chart library that emits bars, areas or slices as
   `<path>` gets no contrast check on labels inside them (`label_on_path_bar_contrast`), and
   `path_to_points` drops arc and curve commands, so a pie's bbox is wrong too.
5. **Dashboard checks stop at the tile border.** Hierarchy inside a tile, status colour
   semantics, sparkline references and grid uniformity are all unmeasured; the four
   dashboard gaming probes score 10.00.

## Eval summaries

```
$ python -m figtree eval --rubric data-figure
21 probes, recall 0.25, precision 0.5, missed 12, false positives 4
  FAIL data-figure.horizontal_bars_long_labels (false_positive): false ['text.words_per_label'] overall 8.97
  FAIL data-figure.label_on_path_bar_contrast (defect): missed ['text.contrast'] overall 10.0
  FAIL data-figure.rotated_ticks_45 (false_positive): false ['text.overlap'] overall 8.67
  FAIL data-figure.rotated_ylabel_export (false_positive): false ['compactness.overflow'] overall 8.83
  FAIL data-figure.units_in_parens_unrotated (false_positive): false ['coverage.axis_labels'] overall 9.08

$ python -m figtree eval --rubric dashboard
8 probes, recall 0.286, precision 1.0, missed 5, false positives 0
  FAIL dashboard.neon_border (defect): missed ['polish.neon'] overall 10.0
```

"missed" counts the `proposed.*` checks (11 data-figure, 4 dashboard) that do not exist yet
plus the two genuine misses (`text.contrast` on path hosts, `polish.neon` on rect strokes);
gaming probes pass by definition when the critic scores them at or above 9.0. The 21
data-figure probes include the three seed probes from `figtree/probes.py`.
