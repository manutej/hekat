# Refinement notes: dashboard tiles and trajectory chart

Two teaching-material artifacts that are not diagrams, each hand-drawn with deliberate
defects and then taken through `python -m figtree refine`. Numbers in both come from the four
bundled trajectories in `output/*.trajectory.json` (bar-chart, slide-pipeline, process-icon,
generated self-application figure): 4 figures refined, mean gain
(2.62 + 2.17 + 0.25 + 1.29) / 4 = +1.58 points, 1 + 2 + 2 + 0 = 5 requests still open.

Files: `dashboard-tiles.svg`, `dashboard-tiles.edits.json`, `dashboard-tiles.score-before.txt`,
`dashboard-tiles.score-after.txt`; `trajectory-chart.svg`, `trajectory-chart.edits.json`,
`trajectory-chart.score-before.txt`, `trajectory-chart.score-after.txt`; renders and
trajectories in `output/` (`*.before.png`, `*.after.png`, `*.refined.svg`, `*.trajectory.json`).

---

## 1. `dashboard-tiles.svg` (rubric `dashboard`, 720x200, fixed canvas)

Deliberate defects: 9px labels and notes; pale grey value (#BBBBBB on #F7F7F7, 1.8:1); values in
Georgia, labels in Arial; a blue linear-gradient tile with #333333 text on it; rx=24 on every
tile; tile widths 190 / 300 / 166; two labels of 8 and 10 words.

### Score trajectory

| Round | Overall | Issues (critical) | Edits | What happened |
|---|---|---|---|---|
| 0 | 7.50 | 22 (3) | 0 | baseline: text_quality 1.0, visual_polish 5.5, compactness 8.5 |
| 1 (auto only, no edit script) | 8.65 | 9 (6) | 16 | mechanical fixes alone: fonts to 12px make the long labels overflow their tiles and collide with the neighbouring tile's label, so criticals go up 3 -> 6 while the overall score still rises |
| 1 (with `dashboard-tiles.edits.json`) | 9.75 | 1 (0) | 35 | content decisions + the same 16 mechanical fixes |
| 2 | 9.75 | 1 (0) | 12 | my colour and hierarchy decisions over the critic's defaults |

Final: text_quality 10, visual_polish 10, compactness 8.5, overall 9.75. The one remaining
request is `canvas aspect 3.60 outside the dashboard tile range 0.8-2.0`: a three-tile strip
is a banner by design, so this is a genuine design decision, not a defect.

### Mechanical (critic `auto_edit`) vs requests

Mechanical, applied in round 1 (16 ops): six `set_attr font-size 12` (all 9px texts), three
`recolor` for contrast (the #BBBBBB value and the two #888888 notes), three
`set_attr font-family Arial` (Georgia values), three `set_attr rx 8`, one `recolor` of the
gradient tile to the critic's flat default `#7BA3C9`.

Requests (needed a decision, 9 after the auto-only pass): two "shorten to a keyword label"
(8- and 10-word labels), three "overflows its block", three "labels overlap" (all three
created or worsened by the font raise), and the aspect warning.

### What the edit script decided

Round 1: labels shortened to "Figures refined" / "Mean score gain" / "Open requests"; notes
rewritten as short qualifiers that fit the tile at 12px ("bar, slide, icon, spec",
"points of 10, 4 trajectories", "need a content decision"); the three tiles made equal
(218px each, 17px gutters) by `set_attr x/width` on the rects and `translate` on their
texts; values set bold.
Round 2 (after the critic's defaults had landed): the gradient tile recoloured from the
critic's `#7BA3C9` to the same `#F7F7F7` + `#E0E0E0` border as its neighbours, so the three
tiles form one set; the gain value in green `#1B7F4B` and the open-requests value in rust
`#B5452A` as the only two accents; notes to `#555555` (6.6:1) so they sit a step below the
labels; labels to 13px so the tile title reads above its footnote.

Ordering caveat learned here: the refiner applies the round's external edits first and the
previous report's mechanical fixes after, so a colour or size decision that disagrees with an
auto-fix must go in the following round or it is overwritten (that is why both scripts have two
rounds).

### What the critic missed that the eye caught

- Text on a gradient tile is contrast-checked against the canvas, not the gradient: the
  #333333 label on the `#5B8DEF -> #1C3F8F` gradient is 1.3:1 at the dark end and was reported
  as fine (`parse_color` returns None for `url(#...)`, so the host is skipped). The gradient
  only got fixed because gradients are banned outright. Candidate rule: resolve a gradient
  fill to its darkest and lightest stop and check text against both.
- Uneven tile widths (190 / 300 / 166) and tile borders present on two tiles but not the
  third are invisible to the critic; a tile set should be checked for equal widths, equal
  gutters and identical border/fill treatment.
- Label and note at the same 12px read as the same thing; the rubric has a minimum font but
  no notion of hierarchy (title > number > note) inside a tile.

---

## 2. `trajectory-chart.svg` (rubric `data-figure`, 560x320)

Deliberate defects: no axis labels; 8px tick labels; the icon series drawn in neon `#00FF66`
(line stroke and markers); a legend crammed at 10px pitch so all four entries overlap; a
one-word title ("Scores").

### Score trajectory

| Round | Overall | Issues (critical) | Edits | What happened |
|---|---|---|---|---|
| 0 | 7.59 | 13 (4) | 0 | baseline: semantic_coverage 4.5 (no axis labels), text_quality 1.0 (three legend overlaps), visual_polish 7.6 (neon markers) |
| 1 (auto only, no edit script) | 8.50 | 4 (4) | 9 | ticks to 10px, neon markers and swatch to `#7BA3C9`; the four requests (axis labels, three overlaps) stay |
| 1 (with `trajectory-chart.edits.json`) | 10.00 | 0 (0) | 19 | axis labels inserted, title rewritten, legend spread out + the 9 mechanical fixes |
| 2 | 10.00 | 0 (0) | 22 | series colour and font decisions over the critic's defaults |

An earlier version of round 2 raised the legend to 11px without moving it, which pushed the
longest entry 3px past the right edge; the critic's mechanical answer was `set_canvas` to
578x325, i.e. it silently broke the 560x320 spec. Fixed by translating the legend 14px left in
the same round; the final canvas is 560x320 and the stop reason is "no edits left".

### Mechanical vs requests

Mechanical (9 ops): six tick labels `set_attr font-size 10`; `recolor` of the two neon markers
and the neon legend swatch to `#7BA3C9`.
Requests (4): "axis label(s) with units are missing" and three "labels ... overlap" pairs
for the legend.

### What the edit script decided

Round 1: x axis label "Refinement round (0 = baseline)" and a rotated y axis label
"Overall score (1-10 scale)" inserted with `data-role="axis-label"`; title changed to the
finding, "One refinement round lifts all four scores" (7 words, under the 8-word limit), at
14px; legend entries moved from a 10px pitch to 18px with `translate` (a legend was kept
rather than direct labels because three series end within 13px of each other at round 1).
Round 2: the icon series recoloured to muted green `#55A868` on line, markers and swatch;
tick and legend fonts raised to 11px; legend shifted 14px left so the 11px labels stay inside
the canvas.

### What the critic missed that the eye caught

- Neon is only checked on fills: the `#00FF66` polyline stroke passed untouched while its
  markers were recoloured, so after the auto-only pass the icon line was still neon with
  blue dots on it. Candidate rule: apply the neon/gradient checks to `stroke` on lines, paths
  and polylines, and keep a series' line, markers and legend swatch the same colour.
- The mechanical replacement colour is a fixed `#7BA3C9`, which is nearly the same blue as the
  existing data-figure series (`#4C72B0`): the auto-fix made two of four series
  indistinguishable. Candidate rule: pick the replacement from the palette not yet used in
  the figure, or hand it back as a request when the figure already has a blue.
- "No title stating the finding" never fired for the one-word title "Scores", because any
  text with three or more words (here a legend entry) satisfies the check. Candidate rule:
  evaluate the title check on the topmost centred text, or on `data-role="title"`.

---

## Summary

| Artifact | Rubric | Before | Auto only | After (with edits) | Rounds | Requests left |
|---|---|---|---|---|---|---|
| `dashboard-tiles.svg` | dashboard | 7.50 | 8.65 | 9.75 | 2 | 1 (banner aspect, by design) |
| `trajectory-chart.svg` | data-figure | 7.59 | 8.50 | 10.00 | 2 | 0 |
