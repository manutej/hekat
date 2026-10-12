# design-sync notes for @hekat/figtree-ds

- Package lives in `design/figtree-ds/` (not a monorepo workspace): install with `npm install` there
  and build with `npm run build` (tsup → `dist/index.js` + `dist/index.d.ts`). The converter runs from
  the repo root with `--node-modules design/figtree-ds/node_modules --entry design/figtree-ds/dist/index.js`;
  config paths (`srcDir`, `cssEntry`, `tokensGlob`, `extraFonts`) are package-relative.
- Icons are generated from the Python family: `npm run gen:icons` (runs `scripts/gen_icons.py`, which
  imports `figtree.icons.ICONS`). Re-run it whenever `figtree/icons.py` changes, then rebuild.
- Fonts: IBM Plex Sans ships from `node_modules/@fontsource/ibm-plex-sans` (400 and 600, OFL) via
  `extraFonts`; a fresh clone needs the package `npm install` before the converter finds them.
- Playwright for the render check comes from `/opt/node-tools/node_modules` on this machine; `.ds-sync/node_modules/playwright`
  is a symlink to it (recreate per clone: `ln -sfn /opt/node-tools/node_modules/playwright .ds-sync/node_modules/playwright`
  and the same for `playwright-core`). Chromium build 1194 matches playwright 1.56.
- Card modes: `Figure`, `Container`, `Flow`, `Block`, `Caption`, `ProgramView` are `column` (figures are wider than a grid cell).
- Known render warns: `[DTS_STYLE_SYSTEM] filtering @types/react props` on every build (the Icon
  spreads SVGProps; the filtered shorthands are not FigTree API).

- `ProgramView` renders `design/contract/examples/figtree-loop.program.json` through the contract; the preview data lives in `.design-sync/previews/figtree-loop.program.ts` (regenerate it from the JSON when the example program changes).

## Re-sync risks

- `extraFonts` points into `node_modules`; an upgrade of `@fontsource/ibm-plex-sans` changes the
  shipped woff2 hashes and re-uploads fonts (harmless).
- Previews inline figure coordinates by hand; a change to preset gaps in `tokens.ts` does not move
  them. Re-check the `Figure` sheet after token edits.
- Toolchain assumed: node 22, tsup 8.5, typescript 5.x, playwright 1.56 + chromium 1194.
