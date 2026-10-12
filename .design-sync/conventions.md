# Building with the FigTree design system

FigTree figures are addressable SVG programs: every element has a stable `id`, blocks carry
`data-role="block"`, flows carry `data-flow="data|control|feedback"`, so a critic can anchor an
issue and an editor can apply a local edit. Build with the six components; style through the
preset tokens; never hand-draw a rectangle where a `Block` belongs.

## Setup

No provider. Import the stylesheet once (`styles.css` imports `_ds_bundle.css`, which holds the
tokens from `tokens.css`) and render a `Figure`. The `Figure` sets `data-preset` on its root,
which selects the token set; HTML content outside a figure (a `Caption`) gets the same tokens
from its own `preset` prop. Without the stylesheet, figures still render in their inline colors
but captions fall back to browser defaults.

## Composition

- `Figure` (`width`, `height` as multiples of 8, `preset` = `paper` | `teaching` | `slide`, `id`) is
  the canvas: white background first, the arrowhead marker `#ft-arrow` and every family icon as a
  `<symbol id="icon-<name>">` in `<defs>`.
- `Container` (`id`, `x`, `y`, `width`, `height`, `title?`) groups a sub-figure; children keep
  figure coordinates, so flows across its boundary are ordinary flows.
- `Block` (`id`, `x`, `y`, `width`, `height`, `label`, `kind`, `tone`, `icon?`, `note?`): kinds
  `block`, `store`, `document`, `decision`, `terminal`, `actor`, `process`; tones `attention`,
  `processing`, `residual`, `input`. Pass `preset` to Block/Container/Flow when the figure is not
  `teaching` (the default).
- `Flow` (`id`, `points` as `[x, y][]` right-angle polylines, `type`, `from`, `to`, `label?`,
  `noHead?`): data flows are solid ink, control flows dashed grey, feedback dashed ink. Keep the
  last segment at least 20 px (paper) / 24 px (teaching) / 28 px (slide) so the arrowhead has a shaft.
- `Icon` (`name`, `size`) draws a family icon in `currentColor`; names are exported as `ICON_NAMES`.
- `Caption` (`lead?`, `preset`, `width`) sits under the figure as HTML.

## Styling idiom

Tokens are CSS custom properties with the `--ft-` prefix, set per preset on `[data-preset]`:
colors `--ft-color-attention`, `--ft-color-processing`, `--ft-color-residual`, `--ft-color-input`,
`--ft-color-container`, `--ft-color-border`, `--ft-color-ink`, `--ft-color-label`,
`--ft-color-title`, `--ft-color-icon`, `--ft-color-control`; type `--ft-font`,
`--ft-font-size-label`, `--ft-font-size-annot`, `--ft-font-size-title`, `--ft-font-size-caption`;
geometry `--ft-grid` (8 px), `--ft-space-gap-h`, `--ft-space-gap-v`, `--ft-space-row`,
`--ft-space-padding`, `--ft-min-arrow`, `--ft-radius-block`, `--ft-radius-container`. The same
values are exported as data in `PRESETS` and `snap(v)` rounds to the grid. Layout glue around a
figure uses these variables; there are no utility classes besides `.ft-figure` and `.ft-caption`.

## Where the truth lives

`styles.css` → `_ds_bundle.css` (all tokens, both presets); `components/general/<Name>/<Name>.d.ts`
for props; `tokens.ts` and `shapes.ts` in the package source for the preset data and the shape paths.

## Idiomatic snippet

```tsx
<Figure width={400} height={96} preset="teaching" id="fig">
  <Block id="a" x={24} y={24} width={120} height={48} label="Grounder" icon="grounder" tone="attention" />
  <Block id="b" x={256} y={24} width={120} height={48} label="Generator" icon="tree" />
  <Flow id="a-b" from="a" to="b" points={[[144, 48], [256, 48]]} label="content plan" />
</Figure>
<Caption lead="Figure 1." preset="teaching" width={400}>Only evidenced components are drawn.</Caption>
```
