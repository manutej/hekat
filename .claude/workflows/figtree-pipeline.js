export const meta = {
  name: 'figtree-pipeline',
  description: 'End to end on a documented concept space: research specs from the corpus, draw and score one figure per spec, design the icon family, animate the overview, build the concept page',
  whenToUse: 'You have a documentation corpus (product docs, tutorials, READMEs) for a concept space such as "agentic workflows in Langflow" and want diagrams, icons, an animated explainer and one HTML page, produced by small-context agents on the model tiers you choose',
  phases: [
    { title: 'Research', detail: 'figtree-research: specs with verbatim evidence, checked mechanically' },
    { title: 'Digest', detail: 'figtree-digest over the specs: generate, score, refine below 8' },
    { title: 'Icons', detail: 'briefs from the specs, then figtree-icon-family' },
    { title: 'Animate', detail: 'figtree animate on the overview figure' },
    { title: 'Page', detail: 'figtree page: the concept page with every figure inline' },
  ],
}

// args: {title, corpus_dir, out_dir, topics?, max_topics?, rubric?='teaching', icons?: [{name, concept, metaphor?}] | 'auto', max_icons?=8, model?, cheap_model?, skip?: ['research'|'icons'|'animate']}
const title = args.title
const corpus = args.corpus_dir
const outDir = args.out_dir
const rubric = args.rubric || 'teaching'
const skip = new Set(args.skip || [])
if (!title || !corpus || !outDir) throw new Error('figtree-pipeline needs args {title, corpus_dir, out_dir}')
const specsDir = `${outDir}/specs`
const digestDir = `${outDir}/figures`
const iconsDir = `${outDir}/icons`
const tiers = { model: args.model, cheap_model: args.cheap_model }
const MODEL = args.model || undefined
const CHEAP = args.cheap_model || MODEL
const run = (prompt, opts = {}) => agent(prompt, { ...((opts.effort === 'low' && CHEAP) ? { model: CHEAP } : MODEL ? { model: MODEL } : {}), ...opts })

const BRIEFS_SCHEMA = {
  type: 'object',
  properties: { briefs: { type: 'array', items: { type: 'object', properties: { name: { type: 'string' }, concept: { type: 'string' }, metaphor: { type: 'string' } }, required: ['name', 'concept'] } } },
  required: ['briefs'],
}
const ANIM_SCHEMA = { type: 'object', properties: { animated: { type: 'string' }, css: { type: 'string' }, tokens: { type: 'integer' } }, required: ['animated'] }
const PAGE_SCHEMA = { type: 'object', properties: { page: { type: 'string' }, kb: { type: 'integer' } }, required: ['page'] }

// 1. research
phase('Research')
let research = null
if (!skip.has('research')) {
  research = await workflow('figtree-research', { corpus_dir: corpus, out_dir: specsDir, topics: args.topics, max_topics: args.max_topics || 8, ...tiers })
  const ok = research ? research.specs.filter((s) => s.ok).length : 0
  log(`research: ${ok}/${research ? research.specs.length : 0} specs ok, overview ${research && research.overview && research.overview.ok ? 'ok' : 'not ok'}`)
}

// 2. digest the specs (every spec is one unit: whole-file units because specs are short)
phase('Digest')
const digest = await workflow('figtree-digest', { inputs: { dir: specsDir }, rubric, out_dir: digestDir, style: rubric === 'slide' ? 'slide' : 'teaching', ...tiers })
const units = digest ? digest.units : []
log(`digest: ${units.length} figure(s), ${units.filter((u) => u.overall >= 8).length} at or above 8`)
const overview = units.find((u) => u.id.startsWith('00-overview')) || units[0]

// 3. icons
phase('Icons')
let icons = null
if (!skip.has('icons')) {
  let briefs = Array.isArray(args.icons) ? args.icons : null
  if (!briefs) {
    const b = await run(`ROLE: ICON BRIEF WRITER for the concept space "${title}".
INPUT: run  grep -h "^- \\*\\*" ${specsDir}/*.md | sort | uniq -c | sort -rn | head -40  (the components named across the specs with their counts); read nothing else.
TASK: choose at most ${args.max_icons || 8} concepts that recur across workflows and deserve an icon of their own (actors, stores, runtimes, protocols), not generic ones the family already has (document, database, user, gear, search, chart, loop, check, eye, wrench, layers, grid, text, bolt, image, palette, split, merge, arrow-right, tree).
OUTPUT: {briefs: [{name: "kebab-case", concept: "≤ 12 words, what it stands for", metaphor: "one recognisable object, ≤ 8 words"}]}. Example: {name: "tool-mode", concept: "a component exposed to an agent as a tool", metaphor: "plug entering a socket"}.
DONE WHEN: names are unique kebab-case and none duplicates a family icon. DON'T: paste file contents; propose letters or logos as metaphors.`, { label: 'icon briefs', schema: BRIEFS_SCHEMA })
    briefs = b ? b.briefs : []
  }
  if (briefs.length) {
    icons = await workflow('figtree-icon-family', { briefs, out_dir: iconsDir, ...tiers })
    log(`icons: ${icons ? icons.icons.filter((i) => i.status === 'accepted' || i.score >= 9.5).length : 0}/${briefs.length} accepted`)
  }
}

// 4. animate the overview
phase('Animate')
let anim = null
if (!skip.has('animate') && overview && overview.svg) {
  anim = await run(`ROLE: ANIMATOR. Input figure: ${overview.svg}.
COMMAND (run exactly): python3 -m figtree animate ${overview.svg} -o ${digestDir}/overview.animated.svg --css ${digestDir}/overview.animation.css
INPUT: only the command's output. OUTPUT: {animated: "${digestDir}/overview.animated.svg", css: "${digestDir}/overview.animation.css", tokens: <number of pulse tokens the command reports, or 0>}.
DONE WHEN: both files exist. DON'T: open or edit the SVG; paste file contents.`, { label: 'animate overview', schema: ANIM_SCHEMA, effort: 'low' })
}

// 5. page
phase('Page')
const page = await run(`ROLE: PAGE BUILDER.
COMMAND (run exactly, one line): python3 -m figtree page --title "${title.replace(/"/g, '\\"')}" --specs ${specsDir} --digest ${digestDir}/digest.json${icons && icons.sheet ? ` --icons-dir ${iconsDir} --sheet ${icons.sheet}` : ''}${anim ? ` --animated ${anim.animated}` : ''} --description "${(args.description || '').replace(/"/g, '\\"')}" -o ${outDir}/index.html
If ${digestDir}/digest.json does not exist, first write it from the digest workflow result below, as {"units": [...]} with fields id, title, source, svg, overall:
${JSON.stringify(units)}
INPUT: only the command's output. OUTPUT: {page: "${outDir}/index.html", kb: <size the command printed>}.
DONE WHEN: the file exists. DON'T: edit the page by hand; paste file contents.`, { label: 'page', schema: PAGE_SCHEMA, effort: 'low' })

return {
  title, out_dir: outDir,
  research: research ? { specs: research.specs.map((s) => ({ id: s.id, ok: s.ok, components: s.components, flows: s.flows })), overview: research.overview, failed: research.failed } : 'skipped',
  figures: units.map((u) => ({ id: u.id, overall: u.overall, status: u.status, svg: u.svg })),
  icons: icons ? icons.icons.map((i) => ({ name: i.name, score: i.score, status: i.status })) : 'skipped',
  animated: anim ? anim.animated : null,
  page: page ? page.page : null,
}
