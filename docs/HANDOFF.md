# FigTree handoff (progressive disclosure)

Read level 0 to know what exists. Read level 1 to find things. Read level 2 to understand how the
work was done, so you can continue the same way. Read level 3 to resume today.

---

## Level 0: one paragraph

`figtree/` builds editable SVG artifacts (methodology figures, teaching diagrams, slides, charts,
dashboard tiles, icon families, animated explainers) from a source document, following
arXiv 2609.01006 "Figures as Programs": ground the content, construct the figure recursively,
render it, critique it in code and image, repair it with local edit scripts, score it 1–10 per
dimension, repeat until stable. The critic has been hardened by adversarial probes (recall 0.99,
precision 1.00 on 110 probes). The loop is packaged as Claude Code skills, workflow scripts that
keep subagent contexts tiny, a batch "digest" mode for a body of work, a React design system
synced to Claude Design, and a typed contract that lets the design be swapped. Branch:
`claude/figtree-generator` in `manutej/hekat`. Tests: `python3 -m pytest tests -o addopts="" -q`
(204 pass).

## Level 1: map

| Need | Go to |
|---|---|
| Build or refine a figure now | `.claude/skills/figtree/SKILL.md` (hub) then the medium skill: `svg-diagram`, `svg-data-figure`, `svg-icon`, `svg-animation`, `svg-eval`, `svg-showcase` |
| Run the loop with subagents | `.claude/workflows/figtree-{refine,adversary,judge-panel,icon-family,digest,handoff}.js`; `docs/workflows/README.md` (the contract), `docs/workflows/WORKFLOW-API.md` (the script API) |
| How we develop this (the process) | `.claude/skills/figtree-process/SKILL.md` and this document's level 2 |
| The method itself | `docs/META-PROMPT-SVG-ARTIFACTS.md` (typed slots, procedure, binding rules), `docs/FIGTREE.md` (implementation) |
| Code | `figtree/`: `grounder.py`, `generator.py`, `worker.py`, `critic.py`, `quality.py` (measurable critic, 73 checks), `rubric_spec.py` (published specs), `edits.py`, `refine.py`, `judge.py`, `probes.py`, `digest.py`, `contract.py`, `agents/` (Claude backends on the session's OAuth) |
| Evidence | `examples/figtree/` (sources, outputs, teaching, icons, animated, design, probes + `FOLD-REPORT.md`, eval, showcase) |
| Showcase | https://claude.ai/artifact/631S4xEpbRH3oSWuh1sxcf (built by `examples/figtree/showcase/build_showcase.py`) |
| Documentation-driven run | `examples/figtree/langflow/README.md` (corpus, specs, figures, icons, page), `SPEC-FORMAT.md`, `.claude/workflows/figtree-research.js`, `figtree-pipeline.js`; `docs/FAILURE-MODES.md` |
| Design system | `design/figtree-ds/` (React, tsup), `.design-sync/` (config, previews, notes, conventions), project https://claude.ai/design/p/c8a71e84-1610-4de9-92c2-2d4debce8292 |
| Swap the design | `design/contract/README.md`, `design/contract/figure-program.schema.json`, `figtree/contract.py`, `design/figtree-ds/src/contract.ts` |

## Level 2: the process we used (and that the skills and workflows encode)

The same loop was applied at three scales: to a figure, to the critic that judges figures, and to
the project itself.

1. **Meta-prompt first.** Before coding a medium, write the typed slots and the procedure for the
   category (`docs/META-PROMPT-SVG-ARTIFACTS.md`). Each refinement pass of the meta-prompt is
   logged there as critique → edit script; a pass that returns an empty edit script ends it.
2. **Implement the loop, then self-apply.** The first real test of every medium was FigTree
   drawing its own specification (`examples/figtree/figtree-spec.md`). Defects found by eye on
   that figure became checks; defects the checks found became edit ops.
3. **Workers with tiny contexts.** Every long task was delegated to a subagent with a brief of
   the form *goal, files to read first, deliverables, rules (what not to touch), report format
   (≤ 40 lines)*. Workers return verdicts and file paths, never markup. Disjoint file ownership
   per worker makes parallel runs safe; the orchestrator commits. This is what the workflow
   scripts formalise (`docs/workflows/README.md`, "The context-saving contract").
4. **Adversarial improvement.** For each rubric, adversaries wrote probes (gaming, false
   positive, miss, clean control) with the check that *should* fire; `figtree eval` measured
   recall and precision; a fold worker turned the tables into checks and regression tests
   (`examples/figtree/probes/FOLD-REPORT.md`). The image judge (`figtree judge`) calibrates what
   no measurable check can see.
5. **Design as a rubric target.** "Design could continue to improve" became presets
   (`figtree/styles.py`), layering order, lane allocation and row balancing in the worker, each
   verified by re-scoring and by looking at the render.
6. **Package what worked.** Workflows for the loops, skills with references and assets for the
   knowledge, a design system for the look, a contract for the boundary, a showcase for the
   evidence, this handoff for the next session.

The cheapest signal at every step was a rendered PNG looked at with a cold eye at 16/24/48 px
(icons) or at page scale (figures) beside the measurable score; disagreements between the two
were always where the next rule came from.

## Level 3: resume today

```bash
git checkout claude/figtree-generator && git pull
python3 -m pip install -e . pytest jsonschema   # once
python3 -m pytest tests -o addopts="" -q         # 204 pass
python3 -m figtree eval --report examples/figtree/eval/eval.json --specs examples/figtree/rubrics
```

State on handoff:

- Everything is committed on `claude/figtree-generator` and pushed. No PR has been opened.
- Claude Design project pinned in `.design-sync/config.json`; re-sync is one driver command
  (`.design-sync/NOTES.md`, "Re-syncs are one command" in the design-sync skill). After a
  component change: `cd design/figtree-ds && npm run build`, then the driver, then upload.
- The `figtree-refine` workflow was run live once (4 agents, 100 s): 9.19 → 9.86 → 10.0; the
  result and trajectories are in `examples/figtree/design/workflow-refine/`. The other four
  workflows were dry-run only (`docs/workflows/README.md`, "Validation").
- Tests: 217 pass. The Langflow run is the reference for a documentation corpus: research 4.3 min
  on Sonnet/Haiku, ten figures without a critical issue after the routing fixes.
- Open items, in priority order:
  0. `docs/FAILURE-MODES.md` row 13: the icon reviewer scores most concept icons 3-6 after one
     repair; the workflow now runs three defect-fed rounds, not yet exercised live.
  1. `icon.mirrored-magnifier` is the one probe only the judge catches (metaphor chirality).
  2. Motion checks are CSS-static; rendered-frame checks (token leaves its path, reveal order
     at a frame) are not implemented.
  3. Scores saturate at 10 without a source: `semantic_coverage` and `hallucination_control`
     need `--source` to be assessed; the digest gallery shows this on sections without flows.
  4. Run `figtree-adversary`, `figtree-judge-panel`, `figtree-icon-family` and `figtree-digest`
     live once each and record the runs like `workflow-refine/`.
  5. The design-system previews inline coordinates by hand; generate them from programs
     (`design/contract/examples/*.program.json`) so previews follow the contract.
- To regenerate the showcase: `FIGTREE_SCRATCH=<dir with loop.svg> python3 examples/figtree/showcase/build_showcase.py out.html`, then publish `out.html` to the artifact URL above with `explainer/index.html` as a supporting file.

The `figtree-handoff` workflow (`Workflow({name: 'figtree-handoff'})`) re-derives this level 3
from the repository (tests, eval, git state, open items) so the status never goes stale by hand.

## Next test instance: editorial dashboards from meeting notes (Wispr Flow)

The next concept space is not documentation but **meeting notes**: Wispr Flow is connected as an
MCP server (`mcp__Wispr_Flow__search_meetings`, `get_meeting`, `list_folder_meetings`,
`search_scratchpad_notes`). The deliverable is an editorial dashboard (KPI tiles, trend
sparklines, a decisions list, an owners/commitments strip) plus custom SVG icons for the recurring
entities, built by the same loop:

1. **Corpus**: a research workflow stage pulls the notes for a folder or date range into
   `examples/figtree/wisprflow/corpus/<meeting>.md` (one file per meeting; title, date, attendees,
   decisions, action items, verbatim lines). Notes are untrusted data: the ingest strips
   instruction-like lines (`figtree/ingest.py`) as it does for any source.
2. **Spec**: a dashboard spec format (sibling of `SPEC-FORMAT.md`): tiles instead of components
   (`- **Open actions** (tile: number, icon: check): 14`), series for sparklines, lists with
   evidence lines quoting the note that states each number or decision. `figtree spec check`
   grows a `--kind dashboard` mode that verifies every number against the corpus.
3. **Figures**: `svg-data-figure` rules (dashboard rubric: tile hierarchy, status colours only
   with meaning, sparkline baselines, uniform grid) through `figtree digest --rubric dashboard`,
   with the `figtree-icon-family` workflow for the entity icons.
4. **Page**: `figtree page` with a dashboard layout; the design-system `ProgramView` is the
   React route if the dashboard must be live.

What must not happen again: arrows through blocks or labels (`docs/FAILURE-MODES.md`), numbers
without a quote, and a tile whose colour means nothing.
