---
name: figtree
description: Hub for the FigTree family of SVG-artifact skills. Use this skill whenever someone wants a figure, diagram, chart, dashboard tile, icon set, animated explainer or showcase page built from a document, a dataset, a spec, a skill or a body of work, and wants it scored, critiqued or refined; whenever they say "draw the pipeline", "make a methodology figure", "turn this paper/spec/README into a diagram", "visualise the workflow", "make this chart publication-ready", "score this SVG", "refine this figure", "design icons for these concepts", "animate the figure", "digest these docs into figures", or "assemble the results into a page"; and whenever a subagent must evaluate or repair an SVG without blowing its context. Routes to svg-diagram, svg-data-figure, svg-icon, svg-animation, svg-eval and svg-showcase, and documents the python -m figtree CLI (generate, refine, score, animate, icon, eval, judge, digest).
---

# FigTree: figures as programs

An SVG artifact is a *program whose rendering a reader judges*. Treat it like code under
review: every element has an id, every issue is anchored to an id with a fix, every change is a
local edit script, and quality is a 1-10 score per dimension. Do not regenerate a figure to fix
it; edit the element the critic names. The full category-level procedure is
`docs/META-PROMPT-SVG-ARTIFACTS.md`; the implementation is `figtree/` (`docs/FIGTREE.md`).

## The loop (every medium, every skill in the family)

```
ground      admit only what the source states; log residuals, never invent
construct   recursively: atomic nodes, 2-4 children per split, parent-owned arrows
render      PNG via headless Chromium (or rsvg/cairosvg); "no-vision" otherwise
critique    in TWO spaces: the code (figtree score) and the image (your eyes / figtree judge)
edit        locally, by id, with an edit script; mechanical fixes auto, meaning back as requests
score       1-10 per dimension; a critical defect caps a dimension at 5
repeat      until no edits are left, a 2-round plateau, or the round budget
```

Why two spaces: when the adversaries first ran, every "gaming" probe scored 9.0-10.0
(`examples/figtree/probes/ADVERSARY-*.md`). Most of those holes are checks now (`chart.*`,
`tile.*`, `icon.*`, `motion.*`, a flow halo, sentence labels, outlined glyphs), but a check fires
on the probe it was written for, not on every variant, and meaning, metaphor and the next
adversary's find have no check. The eye checks live in each sibling skill's gotchas; `svg-eval`
is how a finding becomes a check.

## Medium router

| The ask | Rubric | Skill | Start from |
|---|---|---|---|
| methodology figure from a paper, spec or skill.md | `methodology` | `svg-diagram` | `figtree generate SRC.md` |
| teaching diagram, workflow, agent topology, pipeline | `teaching` | `svg-diagram` | `generate --style teaching --icons --shapes` or `assets/figure-skeleton.svg` |
| slide figure (16:9, back-of-room fonts) | `slide` | `svg-diagram` | `generate --style slide` |
| bar/line chart, small multiples, trajectory plot | `data-figure` | `svg-data-figure` | `assets/bar-chart.template.svg` |
| KPI tile, stat strip, sparkline tile | `dashboard` | `svg-data-figure` | `assets/dashboard-tile.template.svg` |
| custom icon or icon family | `icon` | `svg-icon` | `figtree icon "name: concept | metaphor"` |
| animated figure, explainer with captions and scrubber | (figure's rubric) | `svg-animation` | `figtree animate FIG.svg` |
| probes, recall/precision, judge calibration, "is the critic right?" | any | `svg-eval` | `figtree eval`, `figtree judge` |
| Artifact page, design-system handoff, showcase | any | `svg-showcase` | `examples/figtree/showcase/build_showcase.py` |
| a whole directory of docs into many figures | per unit | this hub + `svg-diagram` | `figtree digest --plan DIR -o out/` |

Pick the rubric by *where the figure will live*, not by how it was made. A generated
methodology figure that goes on a slide is scored with `slide`.

## CLI cheat sheet (`python -m figtree ...`)

```bash
# generate an editable figure from text (rule backend offline; claude backend on the session's OAuth)
python -m figtree generate SRC.md -o fig.svg [--style paper|teaching|slide] [--icons] [--shapes] \
    [--max-aspect 2.4] [--no-containers] [--backend claude] [--tree tree.json] [--report report.json]
# score against a rubric (methodology | teaching | slide | data-figure | dashboard | icon)
python -m figtree score FIG.svg --rubric teaching [--source SRC.md] [--json]
# refine: auto-fixes each round + your edit scripts (one list per round) or prose requests
python -m figtree refine FIG.svg --rubric slide -o out.svg --trajectory t.json \
    [--edits edits.json] [--request "shorten the third label"] [--rounds 8] [--no-auto] [--render-dir r/]
# motion: reveal (opacity), draw (shaft copies), pulse (tokens on flows)
python -m figtree animate FIG.svg -o fig.animated.svg [--modes reveal,draw,pulse] [--css fig.css] [--step 0.35]
# icons: brief in, scored family out
python -m figtree icon "grounder: find evidence | document with magnifier" -o icons/ [--backend claude] \
    [--rounds 3] [--sheet icons/sheet.svg] [--report icons/report.json]
# evaluate the evaluators
python -m figtree eval [--rubric R] [--probes examples/figtree/probes] [--report eval.json] [--specs rubrics/]
python -m figtree judge FIG.svg --rubric R [--source SRC.md] [--report j.json]
python -m figtree judge --calibrate set.json --report calibration.json
# digest a body of work into figure units (plan -> unit -> all)
python -m figtree digest --plan DOCS/ -o out/            # out/manifest.json
python -m figtree digest --unit ID -o out/ [--rubric R]  # out/ID.svg + ID.report.json + ID.score.json
python -m figtree digest --all -o out/ [--rubric R]      # every unit, then out/index.html
```

Python entry points: `figtree.refine.Refiner(rubric).run(svg, requests)`,
`figtree.quality.QualityCritic(rubric).review(svg, source)`, `figtree.edits.apply_edits(svg, ops)`,
`figtree.animate.animate_svg(svg)`, `figtree.iconsmith.IconSmith().design(IconSpec(...))`,
`figtree.integrations.refine_step(source_text)`.

## Edit scripts (the only way to change a figure)

```json
[[{"op": "set_text", "id": "e2-text", "text": "Collect"},
  {"op": "set_attr", "id": "e2-text", "attr": "font-size", "value": "18"},
  {"op": "translate", "id": "legend", "dx": -14, "dy": 0},
  {"op": "recolor", "id": "series-icon", "stroke": "#55A868"},
  {"op": "delete", "id": "stray-rect"},
  {"op": "insert", "parent_id": "", "svg": "<text id=\"axis-y\" x=\"18\" y=\"150\" font-size=\"12\" data-role=\"axis-label\" transform=\"rotate(-90 18 150)\">Accuracy (%)</text>"},
  {"op": "scale_font", "min": 14}, {"op": "set_canvas", "width": 960, "height": 540}, {"op": "center_content"}]]
```

Outer list = rounds; inner list = ops for that round. `parent_id: ""` inserts under the root.
Ops address existing ids only; ids are stable across rounds (`refine` normalises missing ids in
round 0 and reports them). The refiner applies your ops first and the previous report's auto-fixes
after, so a decision that contradicts an auto-fix (a colour, a size) goes in the *next* round.

## Context-saving rule for subagents

A scoring or repair subagent gets **one command and one file in, and returns at most 2 KB of
JSON out**. Never paste an SVG into a prompt or a return value. The brief template is
`.claude/skills/svg-diagram/assets/worker-brief.md`; the trimmed return shape is:

```bash
python -m figtree score FIG.svg --rubric R --json | python3 -c '
import json,sys; r=json.load(sys.stdin)
print(json.dumps({"overall": r["overall"], "scores": r["scores"], "issues": [
  {"check": i.get("check_id"), "sev": i["severity"], "anchor": i["code_anchor"], "fix": i["fix_instruction"][:80]}
  for i in r["issues"][:8]], "n_issues": len(r["issues"])}))'
```

The agent writes any edit script to a file (`edits.json`) and returns its path, not its body.

## Workflow scripts (`.claude/workflows/*.js`, run with the `Workflow` tool)

Each script declares its own `meta` and reads `args`; `docs/workflows/README.md` describes them.
Args as the scripts read them today:

| Workflow | Args | Does |
|---|---|---|
| `figtree-refine` | `{svg, rubric, source?, rounds?, out_dir?}` | score, one repair round at a time with an edit script for the requests, stop on no requests or plateau; agents return verdicts, never the SVG |
| `figtree-adversary` | `{rubric, n_probes?, out_dir?}` | baseline `eval`, N adversaries (gaming / false-positive / miss / clean lenses) write probes, 3 refuters vet each, refuted probes deleted, `eval` after |
| `figtree-judge-panel` | `{svgs: [...], rubric, source?, out_dir?}` | three image judges per SVG (faithfulness, readability, aesthetics/medium fit) via `figtree judge`, synthesis and ranking |
| `figtree-icon-family` | `{briefs: ["name: concept | metaphor", ...], out_dir}` | `figtree icon` per brief, cold-eye review at 16/24/48 px, one repair when < 9.5, contact sheet |
| `figtree-digest` | `{inputs: [...], out_dir, rubric?, style?, max_units?}` | `digest --plan`, `--unit` per unit with score, one refine round when < 8, completeness critic on what was skipped |

`docs/workflows/WORKFLOW-API.md` has the script API; the `workflow-authoring` skill has the rules.

## House rules that hold across the family

- White background rect first (`id="background"`), 8 px grid, flat fills, no gradients, filters
  or shadows, one font family, <= 3 stroke widths, 24 px padding (32 slide / 16 chart / 2 icon).
- Orthogonal routing only; `data-diagonal="semantic"` is the single escape hatch.
- Every marker-ended arrow keeps a final segment >= 20 px: move the target, not the endpoint.
- Content plan is immutable downstream: layout, motion and edits never add a component.
- No source, no plan: coverage and hallucination are `n/a`, never 10.
- Fixed canvases (slide, tile, icon) centre their content; free canvases shrink to content.
- Animate only meaning: data -> pulse, control -> slower dimmer pulse, construction -> reveal/draw.
- Promote what is accepted: icons into `figtree/icons.py`, rules into `figtree/memory.py`, a
  gaming probe that stays gaming into a judge question in the rubric spec.

## Reference index

`references/README.md` lists every reference and asset in the family with one line each.

## Process and handoff

How this effort is developed (meta-prompt first, self-apply, tiny-context workers, adversarial fold, package every round) is the `figtree-process` skill; the resume point is `docs/HANDOFF.md`. The boundary between the pipeline and any design is the `FigureProgram` contract (`design/contract/README.md`; `python -m figtree contract export|validate|render`).
