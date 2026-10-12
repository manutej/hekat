export const meta = {
  name: 'figtree-digest',
  description: 'Plan figure units over a body of documents with figtree digest, then generate, score and (when < 8) refine each unit; a completeness critic reports what was skipped',
  whenToUse: 'A directory of markdown docs, papers, skills or specs should become a gallery of scored figures, one unit per section, fanned out over small-context agents',
  phases: [
    { title: 'Plan', detail: 'one scout runs figtree digest --plan and returns the unit manifest' },
    { title: 'Generate', detail: 'figtree digest --unit ID per unit (svg + report + score on disk)' },
    { title: 'Score', detail: 'read the unit score json, return overall and requests' },
    { title: 'Refine', detail: 'one figtree refine round when overall < 8' },
    { title: 'Critique', detail: 'completeness critic reads the manifest and lists what was skipped and why' },
  ],
}

// args: {inputs: [paths] | {dir}, rubric, out_dir, max_units?, style?}
const inputs = Array.isArray(args.inputs) ? args.inputs : args.inputs && args.inputs.dir ? [args.inputs.dir] : []
const rubric = args.rubric || 'teaching'
const outDir = args.out_dir
const maxUnits = args.max_units || 0
const styleFlag = args.style ? ` --style ${args.style}` : ''
if (!inputs.length || !outDir) throw new Error('figtree-digest needs args {inputs: [paths] | {dir}, out_dir} (rubric, max_units, style optional)')
const REFINE_BELOW = 8

const MANIFEST_SCHEMA = {
  type: 'object',
  properties: {
    manifest_path: { type: 'string' },
    units: {
      type: 'array',
      items: {
        type: 'object',
        properties: { id: { type: 'string' }, title: { type: 'string' }, source: { type: 'string' }, est_components: { type: 'integer' } },
        required: ['id', 'title', 'source'],
      },
    },
    skipped: { type: 'integer' },
  },
  required: ['manifest_path', 'units', 'skipped'],
}

const GEN_SCHEMA = {
  type: 'object',
  properties: { svg: { type: 'string' }, overall: { type: 'number' }, issues: { type: 'integer' }, faithfulness_failures: { type: 'integer' } },
  required: ['svg', 'overall', 'issues'],
}

const SCORE_SCHEMA = {
  type: 'object',
  properties: {
    overall: { type: 'number' },
    critical: { type: 'integer' },
    requests: { type: 'array', items: { type: 'string' } },
  },
  required: ['overall', 'critical', 'requests'],
}

const REFINE_SCHEMA = {
  type: 'object',
  properties: {
    overall_before: { type: 'number' },
    overall_after: { type: 'number' },
    edits_applied: { type: 'integer' },
    output_svg: { type: 'string' },
    remaining_requests: { type: 'array', items: { type: 'string' } },
  },
  required: ['overall_before', 'overall_after', 'edits_applied', 'output_svg', 'remaining_requests'],
}

const CRITIC_SCHEMA = {
  type: 'object',
  properties: {
    skipped: {
      type: 'array',
      items: {
        type: 'object',
        properties: { source: { type: 'string' }, title: { type: 'string' }, reason: { type: 'string' }, worth_a_figure: { type: 'boolean' } },
        required: ['source', 'title', 'reason', 'worth_a_figure'],
      },
    },
    not_covered: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' },
  },
  required: ['skipped', 'not_covered', 'summary'],
}

// 1. scout: one agent plans the units
phase('Plan')
const scout = await agent(
  `You are the SCOUT. Run exactly this command from the repo root:

  python3 -m figtree digest --plan ${inputs.join(' ')} -o ${outDir} --rubric ${rubric}${styleFlag}

Then read ${outDir}/manifest.json (small JSON). Return only JSON: {manifest_path: "${outDir}/manifest.json", units: [{id, title, source, est_components}] in manifest order, skipped: <length of the manifest's skipped list>}. Do not paste file contents into your answer.`,
  { label: 'scout', schema: MANIFEST_SCHEMA, effort: 'low' },
)
if (!scout || !scout.units) throw new Error('scout returned no manifest')
let units = scout.units
if (maxUnits && units.length > maxUnits) {
  for (const u of units.slice(maxUnits)) log(`dropped by max_units=${maxUnits}: ${u.id} (${u.source})`)
  units = units.slice(0, maxUnits)
}
log(`${units.length} unit(s) planned, ${scout.skipped} section(s) skipped by the planner`)

// 2-4. generate -> score -> refine (if < 8), per unit, no barrier
const done = await pipeline(
  units,
  (u) =>
    agent(
      `You are the GENERATOR for unit "${u.id}" (${u.title}). Run exactly:

  python3 -m figtree digest --unit ${u.id} -o ${outDir} --rubric ${rubric}${styleFlag}

It prints one JSON line {id, title, source, svg, overall, issues, critical, status}. Return only JSON: {svg: <svg path>, overall, issues, faithfulness_failures: <length of "faithfulness_failures" in ${outDir}/${u.id}.score.json, or 0>}. Do not paste file contents into your answer; never include the SVG.`,
      { phase: 'Generate', label: `generate ${u.id}`, schema: GEN_SCHEMA, effort: 'low' },
    ),
  (gen, u) => {
    if (!gen) throw new Error(`generation failed for ${u.id}`)
    return agent(
      `You are the SCORER for unit "${u.id}". Read only ${outDir}/${u.id}.score.json (small JSON written by the generator). Return only JSON: {overall: <overall>, critical: <count of issues with severity "critical">, requests: [for each issue whose auto_edit is null: "<code_anchor>: <fix_instruction>" trimmed to 160 chars, at most 8]}. Do not paste file contents into your answer.`,
      { phase: 'Score', label: `score ${u.id}`, schema: SCORE_SCHEMA, effort: 'low' },
    ).then((score) => ({ gen, score }))
  },
  async ({ gen, score }, u) => {
    const overall = score ? score.overall : gen.overall
    const row = { id: u.id, title: u.title, source: u.source, svg: gen.svg, overall, critical: score ? score.critical : null, status: overall >= REFINE_BELOW ? 'ok' : 'low' }
    if (overall >= REFINE_BELOW) return row
    const source = u.source
    const refined = await agent(
      `You are the REPAIRER for unit "${u.id}" (scored ${overall} on the ${rubric} rubric). Input SVG: ${gen.svg}. Content requests: ${score && score.requests.length ? score.requests.map((r, i) => `(${i + 1}) ${r}`).join(' ') : '(none)'}.
If there are content requests, decide each and write an edit script ${outDir}/${u.id}.edits.json: a JSON list containing ONE inner list of ops (figtree.edits ops set_attr/set_text/translate/recolor/delete/insert/scale_font/set_canvas/center_content, each addressing an existing id; find ids with  grep -o 'id="[^"]*"' ${gen.svg} | head -60). Then run exactly (append --edits ${outDir}/${u.id}.edits.json only if you wrote it):

  python3 -m figtree refine ${gen.svg} --rubric ${rubric} --source ${source} --rounds 1 -o ${outDir}/${u.id}.refined.svg --trajectory ${outDir}/${u.id}.trajectory.json

Read ${outDir}/${u.id}.trajectory.json (small JSON). Return only JSON: {overall_before: initial.overall, overall_after: final.overall, edits_applied: trajectory[last].edits_applied, output_svg: "${outDir}/${u.id}.refined.svg", remaining_requests: [requests_remaining as "<code_anchor>: <fix_instruction>" trimmed to 160 chars]}. Do not paste file contents into your answer; never include the SVG.`,
      { phase: 'Refine', label: `refine ${u.id}`, schema: REFINE_SCHEMA, effort: 'low' },
    )
    if (!refined) return { ...row, status: 'low (refine failed)' }
    return { ...row, svg: refined.output_svg, overall_before_refine: refined.overall_before, overall: refined.overall_after, edits_applied: refined.edits_applied, remaining_requests: refined.remaining_requests.length, status: refined.overall_after >= REFINE_BELOW ? 'refined' : 'low after refine' }
  },
)

const rows = done.filter(Boolean)
const failed = units.filter((u) => !rows.some((r) => r.id === u.id)).map((u) => u.id)
for (const f of failed) log(`unit ${f}: a stage failed; not in the result`)

// 5. completeness critic
phase('Critique')
const critic = await agent(
  `You are the COMPLETENESS CRITIC. Read only ${outDir}/manifest.json (small JSON). Its "skipped" list names the sections the planner did not turn into figures and why; its "units" list is what was generated${maxUnits ? `; the orchestrator additionally dropped every unit after the first ${maxUnits}` : ''}${failed.length ? `; these units failed in generation: ${failed.join(', ')}` : ''}.
For every skipped entry judge from its title and reason (do not open the source documents unless a title is ambiguous, and then read at most 40 lines) whether a figure would still have been worth making. Return only JSON: {skipped: [{source, title, reason, worth_a_figure: boolean}], not_covered: [one line per gap a reader of the gallery would notice, including max_units drops and failures], summary: one sentence}. Do not paste file contents into your answer.`,
  { label: 'completeness critic', schema: CRITIC_SCHEMA, effort: 'low' },
)

const low = rows.filter((r) => r.overall < REFINE_BELOW).length
log(`${rows.length} unit(s) done, ${low} still below ${REFINE_BELOW}, ${failed.length} failed`)
return {
  manifest_path: scout.manifest_path,
  rubric,
  units: rows.map((r) => ({ id: r.id, title: r.title, svg: r.svg, overall: r.overall, status: r.status })),
  details: rows,
  skipped: critic ? critic.skipped : [],
  not_covered: critic ? critic.not_covered : [],
  critic_summary: critic ? critic.summary : null,
  failed,
}
