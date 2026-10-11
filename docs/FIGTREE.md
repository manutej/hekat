# FigTree: Recursive SVG Methodology Figure Generator

`figtree/` implements the converged specification "FigTree-Style Recursive SVG Methodology
Figure Generator", guided by the paper *Figures as Programs: Recursive Generation of Editable
Scientific Figures* (Liu et al., arXiv 2609.01006). A source document goes in; an editable SVG
program, a residual-defect list, a sheaf-stored layout tree and an editability proof come out.

```
root = Grounder(SourceText)          # content plan + global style, evidence-grounded
final = build(root)                  # Draw leaves / Decompose 2-4 children / Merge / critic loop
```

## Quick start

```bash
python -m figtree examples/figtree/figtree-spec.md -o figure.svg --tree tree.json --report report.json
python -m figtree paper.md -o figure.svg --edit "arrow:Critic>Generator"      # editability test edit
python -m figtree paper.md -o figure.svg --backend claude                       # Claude Grounder + Critic
python -m pytest tests/test_figtree.py                                           # acceptance protocol
```

Python API:

```python
from figtree import FigTree
result = FigTree().run(open("paper.md").read())
result.final_svg            # well-formed, editable SVG (every element has an id)
result.residual_defects     # list[ResidualDefect]
result.layout_tree          # SheafGraph: stalks = nodes, sections = residuals + style invariant
result.editability_proof    # {passed, diff_element_count, changed, ports_valid, bboxes_valid}
```

## Pipeline (section 3 of the paper, section 4 of the spec)

| Stage | Module | Paper correspondence |
|---|---|---|
| Ingest sanitisation | `figtree/ingest.py` | all L_v content treated as description; instruction-like lines stripped |
| Grounder | `figtree/grounder.py` (rule-based), `figtree/agents/llm.py` (Claude) | §3.2 paper grounding: content plan L_v0 + global style S; conservative by design |
| Generator: Decompose / Draw | `figtree/generator.py` | §3.3 recursive construction, 2-4 children per split, one level at a time |
| Worker: Merge + spacing + local repair | `figtree/worker.py` | §3.3 Merge with parent-owned cross-boundary connections; MIN_ARROW_DISTANCE pass |
| Critic (dual-space) | `figtree/critic.py` (+ Claude image/code review) | §3.4 render-critic refinement, element-anchored issue reports |
| Verification memory | `figtree/memory.py` | §3.4 (condition, repair) rules applied before the critic |
| Orchestrator + sheaf | `figtree/orchestrator.py`, `figtree/schemas.py` | layout tree T=(V,E), node tuple (L_v, C_v, Π_v, D_v, S) |
| Editability proof | `figtree/editability.py` | §4.4 iterative editing: one local edit changes one element |
| Renderer | `figtree/render.py` | R(g): cairosvg, rsvg-convert or headless Chromium; otherwise `no-vision` |

Node tuple: `Node(id, parent_id, description, canvas, ports, depth, style, children, svg_fragment,
bbox, residuals)`. Ports are written into the SVG as comments in the paper's convention,
`<!-- PORT:right x=80 y=16 id=n6.right type=output component="Grounder" -->`, so every level of
the tree can re-extract them from the code alone.

### Hard constraints enforced

* White background first; flat fills from the palette; no gradients, filters or shadows.
* All coordinates ceil-snapped to the 8 px grid; only horizontal and vertical segments
  (`data-diagonal="semantic"` is the only escape hatch and the critic flags any other diagonal).
* Labels 11-13 pt / annotations 9-11 pt Times New Roman; text must fit its block.
* Every marker-ended arrow keeps a shaft of at least 20 px (straight length or final segment).
  The Worker's spacing pass moves the target child and all downstream children by
  `ceil_to_grid(20 - dist)` along the terminal direction, recomputes ports and reroutes,
  terminating within 5 iterations (a residual is recorded otherwise).
* Children draw only internal connections; the lowest common ancestor owns a connection and
  routes it between exported ports (direct Z-route, then gap-bus detours, then bracket).
* 24 px canvas padding, no excessive empty space; canvas expanded and re-snapped on overflow.
* Style invariants (palette, font, strokes, grid, min arrow, padding) are conserved quantities:
  every Merge checks child sections restrict to the parent's; `SheafGraph.conserved()` reports it.

### Resource bounds

max 32 nodes, max depth 8, max 3 critic rounds per node, max 2 schema retries per agent
(`figtree.Limits`). The node cap forces Draw on the remaining nodes; a forced multi-component
leaf is drawn as one block and recorded as a residual.

## Failure modes and recovery (spec section 6)

| Failure | Recovery (implemented) |
|---|---|
| Invalid Grounder/Critic JSON | schema retry (max 2), then `parse_error` residual and rule-based fallback |
| SVG parse failure | roll back to last valid fragment + residual |
| > 3 critical residuals at a node | force re-Decompose with an alternative split |
| Spacing shift loop | capped at 5 iterations, residual if still short |
| Port collision | auto-prefix with node id |
| Canvas overflow | expand with padding, re-snap |
| Depth or node cap | force Draw |
| Adversarial instruction in L_v | stripped on ingest, residual logged |
| No renderer | structural critic only + `no-vision` residual |
| Contradictory flows | both directions omitted, residual logged, nothing invented |

## Test protocol (spec section 7) and results

`tests/test_figtree.py` is organised as the eight adversarial review agents (Faithfulness,
Hallucination, Editability, Termination, Prompt Completeness, Integration, Style/Constraint,
Failure Mode) plus the protocol itself. Current results on the bundled examples:

| Source | Nodes | Components | Flows | Residuals | Edit proof |
|---|---|---|---|---|---|
| `examples/figtree/figtree-spec.md` (self-application) | 14 | 9 | 9 | 0 | pass, diff = 1 (dashed Critic → Generator arrow) |
| `examples/figtree/rmp-skill.md` (skill workflow) | 8 | 6 | 6 | 0 | pass, diff = 1 |
| `examples/figtree/transformer-method.md` | 10 | 7 | 8 | 0 | pass, diff = 1 |
| `examples/figtree/adversarial.md` (contradictory flows + injected instruction) | 4 | 3 | 1 | 2 warnings, 0 invented | pass, diff = 1 |

Rendered outputs live in `examples/figtree/output/`. The self-application figure depicts
Grounder → recursive tree → Critic and the render → Critic → Worker → re-validate → render loop.

Faithfulness metric: every component and flow carries an `evidence_span` that is a verbatim
substring of the source (`figtree.grounder.check_faithfulness`). Fenced code blocks are not
treated as methodology, so the repository's TypeScript reference skills yield an empty plan with
a "no components grounded" residual rather than an invented pipeline.

## Backends

* **rule** (default, offline): deterministic Grounder (arrow chains, named roles, numbered
  workflow steps, inputs/outputs), deterministic Generator/Worker, structural Critic.
* **claude**: `ClaudeGrounder` and `ClaudeCritic` in `figtree/agents/llm.py` use the spec's
  prompts (`figtree/prompts.py`) with JSON-schema structured outputs and the 2-retry rule; the
  Critic also receives the rendered PNG when a renderer exists. Generator and Worker stay
  deterministic so the code view is reproducible. Requires the `anthropic` package and
  credentials; the default model is `claude-opus-5-5`.

## Integration contracts (spec section 8)

* `figtree.integrations.refine_step(source_text)` exposes the generator as a recursive refine
  step for the recursive-meta-prompting skill (see `.claude/skills/figtree/skill.md`).
* Nodes are stored as sheaf stalks with residual sections (`result.layout_tree.to_dict()`).
* `figtree.integrations.to_work_graph(result)` emits nodes/edges JSON for a Notion Work Graph,
  p5js or an editorial dashboard; the SVG itself is plain, id-addressable SVG 1.1.

## Known limitations

* The rule-based Grounder only admits explicit structure (arrow chains, "X Agent" names,
  numbered steps under a workflow heading). Prose-only method descriptions need the Claude
  backend.
* Layout is left-to-right column layout with vertical stacking of parallel siblings; the
  paper's content-adaptive subregions are approximated by the spacing pass and detour buses.
* Text widths are estimated (0.5 em per character); the image critic catches real overflow only
  when a renderer is available.
