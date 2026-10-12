# FigTree workflows (`.claude/workflows/`)

Eight Claude Code `Workflow` scripts turn the loops we used to run by hand with subagents
(score → repair, adversary → refute, judge panel, icon draw → cold eye, digest a directory)
into reusable orchestrations. The script API is in `WORKFLOW-API.md`; this page is the
contract the five scripts share, a table of their arguments, and a worked chain.

## The context-saving contract

The orchestrator (the script, and the main session that reads its result) never sees an
SVG, a PNG or a document. It sees **verdicts**.

| Rule | What it means in a script |
|---|---|
| **Verdicts ≤ 2 KB** | Every `agent()` call has a `schema`; the prompt names the fields, trims strings (120-160 chars), caps lists (≤ 8-12 items) and ends with "do not paste file contents into your answer". |
| **Artifacts stay on disk** | Agents write `.svg`, `.json`, `.png` under `out_dir` (or `examples/figtree/probes/<rubric>/`) and return **paths**. The next stage receives the path, not the content. |
| **One command + one file per agent** | Each prompt says exactly which `python -m figtree …` command to run and exactly which (small JSON) file to read afterwards. Agents that only read a file say "Read only `<file>`". A single agent never gets the whole task. |
| **Schemas are the interface** | Stage N's prompt is built from stage N-1's validated object (`score.requests`, `drawn.svg`, `review.defects`). If a field is not in the schema, the next stage cannot depend on it. |
| **`effort: 'low'` for mechanical stages** | Scorers, repairers that apply an existing edit script, evaluators, file deleters, the scout. Judges, adversaries and draughtsmen inherit the session effort. |
| **No silent caps** | Anything dropped (`max_units`, refuted probes, failed stages, missing judges) goes through `log()` and into the result (`dropped`, `failed`, `missing`, `not_covered`). |
| **Deterministic scripts** | No `Date.now()`, `Math.random()`, filesystem or Node APIs; randomness is lens-by-index; timestamps come in through `args`. Resume replays the unchanged prefix from the journal. |

### `pipeline()` vs `parallel()`

`pipeline(items, stage1, stage2, …)` is the default: a unit can be in its refine stage while
another is still generating; a probe can be under refutation while another adversary is
still drawing. A `parallel()` barrier is used only where a stage genuinely needs *all* of
the previous results at once:

- **majority vote** — the three refuters of one probe (adversary) and the three judges of one
  SVG (judge panel) must all answer before the verdict is computed (`parallel` *inside* a
  pipeline stage, so items still do not wait for each other);
- **early exit / dedup** — nowhere in these five scripts; if you add a "skip verification when
  zero probes were written" barrier, that is the one legitimate reason.

Everything else (flatten, filter, threshold) is plain code inside a stage.

## The eight workflows

| Workflow | Args | Stages (agents) | Returns |
|---|---|---|---|
| `figtree-refine` | `{svg, rubric, source?, rounds?=4, out_dir}` | per round: **scorer** (`figtree score --json`) → **repairer** (`figtree refine --rounds 1` + edit script for content requests); stops when no requests remain or two rounds plateau | `{svg, rubric, rounds_run, stop_reason, history:[{round, stage, overall…}]}` |
| `figtree-adversary` | `{rubric, n_probes?=4, out_dir}` | **eval before** → N **adversaries** (lens by index: gaming, false-positive, miss, clean-control; files `examples/figtree/probes/<rubric>/<lens>-<i>-*.svg|json`) → 3 **refuters** per probe (rendered-reality, spec-consistency, behaviour-match; 2 of 3 refute = drop) → **delete** refuted files → **eval after** | `{kept, dropped:[{id, reasons}], deleted, before:{recall, precision…}, after:{…}}` |
| `figtree-judge-panel` | `{svgs:[path \| {svg, source?}], rubric, source?, out_dir?}` | per SVG: 3 **judges** in parallel (faithfulness-vs-source, readability-at-a-glance, aesthetics/medium fit; each runs `figtree judge --report`) → arithmetic synthesis (mean, min, spread, union of vetoes) | `{ranking:[{rank, svg, overall, vetoes, spread}], verdicts:[{svg, dimensions:{d:{score, min, why[]}}, headlines}], missing}` |
| `figtree-icon-family` | `{briefs:[{name, concept, metaphor?}], out_dir}` | per brief: **draughtsman** (`figtree icon --backend claude`, rule/hand fallback) → **cold-eye reviewer** (renders 16/24/48 px, `{score, defects}`) → **repair** + re-review once when < 9.5 → one **sheet** agent (`iconsmith.sheet`) | `{out_dir, sheet, icons:[{name, svg, score, defects, repaired, status}], failed}` |
| `figtree-digest` | `{inputs:[paths] \| {dir}, rubric, out_dir, max_units?, style?}` | **scout** (`figtree digest --plan` → manifest) → per unit: **generate** (`figtree digest --unit ID`) → **score** (reads `<id>.score.json`) → **refine** one round when < 8 → **completeness critic** (reads the manifest's `skipped`) | `{manifest_path, units:[{id, title, svg, overall, status}], skipped:[{source, title, reason, worth_a_figure}], not_covered, failed}` |
| `figtree-handoff` | `{out?='docs/HANDOFF-STATUS.md', branch?}` | 4 **measurers** in parallel (tests, `figtree eval`, git state, open items from FOLD-REPORT / NOTES / workflows README) → 1 **writer** composes the resume-today status | `{tests, eval, git, open_items, status_md, missing}` |
| `figtree-research` | `{corpus_dir, out_dir, topics?, max_topics?=8, model?, cheap_model?, format?}` | **scout** (or `args.topics`) → per topic **researcher** writes a spec in `SPEC-FORMAT.md` → **checker** runs `figtree spec check` → **fixer** ≤ 2 rounds from the check's list → **synthesizer** writes `00-overview.md` | `{specs:[{id, spec, ok, components, flows, fix_rounds, remaining}], overview, failed}` |
| `figtree-pipeline` | `{title, corpus_dir, out_dir, topics?, rubric?, icons?, max_icons?, model?, cheap_model?, skip?}` | `workflow('figtree-research')` → `workflow('figtree-digest')` over the specs → icon briefs + `workflow('figtree-icon-family')` → **animator** → **page builder** (`figtree page`) | `{research, figures, icons, animated, page}` |

Example calls:

```js
Workflow({ name: 'figtree-refine', args: { svg: 'examples/figtree/teaching/slide-pipeline.svg', rubric: 'slide', source: 'examples/figtree/loop.md', rounds: 4, out_dir: '/tmp/refine' } })
Workflow({ name: 'figtree-adversary', args: { rubric: 'teaching', n_probes: 4, out_dir: '/tmp/adversary' } })
Workflow({ name: 'figtree-judge-panel', args: { svgs: ['/tmp/a.svg', { svg: '/tmp/b.svg', source: 'examples/figtree/loop.md' }], rubric: 'teaching' } })
Workflow({ name: 'figtree-icon-family', args: { briefs: [{ name: 'grounder', concept: 'extract only evidenced elements', metaphor: 'magnifier over a page' }, { name: 'critic', concept: 'dual-space review' }], out_dir: 'examples/figtree/icons/wf' } })
Workflow({ name: 'figtree-pipeline', args: { title: 'Agentic workflows in Langflow', corpus_dir: 'examples/figtree/langflow/corpus', out_dir: 'examples/figtree/langflow', model: 'sonnet', cheap_model: 'haiku' } })
Workflow({ name: 'figtree-handoff', args: { out: 'docs/HANDOFF-STATUS.md' } })
Workflow({ name: 'figtree-digest', args: { inputs: { dir: 'examples/figtree' }, rubric: 'teaching', out_dir: '/tmp/digest', max_units: 12 } })
```

`args` is passed as a JSON value, never as a JSON-encoded string.

## The CLI underneath

```
python -m figtree digest --plan DOCS… -o OUT [--rubric R] [--style S]   # OUT/manifest.json {units:[{id, source, title, span, chars, est_components}], skipped:[…]}
python -m figtree digest --unit ID -o OUT [--rubric R]                   # OUT/ID.svg, ID.report.json, ID.score.json; prints one JSON line
python -m figtree digest --all -o OUT [--rubric R]                       # every unit sequentially, then OUT/index.html (title, score, inline svg) and OUT/digest.json
```

A unit is an H1/H2 section whose text grounds to ≥ 3 components (arrow chains, named roles,
numbered steps as `RuleBasedGrounder` detects them), or a whole file when it is small (≤ 2.5 KB
or no H2). Rubric → style: `teaching`/`slide` use their preset, everything else `paper`.
Thin sections are listed under `skipped` with the reason. `figtree score`, `refine`, `judge`,
`eval` and `icon` are documented in `../FIGTREE.md`.

## Worked example: digest → judge panel → refine on `examples/figtree/`

Each step is one `Workflow` call; read the result between calls and decide the next one.

**1. Digest the directory.**

```js
const d = Workflow({ name: 'figtree-digest', args: { inputs: { dir: 'examples/figtree' }, rubric: 'teaching', out_dir: '/tmp/digest' } })
// d.units -> [{id:'loop', svg:'/tmp/digest/loop.svg', overall:9.11, status:'ok'},
//             {id:'notes--round-4-rebuilt-on-the-redesigned-figure', svg:'…refined.svg', overall:8.2, status:'refined'}, …]
// d.skipped -> 22 thin sections (probe tables, eval summaries) with worth_a_figure flags; d.not_covered -> what a reader would miss
```

Running the CLI by hand gives the same gallery without agents: `python -m figtree digest --plan examples/figtree -o /tmp/digest && python -m figtree digest --all -o /tmp/digest`
(13 units in ~40 s; 11 score ≥ 8 on first generation, two land at 7.4-7.7 and are the refine candidates).

**2. Rank the contenders with the judge panel** (the measurable critic cannot see a
backwards semantic or a misleading container; the three lenses can).

```js
const j = Workflow({ name: 'figtree-judge-panel', args: {
  svgs: d.units.filter(u => u.overall >= 8).map(u => ({ svg: u.svg, source: `examples/figtree/${u.id}.md` })),
  rubric: 'teaching' } })
// j.ranking -> [{rank:1, svg:'/tmp/digest/loop.svg', overall:8.67, vetoes:0, spread:1.0}, …]
// j.verdicts[i].dimensions.semantic_coverage.why -> the three one-line justifications
```

**3. Refine the figure the panel liked least** (or every `status: 'low…'` unit from step 1),
with the source so coverage and hallucination are assessed:

```js
const worst = j.ranking[j.ranking.length - 1]
const r = Workflow({ name: 'figtree-refine', args: { svg: worst.svg, rubric: 'teaching', source: 'examples/figtree/transformer-method.md', rounds: 4, out_dir: '/tmp/refine' } })
// r.history -> [{round:1, stage:'score', overall:8.46, issues:3, requests:1}, {round:1, stage:'repair', overall_before:8.46, overall_after:9.2, edits_applied:2, remaining:1}, …]
// r.stop_reason -> 'no requests remain' | 'score plateau after 2 rounds' | 'round budget exhausted'
```

Then feed `r.svg` back into the judge panel to confirm the gain is visible, not just measured.
The whole chain costs the main session three result objects of a few hundred bytes each; every
SVG, PNG, trajectory and manifest stays under `/tmp/digest` and `/tmp/refine`.

## Validation

The scripts are ESM with a top-level `return` (the runtime wraps the body in an async
function, as the API's own examples assume), so `node --check --input-type=module < file`
reports exactly one diagnostic, the final `return`. A dry-run harness that strips the
`export`, wraps the body and stubs `agent/pipeline/parallel/phase/log/args` exercises every
stage with schema-shaped fakes; run it when you change a script.

## Model tiers

Every script accepts `args.model` (all agents) and `args.cheap_model` (stages marked `effort: 'low'`: scorers, checkers, listers, file writers). The prompts are spec cards (`.claude/skills/figtree-process/references/spec-card.md`): one command, one file, one JSON shape, so Sonnet writes and Haiku checks without any prompt changing. The Langflow run used `model: 'sonnet', cheap_model: 'haiku'`.
