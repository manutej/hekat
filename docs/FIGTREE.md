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

`tests/test_figtree.py` (generator) and `tests/test_figtree_refine.py` (refinement loop) are organised as the eight adversarial review agents (Faithfulness,
Hallucination, Editability, Termination, Prompt Completeness, Integration, Style/Constraint,
Failure Mode) plus the protocol itself. Current results on the bundled examples:

| Source | Nodes | Components | Flows | Residuals | Edit proof |
|---|---|---|---|---|---|
| `examples/figtree/figtree-spec.md` (self-application) | 14 | 9 | 9 | 0 | pass, diff = 1 (dashed Critic → Generator arrow, spacing flagged) |
| `examples/figtree/rmp-skill.md` (skill workflow) | 8 | 6 | 6 | 0 | pass, diff = 1 |
| `examples/figtree/transformer-method.md` | 10 | 7 | 8 | 0 | pass, diff = 1 |
| `examples/figtree/adversarial.md` (contradictory flows + injected instruction) | 4 | 3 | 1 | 2 warnings, 0 invented | pass, diff = 1 |

Rendered outputs live in `examples/figtree/output/`. The self-application figure depicts
Grounder → recursive tree → Critic and the render → Critic → Worker → re-validate → render loop.

Faithfulness metric: every component and flow carries an `evidence_span` that is a verbatim
substring of the source (`figtree.grounder.check_faithfulness`). Fenced code blocks are not
treated as methodology, so the repository's TypeScript reference skills yield an empty plan with
a "no components grounded" residual rather than an invented pipeline.

## Iterative refinement for teaching material (figures, data charts, slides, tiles, icons)

The paper's iterative-editing evaluation (Section 4.4: a defective figure, an edit request per
round, a quality score per round) is available as a tool for any SVG, not only generated
methodology figures.  It is the loop you run on diagrams and data figures built for teaching
materials, dashboards, presentations and icon sets:

```
round 0:  normalise ids  ->  render  ->  score against the rubric
round r:  edits = mechanical fixes from the critic + external edit requests for this round
          apply (local, anchored)  ->  render  ->  score  ->  trajectory point
stop:     nothing left to apply, score plateau, or round budget
```

```bash
python -m figtree score  figure.svg --rubric slide                                  # where does it stand?
python -m figtree refine figure.svg --rubric data-figure -o out.svg --trajectory t.json
python -m figtree refine figure.svg --rubric slide --edits edits.json               # with your decisions
```

| Module | Role |
|---|---|
| `figtree/program.py` | makes any SVG an addressable program: stable ids for every element, inherited typography and colour resolved, absolute bounding boxes (rotated text included) |
| `figtree/rubrics.py` | profiles `methodology`, `teaching`, `slide`, `data-figure`, `dashboard`, `icon`: the paper's eight diagnostic dimensions with medium-specific thresholds (minimum font, contrast, palette size, words per label, aspect, margins, stroke widths, fixed canvas) |
| `figtree/quality.py` | `QualityCritic`: measurable signals per dimension, 1-10 scores with the paper's anchors (a critical defect caps a dimension at 5), every issue anchored to an element id with a fix instruction and, when mechanical, an `auto_edit` |
| `figtree/edits.py` | edit scripts: `set_attr`, `set_text`, `translate`, `recolor`, `delete`, `insert`, `scale_font`, `set_canvas`, `center_content`; applied in place, failures reported, never regenerated |
| `figtree/refine.py` | `Refiner`: the loop, the score trajectory, and the list of requests that still need a content decision |

Mechanical fixes (font below the medium minimum, low contrast, gradient or neon fill, filter,
oversized corner radius, stroke-width or font-family unification, square icon canvas, canvas
shrink or content centring) are applied automatically. Everything that changes meaning (a
missing axis label, a ten-word label on a slide, text in an icon, a crossing that needs a
re-ordering) is handed back as an edit request with its anchor, so a person or a VLM decides.
`ClaudeEditor` is the hook for turning a prose request into an edit script when credentials
exist; `--edits` takes one script per round from a file.

Results on the bundled teaching examples (`examples/figtree/teaching/`, before/after PNGs and
trajectories in `teaching/output/`):

| Figure | Rubric | Score before -> after | Mechanical fixes | Requests left |
|---|---|---|---|---|
| `bar-chart.svg` (8px ticks, grey title, gradient and neon bars, two fonts, no axis labels) | data-figure | 7.24 -> 9.86 | 13, plus the axis labels and title from `bar-chart.edits.json` | stroke widths |
| `slide-pipeline.svg` (12px labels, grey text, ten-word label) | slide | 7.50 -> 9.67 | fonts to 18px, contrast, content centred; the label shortened by `slide-pipeline.edits.json` | enlarge the content to fill the 16:9 canvas |
| `process-icon.svg` (non-square, three stroke widths, text) | icon | 8.58 -> 8.83 | square canvas, one stroke width | remove the text |
| generated self-application figure | teaching | 8.71 -> 10.0 | labels to 14px | none |

The generator itself was improved alongside: wide pipelines fold into rows (`--max-aspect`,
default 3.0) instead of producing banners, feedback edges loop under or over only the blocks
they span, and containers are titled only when the title says more than the list of blocks.

## Elements, icons and motion

* **Element kinds** (`figtree/elements.py`, `--shapes`): stores are cylinders, documents have a
  folded corner, decisions are diamonds, start/end states are pills, people are actors. Each is
  one `<path data-role="block" data-bbox=…>`, so ports, critic and rubric treat it like a block.
* **Icons** (`figtree/icons.py`, `--icons`): a monoline family on a 24-grid (stroke 2,
  `currentColor`, round joins) emitted as `<symbol>` definitions and placed with `<use>` inside
  blocks by role (grounder → search, critic → eye, worker → wrench, render → image, …).
* **Animation** (`figtree/animate.py`, `figtree animate`): three motions, each tied to meaning:
  *reveal* builds the figure in reading order (the way the recursion builds it), *draw* grows
  each connector before its arrowhead appears (a marker-less shaft copy draws first, so no
  standalone triangles), *pulse* sends a token along every data flow, slower and dimmer on
  dashed control edges. Delays are derived from the program, so the timeline is deterministic;
  `prefers-reduced-motion` shows the final state. Frames can be checked with headless Chromium's
  `--virtual-time-budget`.
* **Icon smith** (`figtree/iconsmith.py`, `figtree icon "name: concept | metaphor"`): the same
  loop applied to icon design. A draughtsman (rule-based composition, or Claude) proposes the
  inner SVG; the icon rubric plus family rules (safe margin, stroke count, coverage, one stroke
  width, no fills, no text) score it; mechanical fixes apply; accepted icons join the library.

## Backends

* **rule** (default, offline): deterministic Grounder (arrow chains, named roles, numbered
  workflow steps, inputs/outputs), deterministic Generator/Worker, structural Critic.
* **claude**: `ClaudeGrounder`, `ClaudeCritic`, `ClaudeEditor` (prose request → edit script)
  and `ClaudeDraughtsman` (icon brief → inner SVG) in `figtree/agents/llm.py` use the spec's
  prompts (`figtree/prompts.py`) with JSON-schema structured outputs and the 2-retry rule.
  Credentials are resolved by `default_backend()`:
  1. the Anthropic SDK when `ANTHROPIC_API_KEY` / `ANTHROPIC_AUTH_TOKEN` is set (the critic
     then also receives the rendered PNG);
  2. otherwise the **Claude Code CLI** (`figtree/agents/claude_code.py`): `claude -p` with
     `--json-schema`, no tools, no session persistence, running on the OAuth login of the
     Claude Code session itself. No key to manage; a structured call costs about a cent.
  Generator and Worker stay deterministic so the code view is reproducible. The Claude critic
  reviews internal (merged) nodes by default (`scope="internal"`, `max_calls=12`); leaves are
  fully covered by the structural rules.

## Integration contracts (spec section 8)

* `figtree.integrations.refine_step(source_text)` exposes the generator as a recursive refine
  step for the recursive-meta-prompting skill (see `.claude/skills/figtree/skill.md`).
* Nodes are stored as sheaf stalks with residual sections (`result.layout_tree.to_dict()`).
* `figtree.integrations.to_work_graph(result)` emits nodes/edges JSON for a Notion Work Graph,
  p5js or an editorial dashboard; the SVG itself is plain, id-addressable SVG 1.1.

## Showcase and worker rounds

`examples/figtree/showcase/build_showcase.py` assembles every result into one page
(`showcase.html`): the loop figure generated from `examples/figtree/loop.md`, the three
methodology figures with icons and shapes, the Claude-grounded variant, five refinement
before/after pairs with their score trajectories, the icon family sheet, the animated figure,
the meta-prompt skeleton and the rules the loop learned. Every figure is inlined as editable
SVG with namespaced ids. The full animated explainer with scrubber and captions is
`examples/figtree/animated/index.html`.

Three worker agents ran iterative rounds on their own areas and left notes:
`examples/figtree/icons/NOTES.md` (icon family), `examples/figtree/animated/NOTES.md`
(explainer: headless virtual time starved by a rAF loop, caption pacing, dark-theme legend),
`examples/figtree/teaching/NOTES-dashboard-chart.md` (dashboard tiles and trajectory chart:
mechanical fixes that create overflow, gradient contrast, neon strokes, prominent-text titles).

Findings from the Claude-grounded run (`examples/figtree/claude/`): the model finds components
the rules cannot (SourceText, Rollback, FinalSVG, resource bounds) but returns a sparser flow
graph and conditional edges, which the deterministic layout draws less cleanly than a dense
pipeline; its global style is not adopted by default; its critic findings are advisory (anchor
`model:`) and never trigger the structural re-decompose rule; it reads up to 16000 characters
of source rather than the specification's 5000, because a truncated root figure made it report
the truncation as a defect.

## Evaluating the evaluators

* `examples/figtree/rubrics/<rubric>.json` (`figtree eval --specs DIR`): the machine-readable
  rubric specs: eight dimensions with 1-10 anchors and judge questions, every check with its id,
  signal, severity and whether a mechanical fix exists, the veto rules after PaperBananaBench,
  and the scoring formula. Critic issues carry a `check_id`.
* `figtree eval [--rubric R] [--probes DIR] [--report out.json]`: runs seed probes
  (`figtree/probes.py`) plus adversarial probes (`examples/figtree/probes/<rubric>/<id>.svg` +
  `.json`) and reports recall and precision per check, failing probes, and checks without a probe.
  Gaming probes (bad figures that pass every measurable check) are recorded, not failed: they are
  the judge's job.
* `figtree judge FILE --rubric R [--source TEXT]`: the paper's fine-grained diagnostic evaluator
  reading the rendered PNG through the Claude Code CLI's Read tool on the session's own login;
  scores, justification and tags per dimension, veto rules applied.
  `figtree judge --calibrate set.json --report out.json` compares judged and measured scores
  over a set and lists blind spots (measured ≥ 9, judged ≤ 6) and rules to reconsider
  (measured ≤ 6, judged ≥ 9).
* Adversaries (worker agents) write probes against each rubric; their tables live in
  `examples/figtree/probes/ADVERSARY-*.md`, and the resulting rule changes are recorded in the
  showcase.

## Digest: a body of work at once

* `figtree digest --plan DOCS… -o OUT [--rubric R]` scans markdown/text files (a directory
  recursively) and splits each into *units*: H1/H2 sections that ground to ≥ 3 components
  (arrow chains, named roles, numbered steps, as `RuleBasedGrounder` sees them), or the whole
  file when it is small. `OUT/manifest.json` lists `units[{id, source, title, span, chars,
  est_components}]` and `skipped[{…, reason}]`.
* `figtree digest --unit ID -o OUT` generates that unit (`OUT/ID.svg`, `ID.report.json`), scores
  it with the rubric (`ID.score.json`) and prints one JSON line; teaching/slide rubrics use their
  style preset, the others the paper preset. `--all` does every unit and writes `OUT/index.html`
  (title, score badge, inline SVG per unit) plus `digest.json`.
* The Claude Code workflow scripts under `.claude/workflows/` (`figtree-digest`, `-refine`,
  `-adversary`, `-judge-panel`, `-icon-family`) fan these commands out over small-context
  subagents that hand back JSON verdicts only; see `docs/workflows/README.md`.

## Known limitations

* The rule-based Grounder only admits explicit structure (arrow chains, "X Agent" names,
  numbered steps under a workflow heading). Prose-only method descriptions need the Claude
  backend.
* Layout is left-to-right column layout with vertical stacking of parallel siblings; the
  paper's content-adaptive subregions are approximated by the spacing pass and detour buses.
* Text widths are estimated (0.5 em per character); the image critic catches real overflow only
  when a renderer is available.

## The FigureProgram contract (generative UI)

`python -m figtree contract export FIG.svg -o prog.json` lifts any FigTree SVG into a design-free
program (`design/contract/figure-program.schema.json`: canvas, containers, nodes with kind/tone/icon,
flows with type and polyline, ports, caption, residuals); `contract validate` checks it;
`contract render prog.json -o out.svg [--preset paper|teaching|slide]` draws it through the
reference `HouseRenderer`. Swapping the design means implementing another `Renderer`
(`figtree/contract.py`) or `DesignAdapter` (`design/figtree-ds/src/contract.ts`); ids survive, so
the critic and the edit scripts keep working. See `design/contract/README.md`.
