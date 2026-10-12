export const meta = {
  name: 'figtree-research',
  description: 'Turn a documentation corpus into figure-ready spec docs: researchers write one spec per workflow, a mechanical checker verifies evidence and grounding, fixers repair until the check passes, a synthesizer writes the overview',
  whenToUse: 'A concept space is documented in pages (product docs, READMEs, tutorials) rather than a paper, and you want small-context agents (Sonnet for writing, Haiku for checking) to produce specs that figtree digest can draw faithfully',
  phases: [
    { title: 'Scout', detail: 'one agent lists the corpus and proposes the workflows to specify (or args.topics is used as given)' },
    { title: 'Research', detail: 'per topic: researcher writes the spec from ≤ 4 pages' },
    { title: 'Check', detail: 'per topic: python -m figtree spec check; fixer repairs from the check list, up to 2 rounds' },
    { title: 'Synthesize', detail: 'one agent writes the overview spec (how the workflows coordinate) and checks it' },
  ],
}

// args: {corpus_dir, out_dir, topics?: [{id, title, files:[names in corpus], question}], max_topics?, model?, cheap_model?, format?}
const corpus = args.corpus_dir
const outDir = args.out_dir
const FORMAT = args.format || 'examples/figtree/langflow/SPEC-FORMAT.md'
const maxTopics = args.max_topics || 8
if (!corpus || !outDir) throw new Error('figtree-research needs args {corpus_dir, out_dir} (topics, max_topics, model, cheap_model, format optional)')

const MODEL = args.model || undefined
const CHEAP = args.cheap_model || MODEL
const run = (prompt, opts = {}) => agent(prompt, { ...((opts.effort === 'low' && CHEAP) ? { model: CHEAP } : MODEL ? { model: MODEL } : {}), ...opts })

const TOPICS_SCHEMA = {
  type: 'object',
  properties: {
    topics: {
      type: 'array',
      items: {
        type: 'object',
        properties: { id: { type: 'string' }, title: { type: 'string' }, files: { type: 'array', items: { type: 'string' } }, question: { type: 'string' } },
        required: ['id', 'title', 'files', 'question'],
      },
    },
    corpus_files: { type: 'integer' },
  },
  required: ['topics', 'corpus_files'],
}
const SPEC_SCHEMA = {
  type: 'object',
  properties: { spec: { type: 'string' }, components: { type: 'integer' }, flows: { type: 'integer' }, evidence_lines: { type: 'integer' }, sources: { type: 'array', items: { type: 'string' } } },
  required: ['spec', 'components', 'flows', 'evidence_lines', 'sources'],
}
const CHECK_SCHEMA = {
  type: 'object',
  properties: {
    ok: { type: 'boolean' }, components: { type: 'integer' }, flows: { type: 'integer' },
    evidence_missing: { type: 'array', items: { type: 'string' } },
    components_without_evidence: { type: 'array', items: { type: 'string' } },
    unknown_icons: { type: 'array', items: { type: 'string' } },
    unknown_kinds: { type: 'array', items: { type: 'string' } },
    unknown_flow_names: { type: 'array', items: { type: 'string' } },
    contradictions: { type: 'array', items: { type: 'string' } },
    not_grounded: { type: 'array', items: { type: 'string' } },
    flows_not_grounded: { type: 'array', items: { type: 'string' } },
    prose_arrows: { type: 'integer' },
  },
  required: ['ok', 'components', 'flows', 'evidence_missing', 'components_without_evidence', 'unknown_icons', 'unknown_kinds', 'unknown_flow_names', 'contradictions', 'not_grounded', 'flows_not_grounded', 'prose_arrows'],
}
const FIX_SCHEMA = { type: 'object', properties: { spec: { type: 'string' }, changes: { type: 'array', items: { type: 'string' } } }, required: ['spec', 'changes'] }

const DONT = `DON'T: paste file contents into your answer; invent a component or flow the pages do not state (list the gap under "## Not in the documentation" instead); reword a quote (quotes are verbatim substrings of a corpus file, ≤ 200 chars); write both A → B and B → A; use arrows outside the Flows section.`

const checkCmd = (spec) => `python3 -m figtree spec check ${spec} --corpus ${corpus}`

function scoutPrompt() {
  return `ROLE: SCOUT for a documentation corpus.
INPUT: run  ls ${corpus}  and read ${corpus}/SOURCES.md if it exists (≤ 40 lines). Then read the first 25 lines of at most 12 files whose names suggest agents, flows, tools, memory, MCP, playground or API.
TASK: propose at most ${maxTopics} workflows worth one figure each: a workflow is a thing a user builds or that the system executes (an agent calling tools; a flow run through the API; memory across sessions; an MCP server exposing flows; multi-agent delegation), NOT a reference page. Each topic names 2-4 corpus files that document it and a one-sentence question the figure must answer.
OUTPUT: {topics: [{id: "kebab-case", title: "Noun phrase", files: ["file.mdx", ...], question: "..."}], corpus_files: <count from ls>}. Example topic: {id: "agent-with-tools", title: "An agent calling tools", files: ["Agents_agents.mdx", "Agents_agents-tools.mdx"], question: "What connects to what when an agent uses tools?"}.
DONE WHEN: ids are unique, every file exists in the corpus, topics ≤ ${maxTopics}.
DON'T: paste file contents; propose topics the files do not cover; exceed 4 files per topic.`
}

function researchPrompt(t) {
  const files = t.files.slice(0, 4).map((f) => `${corpus}/${f}`).join(' ')
  return `ROLE: RESEARCHER for the workflow "${t.title}" (id ${t.id}). Question the figure must answer: ${t.question}
INPUT: read ${FORMAT} (the format, ≤ 120 lines) and then these pages only: ${files}. Read each page fully but skip code blocks and parameter tables after the first screen; you need the components, the ports and what connects to what.
TASK: write ${outDir}/${t.id}.md in exactly the format: H1 title, one or two sentences, "## Components" (3-9 bullets "- **Name** (kind: k, icon: i): role", names 1-3 words in the docs' own terms, icons from the family list in the format doc), "## Flows" (arrow lines, one direction per pair, "(control)" for tool calls/triggers, "(feedback)" for loops), "## Steps" (3-7 numbered imperative sentences), an optional "## Not in the documentation" list, and a fenced block tagged evidence with one verbatim quote per component and per control/feedback flow, each naming its corpus file.
COMMAND (after writing): ${checkCmd(`${outDir}/${t.id}.md`)}   and read only its JSON output.
OUTPUT: {spec: "${outDir}/${t.id}.md", components: <from the check>, flows: <from the check>, evidence_lines: <from the check>, sources: [corpus file names you quoted]}.
DONE WHEN: the file exists and the check printed "ok": true, or you have run the check twice and fixed what it listed (evidence_missing means the quote is not verbatim: copy it again from the page; not_grounded means the name in Flows differs from the name in Components).
${DONT}`
}

function checkPrompt(spec) {
  return `ROLE: CHECKER for ${spec}.
COMMAND (run exactly, from the repo root): ${checkCmd(spec)}
INPUT: only the command's stdout (JSON).
OUTPUT: return that JSON object's fields ok, components, flows, evidence_missing, components_without_evidence, unknown_icons, unknown_kinds, unknown_flow_names, contradictions, not_grounded, flows_not_grounded, prose_arrows; trim every list to its first 8 items.
DONE WHEN: you have returned the JSON once. DON'T: open the spec or the corpus; rewrite the spec; add fields.`
}

function fixPrompt(spec, check, round) {
  const items = []
  for (const q of check.evidence_missing) items.push(`evidence not found verbatim -> reopen the named corpus file, copy the sentence exactly (≤ 200 chars), or pick a different sentence: ${q}`)
  for (const c of check.components_without_evidence) items.push(`component has no evidence line -> add one verbatim quote from the corpus naming it, or remove the component and its flows: ${c}`)
  for (const i of check.unknown_icons) items.push(`unknown icon -> choose one from the family list in ${FORMAT}: ${i}`)
  for (const k of check.unknown_kinds) items.push(`unknown kind -> one of block, store, document, decision, terminal, actor, process: ${k}`)
  for (const n of check.unknown_flow_names) items.push(`flow names a component that is not in Components -> add the bullet or spell the name exactly as the bullet: ${n}`)
  for (const c of check.contradictions) items.push(`both directions present -> keep one (tool call = Agent → Tool as control; return = leave implicit): ${c}`)
  for (const n of check.not_grounded) items.push(`the grounder did not recover this component -> make sure it appears in a Flows arrow line with the exact bullet name: ${n}`)
  for (const f of check.flows_not_grounded) items.push(`the grounder did not recover this flow -> write it as its own arrow line "A → B" with names spelled exactly as the bullets: ${f}`)
  if (check.prose_arrows) items.push(`${check.prose_arrows} arrow(s) outside the Flows section -> replace with the word "then"`)
  if (check.components < 3) items.push(`only ${check.components} components -> add the missing actors the pages name (inputs, outputs, tools, stores)`)
  if (check.components > 9) items.push(`${check.components} components -> keep the 9 that answer the figure's question; move the rest to "## Not in the documentation" or a second spec`)
  if (check.flows < 2) items.push(`only ${check.flows} flows -> every component must connect; add the arrow lines the pages describe`)
  return `ROLE: FIXER (round ${round}) for ${spec}.
INPUT: read ${spec} (≤ 80 lines) and ${FORMAT} (≤ 120 lines); reopen a corpus page under ${corpus} only when an item below says so.
TASK: apply each item, nothing else:
${items.map((s, i) => `  ${i + 1}. ${s}`).join('\n')}
COMMAND (after editing): ${checkCmd(spec)}
OUTPUT: {spec: "${spec}", changes: [one line per item applied, ≤ 8]}.
DONE WHEN: the check prints "ok": true, or every item above has been applied once.
${DONT}`
}

// 1. scout
phase('Scout')
let topics = Array.isArray(args.topics) && args.topics.length ? args.topics : null
let corpusFiles = null
if (!topics) {
  const s = await run(scoutPrompt(), { label: 'scout', schema: TOPICS_SCHEMA })
  if (!s || !s.topics.length) throw new Error('scout proposed no topics')
  topics = s.topics
  corpusFiles = s.corpus_files
}
if (topics.length > maxTopics) {
  for (const t of topics.slice(maxTopics)) log(`dropped by max_topics=${maxTopics}: ${t.id}`)
  topics = topics.slice(0, maxTopics)
}
log(`${topics.length} topic(s): ${topics.map((t) => t.id).join(', ')}`)

// 2-3. research -> check -> fix (≤ 2 rounds) per topic, no barrier
const results = await pipeline(
  topics,
  (t) => run(researchPrompt(t), { phase: 'Research', label: `research ${t.id}`, schema: SPEC_SCHEMA }),
  async (r, t) => {
    if (!r) throw new Error(`research failed for ${t.id}`)
    let check = await run(checkPrompt(r.spec), { phase: 'Check', label: `check ${t.id}`, schema: CHECK_SCHEMA, effort: 'low' })
    let rounds = 0
    const changes = []
    while (check && !check.ok && rounds < 2) {
      rounds += 1
      const fix = await run(fixPrompt(r.spec, check, rounds), { phase: 'Check', label: `fix ${t.id} r${rounds}`, schema: FIX_SCHEMA })
      if (fix) changes.push(...fix.changes)
      check = await run(checkPrompt(r.spec), { phase: 'Check', label: `recheck ${t.id} r${rounds}`, schema: CHECK_SCHEMA, effort: 'low' })
    }
    return { id: t.id, title: t.title, spec: r.spec, sources: r.sources, ok: Boolean(check && check.ok), components: check ? check.components : r.components, flows: check ? check.flows : r.flows, fix_rounds: rounds, changes, remaining: check && !check.ok ? [...check.evidence_missing, ...check.not_grounded, ...check.flows_not_grounded, ...check.contradictions].slice(0, 6) : [] }
  },
)
const rows = results.filter(Boolean)
const failed = topics.filter((t) => !rows.some((r) => r.id === t.id)).map((t) => t.id)
for (const f of failed) log(`topic ${f}: a stage failed`)

// 4. synthesizer: the overview spec
phase('Synthesize')
const okRows = rows.filter((r) => r.ok)
const overviewSpec = `${outDir}/00-overview.md`
const synth = await run(`ROLE: SYNTHESIZER. The researchers wrote these spec docs (read each, ≤ 80 lines): ${okRows.map((r) => r.spec).join(' ')}. Read ${FORMAT} too.
TASK: write ${overviewSpec}: the one figure that shows how the workflows coordinate in this concept space. Its components are the 5-9 actors that appear across several specs (the user, the agent, tools, stores, the runtime, external clients); its flows are the connections the specs agree on; each evidence line may reuse a quote from a spec's evidence block (same file name). Add "## Steps" as the order in which a reader should learn the workflows, one per spec, naming the spec id.
COMMAND (after writing): ${checkCmd(overviewSpec)}
OUTPUT: {spec: "${overviewSpec}", components, flows, evidence_lines, sources: [spec ids used]}.
DONE WHEN: the check prints "ok": true or you fixed what it listed once.
${DONT}`, { label: 'overview', schema: SPEC_SCHEMA })
const overviewCheck = synth ? await run(checkPrompt(overviewSpec), { label: 'check overview', schema: CHECK_SCHEMA, effort: 'low' }) : null

log(`${okRows.length}/${rows.length} spec(s) pass the check; overview ${overviewCheck && overviewCheck.ok ? 'ok' : 'needs work'}`)
return {
  corpus, out_dir: outDir, corpus_files: corpusFiles,
  specs: rows.map((r) => ({ id: r.id, title: r.title, spec: r.spec, ok: r.ok, components: r.components, flows: r.flows, fix_rounds: r.fix_rounds, remaining: r.remaining })),
  overview: synth ? { spec: overviewSpec, ok: Boolean(overviewCheck && overviewCheck.ok), components: overviewCheck ? overviewCheck.components : null } : null,
  failed,
}
