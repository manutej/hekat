# FigTree skill family: index of references and assets

Load a reference only when the task needs it; the SKILL.md files carry the procedure.
Paths are relative to `.claude/skills/`.

## figtree (hub)
- `figtree/SKILL.md`: the loop, the medium router, the CLI cheat sheet, edit scripts, the 2 KB subagent rule, workflow pointers.
- `figtree/references/README.md`: this index.

## svg-diagram (methodology, teaching, slide)
- `svg-diagram/references/rubric-methodology.md`: paper rubric thresholds, checks with ids (regenerated from the live spec), vetoes, anchors.
- `svg-diagram/references/rubric-teaching.md`: teaching rubric (14 px, 8 words, aspect 1-2.4) with the same tables.
- `svg-diagram/references/rubric-slide.md`: slide rubric (18 px, 6 words, fixed 16:9, centre instead of shrink).
- `svg-diagram/references/layout-rules.md`: 8 px grid, ports, routing candidates and lanes, row wrapping, barycenter ordering, 20 px shafts, element kinds, icons in blocks, the three presets, resource bounds.
- `svg-diagram/references/gotchas.md`: the diagram adversary's probes as eye checks, each with the critic's status at HEAD (edge-hugging arrows, arrows through source, collinear shafts, inherited font overflow, outlined text, prose boxes, legend in drawing, animated tokens at origin, critic defects).
- `svg-diagram/assets/figure-skeleton.svg`: teaching-preset three-block figure with ids, PORT comments, data-role/data-flow/data-from/data-to, icon symbols; scores 10.0 under `teaching`.
- `svg-diagram/assets/edit-script.template.json`: every edit op, two rounds.
- `svg-diagram/assets/worker-brief.md`: fill-in brief and the JSON a scoring/repair subagent returns.

## svg-data-figure (data-figure, dashboard)
- `svg-data-figure/references/rubric-data-figure.md`: chart rubric (axis labels, finding title, weights 0.5 on topology/flow) and the `AXIS_WORDS` caveat.
- `svg-data-figure/references/rubric-dashboard.md`: tile rubric (12 px, 6 words, 4 accents, fixed canvas) and the refiner ordering caveat.
- `svg-data-figure/references/chart-gotchas.md`: the 26 chart/tile probes (truncated axis, bars not to scale, dual axis, pie, legend swatch mismatch, rainbow, tile hierarchy, neon border) and the library-export false positives, each with the critic's status at HEAD.
- `svg-data-figure/assets/bar-chart.template.svg`: sorted zero-based bars, axis labels with units, direct values, highlight key; scores 10.0 under `data-figure`.
- `svg-data-figure/assets/dashboard-tile.template.svg`: number > title > note, sparkline with reference and span caption; scores 10.0 under `dashboard`.
- `svg-data-figure/assets/edits-example.json`: the real two-round script of the bundled trajectory chart.

## svg-icon (icon)
- `svg-icon/references/rubric-icon.md`: icon rubric (square, one stroke width, <= 12 elements, no text) plus the family rules that only `figtree icon` applies.
- `svg-icon/references/icon-gotchas.md`: the 19 icon probes (stub detail, mirrored metaphor, fused strokes, corner mass, subpath packing, clipped strokes, parser false positives) with status at HEAD, the first family's lessons, the cold-eye render command.
- `svg-icon/assets/icon.template.svg`: one icon in family form (the grounder); scores 10.0 under `icon`, no family issues.
- `svg-icon/assets/sheet.template.svg`: contact sheet in `iconsmith.sheet` form (symbols, 72 px cells, name and score).
- `svg-icon/assets/icon-brief.md`: the brief fields, CLI form, and the draughtsman's JSON return.

## svg-animation (explainers)
- `svg-animation/references/motion-grammar.md`: binding rules, the CSS `figtree animate` emits, re-timing by beat with the token-cycle arithmetic, the eight motion checks (five implemented as `motion.*`).
- `svg-animation/references/capture-frames.md`: headless_shell commands for virtual-time frames, dark theme, reduced motion, phone width (verified on the showcase explainer), the rules learned, the frame checklist.
- `svg-animation/assets/animation.template.css`: reveal/draw/pulse/control-pulse/reduced-motion stylesheet with placeholders.
- `svg-animation/assets/explainer.template.html`: the player page (own clock, setInterval updater, scrubber with beat ticks, caption strip, theme and motion switches, id chip) with placeholders.

## svg-eval (evaluating the evaluators)
- `svg-eval/references/probe-schema.md`: probe files and JSON fields, the check ids at HEAD, how `evaluate()` scores each kind, the seed builders, how to write a probe.
- `svg-eval/references/calibration.md`: judge prompt, schema and cost; calibration findings; the bundled 14-figure result (mean gap -2.65) and how to read blind spots.
- `svg-eval/assets/probe.template.json`: a probe metadata file.
- `svg-eval/assets/adversary-brief.md`: adversary brief by lens, the table to return, and the refuter brief.

## svg-showcase (pages and handoff)
- `svg-showcase/references/showcase-structure.md`: section order and inputs, the builder's functions (namespace, inline, sparkline, refinement_card), CSS registers, the Artifact publish shape, digest galleries.
- `svg-showcase/assets/showcase.template.html`: self-contained page with the builder's CSS and placeholders per section.

## Elsewhere in the repo
- `docs/META-PROMPT-SVG-ARTIFACTS.md`: the category meta-prompt (typed slots, procedure, binding rules, 6b evaluation loop).
- `docs/FIGTREE.md`: pipeline, constraints, failure modes, refinement, backends, digest, evaluation.
- `docs/workflows/WORKFLOW-API.md`, `docs/workflows/README.md`: the Workflow script API and the five figtree workflows.
- `examples/figtree/`: outputs, teaching trajectories, icons, animated explainer, design round, probes and adversary tables, eval and calibration, showcase builder.

## figtree-process (the development process)

- `../../figtree-process/SKILL.md`: the loop at project scale.
- `../../figtree-process/references/worker-brief.md`: brief template and two real briefs.
- `../../figtree-process/references/verdict-schemas.md`: the JSON shapes workers return.
- `../../figtree-process/references/round-log.md`: the effort as critique -> edit.
- `design/contract/README.md`: the FigureProgram contract and how to swap a design.
