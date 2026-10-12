export const meta = {
  name: 'figtree-handoff',
  description: 'Re-derive the resume-today status of the FigTree effort from the repository (tests, eval, git state, open items) and write it as a handoff section',
  whenToUse: 'Before ending a session on the FigTree work, or when docs/HANDOFF.md level 3 may be stale: four small-context agents measure the repo and one writes the status; nothing is edited except the status file',
  phases: [
    { title: 'Measure', detail: 'tests, eval numbers, git state, open items (parallel, one command or one file each)' },
    { title: 'Write', detail: 'one agent composes the level-3 status markdown from the four verdicts' },
  ],
}

// args: {out?: path for the status markdown (default docs/HANDOFF-STATUS.md), branch?: expected branch}
const out = (args && args.out) || 'docs/HANDOFF-STATUS.md'
const branch = (args && args.branch) || 'claude/figtree-generator'

const TESTS = {
  type: 'object',
  properties: { passed: { type: 'integer' }, failed: { type: 'integer' }, errors: { type: 'integer' }, seconds: { type: 'number' }, failing: { type: 'array', items: { type: 'string' } } },
  required: ['passed', 'failed', 'errors', 'failing'],
}
const EVAL = {
  type: 'object',
  properties: {
    probes: { type: 'integer' }, recall: { type: 'number' }, precision: { type: 'number' },
    per_rubric: { type: 'array', items: { type: 'object', properties: { rubric: { type: 'string' }, probes: { type: 'integer' }, recall: { type: 'number' }, precision: { type: 'number' } }, required: ['rubric', 'probes', 'recall', 'precision'] } },
    missed: { type: 'array', items: { type: 'string' } },
  },
  required: ['probes', 'recall', 'precision', 'per_rubric', 'missed'],
}
const GIT = {
  type: 'object',
  properties: { branch: { type: 'string' }, clean: { type: 'boolean' }, dirty_files: { type: 'array', items: { type: 'string' } }, ahead: { type: 'integer' }, behind: { type: 'integer' }, last_commits: { type: 'array', items: { type: 'string' } } },
  required: ['branch', 'clean', 'dirty_files', 'ahead', 'behind', 'last_commits'],
}
const ITEMS = {
  type: 'object',
  properties: { items: { type: 'array', items: { type: 'object', properties: { source: { type: 'string' }, item: { type: 'string' }, priority: { type: 'integer' } }, required: ['source', 'item', 'priority'] } } },
  required: ['items'],
}
const WRITE = { type: 'object', properties: { path: { type: 'string' }, lines: { type: 'integer' } }, required: ['path', 'lines'] }

const noPaste = 'Do not paste file contents into your answer; return only the JSON object.'

phase('Measure')
const [tests, evalr, git, items] = await parallel([
  () => agent(`Run exactly: python3 -m pytest tests -o addopts="" -q 2>&1 | tail -15
Read only that output. Return {passed, failed, errors, seconds, failing:[test ids that failed, at most 10]}. ${noPaste}`, { label: 'tests', phase: 'Measure', schema: TESTS, effort: 'low' }),
  () => agent(`Run exactly: python3 -m figtree eval --report /tmp/figtree-handoff-eval.json 2>&1 | tail -12
Then read only /tmp/figtree-handoff-eval.json (keys: summary{probes, recall, precision}, per_rubric or per_check, probes[]). Return {probes, recall, precision, per_rubric:[{rubric, probes, recall, precision}], missed:[probe ids whose expected checks did not fire, at most 10]}. If the report has no per_rubric, run "python3 -m figtree eval --rubric R | head -2" for R in methodology, teaching, slide, data-figure, dashboard, icon and read the first line of each. ${noPaste}`, { label: 'eval', phase: 'Measure', schema: EVAL, effort: 'low' }),
  () => agent(`Run exactly: git status --short --branch | head -30; git log --oneline -5; git rev-list --left-right --count origin/${branch}...HEAD 2>/dev/null
Return {branch, clean (true when status lists no files), dirty_files:[paths, at most 20], ahead, behind (from rev-list: behind<TAB>ahead), last_commits:[the 5 oneline entries]}. ${noPaste}`, { label: 'git', phase: 'Measure', schema: GIT, effort: 'low' }),
  () => agent(`Read only these files and extract open items (things named as remaining, unfinished, gaming-only, judge-only, risk, TODO): examples/figtree/probes/FOLD-REPORT.md (section about what remains), .design-sync/NOTES.md (Re-sync risks), docs/workflows/README.md (any "not run live" or validation caveats), docs/HANDOFF.md (level 3 open items, if present). Return {items:[{source: file path, item: one line ≤ 140 chars, priority: 1 (blocks the next step) to 3 (nice to have)}]}, at most 12 items, deduplicated. ${noPaste}`, { label: 'open items', phase: 'Measure', schema: ITEMS, effort: 'low' }),
])

const missing = [['tests', tests], ['eval', evalr], ['git', git], ['open items', items]].filter(([, v]) => !v).map(([k]) => k)
if (missing.length) log(`measure stage lost: ${missing.join(', ')} (the status will say so)`)

phase('Write')
const summary = JSON.stringify({ tests, eval: evalr, git, open_items: items && items.items, expected_branch: branch, missing })
const written = await agent(`Write the file ${out} (markdown, ≤ 60 lines) titled "# Resume today (generated by figtree-handoff)" from this measured state (JSON): ${summary}
Sections, in this order: Commands (git checkout the branch, install, run tests, run eval); State (tests passed/failed, eval probes/recall/precision with the per-rubric table, git branch and whether the tree is clean and pushed; name any measure that is missing as "not measured this run"); Open items (numbered, priority order, with the source file in parentheses); What to read first (docs/HANDOFF.md levels 0-2, .claude/skills/figtree-process/SKILL.md). Plain sentences, no em-dashes. Do not edit any other file. Return {path, lines}.`, { label: 'status', phase: 'Write', schema: WRITE, effort: 'low' })

return { tests, eval: evalr, git, open_items: items && items.items, status_md: written && written.path, missing }
