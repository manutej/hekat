# Icon gotchas: what the icon critic missed

Source: `examples/figtree/probes/ADVERSARY-icon-motion.md` (19 icon probes under `icon/`) and
`examples/figtree/icons/NOTES.md`. The **status** column is the critic at HEAD (2026-10-12,
computed with `figtree.probes.evaluate`; re-run `python -m figtree eval` before quoting): the
adversary's proposals became the `icon.*` checks (`safe_margin`, `coverage`, `subpath_count`,
`solid_fill`, `invisible_shape`, `min_feature_size`, `min_gap`, `crossing_density`,
`ink_distribution`), which run inside `QualityCritic` for the icon rubric, so `figtree score`
and `figtree eval` see them. Two harness facts:

1. When the adversary ran, the family rules lived only in `IconSmith.score`; now they are
   `figtree.quality.icon_family_issues`, and `IconSmith` only adds the brief's `max_strokes` and
   `must_read_at`.
2. `flow.*` is skipped for the icon medium (a marker is drawing, not a flow); on a textless icon
   the checks that can fire are `compactness.*`, `polish.*`, `medium.*`, `icon.*` and `content.none`.

## Check this by eye at 16 px (gaming probes; all scored 10.0 when written)

| Look for | Why the critic was silent | Probe | Status at HEAD |
|---|---|---|---|
| **Sub-pixel detail**: a ring plus five 0.5 px stubs (the grounder's round-1 "text") | no minimum feature size | `icon.stub-detail` | fires `icon.min_feature_size` (9.75) |
| **Mirrored metaphor**: magnifier handle up-left reads as a balloon | orientation is not measured | `icon.mirrored-magnifier` | silent, still fooled (10.00) |
| **Solid fill in an outline family** (a filled star) | the family rule exempted `currentcolor` fills, exactly what solid icons use | `icon.solid-currentcolor` | fires `icon.solid_fill` (9.80) |
| **Twelve strokes 1.5 px apart**: a grey slab | 12 is the limit; gaps were not measured | `icon.twelve-stroke-noise` | fires `icon.min_gap` (9.75) |
| **Ink in one corner** behind two axis lines that fake a 56 % bbox | coverage was a bbox ratio, not an ink distribution | `icon.corner-mass` | fires `icon.ink_distribution`, `icon.min_feature_size`, `icon.min_gap` (9.25) |
| **18 strokes packed into one `<path>`** with 18 `M` subpaths | the element count saw one element | `icon.subpath-packing` | fires `icon.min_gap`, `icon.subpath_count` (9.50) |
| **Invisible rect** (`fill=none stroke=none`) that supplies the bbox around a 3 px glyph | invisible shapes counted toward the content bbox | `icon.invisible-coverage` | fires `icon.coverage`, `icon.invisible_shape` (8.38) |

## Defects the critic missed

| Look for | Why | Probe | Status at HEAD |
|---|---|---|---|
| Four 2 px strokes crossing at one point: a 4 px blob | `flow.crossings` only sees flows | `icon.crossing-asterisk` | fires `icon.crossing_density` (9.75) |
| Two lines 2.5 px apart centre to centre fuse at 16 px | no minimum gap | `icon.merge-at-16px` | fires `icon.min_gap` (9.75) |
| Ring `r=12.4` with a 2 px stroke clipped on all sides | bbox ignored stroke width; `int()` truncated -0.4 to 0 | `icon.stroke-clipped` | fires `compactness.overflow`, `icon.safe_margin` (7.75) |
| 17x17 square rotated 45 degrees, tips at -1 and 25, clipped | `rotate()` was not applied to bboxes | `icon.rotated-into-margin` | fires `compactness.overflow`, `icon.safe_margin` (7.75) |
| A 1.5 px detail stroke beside 2 px strokes | caught: `polish.stroke_widths` (true positive, auto-fix to 2 is right) | `icon.detail-stroke-1-5` | fires `polish.stroke_widths` (9.88) |
| Calendar with nine `h.01` dots, 13 elements, 1 px gaps | caught: `medium.icon_elements`; the dot rows still fuse at 16 px | `icon.thirteen-elements` | fires `icon.subpath_count`, `medium.icon_elements` (9.62) |

## False positives (the icon is right)

| Look for | Why it fired | Probe | What to do | Status at HEAD |
|---|---|---|---|---|
| Library page icon written with relative `m h l v` | `path_to_points` handled only `M H V L`: `content.none` critical | `icon.relative-path-commands` | relative commands parse now; absolute commands still read more safely | silent (10.00) |
| External-link icon whose arrowhead is a `<marker>` | `flow.diagonal`, `flow.short_shaft` fired | `icon.marker-arrowhead` | `flow.*` is skipped for icons now; draw arrowheads as polylines anyway | silent (10.00) |
| Toggle switch with `rx = h/2` (a pill) | `polish.corner_radius`; the auto-fix would have squared it | `icon.pill-toggle` | pills are exempt on icons now | silent (10.00) |
| Magnifier authored on a 48 grid in `<g transform="scale(0.5)">` | `scale()` was not applied: `compactness.overflow` critical, 8.25 | `icon.scaled-group` | full transform parsing landed; bake the scale in anyway | silent (10.00) |
| Trending-up icon with `<polyline>` + `<polygon>`, flat metaphor | rubric silent; the smith reported 31 % coverage ("will vanish") | `icon.polyline-polygon` | flat metaphors (minus, equals, trending, toggle) are measured by their long side now | fires `icon.ink_distribution` (9.75) |
| Family magnifier at `width="16" height="16"` with viewBox 24 and `<title>`/`<desc>` | silent (guard) | `icon.viewbox24-size16` | this is the 16 px cold-eye copy form | silent (10.00) |

## Eval numbers

```
# adversary run: 23 probes, recall 0.312, precision 0.5, missed 11, fp 5
# HEAD 2026-10-12: 23 probes, recall 0.938, precision 1.0, missed 1, fp 0
```

## What the first family taught (NOTES.md)

- Every round-1 icon scored 10.0; 7 of 12 needed a second round for defects visible only in the
  image: text stubs (grounder), a pencil that read as a kite (draw-leaf), a wrench that was a
  notched circle (repair), strokes colliding at 16 px (merge, edit-script, the critic's slit eye).
- The step that exposed them: rendering the sheet at 16 px beside 96 px.
- The coverage rule under-read multi-segment relative paths at the time: the critic icon was
  rewritten as polylines to score what it already drew (relative commands parse at HEAD).
- Open items after acceptance: `residual` reads as a road sign more than a flag; `merge` has the
  least clearance (arrowhead to box) and softens first at 16 px.

## Cold-eye render

Render the sheet (or one icon) at several sizes with the headless shell used by the renderer:

```bash
HS=$(ls /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell | head -1)
cat > /tmp/sheet.html <<'HTML'
<!doctype html><meta charset="utf-8"><style>body{margin:16px;background:#fff;color:#1F1F1F;font:12px sans-serif}
.dark{background:#17181A;color:#ECEAE4}img{image-rendering:pixelated;vertical-align:middle;margin:0 8px}</style>
<div><img src="icon.svg" width="16"><img src="icon.svg" width="24"><img src="icon.svg" width="48"><img src="icon.svg" width="96"></div>
<div class="dark"><img src="icon.svg" width="16"><img src="icon.svg" width="24"><img src="icon.svg" width="48"></div>
HTML
"$HS" --no-sandbox --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=400,160 \
      --screenshot=/tmp/sheet.png file:///tmp/sheet.html
```
`<img>` of an SVG with `stroke="currentColor"` does not inherit the page colour; for the dark
row inline the SVG or set `stroke="#ECEAE4"` on a copy. Then view the PNG and write the table:
icon, score, rounds, what changed per round.
