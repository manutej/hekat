# FigTree icon family: design notes

Twelve monoline icons for the FigTree showcase, drawn on the family grid (24x24, stroke-width 2,
`stroke=currentColor`, `fill=none`, round caps and joins, at most 12 strokes, 2px safe margin, no
text, no fills, no gradients, no transforms). Round 1 was the Claude draughtsman run through the
icon-smith loop (`python -m figtree icon ... --backend claude`); round 2 was a hand edit of the
inner markup after a cold read of the rendered sheet at 16/24/48/96 px on light and dark, then a
re-score with the icon rubric. Scores are the icon rubric overall (1-10); acceptance is >= 9.5.

| Icon | Score | Rounds | What changed per round |
|---|---|---|---|
| grounder | 10.0 | 2 | R1: document, magnifier and two 1-1.5px "text" stubs. R2: dropped the stubs, which were sub-pixel noise at 16px; document + magnifier only. |
| decompose | 10.0 | 1 | R1 accepted: one node over three, joined by a stem and a rounded bus. |
| draw-leaf | 10.0 | 2 | R1: the "pencil" was a five-point polygon that read as a kite/arrow. R2: library-style pencil (body + ferrule band) at the lower right, square shrunk to 10x10 so the two never touch. |
| merge | 10.0 | 2 | R1: 5-6px boxes with the arrowhead colliding with the target box; a blob at 16px. R2: two rounded boxes, a bracket, a short arrow with 1.5px of clearance, one larger target box. |
| render | 10.0 | 1 | R1 accepted: frame, sun, mountain polyline. |
| critic | 10.0 | 2 | R1: the eye was a 9px-tall slit under the code brackets. R2: eye opened to 11px with a larger pupil; brackets rewritten as polylines (the rubric's bbox misreads multi-segment relative `l` paths as 29% coverage). |
| repair | 10.0 | 2 | R1: the wrench was a circle with a notch on a stick. R2: the library wrench scaled to 0.75 and set diagonally above a 5x5 square. |
| residual | 10.0 | 1 | R1 accepted: warning triangle with exclamation on a stem (a sign/flag). |
| sheaf | 10.0 | 1 | R1 accepted: three stacked layers (matches the library `layers`). |
| ports | 10.0 | 1 | R1 accepted: square outline broken at the midpoints by four circles. |
| edit-script | 10.0 | 2 | R1: two list lines were drawn through the pencil, a muddle at 16px. R2: three left-aligned list lines of decreasing length, pencil at the lower right, no overlap. |
| trajectory | 10.0 | 1 | R1 accepted: three dots on a rising line. |

Open items: none below 9.5. `residual` reads as a road sign more than a flag; `merge` has the
least clearance of the set (arrowhead to box) and is the first to soften at 16px.

## What the loop caught that the first draft missed

The measurable critic scored every round-1 icon 10.0, so the defects that mattered were only
visible in the image space: sub-pixel text stubs (grounder), a pencil that was not a pencil
(draw-leaf), a wrench that was a notched circle (repair), and strokes colliding at 16px (merge,
edit-script, critic's slit eye). Rendering the sheet at 16px beside 96px was the step that
exposed them, which is exactly the dual-space review the critic prescribes but cannot yet do
without a VLM. One rubric defect surfaced in the other direction: the coverage check under-reads
multi-segment relative path commands, so the critic icon had to be rewritten with polylines to
score what it already drew.
