# Worker brief template

Every delegated task in this effort used this shape. Copy it; fill every slot; delete nothing.

```
You are a worker in the HEKAT repo at /home/user/hekat (<runtime facts: Python version, how to
run tests, what passes today>). <One paragraph of context: what the subsystem is and where it lives.>

GOAL: <one sentence; the outcome, not the activity>.

Read first: <explicit paths, in reading order, with a note on what each gives>.

DELIVERABLES
1. <file or directory> — <what it must contain, including formats and schemas>.
2. ...
N. <how to verify: the exact commands and the numbers that count as done>.

Rules: edit only <paths>; do not touch <paths> (other workers own them). Keep tests green.
Known failure modes to avoid and to log if seen again: docs/FAILURE-MODES.md (an arrow through a
block or label is never acceptable output).
Do not commit. Final answer: a ≤ 40-line report listing files created/changed, the numbers
before/after, and anything you could not finish.
```

Why each slot exists:

- **Runtime facts** stop the worker spending its first ten tool calls rediscovering the toolchain.
- **Read first** is paths, not summaries, because a summary is already stale and the worker
  needs the real contract (a schema, a check table, a CLI flag).
- **Deliverables as files** make the report verifiable: the orchestrator runs `ls` and the tests.
- **Rules** are file ownership. Parallel workers never share a file; the orchestrator commits.
- **Report ≤ 40 lines** is the context budget of the orchestrator, which reads six of these.

## Two real briefs from this effort (abridged)

### Fold the adversary findings into the critic

```
GOAL: fold the findings into the critic. Priority: (1) every false_positive probe stops firing
(fix the rule for that medium, not the figure); (2) proposed checks of severity veto/critical/high
become real checks (rename proposed.* to the implemented id, keep the meaning); (3) cheap
medium/low rows. Each new check needs an entry in rubric_spec.CHECKS, a threshold where
applicable, and a probe that proves it.
Process: run `python -m figtree eval --rubric R` per rubric before you start and record the
numbers; work rubric by rubric; re-run eval and the suite after each change; add a fire/silent
test pair per check. Seed figures must not regress below their current overall.
Finish with eval.json and probes/FOLD-REPORT.md (before/after table, implemented checks,
what remains gaming-only). Target recall ≥ 0.85, precision ≥ 0.9; if unreachable, name the probes.
Rules: edit only figtree/quality.py, rubric_spec.py, rubrics.py, iconsmith.py, program.py,
probes.py, tests/, examples/figtree/probes/**, eval/eval.json, rubrics/*.json.
```
Result: recall 0.43 → 0.99, precision 0.68 → 1.00, 133 → 197 tests, one leftover named.

### Build the skill family

```
GOAL: turn what this repo learned into a family of skills with references and assets, so a
future session can digest a body of work and produce diagrams, charts, icons, animations and
showcases without re-deriving the method. Follow skill-creator conventions (frontmatter with a
pushy description listing user phrasings; body < 300 lines, imperative, explain the why;
references/ for on-demand docs; assets/ for templates).
Quality bar: every claim must be true of the code today (grep before writing; check ids must
match rubric_spec.py); every asset must parse; every frontmatter must be YAML.
Rules: do not touch figtree/*.py, .claude/workflows/, examples/figtree/probes/ or design/.
```
Result: 7 skills, 40 files, templates scoring 10.0 under their rubrics, status columns computed
with `figtree.probes.evaluate` at the end.
