export const meta = {
  name: 'figtree-judge-panel',
  description: 'Three image-space judges with distinct lenses score each SVG with figtree judge; verdicts are synthesized per SVG and ranked',
  whenToUse: 'You need a defensible quality ranking of several candidate figures (or the same figure after several refinement runs) that no measurable check can give',
  phases: [
    { title: 'Judge', detail: 'per SVG: faithfulness-vs-source, readability-at-a-glance, aesthetics/medium-fit judges run figtree judge' },
    { title: 'Synthesize', detail: 'one verdict object per SVG from the three panels, then a ranking' },
  ],
}

// Model tiers (optional): args.model for every agent, args.cheap_model for the mechanical stages
// (effort 'low'). Omit both to inherit the session model. Small models work because every prompt
// is a spec card: one command, one file, one JSON shape.
const MODEL = args.model || undefined
const CHEAP = args.cheap_model || MODEL
const run = (prompt, opts = {}) => agent(prompt, { ...((opts.effort === 'low' && CHEAP) ? { model: CHEAP } : MODEL ? { model: MODEL } : {}), ...opts })

// args: {svgs: [path | {svg, source?}], rubric}
const rubric = args.rubric || 'teaching'
const items = (args.svgs || []).map((s) => (typeof s === 'string' ? { svg: s, source: args.source || '' } : { svg: s.svg, source: s.source || args.source || '' }))
if (!items.length) throw new Error('figtree-judge-panel needs args {svgs: [...], rubric}')
const outDir = args.out_dir || '/tmp/figtree-judge-panel'

const LENSES = [
  { id: 'faithfulness', brief: 'FAITHFULNESS VS SOURCE: weigh semantic_coverage and hallucination_control above all; a pretty figure that invents or omits a mechanism is a failure.' },
  { id: 'readability', brief: 'READABILITY AT A GLANCE: weigh readability, flow_clarity and compactness; ask what a reader gets in five seconds and where the eye gets lost.' },
  { id: 'aesthetics', brief: 'AESTHETICS AND MEDIUM FIT: weigh polish, medium_fit and typography; ask whether it looks native to its medium (paper, teaching page, slide, tile, icon).' },
]

const JUDGE_SCHEMA = {
  type: 'object',
  properties: {
    overall: { type: 'number' },
    dimensions: {
      type: 'object',
      additionalProperties: {
        type: 'object',
        properties: { score: { type: 'integer' }, why: { type: 'string' } },
        required: ['score', 'why'],
      },
    },
    vetoes: { type: 'array', items: { type: 'string' } },
    headline: { type: 'string' },
  },
  required: ['overall', 'dimensions', 'vetoes', 'headline'],
}

function judgePrompt(item, lens, index) {
  const sourceFlag = item.source ? ` --source ${item.source}` : ''
  const report = `${outDir}/judge-${index}-${lens.id}.json`
  return `You are one of three judges on a panel; your lens: ${lens.brief}
Run exactly this command from the repo root (it renders the SVG and asks the image judge; it may take a minute):

  python3 -m figtree judge ${item.svg} --rubric ${rubric}${sourceFlag} --report ${report}

Read ${report} (small JSON: scores, justifications, vetoes). Re-weigh it through your lens: you may move any dimension by at most 2 points from the report's score when your lens sees something the generic judge under- or over-weighted, and you must say why in one line.
Return only JSON: {overall: number (mean of your dimension scores, 2 decimals), dimensions: {<dimension>: {score: 1-10 integer, why: one line}}, vetoes: [strings], headline: one sentence}. Use every dimension key present in the report. Do not paste file contents into your answer; never include SVG or PNG data.`
}

phase('Judge')
const panels = await pipeline(
  items,
  (item, _orig, index) =>
    parallel(LENSES.map((lens) => () => run(judgePrompt(item, lens, index), { phase: 'Judge', label: `${lens.id} #${index}`, schema: JUDGE_SCHEMA }))).then((rs) =>
      rs.map((r, k) => (r ? { lens: LENSES[k].id, ...r } : null)).filter(Boolean),
    ),
  (judgements, item) => {
    // synthesis is arithmetic on three small objects: no agent needed
    const dims = {}
    for (const j of judgements) {
      for (const [d, v] of Object.entries(j.dimensions || {})) {
        if (!dims[d]) dims[d] = { scores: [], why: [] }
        dims[d].scores.push(v.score)
        dims[d].why.push(`${j.lens}: ${v.why}`)
      }
    }
    const dimensions = {}
    for (const [d, v] of Object.entries(dims)) {
      dimensions[d] = { score: Math.round((v.scores.reduce((a, b) => a + b, 0) / v.scores.length) * 100) / 100, min: Math.min(...v.scores), why: v.why }
    }
    const overalls = judgements.map((j) => j.overall)
    const overall = overalls.length ? Math.round((overalls.reduce((a, b) => a + b, 0) / overalls.length) * 100) / 100 : null
    const vetoes = [...new Set(judgements.flatMap((j) => j.vetoes || []))]
    const spread = overalls.length ? Math.round((Math.max(...overalls) - Math.min(...overalls)) * 100) / 100 : null
    return { svg: item.svg, overall, spread, judges: judgements.length, vetoes, dimensions, headlines: judgements.map((j) => `${j.lens}: ${j.headline}`) }
  },
)

phase('Synthesize')
const verdicts = panels.filter(Boolean)
const missing = items.filter((it) => !verdicts.some((v) => v.svg === it.svg)).map((it) => it.svg)
for (const m of missing) log(`no verdict for ${m} (judges failed)`)
for (const v of verdicts) if (v.judges < 3) log(`${v.svg}: only ${v.judges}/3 judges answered`)
const ranking = verdicts
  .filter((v) => v.overall !== null)
  .sort((a, b) => b.overall - a.overall || a.vetoes.length - b.vetoes.length)
  .map((v, rank) => ({ rank: rank + 1, svg: v.svg, overall: v.overall, vetoes: v.vetoes.length, spread: v.spread }))
if (ranking.length) log(`winner: ${ranking[0].svg} (${ranking[0].overall})`)

return { rubric, ranking, verdicts, missing }
