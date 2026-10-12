export const meta = {
  name: 'figtree-adversary',
  description: 'Adversaries write probes against a rubric, 3 refuters vet each probe, refuted probes are deleted, figtree eval reports recall/precision before and after',
  whenToUse: 'A rubric\'s checks need hardening: you want new gaming, false-positive, miss and clean-control probes under examples/figtree/probes/<rubric>/ that survive an adversarial review',
  phases: [
    { title: 'Baseline', detail: 'figtree eval --rubric R before any new probe' },
    { title: 'Attack', detail: 'N adversaries, one lens each (gaming, false-positive, miss, clean-control), write .svg + .json probes' },
    { title: 'Verify', detail: '3 refuters per probe try to show the probe does not demonstrate its claimed defect; majority rules' },
    { title: 'Prune', detail: 'delete refuted probe files' },
    { title: 'Eval', detail: 'figtree eval --rubric R --report after the surviving probes are in place' },
  ],
}

// args: {rubric, n_probes?, out_dir}
const rubric = args.rubric
const nProbes = Math.max(1, Math.min(args.n_probes || 4, 12))
const outDir = args.out_dir
if (!rubric || !outDir) throw new Error('figtree-adversary needs args {rubric, out_dir} (n_probes optional)')
const probeDir = `examples/figtree/probes/${rubric}`
const LENSES = ['gaming', 'false-positive', 'miss', 'clean-control']

const EVAL_SCHEMA = {
  type: 'object',
  properties: {
    probes: { type: 'integer' },
    recall: { type: ['number', 'null'] },
    precision: { type: ['number', 'null'] },
    missed: { type: 'integer' },
    false_positives: { type: 'integer' },
    failing_probes: { type: 'array', items: { type: 'string' } },
  },
  required: ['probes', 'recall', 'precision', 'missed', 'false_positives', 'failing_probes'],
}

const PROBES_SCHEMA = {
  type: 'object',
  properties: {
    probes: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          kind: { type: 'string' },
          expect_fire: { type: 'array', items: { type: 'string' } },
          expect_silent: { type: 'array', items: { type: 'string' } },
          rationale: { type: 'string' },
        },
        required: ['id', 'kind', 'expect_fire', 'expect_silent', 'rationale'],
      },
    },
  },
  required: ['probes'],
}

const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    refuted: { type: 'boolean' },
    reason: { type: 'string' },
  },
  required: ['refuted', 'reason'],
}

const DELETE_SCHEMA = {
  type: 'object',
  properties: { deleted: { type: 'array', items: { type: 'string' } } },
  required: ['deleted'],
}

function evalPrompt(label, reportPath) {
  return `Run exactly this command from the repo root (exit code 1 only means some probe fails; that is expected):

  python3 -m figtree eval --rubric ${rubric} --report ${reportPath}

Then read ${reportPath} and return only its "summary" fields as JSON: {probes, recall, precision, missed, false_positives, failing_probes}. Use null for a recall or precision that is null. This is the ${label} measurement. Do not paste file contents into your answer.`
}

function attackPrompt(index) {
  const lens = LENSES[index % LENSES.length]
  const slugPrefix = `${lens}-${index}`
  const lensBrief = {
    'gaming': 'GAMING: a figure that satisfies every measurable check in the spec yet is bad for a cold reader (expect_fire lists the check that SHOULD catch it, using an existing check id or "proposed.<dimension>.<name>").',
    'false-positive': 'FALSE POSITIVE: a good, house-style figure that the critic wrongly flags (expect_silent lists the check that must NOT fire; kind "false_positive").',
    'miss': 'MISS: a real defect in a shape the critic does not handle yet (nested transforms, inherited styles, polylines, tspans, unusual units); expect_fire lists the existing check id that should fire; kind "defect".',
    'clean-control': 'CLEAN CONTROL: a compliant figure where nothing may fire (kind "clean", expect_silent = every check id in the spec for this rubric).',
  }[lens]
  return `You are ADVERSARY #${index} attacking the "${rubric}" rubric through one lens.
${lensBrief}

Read the spec first (one file, small): run  python3 -m figtree eval --rubric ${rubric} --specs ${outDir}/specs  then read ${outDir}/specs/${rubric}.json for the check ids, severities and vetoes. Read examples/figtree/probes/ADVERSARY-diagram.md lines 1-40 for the house style of a probe (Times New Roman, #7BA3C9 blocks, #333333 1.2px strokes, white background rect first, every element with an id, no scripts) — nothing else.

Write between 1 and 3 probes into ${probeDir}/ as <slug>.svg + <slug>.json. Every slug MUST start with "${slugPrefix}-" so it cannot collide with another adversary. The JSON sidecar is exactly:
  {"id": "${rubric}.<slug>", "rubric": "${rubric}", "kind": "<defect|clean|gaming|false_positive>", "expect_fire": [...], "expect_silent": [...], "rationale": "<one sentence a cold reader would agree with>", "source": "workflow-adversary"}
Check each probe with  python3 -m figtree score ${probeDir}/<slug>.svg --rubric ${rubric} --json  and keep only probes whose behaviour matches the lens (a gaming probe must score >= 9 with the expected check silent; a false-positive probe must currently fire the listed check; a miss must currently NOT fire the listed check; a clean control must have no issues).

Return only JSON: {probes: [{id, kind, expect_fire, expect_silent, rationale}]} describing the files you wrote. Do not paste file contents into your answer.`
}

function refutePrompt(probe, lens) {
  const slug = probe.id.replace(`${rubric}.`, '')
  const svgPath = `${probeDir}/${slug}.svg`
  return `You are a REFUTER (lens: ${lens}). A probe claims to demonstrate a specific property of the "${rubric}" rubric. Try hard to show the claim is WRONG; default to refuted=true when uncertain.

Probe: id ${probe.id}, kind ${probe.kind}, expect_fire ${JSON.stringify(probe.expect_fire)}, expect_silent ${JSON.stringify(probe.expect_silent)}
Rationale: ${probe.rationale}

Do exactly this: render and look at the probe with
  python3 -c "from figtree.render import render_png; print(render_png(open('${svgPath}').read(), '${outDir}/renders', '${slug}'))"
then view the printed PNG with the Read tool, and run
  python3 -m figtree score ${svgPath} --rubric ${rubric} --json
Refutation grounds by lens:
- rendered-reality: the picture does not show the defect (or the cleanliness) the rationale claims; a cold reader would not notice it.
- spec-consistency: the expected check id does not exist in the spec, or it is the wrong check for this signal, or the probe breaks the house style so badly that unrelated checks fire.
- behaviour-match: the critic output contradicts the probe's kind (a gaming probe below 9.0, a false-positive probe whose listed check is already silent, a miss whose check already fires, a clean control with issues).
Return only JSON: {refuted: boolean, reason: one sentence}. Do not paste file contents into your answer.`
}

// 1. baseline
phase('Baseline')
const before = await agent(evalPrompt('BEFORE', `${outDir}/eval-before.json`), { label: 'eval before', schema: EVAL_SCHEMA, effort: 'low' })
log(`baseline: ${before ? `${before.probes} probes, recall ${before.recall}, precision ${before.precision}` : 'eval failed'}`)

// 2+3. attack, then verify each probe by 3 refuters (no barrier between attack and verify)
const REFUTER_LENSES = ['rendered-reality', 'spec-consistency', 'behaviour-match']
const vetted = await pipeline(
  Array.from({ length: nProbes }, (_, i) => i),
  (i) => agent(attackPrompt(i), { phase: 'Attack', label: `adversary ${i} (${LENSES[i % LENSES.length]})`, schema: PROBES_SCHEMA }),
  async (result, i) => {
    const probes = (result && result.probes) || []
    if (!probes.length) {
      log(`adversary ${i} produced no probes`)
      return []
    }
    return Promise.all(
      probes.map((p) =>
        parallel(REFUTER_LENSES.map((lens) => () => agent(refutePrompt(p, lens), { phase: 'Verify', label: `refute ${p.id} (${lens})`, schema: VERDICT_SCHEMA, effort: 'low' })))
          .then((votes) => {
            const valid = votes.filter(Boolean)
            const refutations = valid.filter((v) => v.refuted)
            const kept = valid.length >= 2 && refutations.length <= valid.length - 2
            return { probe: p, kept, votes: valid.length, refuted_by: refutations.map((v) => v.reason) }
          }),
      ),
    )
  },
)

const verdicts = vetted.filter(Boolean).flat()
const kept = verdicts.filter((v) => v.kept).map((v) => v.probe)
const dropped = verdicts.filter((v) => !v.kept)
for (const d of dropped) log(`dropped ${d.probe.id} (${d.probe.kind}): ${d.refuted_by[0] || 'too few verifier votes'}`)

// 4. prune (one agent deletes every refuted probe's files)
phase('Prune')
let deleted = []
if (dropped.length) {
  const files = dropped.flatMap((d) => {
    const slug = d.probe.id.replace(`${rubric}.`, '')
    return [`${probeDir}/${slug}.svg`, `${probeDir}/${slug}.json`]
  })
  const res = await agent(
    `Delete exactly these files (they are refuted adversarial probes) with one command:  rm -f ${files.join(' ')}\nThen run  ls ${probeDir}  and return only JSON {deleted: [paths that no longer exist]}. Do not paste file contents into your answer.`,
    { label: `delete ${dropped.length} probe(s)`, schema: DELETE_SCHEMA, effort: 'low' },
  )
  deleted = (res && res.deleted) || []
}

// 5. eval after
phase('Eval')
const after = await agent(evalPrompt('AFTER', `${outDir}/eval-after.json`), { label: 'eval after', schema: EVAL_SCHEMA, effort: 'low' })
log(`after: ${after ? `${after.probes} probes, recall ${after.recall}, precision ${after.precision}` : 'eval failed'}`)

return {
  rubric,
  probe_dir: probeDir,
  kept: kept.map((p) => ({ id: p.id, kind: p.kind, expect_fire: p.expect_fire, expect_silent: p.expect_silent })),
  dropped: dropped.map((d) => ({ id: d.probe.id, kind: d.probe.kind, reasons: d.refuted_by })),
  deleted,
  before,
  after,
}
