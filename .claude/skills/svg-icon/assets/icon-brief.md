# Icon brief (one per icon; a family is a list of these)

Family: FigTree monoline. `viewBox 0 0 24 24`, `stroke-width 2`, `stroke currentColor`,
`fill none`, round caps and joins, at most 12 strokes, all ink inside 2..22, no text, no
markers, no transforms, must read at 16 px, consistent with the library in `figtree/icons.py`
(document, search, tree, eye, wrench, image, database, gear, user, chart, loop, split, merge,
check, layers, grid, arrow-right, bolt, text, palette, grounder, decompose, draw-leaf, render,
critic, repair, residual, sheaf, ports, edit-script, trajectory).

```
name:        {kebab-case, used as icon-{name}}
concept:     {what it means in one clause, e.g. "find evidence in the source"}
metaphor:    {a literal object or two, e.g. "a document with a magnifier at the lower right"}
sits beside: {library icons it will appear next to; keep chirality and weight consistent}
must not:    {what it must not resemble, e.g. "a balloon on a string; a kite"}
base:        {optional library icon to adapt, e.g. search}
must read at: 16
```

CLI form: `"{name}: {concept} | {metaphor}"`.

## Return (draughtsman or subagent), <= 1 KB

```json
{"name": "grounder", "inner": "<path d=\"M9 21H5V3h8l6 6v1\"/><path d=\"M13 3v6h6\"/><circle cx=\"14.5\" cy=\"15.5\" r=\"3.5\"/><path d=\"M17 18l3.5 3.5\"/>",
 "strokes": 4, "bbox": [5, 3, 20.5, 21.5], "coverage": 0.57,
 "cold_eye_16px": "document and lens read; handle points down-right; no fused strokes",
 "score": 10.0, "family_issues": [], "rounds": 2,
 "changed": ["dropped two 1 px text stubs that were sub-pixel smudge at 16 px"]}
```

Inner markup only (no `<svg>` wrapper), absolute path commands or polylines, no `style`
attributes. If the metaphor cannot be drawn in 12 strokes, return `{"name": ..., "refused":
"<why>", "alternative metaphor": "..."}` instead of a crowded icon.
