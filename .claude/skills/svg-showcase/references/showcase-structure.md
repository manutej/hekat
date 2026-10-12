# Showcase structure

Reference implementation: `examples/figtree/showcase/build_showcase.py` (+ `showcase.css`, a
`<title>` + Google Fonts `<link>` + `<style>` head fragment it reads verbatim). Output:
`examples/figtree/showcase/showcase.html`, ~1.7 MB with every figure inlined (size grows with the
sections present; check it against the 16 MB Artifact limit).

## Section order and what each needs

1. `<header class="hero">`: eyebrow, h1, lede, `<dl class="stats">` (acceptance tests,
   artifacts refined = number of `*.trajectory.json`, mean score gain = mean of
   `final.overall - initial.overall`, icons designed = `.svg` files in `icons/` minus the sheet).
2. `<nav class="toc">`: anchors to every section.
3. `#loop`: the loop figure (`loop.svg`, from `examples/figtree/loop.md`; `FIGTREE_SCRATCH`
   overrides the path).
4. `#figures`: the three rule-grounded figures from `output/`, then the Claude-grounded one
   with its content plan's components listed from `report.json`.
5. `#refine`: `<div class="cards">` of `refinement_card()` per artifact: head (title, rubric
   chip, sparkline), `.pair` of before/after figures with issue counts and scores in the
   captions, trajectory table (round, score, issues, critical, edits, diff), "decided by a
   person" and "still open" (requests_remaining).
6. `#icons`: the contact sheet, the report table (icon, score, rounds, accepted), NOTES in a
   `<details>`.
7. `#design`: paper vs teaching register pair with judged overalls, the per-round judge table
   (`judge-paper.json`, `judge-teaching-round{1,2}.json`, `judge-teaching.json`).
8. `#motion`: the animated SVG with its CSS (from its `<style>` or the sibling `.animation.css`),
   a Replay button (re-inserts the sheet's innerHTML to restart CSS animations), link to
   `explainer/index.html`, NOTES in a `<details>`.
9. `#meta`: the meta-prompt skeleton (typed slots, procedure, binding rules, refinement log).
10. `#evaluation`: stats from `eval.json` (probes, recall, precision, gaming and false-positive
    counts), per-check table in a `<details>`, "what still fools the measurable critic" list,
    the calibration table and findings, the three adversary tables in `<details>`.
11. `#system`: what the loop folded back into the repo: the checks that grew out of the adversary
    tables (with before/after recall and precision), a table of the `.claude/workflows/` scripts
    (name, what it does, when to use), the skill family list, and the design-system note
    (`design/figtree-ds`: presets as tokens, the icon family generated from `figtree/icons.py`,
    components whose output is the same addressable program the critic reads).
12. `#learned`: the rules the loop learned, and the footer.

## The builder's functions

```python
namespace(svg, prefix, css="") -> (svg, css)
    id="X" -> id="PREFIXX"; href="#X" -> "#PREFIXX"; url(#X) -> url(#PREFIXX); data-from/data-to likewise;
    first <title> removed; every <style> removed; css selectors "#X" -> "#PREFIXX" (escaped dots kept)
inline(path, prefix, label, caption, css="") -> <figure class="fig">[<style>css</style>]<div class="sheet">svg</div><figcaption>…</figcaption></figure>
    adds role="img" aria-label=label to <svg>, strips width/height (viewBox scales it)
sparkline(trajectory, prefix) -> 160x56 inline SVG: a 10.0 gridline, the score line, dots, final value
refinement_card(name, title, rubric, before_svg, after_svg, traj_path, prefix, decided) -> <article class="card">
build() -> the whole page string; sections guarded by os.path.exists
```

Prefixes used: `loop-`, `<name>-` for figures, `<name>-b-` / `<name>-a-` for before/after,
`claude-`, `icons-`, `dz-paper-` / `dz-teach-`, `anim-`. Choose a prefix that cannot collide
with another figure's natural ids (`n1`, `e2-text`, `background`, `figtree-arrow`).

## CSS registers (`showcase.css`)

- Tokens on `:root` with a dark redefinition under `@media (prefers-color-scheme: dark)` guarded
  by `:root:not([data-theme="light"])` and again under `:root[data-theme="dark"]`; `--sheet`
  stays white in both so figures render as printed.
- Display face Newsreader for headings, IBM Plex Sans body, IBM Plex Mono for ids and chips;
  the Google Fonts `<link>` is acceptable for a page people open in a browser, and is exactly
  what a headless frame capture must not have (`svg-animation/references/capture-frames.md`).
- `.sheet` is the white card with `overflow-x: auto`; `.pair` is an auto-fit grid of 320 px
  minimum; `.traj` tables are right-aligned tabular numbers; `.learned` is the findings list.
- `@media (prefers-reduced-motion: reduce) { * { animation: none !important } }` for the
  embedded animated figure.

## Publishing shape

```
Artifact publish  file_path=<scratchpad>/showcase.html  icon="chart"
                  description="FigTree results: figures from text, refinement trajectories, icons, motion, evaluation"
                  files={"explainer/index.html": "<scratchpad>/explainer.html"}
```

The explainer is a complete document of its own (doctype, charset, viewport, styles, script):
files in `files` are served as-is. Inline SVGs inside the showcase need no files. Total size
must stay under 16 MB; the bundled showcase is ~1.7 MB. On update, pass the same `url`;
files left out are kept.

## Digest galleries

`figtree digest --all -o OUT` writes `OUT/index.html` (title, score badge, inline SVG per
unit) and `digest.json`; treat it as a section source: read `manifest.json` for units and
`skipped` (with reasons), each `<id>.score.json` for the badge, and inline each `<id>.svg`
namespaced by its unit id. Say what was skipped and why; a gallery that hides skips misreports
coverage.
