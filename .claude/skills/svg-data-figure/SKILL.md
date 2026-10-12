---
name: svg-data-figure
description: Build, score and repair charts and dashboard tiles as editable SVG under the FigTree data-figure and dashboard rubrics. Use when someone asks for a bar chart, line chart, trajectory plot, small multiples, a KPI/stat tile, a sparkline tile, a dashboard strip, "make this chart publication-ready", "the axis has no units", "fix the legend", "score this chart", "turn these numbers into a figure", or wants chart conventions enforced (sorted bars, zero-based bars, no dual axis, no pie, at most 6 hues, units in axis labels, direct labels, a title that states the finding). Also use when a chart exported from d3, matplotlib or Vega trips the critic falsely. Not for flow diagrams (svg-diagram) or icons (svg-icon).
---

# SVG data figures: charts and dashboard tiles

A chart's job is to let a reader read a value and a comparison without being misled. The
measurable critic (`figtree score --rubric data-figure|dashboard`) checks typography, colour,
margins, axis labels, the title and, since the chart adversary, the data encoding (`chart.*`:
units, zero-based bars, bar scale, dual axis, pie, rainbow, legend swatches, pseudo-3D,
gridline weight; `tile.*`: hierarchy, status colour, sparkline reference, grid uniformity).
Those checks were written against the probes in `references/chart-gotchas.md` and catch the
probe's form of each lie. So: follow the canon by construction, score, and read the data back
from the PNG yourself.

## Chart canon (build it this way and most checks never fire)

1. **Bars sorted** by value unless the category order carries meaning (time, ordinal scale).
2. **Bars start at zero.** A truncated axis turns a 1.3-point spread into a 3x bar. Lines may
   use a non-zero baseline; bars may not.
3. **No dual axis.** Two series on two scales "cross" wherever you want them to. Use two panels.
4. **No pie, no 3D, no gradients, no filters.** Angles are read worse than lengths; skewed faces
   make the value edge ambiguous (`pseudo_3d_bars`).
5. **At most 6 hues**, and only as many as there are series. One series = one hue (a highlight
   is a second hue with a key). Six bars in six hues encode nothing (`rainbow_palette`).
6. **Units in the axis labels**: `Accuracy (%)`, `Latency (ms)`, `Revenue ($M)`. Tag each
   `<text data-role="axis-label">` and put the unit in the text: `chart.axis_units` is critical
   on a numeric axis whose label has no parenthesised unit, `%` or currency sign.
7. **Direct labels beat a legend.** Label the series at its end or the bar at its top. When a
   legend is unavoidable (series ending within a few px of each other), every swatch fill must
   equal the series' stroke/fill (`chart.legend_swatch_colour`).
8. **The title states the finding** in >= 3 words with a verb or comparative: "Variant B reaches
   the highest accuracy", not "Quarterly Sales Overview". `coverage.title` reads the largest
   text: under 3 words, or under 5 without a verb or comparative, it fires.
9. **Gridlines thinner and lighter than every mark** (`chart.gridline_weight`); ticks >= 10 px
   (chart) / 12 px (tile); tick labels tagged `data-role="tick"` (exempt from the word limit)
   and rotated no more than they must be; prefer horizontal bars for long category names.
10. **Series colour is one colour everywhere**: line, markers, swatch. The neon auto-fix covers
    strokes on every shape now but recolours each element to the same `#7BA3C9`; recolour line,
    markers and swatch to one chosen colour in one edit.

Palette that passed every bundled example: `#4C72B0` blue, `#DD8452` orange, `#55A868` green,
`#C44E52` red, `#8172B3` purple, `#937860` brown (muted, colour-blind-safe at <= 6).

## Dashboard tile canon

- One title (<= 6 words), one key number, one qualifier. **Number > title > note** in size
  (`tile.hierarchy` is critical when the number is not the largest text in its tile).
- Tiles in a row share width within 4 px, gutters within 2 px, the same border and fill
  (`tile.grid_uniform`).
- Red/green only on a signed delta, a threshold or a status word in the same tile; neutral
  metrics stay neutral (`tile.status_colour`).
- A sparkline needs a reference (dashed baseline), labelled end values or a span caption
  (`tile.sparkline_reference`).
- The canvas is fixed: the critic centres content instead of resizing. A three-tile strip is a
  banner (aspect 3.6 > 2.0) and will raise `compactness.aspect` as a request; accept it.

## Build

Start from `assets/bar-chart.template.svg` (data-figure, 480 x 300) or
`assets/dashboard-tile.template.svg` (dashboard, 320 x 200). Keep the ids and the `data-role`
attributes; the critic reads `axis-label` (and `x-label`/`y-label`) and `tick`/`category`/
`tick-label` (exempt from the word limit); `mark`, `legend`, `value`, `title`, `reference` are
conventions that people, the judge and future checks read. Rules of construction:

- `<rect id="background">` first; one font family; <= 3 stroke widths (chart) / 2 (tile).
- Axis labels: x centred under the axis; y rotated with a centre, `transform="rotate(-90 18 150)"`
  (the centred form keeps `translate` edits predictable; un-centred library exports parse too).
- Bars as `<rect>` standing on the x axis line: the form `chart.bar_axis_zero` and
  `chart.bar_scale` were written against.
- Value labels above bars or at the end of lines, 11 px, the figure's text colour.
- Canvas aspect 1.0-2.2 (chart) at >= 480 px; margins 16 px, blank bands under 15 % of the side.

Compute the geometry, do not eyeball it: `y = y0 - value * (plot_height / y_max)`; write the
tick values that this mapping gives, and check that the tallest bar's label still clears the
title. A bar whose height contradicts its own value label is `chart.bar_scale` (tolerance 5 %
of the tick range).

## Score, read, repair

```bash
python -m figtree score chart.svg --rubric data-figure --json > score.json
python -m figtree refine chart.svg --rubric data-figure -o chart.refined.svg --trajectory t.json \
    --edits edits.json --render-dir r/
```

Then open `r/round0.png` and read the chart as a stranger: do the bar heights match the labels?
Does the lowest y tick read 0 under bars? Is each legend swatch the colour of its series? Is
the lightest text >= 4.5:1 on its host? Are the units there? `references/chart-gotchas.md` is
the list; `references/rubric-data-figure.md` / `rubric-dashboard.md` are the thresholds.

Repair with an edit script (`assets/edits-example.json` is the real two-round script that took
the bundled trajectory chart from 7.59 to 10.0). Typical ops: `insert` the two axis labels,
`set_text` the title to the finding, `translate` legend entries apart, `recolor` a series on
line + markers + swatch together, `set_attr font-size` on ticks. Contradict an auto-fix (the
critic's default `#7BA3C9`, which is nearly the blue you already use) in the *next* round.

## What the checks know and what they do not

Each `chart.*` and `tile.*` check was written against one probe (`references/chart-gotchas.md`);
a chart that lies in another form passes. Still only yours: whether the finding in the title is
true, whether the comparison is the right one, whether a legend is needed at all, whether the
numbers are current. Run `figtree judge` on anything that will be published. When you find a
new lie, write the probe first (`.claude/skills/svg-eval`) so the eval proves the check.

## References and assets

- `references/rubric-data-figure.md`, `rubric-dashboard.md`: thresholds, checks, vetoes, anchors from the live spec.
- `references/chart-gotchas.md`: the 26 chart/tile probes and what fooled the critic, as eye checks.
- `assets/bar-chart.template.svg`: sorted zero-based bars, axis labels with units, direct values, highlight key.
- `assets/dashboard-tile.template.svg`: number > title > note, sparkline with reference and span caption.
- `assets/edits-example.json`: the two-round trajectory-chart script (axis labels, finding title, legend spacing, series recolour).
