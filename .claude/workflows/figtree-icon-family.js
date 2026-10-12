export const meta = {
  name: 'figtree-icon-family',
  description: 'Draw an icon per brief with figtree icon, review each at 16/24/48 px with a cold eye, repair up to three times from the reviewer's defects while below 9.5, build the contact sheet',
  whenToUse: 'A family of custom 24-grid stroke icons must be designed and must survive small sizes; each brief is a name, a concept and an optional metaphor',
  phases: [
    { title: 'Draw', detail: 'figtree icon --backend claude per brief (hand-drawn fallback when the backend fails)' },
    { title: 'Review', detail: 'render at 16/24/48 px, cold-eye score and defects' },
    { title: 'Repair', detail: 'up to three repair rounds fed with the reviewer defects while score < 9.5' },
    { title: 'Sheet', detail: 'contact sheet of the accepted icons' },
  ],
}

// Model tiers (optional): args.model for every agent, args.cheap_model for the mechanical stages
// (effort 'low'). Omit both to inherit the session model. Small models work because every prompt
// is a spec card: one command, one file, one JSON shape.
const MODEL = args.model || undefined
const CHEAP = args.cheap_model || MODEL
const run = (prompt, opts = {}) => agent(prompt, { ...((opts.effort === 'low' && CHEAP) ? { model: CHEAP } : MODEL ? { model: MODEL } : {}), ...opts })

// args: {briefs: [{name, concept, metaphor?}], out_dir}
const briefs = (args.briefs || []).filter((b) => b && b.name && b.concept)
const outDir = args.out_dir
if (!briefs.length || !outDir) throw new Error('figtree-icon-family needs args {briefs: [{name, concept, metaphor?}], out_dir}')
const ACCEPT = 9.5
const ROUNDS = Math.max(1, Math.min(args.rounds || 3, 4))  // cold-eye repair rounds per icon

const DRAW_SCHEMA = {
  type: 'object',
  properties: {
    svg: { type: 'string' },
    score: { type: 'number' },
    backend: { type: 'string' },
    strokes: { type: 'integer' },
  },
  required: ['svg', 'score', 'backend'],
}

const REVIEW_SCHEMA = {
  type: 'object',
  properties: {
    score: { type: 'number' },
    defects: { type: 'array', items: { type: 'string' } },
    recognisable_at_16: { type: 'boolean' },
  },
  required: ['score', 'defects', 'recognisable_at_16'],
}

const SHEET_SCHEMA = {
  type: 'object',
  properties: { sheet: { type: 'string' }, icons: { type: 'integer' } },
  required: ['sheet', 'icons'],
}

const spec = (b) => `${b.name}: ${b.concept}${b.metaphor ? ` | ${b.metaphor}` : ''}`

function drawPrompt(b) {
  return `You are the DRAUGHTSMAN for one icon. Brief: name "${b.name}", concept "${b.concept}", metaphor "${b.metaphor || '(choose one: a single recognisable object, never a letter)'}".
Run exactly:
  python3 -m figtree icon "${spec(b).replace(/"/g, '\\"')}" -o ${outDir} --backend claude --rounds 3 --report ${outDir}/${b.name}.draw.json
If that command fails (no claude backend, non-zero exit) run it again with --backend rule, then hand-draw: overwrite ${outDir}/${b.name}.svg with a 24x24 viewBox icon in the family style (stroke #333333, stroke-width 2, round caps and joins, fill none, at most 12 strokes, 2 px safe margin, no text), ids on every element, and set backend to "hand".
Then run  python3 -m figtree score ${outDir}/${b.name}.svg --rubric icon --json  and read only "overall".
Return only JSON: {svg: "${outDir}/${b.name}.svg", score: <overall>, backend: "claude"|"rule"|"hand", strokes: <count of path/line/circle/rect/polyline elements>}. Do not paste file contents into your answer.`
}

function reviewPrompt(b, svgPath, round) {
  return `You are a COLD-EYE REVIEWER (round ${round}) who has never seen the brief's reasoning. Icon file: ${svgPath}. It should read as "${b.concept}".
Render it at three sizes with one command and look at the three PNGs with the Read tool:
  python3 -c "
import re,sys
from figtree.render import render_png
s=open('${svgPath}').read()
for px in (16,24,48):
    t=re.sub(r'width=\\"[^\\"]*\\"', 'width=\\"%d\\"'%px, s, 1); t=re.sub(r'height=\\"[^\\"]*\\"', 'height=\\"%d\\"'%px, t, 1)
    print(render_png(t, '${outDir}/renders', '${b.name}-${round}-%dpx'%px))
"
Also run  python3 -m figtree score ${svgPath} --rubric icon --json  and note "overall" and the issues' fix_instruction fields.
Score 1-10 with these rules: 10 only if the 16 px render is instantly recognisable as the concept, strokes do not merge, nothing touches the edge, weight matches a 2 px/24-grid family; subtract for every defect you can name. Combine with the measured overall (take the lower of the two when they disagree by more than 1).
Return only JSON: {score: number, defects: [one line each, concrete, e.g. "16px: inner circle merges with the ring"], recognisable_at_16: boolean}. Do not paste file contents into your answer; never include SVG or PNG data.`
}

function repairPrompt(b, svgPath, review) {
  return `You are the REPAIRER for icon "${b.name}" (${svgPath}); concept "${b.concept}". A cold-eye reviewer scored it ${review.score} with these defects:
${review.defects.map((d, i) => `  ${i + 1}. ${d}`).join('\n') || '  (none listed)'}
Fix every defect you can with the smallest edit: open the file, change only the offending path/stroke coordinates (keep ids, viewBox 0 0 24 24, stroke 2, round caps, no text, at most 12 strokes). Keep a backup first:  cp ${svgPath} ${outDir}/${b.name}.before-repair.svg
Then run  python3 -m figtree score ${svgPath} --rubric icon --json  and read only "overall".
Return only JSON: {svg: "${svgPath}", score: <overall>, backend: "repair", strokes: <element count>}. Do not paste file contents into your answer.`
}

const results = await pipeline(
  briefs,
  (b) => run(drawPrompt(b), { phase: 'Draw', label: `draw ${b.name}`, schema: DRAW_SCHEMA }),
  (drawn, b) => {
    if (!drawn) throw new Error(`draw failed for ${b.name}`)
    return run(reviewPrompt(b, drawn.svg, 1), { phase: 'Review', label: `review ${b.name}`, schema: REVIEW_SCHEMA, effort: 'low' }).then((review) => ({ drawn, review }))
  },
  async ({ drawn, review }, b) => {
    if (!review) return { name: b.name, svg: drawn.svg, backend: drawn.backend, score: drawn.score, defects: [], repaired: false, status: 'unreviewed' }
    // up to ROUNDS repair rounds, each fed the latest cold-eye defects; stop at ACCEPT
    let current = { svg: drawn.svg, backend: drawn.backend }
    let verdict = review
    let rounds = 0
    const history = [review.score]
    while (verdict.score < ACCEPT && rounds < ROUNDS) {
      rounds += 1
      const fixed = await run(repairPrompt(b, current.svg, verdict), { phase: 'Repair', label: `repair ${b.name} r${rounds}`, schema: DRAW_SCHEMA })
      if (!fixed) break
      current = { svg: fixed.svg, backend: 'repair' }
      const again = await run(reviewPrompt(b, fixed.svg, rounds + 1), { phase: 'Review', label: `re-review ${b.name} r${rounds}`, schema: REVIEW_SCHEMA, effort: 'low' })
      if (!again) break
      verdict = again
      history.push(again.score)
    }
    return {
      name: b.name,
      svg: current.svg,
      backend: current.backend,
      score: verdict.score,
      score_history: history,
      defects: verdict.defects,
      repaired: rounds > 0,
      rounds,
      status: verdict.score >= ACCEPT ? 'accepted' : 'needs work',
    }
  },
)

const icons = results.filter(Boolean)
const failed = briefs.filter((b) => !icons.some((i) => i.name === b.name)).map((b) => b.name)
for (const f of failed) log(`${f}: draw or review stage failed, not on the sheet`)

phase('Sheet')
const accepted = icons.filter((i) => i.status === 'accepted')
let sheet = null
if (icons.length) {
  sheet = await run(
    `Build the contact sheet of the finished icons without redrawing them. Run exactly:
  python3 -c "
import json,os
from figtree.iconsmith import IconResult, IconSpec, _inner_of, sheet
rs=[]
for it in json.loads('${JSON.stringify(icons.map((i) => ({ name: i.name, svg: i.svg, score: i.score, accepted: i.status === 'accepted' })))}'):
    s=open(it['svg']).read()
    rs.append(IconResult(IconSpec(it['name'], it['name'], ''), _inner_of(s), s, float(it['score']), [], [], bool(it['accepted'])))
open('${outDir}/sheet.svg','w').write(sheet(rs))
print(len(rs))
"
Then run  python3 -m figtree score ${outDir}/sheet.svg --rubric teaching --json  and read only "overall" to confirm the sheet is well formed. Return only JSON: {sheet: "${outDir}/sheet.svg", icons: <count printed>}. Do not paste file contents into your answer.`,
    { label: 'contact sheet', schema: SHEET_SCHEMA, effort: 'low' },
  )
}

log(`${accepted.length}/${briefs.length} icon(s) accepted at >= ${ACCEPT}`)
return { out_dir: outDir, sheet: sheet ? sheet.sheet : null, icons, failed }
