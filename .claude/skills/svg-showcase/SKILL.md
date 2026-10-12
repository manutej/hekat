---
name: svg-showcase
description: Assemble FigTree results (figures, before/after refinement pairs with trajectories, icon sheets, animated figures, eval tables) into one shareable page or a design-system handoff. Use when someone says "put the figures on a page", "showcase", "gallery of results", "publish this as an Artifact", "share the figures with the team", "before and after with scores", "embed the explainer", "design system / tokens / React package for the figures", or when a digest run has produced many scored SVGs that need an index. Covers namespacing inline SVGs by prefix, the explainer as a supporting file, the showcase builder script, publishing with the Artifact tool, and what `design/figtree-ds` exposes. Not for building or scoring the figures themselves.
---

# SVG showcase: results into a page, or a design system

A showcase is itself an artifact under the loop: every figure on it stays an editable SVG
program (ids intact, namespaced), every number on it comes from a JSON the loop wrote
(trajectories, reports, eval, calibration), and the page is read in two spaces too (render
it, look at it at desktop and phone width, in light and dark).

## 1. Collect what the loop produced

| Section | Inputs | Written by |
|---|---|---|
| figures from text | `examples/figtree/output/<name>.svg` + `.report.json` | `figtree generate --report` |
| refinement cards | `teaching/<name>.svg`, `teaching/output/<name>.refined.svg`, `<name>.trajectory.json` | `figtree refine --trajectory` |
| icon family | `icons/sheet.svg`, `icons/report.json`, `icons/NOTES.md` | `figtree icon --sheet --report` |
| design round | `design/*.svg`, `judge-*.json` | `figtree judge --report` |
| motion | `*.animated.svg` (+ `.animation.css`), `animated/index.html`, `NOTES.md` | `figtree animate`, the explainer |
| evaluation | `eval/eval.json`, `eval/calibration.json`, `probes/ADVERSARY-*.md` | `figtree eval --report`, `judge --calibrate` |
| digest gallery | `out/manifest.json`, `out/<id>.svg`, `<id>.score.json`, `out/index.html` | `figtree digest --all` |

Sections appear only when their inputs exist, so the page can be rebuilt as workers deliver.

## 2. Build with the script, or from the template

```bash
python examples/figtree/showcase/build_showcase.py OUT.html      # default: examples/figtree/showcase/showcase.html
FIGTREE_SCRATCH=/path/with/loop.svg python examples/figtree/showcase/build_showcase.py OUT.html
```

`build_showcase.py` is the reference implementation (`references/showcase-structure.md`
walks it): `namespace()` prefixes ids, `href="#"`, `url(#)`, `data-from`/`data-to`, strips
the first `<title>` and every `<style>`, and prefixes the ids in a sibling stylesheet;
`inline()` wraps the SVG in `<figure class="fig"><div class="sheet">…</div><figcaption>` with
`role="img"` and `aria-label`, drops `width`/`height` so it scales; `sparkline()` draws the
score-per-round line; `refinement_card()` is before/after + trajectory table + decisions + open
requests. For a new page copy `assets/showcase.template.html` and fill its placeholders with
the same functions.

Rules that keep the page honest:
- **Namespace every inline SVG** by a unique prefix (`loop-`, `bar-chart-b-`, `anim-`); two
  figures sharing `#background` or `#figtree-arrow` break each other's markers and animations.
- **Figures sit on white sheets** whatever the theme; the page text follows the theme
  (`--sheet:#FFFFFF` in both modes). SVG strokes in `currentColor` outside a sheet (legend
  swatches) must inherit the page foreground.
- **Numbers come from JSON**, never typed: the stats row, the trajectory tables, the eval
  recall/precision, the calibration gaps.
- **The explainer is a supporting file**, not inlined: the showcase embeds the animated SVG with
  a Replay button and links `explainer/index.html`; the explainer keeps its own clock and
  controls (`svg-animation`).
- Write down what still fools the critic (gaming probes) and what the eye caught; a showcase
  that only shows 10.0s is not a showcase of the loop.

## 3. Publish as an Artifact

Load the `artifact-design` skill first (title of 2-4 words, colour tokens on `:root` with a
dark-mode redefinition, body background set, 16 px phone gutters, 16 MB limit, scripts only
from the allowed CDNs, no font `<link>` if the page must render headless). Then:

```
Artifact publish
  file_path:  <scratchpad>/showcase.html
  files:      {"explainer/index.html": "<path>/explainer.html"}    # own doctype, charset, viewport; it is served as its own page
  icon:       "chart"      description: one sentence for the gallery card
```

Supporting HTML files are not wrapped by the publisher, so the explainer must carry its own
`<!doctype html>`, metas and styles (the template does). Republish to the same `url` to update;
pass `files` again only for files that changed (`null` removes one). Keep the page private
unless the person wants a link; offer the URL once.

## 4. Design-system handoff (`design/figtree-ds/`, if present)

A React/TypeScript package `@hekat/figtree-ds` (built with tsup, `react >= 18` peer) exposes
what a front end needs to draw in the house style without Python (`src/index.ts`):
- Components: `Figure` (+ `MARKER_ID`), `Container`, `Block`, `Flow` (`FlowType`), `Icon`,
  `Caption`, with their `*Props` types; their output is the same addressable program the critic
  reads (ids, `data-role`, `data-flow`).
- `tokens.ts`: `PRESETS` (`paper | teaching | slide`) with palette tones (`attention`,
  `processing`, `residual`, `input`), font, sizes, strokes, gaps; `snap(v, grid = 8)`;
  `tokens.css` as CSS custom properties (`./tokens.css` export).
- `shapes.ts`: `KINDS`, `shapePath(kind, w, h)`, `textInset(kind)`, ports of `figtree/elements.py`.
- `icons.generated.ts`: `ICON_VIEWBOX`, `ICON_PATHS` (every library and family icon's inner
  markup), `IconName`, `ICON_NAMES`; regenerated from `figtree/icons.py` by
  `scripts/gen_icons.py` (`npm run gen:icons`).

It is owned by another worker: check `design/figtree-ds/src/index.ts` before promising an
export. Hand off the figures as SVG files plus their trajectories; hand off the style as the
preset the figures used; point the front end at the components for new figures.

## 5. Check the page like a figure

Render at 1200 and 390 px wide, light and dark (`?theme=` is not wired on the showcase; use
`--force-dark-mode` or set `data-theme="dark"` on `<html>`), and look: no horizontal page
scroll, sheets white in dark mode, every figure's arrowheads present (namespacing), replay
works, tables fit, the explainer link resolves. Headless console: no script errors.

## References and assets

- `references/showcase-structure.md`: section order, the builder's functions, the CSS registers, the Artifact publish shape.
- `assets/showcase.template.html`: a self-contained page with the sections as placeholders and the builder's CSS.
