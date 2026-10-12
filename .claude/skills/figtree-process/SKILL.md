---
name: figtree-process
description: How the FigTree effort is developed and handed off, so the next session continues the same way. Use this skill whenever someone says "continue the FigTree work", "resume where we left off", "how have we been developing this", "prepare a handoff", "compact and hand off", "brief a worker", "run an adversarial round", "fold the findings", "what is the process", or starts any multi-session effort that mixes a meta-prompt, subagent workers, adversarial evaluation and packaging into skills, workflows and a design system. It is the process layer above the figtree hub skill (which is about making figures); read it before delegating work or writing a status report on this repository.
---

# The FigTree development process

The project applies one loop at three scales: to an artifact (a figure), to the judge of
artifacts (the critic and its rubrics), and to the project itself (meta-prompt, code, skills,
workflows, design system, handoff). The loop is: **ground → construct → render → critique in two
spaces → edit locally → score → repeat until stable → promote what held**. Keep the three scales
in mind; most confusion comes from applying a step at the wrong scale.

## 1. Start from the meta-prompt, not from code

`docs/META-PROMPT-SVG-ARTIFACTS.md` is the typed statement of the category (slots, procedure,
binding rules) with a refinement log. When a new medium, motion or evaluation idea appears,
write it as a slot or a binding rule there first, then implement. When a pass over the
meta-prompt yields an empty edit script, it is stable; log that too. Why: the meta-prompt is
what every skill, workflow and worker brief is derived from. A rule that lives only in code is
invisible to the next session.

## 2. Self-apply before generalising

The first test of anything is FigTree on its own specification (`examples/figtree/figtree-spec.md`
→ `examples/figtree/design/`). Look at the render. A defect you can see and the critic cannot
is the next check; a check that fires on a good figure is the next false-positive probe.

## 3. Delegate to workers with tiny contexts

Write a brief with exactly these parts (template: `references/worker-brief.md`):
goal in one sentence · files to read first (paths, not summaries) · deliverables as a list of
files · rules (what not to touch, because another worker owns it) · report format (≤ 40 lines:
files created, numbers before/after, what is unfinished). Give disjoint file sets to parallel
workers; the orchestrator alone commits. Workers return paths and verdicts, never markup.
Why: a worker that re-derives the repo wastes its context; a worker that writes outside its set
corrupts another's work; a report longer than 40 lines is one the orchestrator will skim.

For loops that repeat (score → repair, adversary → refute, judge panel, icon draw → cold eye,
digest), do not write briefs by hand: run the workflow scripts in `.claude/workflows/`
(`docs/workflows/README.md`). They encode the same brief shape with JSON schemas as the
interface, so each agent sees one command and one file and returns ≤ 2 KB.

## 4. Improve adversarially, then fold

1. Publish the rubric specs: `python -m figtree eval --specs examples/figtree/rubrics`.
2. Adversaries write probes per rubric (gaming, false positive, miss, clean control), each with
   the check that *should* fire (`proposed.*` when it does not exist yet), into
   `examples/figtree/probes/<rubric>/` and a table in `ADVERSARY-<area>.md`.
3. Measure: `python -m figtree eval --rubric R` (recall, precision, per-check).
4. Fold: a worker turns every row into a check + threshold + regression test, renames
   `proposed.*` to the real id, records the before/after table in `probes/FOLD-REPORT.md`.
   Rule: fix a false positive by changing the rule for that medium, never the probe.
5. Calibrate: `python -m figtree judge --calibrate` on the example set; a |gap| ≥ 3 between
   judged and measured is a blind spot or a rule to reconsider.
6. What stays gaming-only after a round is listed as "judge is the only defence" in the fold
   report and the showcase. Do not hide it.

## 5. Treat design as a rubric target

"The design should improve" becomes: a preset (`figtree/styles.py`), a worker change (layering,
lanes, row balancing), a re-score, and a look at the render. Promote accepted looks into the
design system (`design/figtree-ds`) and keep the critic reading the same ids and data attributes
whatever the design: the contract (`design/contract/README.md`) is the boundary.

## 6. Package every round

After a round of work, four things are updated or they rot: the skill that teaches the medium
(`.claude/skills/svg-*`), the workflow that runs the loop, the showcase that shows the evidence
(`examples/figtree/showcase/build_showcase.py` → the Artifact), and `docs/HANDOFF.md`. Commit on
`claude/figtree-generator` with the attribution lines the session requires; push; no PR unless
asked.

## 7. Hand off with progressive disclosure

`docs/HANDOFF.md` has four levels: one paragraph, a map, the process, and resume-today with
open items. Keep the levels separate so a reader stops when they know enough. The
`figtree-handoff` workflow regenerates level 3 from the repository (tests, eval numbers, git
state, open items in the fold report and NOTES files); run it before ending a session and paste
its result into the document.

## References

- `references/worker-brief.md`: the brief template and two real briefs from this effort.
- `references/verdict-schemas.md`: the JSON shapes workers and workflow agents return.
- `references/round-log.md`: the rounds this project went through, each as critique → edit.
- `docs/workflows/README.md`, `docs/HANDOFF.md`, `docs/META-PROMPT-SVG-ARTIFACTS.md`.
