---
name: svg-diagram
description: Build, score and repair editable SVG methodology figures, teaching diagrams, workflow/pipeline/agent-topology drawings and slide figures under the FigTree rubrics (methodology, teaching, slide). Use when someone says "draw the architecture", "make a figure of this method", "diagram the workflow/pipeline", "turn this paper, spec, README or skill.md into a figure", "make a teaching diagram", "put this on a slide", "fix this diagram", "the arrows cross / the labels overflow", "score this figure", or when a HEKAT query or RMP refine step needs a figure of an agent topology. Covers the house style (8 px grid, ports, 20 px arrow shafts, presets), edit scripts, what the critic measures and what only the eye catches (edge-hugging arrows, collinear overlap, inherited font overflow). Not for charts or tiles (svg-data-figure), icons (svg-icon) or motion (svg-animation).
---

# SVG diagrams: methodology figures, teaching diagrams, slides

A diagram draws *mechanism, not names*: components the source states, flows the source states,
grouping the source implies. Everything else is a residual to report. Build it as an addressable
program, score it in code and in the image, and repair it by id. The loop and the CLI are in the
hub (`.claude/skills/figtree/SKILL.md`); this skill holds the medium-specific rules.

## 1. Choose the register and the rubric

| Where it lives | Preset (`--style`) | Rubric | Minimum font | Words/label | Canvas |
|---|---|---|---|---|---|
| paper, report, README | `paper` (Times, flat #7BA3C9 blocks, dashed containers) | `methodology` | 9 px | 15 | free, aspect 1.2-4.0 |
| teaching material, docs, explainer | `teaching` (IBM Plex Sans, tinted fills, ink border #2B3A4A, no containers) | `teaching` | 14 px | 8 | free, aspect 1.0-2.4 |
| deck | `slide` (same family, bigger everything) | `slide` | 18 px | 6 | fixed 16:9, aspect 1.6-1.9 |

Read `references/rubric-<name>.md` for the exact thresholds, check ids and vetoes before you
score. The three rubrics share the 8 dimensions; they differ in thresholds and in whether the
canvas is fixed (slides centre content; the others shrink the canvas to content).

## 2. Ground before you draw

From a text source, run the generator: it admits only evidenced structure (arrow chains like
`A -> B`, "X Agent" names, numbered steps under a workflow heading, inputs/outputs) and logs
everything else as a residual.

```bash
python -m figtree generate SRC.md -o fig.svg --style teaching --icons --shapes --max-aspect 2.4 \
    --report report.json            # report.json: content_plan, residual_defects, editability proof
python -m figtree generate SRC.md -o fig.svg --backend claude   # prose-only methods; keeps the paper style
```

When you draw by hand (a sketch, a whiteboard, a concept with no text source), write the content
plan first as a list: components with the sentence that names each, flows with direction and
type (`data`, `control`, `conditional`), inputs, outputs. Then draw exactly that. If the critic
later asks for a component that is not in the plan, the answer is a residual, not an invention.

## 3. Construct on the house grid

Start from `assets/figure-skeleton.svg` when drawing by hand. The rules that make a figure
scorable and editable (details in `references/layout-rules.md`):

- `<rect id="background" data-role="background">` first, white, full canvas.
- Every element has an id; blocks carry `data-role="block"` (a `<path>` with `data-role="block"`
  is a block too: cylinder, document, diamond, pill, actor from `figtree/elements.py`).
- Labels are `<text data-kind="label">` centred in their block, one font family for the figure.
- Flows are `<path d="M.. H.. V..">` with `data-flow="data|control|conditional"`,
  `data-from`/`data-to` ids and `marker-end="url(#figtree-arrow)"`; dashed only for control/feedback.
- Orthogonal routing; final segment of every marker-ended arrow >= 20 px (24 teaching, 28 slide):
  move the target block, never shorten the shaft.
- 8 px grid for every coordinate; 24/32/40 px padding by preset; wide pipelines fold into rows.
- Four `<!-- PORT:side x= y= id= type= component= -->` comments per block so a parent can route
  to a child by reading the code alone.
- Icons: `<use href="#icon-name">` from `figtree/icons.py` symbols, 16 px inside a block.

## 4. Score in two spaces

```bash
python -m figtree score fig.svg --rubric teaching --json > score.json
# a PNG for the eye: refine --render-dir r/ keeps per-round renders; one-off renders use the headless
# command in .claude/skills/svg-animation/references/capture-frames.md (no virtual time needed)
```

Then look at the PNG with the questions in `references/gotchas.md`. The diagram adversary's
14 gaming probes all scored 10.0 at the time; at HEAD each fires a check (through-block with a
4 px halo, through-text, collinear shafts, sentence labels, outlined glyphs, duplicate labels,
legend in the drawing, container/label mismatch, clip-art, embedded title, a role lexicon for
backwards semantics). Those checks know their probes; they do not know your figure. Read the
render as a stranger would and anchor what you find to an id.

## 5. Repair by id

Mechanical defects (font below minimum, contrast, gradient, neon, filter, corner radius, font
family, canvas overflow on the right/bottom, blank trailing bands, centring on fixed canvases)
are auto-fixed by `refine`. Content decisions come back as anchored requests. Answer them with an
edit script (template: `assets/edit-script.template.json`; ops in the hub):

```bash
python -m figtree refine fig.svg --rubric slide -o fig.refined.svg --trajectory t.json --edits edits.json
python -m figtree refine fig.svg --rubric teaching -o out.svg --request "shorten the Preprocessing label to one word"
```

Rules of repair that the trajectories taught:
- Raising fonts to the minimum creates overflow and overlap *in the same round*: shorten labels
  in the same script, or expect three new criticals.
- A decision that contradicts an auto-fix (colour, size) goes in the next round or is overwritten.
- A trailing overflow is auto-fixed by `set_canvas`; on a slide or tile that would break the
  medium, so the critic centres instead and asks you to shorten.
- Measure editability: `diff` in the trajectory is the number of changed elements; one request
  should change one or a few elements. If a round changes dozens, you regenerated, not edited.

## 6. Convergence and handoff

Stop when `refine` reports `no edits left`, a plateau of two rounds, or the budget. Keep the
trajectory JSON next to the figure; the showcase skill reads it. Open requests you decide not to
act on (a banner aspect that is a design choice, a legend kept instead of direct labels) are
written down, not silently dropped. A figure that passes becomes the input of the next medium:
`svg-animation` for an explainer, `svg-showcase` for the page.

## 7. Delegating to a subagent

Fill `assets/worker-brief.md`: one file path, one rubric, one command, the 2 KB return shape.
The subagent never pastes SVG; it returns scores, the top issues with anchors, and the path of
the edit script it wrote.

## References and assets

- `references/rubric-methodology.md`, `rubric-teaching.md`, `rubric-slide.md`: thresholds, checks (ids match `figtree/rubric_spec.py`), vetoes, anchors.
- `references/layout-rules.md`: grid, ports, routing lanes, row wrapping, barycenter ordering, presets.
- `references/gotchas.md`: what the critic misses, written as eye checks.
- `assets/figure-skeleton.svg`: house-style starting file with ids, ports and data-role attributes.
- `assets/edit-script.template.json`: every op, one round per list.
- `assets/worker-brief.md`: fill-in brief for a scoring/repair subagent.

## Never accept an arrow through a block or a label

This was the one defect every small-model run reproduced (`docs/FAILURE-MODES.md`, rows 1-3).
The worker now routes around every block with a 4 px halo and re-routes anything that still
collides, so a figure that shows it is a bug to report, not a figure to ship. Before you hand
a figure back:

1. `python -m figtree score FIG.svg --rubric <medium> --json` must list no `flow.through_block`,
   `flow.through_text` or `flow.collinear_overlap` issue. If it does, regenerate (the generator
   and worker changed) or run `figtree refine`; never edit the arrow by hand in the SVG.
2. Look at the PNG once: a shaft grazing a container title, an arrow label on another shaft,
   or two heads on one line are the cases the checks can still miss.
3. In a workflow, these three check ids are blocking: the refine and digest scripts repair on
   any critical, and a spec card's DON'T names them.
