# Layout rules for FigTree diagrams

What the generator (`figtree/generator.py`, `figtree/worker.py`) enforces and what a hand-drawn
figure must reproduce to score and edit the same way. Numbers are the code's defaults.

## Grid and canvas

- Every coordinate is ceil-snapped to the 8 px grid (`GlobalStyle.grid = 8`); block heights come
  out at 32 px because the grid forces it, widths at 64-112 px for paper labels.
- Padding: 24 px (paper), 32 px (teaching), 40 px (slide). The critic's blank-band limit is
  `max(margin + 8, max_margin_ratio x side)`: 12 % of the side for paper/teaching, 15 % slide.
- Free canvases (paper, teaching) are shrunk to content + margin by the auto-fix `set_canvas`;
  fixed canvases (slide 16:9, dashboard tile, icon) keep their size and get `center_content`.
- The aspect check only applies when the longer side is >= 480 px; a small figure takes the
  aspect its content dictates.

## Column layout, rows and ordering

- Leaves are placed in columns left-to-right in flow order; parallel siblings stack vertically
  in one column.
- Barycenter ordering: each column is sorted by the mean index of its sources in the previous
  column (`Worker._barycenter`), so sibling arrows stop crossing.
- Row wrapping (root node only): when there are >= 4 columns and total width / tallest column
  exceeds `--max-aspect` (default 3.0; the showcase used 2.2-2.4), the column sequence is split
  into contiguous rows by dynamic programming that minimises the widest row. Rows are separated
  by `row_gap` (48 paper, 64 teaching, 80 slide).
- Gaps between columns: `gap_h` 24/40/56; between stacked siblings: `gap_v` 16/24/32.

## Ports

Each block exports four ports, written as comments so any level of the tree can re-extract them
from the code alone:

```
<!-- PORT:left   x=80  y=64 id=n6.left   type=input  component="Grounder" -->
<!-- PORT:right  x=176 y=64 id=n6.right  type=output component="Grounder" -->
<!-- PORT:top    x=128 y=48 id=n6.top    type=input  component="Grounder" -->
<!-- PORT:bottom x=128 y=80 id=n6.bottom type=output component="Grounder" -->
```

Left/top are inputs, right/bottom outputs. A second arrow into an already-used port enters from
another side. Port ids are prefixed with the node id on collision.

## Routing

Children draw only their internal connections; the lowest common ancestor owns a cross-boundary
connection and routes it between exported ports. Candidates are tried in order and the first
that hits no block and keeps the final segment >= `min_arrow` wins:

1. Direct route: straight line, or a Z-route (4 points). Each arrow between the same pair of
   columns gets its own vertical lane.
2. Gap bus: exit right into the inter-column gap, run along a horizontal bus, enter the target
   from the left through the lane just right of the column preceding it (so the spacing pass
   lengthens the final segment instead of moving the lane).
3. Gap bus entering the target from its top/bottom port.
4. Bracket: top/bottom exit and entry (over-the-top or under-the-bottom).

Cross-row arrows exit right, travel along the row gap (each in its own 8 px lane), and re-enter
from the left. Feedback edges are dashed (`stroke-dasharray="4 2"`, `data-flow="control"`) and
loop under or over only the blocks they span.

`flow.through_block` tests segments against block boxes inflated by `Rubric.flow_halo` (4 px)
and spares only the blocks an arrow connects, so an arrow drawn along a border or exiting
through its own source counts; `flow.collinear_overlap` flags two arrows sharing a shaft.

Diagonals are refused unless the path carries `data-diagonal="semantic"` (a fan-in across empty
canvas, for example); the critic flags every other diagonal (`flow.diagonal`).

## Minimum arrow shaft (the 20 px rule)

Every marker-ended arrow keeps a final segment of at least `min_arrow` (20 paper, 24 teaching,
28 slide). The spacing pass finds short shafts, shifts the target child and all downstream
children by `ceil_to_grid(min_arrow - dist)` along the terminal direction, recomputes ports and
reroutes; it terminates within 5 iterations or records a residual. By hand: move the target,
never clip the shaft, never move the arrowhead onto the block border.

Arrowheads are `<marker id="figtree-arrow" markerUnits="userSpaceOnUse">` triangles: 5 x 3.5
(paper), 8 x 6 (teaching), 10 x 7 (slide), `refX` at the tip so the head ends on the port.

## Containers

Stage groups are boxed only when the container title says more than the list of its blocks;
`--no-containers` turns boxing off (the teaching preset does not box). Container rects carry
`data-role="container"`; an empty one is deleted mechanically (`topology.empty_container`).
Paper containers: `#F5F5F5` fill, `#333333` dashed `4 2` border, rx 4. Teaching: `#F8F9FB`
fill, `#D5DBE4` solid border, rx 10.

## Element kinds (`--shapes`, `figtree/elements.py`)

`block` (rect), `store` (cylinder), `document` (folded corner), `decision` (diamond),
`terminal` (pill), `actor` (head and shoulders, label below), `process` (double side bars).
Each is one `<path data-role="block" data-bbox="x y w h">` so ports, critic and rubric treat it
as a rectangle of the same bbox. Keyword mapping: database/store/memory/cache -> store;
document/paper/spec/report -> document; decision/check/gate/branch -> decision; user/human/
reader/reviewer -> actor; input/output/start/end -> terminal. Text insets: decision 16/16,
terminal 8/8, document 4/12, process 8/8.

## Icons inside blocks (`--icons`, `figtree/icons.py`)

A `<use href="#icon-name" width="16" height="16">` at the left of the block, label from x+32;
the symbol is defined once in `<defs>` (24 grid, stroke 2, `currentColor`). Role keywords pick
the icon: grounder/search -> search, critic/review/judge -> eye, worker/repair/merge -> wrench,
render/image -> image, tree/decompose -> tree, memory/store -> database, loop/iterate -> loop,
user -> user, chart/metric -> chart, parallel/fan -> split, input/source/document -> document,
encoder/model/layer -> layers, attention -> grid, classif/output/check -> check,
embed/generator/process -> gear.

## Presets (`figtree/styles.py`)

| | paper | teaching | slide |
|---|---|---|---|
| font | Times New Roman | IBM Plex Sans, Helvetica Neue, Arial | same as teaching |
| label / annotation size | 11-13 / 9-11 pt | 14-16 / 11-13 pt | 18-20 / 13-15 pt |
| palette | attention #F4A460, processing #7BA3C9, residual #FFF3CD, input #D5D5D5, container #F5F5F5, border #333333 | attention #F3C9A4, processing #C9DCF0, residual #F6EFD2, input #E6E8EC, container #F8F9FB, border #2B3A4A | same as teaching |
| strokes main / border | 1.2 / 1.4 | 1.4 / 1.0 | 1.6 / 1.2 |
| min arrow, padding | 20, 24 | 24, 32 | 28, 40 |
| gaps h / v / row | 24 / 16 / 48 | 40 / 24 / 64 | 56 / 32 / 80 |
| block rx, marker | 4, 5x3.5 | 6, 8x6 | 8, 10x7 |
| label / title colour | #333333 / #333333 | #1C2630 / #5B6B7C | #1C2630 / #5B6B7C |

Style invariants (palette, font, strokes, grid, min arrow, padding) are conserved quantities:
every Merge checks the children's style restricts to the parent's, and
`SheafGraph.conserved()` reports it. A hand edit that introduces a second font or stroke width
breaks the invariant and the critic says so (`polish.font_families`, `polish.stroke_widths`).

## Resource bounds

Max 32 nodes, depth 8, 3 critic rounds per node, 2 schema retries per agent (`figtree.Limits`).
The node cap forces Draw on the remaining nodes; a forced multi-component leaf is drawn as one
block and recorded as a residual.
