# Round log: the effort as critique → edit

Each round is written the way the critic writes an issue: what was seen, what was changed. This
is the project-scale trajectory; `examples/figtree/animated/NOTES.md`, `icons/NOTES.md` and
`probes/FOLD-REPORT.md` hold the artifact-scale and critic-scale ones.

| Round | Critique (what was seen) | Edit (what changed) |
|---|---|---|
| 1 Spec | A detailed spec and the paper; nothing implemented | `figtree/` package: grounder, recursive generator, worker merge with 20 px shafts, dual-space critic, sheaf storage, editability proof; 41 tests; self-application on the spec |
| 2 "That diagram is terrible" | The method only made paper figures; no way to improve an existing SVG | Rubrics per medium, `figtree score`, `figtree refine` with edit scripts and trajectories; teaching examples (chart, slide, icon, tiles) before/after |
| 3 Come to life | Blocks were rectangles; no icons; no motion; the Claude backend needed an API key | Element kinds, icon library + icon-smith loop, `figtree animate` (reveal/draw/pulse bound to meaning), `ClaudeCodeBackend` on the session's OAuth, meta-prompt document, showcase artifact |
| 4 Adversarial | Scores of 10 on figures that were bad; checks unproven | Rubric specs published, probe harness, `figtree eval`, image judge + calibration; three adversary workers wrote 108 probes: recall 0.43, precision 0.70 |
| 5 Design | X-crossings, nested wrapping, shared lanes, short first rows, paper look on teaching material | Presets (paper, teaching, slide), barycenter ordering, lane allocation, DP row balancing, preset-sized markers; judge 5.6 → 6.4 on the self-application figure |
| 6 Fold + package | Findings were tables, loops were hand-run, knowledge was in chat | Fold worker (recall 0.99, precision 1.00, 197 tests); five workflow scripts + `figtree digest`; seven skills with references/assets; React design system synced to Claude Design; showcase v4 |
| 7 Handoff | Design was welded to the pipeline; process lived in the transcript | `FigureProgram` contract (schema, Python, TypeScript, `ProgramView`); `figtree-process` skill; `figtree-handoff` workflow; `docs/HANDOFF.md`; live run of `figtree-refine` (9.19 → 10.0) |

What each round taught about the process itself:

- Looking at the render beside the score found every defect that mattered (rounds 2, 3, 5).
- A worker needs file ownership and a ≤ 40-line report, nothing else (rounds 4, 6).
- A rubric is an artifact; its probes are its tests (round 4) and its fold is its refinement (6).
- Packaging is not the last step but part of every round; what is not in a skill, a workflow or
  a document is lost at the next compaction (rounds 6, 7).
