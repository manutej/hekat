# FigTree Figure Generator Skill

Generate an editable SVG methodology figure from a paper, a skill.md or any methodology
document, following the FigTree recursive construction (Grounder → recursive Generator tree →
Worker Merge → dual-space Critic loop).

## When to use
- A HEKAT query or RMP refine step needs a figure of a workflow, pipeline or agent topology.
- A document must be visualised without inventing structure: only explicit components and flows
  are drawn; everything else is logged as a residual.

## Commands
```bash
python -m figtree SOURCE.md -o figure.svg --tree tree.json --report report.json
python -m figtree SOURCE.md -o figure.svg --edit "arrow:A>B"       # editability proof edit
python -m figtree SOURCE.md -o figure.svg --backend claude          # Claude Grounder + Critic
```

## Iterative refinement of any figure (teaching diagrams, charts, slides, tiles, icons)
```bash
python -m figtree score  FIG.svg --rubric slide                 # 1-10 per dimension + anchored issues
python -m figtree refine FIG.svg --rubric data-figure -o out.svg --trajectory t.json [--edits edits.json]
```
Rubrics: `methodology`, `teaching`, `slide`, `data-figure`, `dashboard`, `icon`. Mechanical
defects are fixed automatically round by round; content decisions come back as anchored edit
requests. Answer them with an edit script (one list per round):
```json
[[{"op": "set_text", "id": "e2-text", "text": "Collect"},
  {"op": "insert", "parent_id": "", "svg": "<text x=\"270\" y=\"290\" font-size=\"12\" data-role=\"axis-label\">Configuration</text>"}]]
```
Python: `from figtree.refine import Refiner; Refiner("teaching").run(svg, requests)`.

## Refine-step contract (recursive-meta-prompting integration)
```python
from figtree.integrations import refine_step
out = refine_step(source_text)   # {"svg", "residual_defects", "layout_tree", "editability", "content_plan"}
```
Treat `residual_defects` as the review report of the step; a step converges when no critical
residual remains for two successive iterations and `editability["passed"]` is true.

## Constraints the output always satisfies
8 px grid, flat palette fills, right-angle routing, 20 px minimum arrow shafts, Times New Roman
11-13 pt labels, 24 px padding, white background first, ports as `<!-- PORT:side x= y= -->`
comments, style invariants conserved across the tree.

Full documentation: `docs/FIGTREE.md`. Tests: `tests/test_figtree.py`.
