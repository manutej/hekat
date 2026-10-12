export const meta = {
  name: 'figtree-refine',
  description: 'Score an SVG against a rubric, repair it one round at a time, stop when no requests remain or the score plateaus',
  whenToUse: 'An existing SVG (figure, chart, slide, tile) needs to reach a rubric target and you want the loop run by small-context agents that hand back verdicts, not the SVG',
  phases: [
    { title: 'Score', detail: 'figtree score --json: overall, per-dimension scores, anchored issues, content requests' },
    { title: 'Repair', detail: 'figtree refine --rounds 1 plus an edit script for the content requests; returns before/after' },
  ],
}

// Model tiers (optional): args.model for every agent, args.cheap_model for the mechanical stages
// (effort 'low'). Omit both to inherit the session model. Small models work because every prompt
// is a spec card: one command, one file, one JSON shape.
const MODEL = args.model || undefined
const CHEAP = args.cheap_model || MODEL
const run = (prompt, opts = {}) => agent(prompt, { ...((opts.effort === 'low' && CHEAP) ? { model: CHEAP } : MODEL ? { model: MODEL } : {}), ...opts })

// args: {svg, rubric, source?, rounds?, out_dir}
const svg = args.svg
const rubric = args.rubric || 'teaching'
const source = args.source || ''
const rounds = Math.max(1, Math.min(args.rounds || 4, 8))
const outDir = args.out_dir
if (!svg || !outDir) throw new Error('figtree-refine needs args {svg, out_dir} (rubric, source, rounds optional)')

const sourceFlag = source ? ` --source ${source}` : ''

const SCORE_SCHEMA = {
  type: 'object',
  properties: {
    overall: { type: 'number' },
    scores: { type: 'object' },
    issues: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          check_id: { type: 'string' },
          severity: { type: 'string' },
          anchor: { type: 'string' },
          fix: { type: 'string' },
        },
        required: ['check_id', 'severity', 'anchor', 'fix'],
      },
    },
    requests: { type: 'array', items: { type: 'string' } },
  },
  required: ['overall', 'scores', 'issues', 'requests'],
}

const REPAIR_SCHEMA = {
  type: 'object',
  properties: {
    overall_before: { type: 'number' },
    overall_after: { type: 'number' },
    edits_applied: { type: 'integer' },
    remaining_requests: { type: 'array', items: { type: 'string' } },
    output_svg: { type: 'string' },
    note: { type: 'string' },
  },
  required: ['overall_before', 'overall_after', 'edits_applied', 'remaining_requests', 'output_svg'],
}

function scorePrompt(file, round) {
  return `You are the SCORER for round ${round} of a figtree refinement loop. Run exactly this command from the repo root:

  python3 -m figtree score ${file} --rubric ${rubric}${sourceFlag} --json

Read only its stdout (a QualityReport JSON). Do not open the SVG and do not paste file contents into your answer.
Return a JSON object with this schema, at most 2 KB total:
  {overall: number, scores: {dimension: number|null}, issues: [{check_id, severity, anchor, fix}], requests: [string]}
- issues: one entry per issue in the report; check_id = issue.check_id (use "unclassified" when null), severity = issue.severity, anchor = issue.code_anchor, fix = issue.fix_instruction trimmed to 120 characters. Keep at most 12 issues (critical first).
- requests: for every issue whose auto_edit is null, one line "<code_anchor>: <fix_instruction>" trimmed to 160 characters. These are the content decisions a repairer must make.
No prose, no markdown, no SVG.`
}

function repairPrompt(file, outFile, round, score) {
  const requests = (score.requests || []).slice(0, 8)
  return `You are the REPAIRER for round ${round} of a figtree refinement loop. Input SVG: ${file}. Rubric: ${rubric}. Current overall: ${score.overall}.
Content requests from the scorer (each needs a decision, the mechanical issues are fixed automatically):
${requests.length ? requests.map((r, i) => `  ${i + 1}. ${r}`).join('\n') : '  (none)'}

Steps:
1. If there are content requests, decide each one and write an edit script to ${outDir}/edits-round${round}.json: a JSON list with ONE inner list of edit ops (figtree.edits ops: set_attr, set_text, translate, recolor, delete, insert, scale_font, set_canvas, center_content; every op addresses an existing element id, e.g. {"op":"set_text","id":"t3","text":"Encoder"}). Look up the ids you need with: grep -o 'id="[^"]*"' ${file} | head -80. Skip a request you cannot resolve safely and list it in remaining_requests.
2. Run exactly (add --edits ${outDir}/edits-round${round}.json only if you wrote that file):
     python3 -m figtree refine ${file} --rubric ${rubric}${sourceFlag} --rounds 1 -o ${outFile} --trajectory ${outDir}/trajectory-round${round}.json [--edits ${outDir}/edits-round${round}.json]
3. Read ${outDir}/trajectory-round${round}.json (small JSON) for initial.overall, final.overall, trajectory[last].edits_applied and requests_remaining.

Return only this JSON object (max 2 KB): {overall_before, overall_after, edits_applied, remaining_requests: [string, each "<code_anchor>: <fix_instruction>" trimmed to 160 chars], output_svg: "${outFile}", note: one line}.
Do not paste file contents into your answer. Never include the SVG.`
}

const history = []
let current = svg
let best = -1
let stale = 0
let stopReason = 'round budget exhausted'

for (let round = 1; round <= rounds; round++) {
  const outFile = `${outDir}/round${round}.svg`
  const [repair] = await pipeline(
    [current],
    (file) => run(scorePrompt(file, round), { phase: 'Score', label: `score r${round}`, schema: SCORE_SCHEMA, effort: 'low' }),
    (score, file) => {
      if (!score) throw new Error('scorer returned nothing')
      history.push({ round, stage: 'score', overall: score.overall, issues: score.issues.length, requests: score.requests.length })
      if (score.requests.length === 0 && score.issues.length === 0) return { skip: true, score }
      return run(repairPrompt(file, outFile, round, score), { phase: 'Repair', label: `repair r${round}`, schema: REPAIR_SCHEMA, effort: 'low' })
        .then((r) => (r ? { ...r, score } : null))
    },
  )
  if (!repair) {
    log(`round ${round}: a stage failed; keeping ${current}`)
    stopReason = 'stage failure'
    break
  }
  if (repair.skip) {
    stopReason = 'no issues and no requests'
    break
  }
  history.push({ round, stage: 'repair', overall_before: repair.overall_before, overall_after: repair.overall_after, edits_applied: repair.edits_applied, remaining: repair.remaining_requests.length })
  current = repair.output_svg || outFile
  log(`round ${round}: ${repair.overall_before} -> ${repair.overall_after}, ${repair.edits_applied} edit(s), ${repair.remaining_requests.length} request(s) left`)
  if (repair.remaining_requests.length === 0 && repair.edits_applied === 0) {
    stopReason = 'no requests remain'
    break
  }
  if (repair.overall_after > best + 1e-9) {
    best = repair.overall_after
    stale = 0
  } else {
    stale += 1
    if (stale >= 2) {
      stopReason = 'score plateau after 2 rounds'
      break
    }
  }
}

return { svg: current, rubric, rounds_run: history.filter((h) => h.stage === 'repair').length, stop_reason: stopReason, history }
