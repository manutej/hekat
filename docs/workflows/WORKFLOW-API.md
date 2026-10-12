# Workflow script API (Claude Code `Workflow` tool) — condensed reference

Scripts live in `.claude/workflows/<name>.js`, are plain JavaScript (no TypeScript syntax), run in an
async context (top-level `await` is fine), and are started with `Workflow({name: "<name>", args: ...})`.

Every script begins with a PURE LITERAL `meta` (no variables, calls or interpolation):

```js
export const meta = {
  name: 'figtree-refine',
  description: 'one line, shown in the permission dialog',
  whenToUse: 'optional, shown in the workflow list',
  phases: [{ title: 'Score', detail: '...' }, { title: 'Repair', detail: '...' }],
}
```

Globals available in the script body:

- `agent(prompt, opts?) -> Promise<any>` — spawn a subagent. Without `schema` it returns the agent's
  final text; with `schema` (JSON Schema, root `{type:'object', properties:{...}, required:[...]}`)
  the agent is forced to return a validated object. Returns `null` if the agent dies or is skipped.
  `opts`: `label`, `phase` (progress group; use inside pipeline/parallel stages), `schema`, `model`
  (omit by default), `effort` ('low'|'medium'|'high'|'xhigh'|'max'; 'low' for mechanical stages),
  `isolation: 'worktree'` (only when agents mutate files in parallel), `agentType`.
- `pipeline(items, stage1, stage2, ...) -> Promise<any[]>` — each item flows through all stages with
  NO barrier between stages. Every stage receives `(prevResult, originalItem, index)`. A stage that
  throws drops the item to `null`. DEFAULT for multi-stage work.
- `parallel(thunks) -> Promise<any[]>` — barrier: runs `() => Promise` thunks concurrently and waits
  for all; a failing thunk resolves to `null`. Use only when a stage needs ALL prior results (dedup,
  early exit, cross-item comparison).
- `phase(title)`, `log(message)` — progress display / narrator line.
- `args` — the `args` value passed to the Workflow tool, verbatim (arrays/objects as JSON values).
- `budget` — `{total, spent(), remaining()}`; guard loops with `budget.total &&`.
- `workflow(nameOrRef, args?)` — run another saved workflow inline (one nesting level).

Forbidden in scripts: `Date.now()`, `Math.random()`, argless `new Date()` (they break resume), any
filesystem or Node API. Timestamps come in through `args`. Concurrency is capped at
min(16, cpus-2); the lifetime cap is 1000 agents.

Subagents receive the repo's CLAUDE.md automatically and are told their final text IS the return
value, so prompts should ask for data, not prose. Agents can run Bash, read files, and reach MCP
tools via ToolSearch.

Patterns: adversarial verify (N refuters per claim, majority rules); perspective-diverse verify
(one lens per verifier); judge panel (N attempts, parallel judges, synthesize from the winner);
loop-until-dry (stop after K empty rounds); multi-modal sweep; completeness critic; no silent caps
(`log()` what was dropped).

Resume: `Workflow({scriptPath, resumeFromRunId})` replays the unchanged prefix of agent() calls from
cache; the journal at `<transcriptDir>/journal.jsonl` records every agent's return value.
