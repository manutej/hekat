# Adversarial probes: icon rubric and the animation layer

Scope: break the `icon` rubric (`figtree/quality.py` + the family rules in
`figtree/iconsmith.py:icon_structural_issues`) and the motion rules of
`docs/META-PROMPT-SVG-ARTIFACTS.md` ("data → pulse, control → slower dimmer pulse, construction
order → reveal/draw, reduced-motion users get the final state, decoration is refused").

Probe files live in `icon/` and `teaching/` (`<slug>.svg` + `<slug>.json`, `source:
adversary-icon`). `proposed.*` check ids name checks that do not exist yet; the harness counts
them as missed, which is the point. Every icon probe was rendered at 16/24/48 px (nearest-neighbour
upscales beside true size) for the cold-eye test; every animated probe was frame-captured in
headless Chromium with `--virtual-time-budget`, and the reduced-motion ones also with
`--force-prefers-reduced-motion`.

Two facts about the harness matter for reading the table:

1. `figtree score` and `figtree eval` run only `QualityCritic`. The family rules (safe margin,
   stroke count, coverage, stroke widths, fills) in `icon_structural_issues` are applied only
   inside `IconSmith.score`, so the eval cannot measure them. The "critic" column below reports
   both, with the smith result in brackets.
2. The icon rubric's flow checks (`flow.*`) run on icons whenever a stroke carries `marker-end`
   or `data-flow`; the text checks never run (no text); so for a textless icon the only checks
   that can fire are `compactness.*`, `polish.*`, `medium.*`, `content.none`.

## Probe table

| id | kind | what it shows | what the critic did | proposed check or rule | severity |
|---|---|---|---|---|---|
| icon.stub-detail | gaming | r=9.5 circle + five 0.5 px stubs; at 16 px a ring with a smudge (the grounder round-1 failure) | 10.0, silent [smith silent] | `proposed.icon.min_feature_size`: every stroke's extent (length, bbox) at `must_read_at` px must be >= ~1.5 device px | warning |
| icon.mirrored-magnifier | gaming | magnifier with the handle up-left; reads as a balloon on a string | 10.0, silent [silent] | `proposed.icon.metaphor_orientation`: judge question; mechanical proxy = chirality test against the library icon the brief names (render, compare to flipped library icon) | warning |
| icon.solid-currentcolor | gaming | solid filled star in an outline family | 10.0, silent [silent: the smith exempts `currentcolor` fills, exactly what solid icons use] | `proposed.icon.solid_fill`: any shape with fill != none and area beyond a dot (r > 1.5) in an outline family | warning |
| icon.twelve-stroke-noise | gaming | exactly 12 verticals 1.5 px apart (2 px strokes), 75% coverage; a grey slab at 16 px | 10.0, silent [silent] | `proposed.icon.min_gap`: min gap between parallel strokes (centre distance minus stroke width) at `must_read_at` >= 1 device px | warning |
| icon.corner-mass | gaming | two axis lines give a 56% bbox; all meaning sits in a 6x5 corner cluster | 10.0, silent [silent] | `proposed.icon.ink_distribution`: sample strokes, measure ink centroid offset from (12,12) and per-quadrant ink share | warning |
| icon.subpath-packing | gaming | 18 strokes packed into one `<path>` with 18 `M` subpaths; 1 element | 10.0, silent [silent: counts elements] | `proposed.icon.subpath_count`: count `M`/`m` subpaths across all paths as strokes, limit 12 | warning |
| icon.invisible-coverage | gaming | 3 px glyph inside a rect with `fill=none stroke=none` that supplies the bbox | 10.0, silent [silent: coverage 56%] | `proposed.icon.invisible_shape`: exclude shapes with no fill and no stroke, `opacity=0`, `visibility=hidden`, `display=none` from the content bbox | critical |
| icon.crossing-asterisk | defect | four 2 px strokes crossing at one point; a 4 px blob at 16 px | 10.0, silent [silent] (`flow.crossings` only sees flows) | `proposed.icon.crossing_density`: pairwise stroke intersections; flag >2 strokes through one ~2 px cell | warning |
| icon.merge-at-16px | defect | two menu lines 2.5 px apart centre to centre (0.5 px gap) fuse at 16 px | 10.0, silent [silent] | `proposed.icon.min_gap` (as above) | warning |
| icon.stroke-clipped | defect | ring r=12.4 with a 2 px stroke: clipped on all four sides | 10.0, silent; `compactness.overflow` missed [smith: "enters the safe margin" only] | bbox must include stroke-width/2; use floor/ceil, not `int()` (which truncates -0.4 to 0) | critical |
| icon.rotated-into-margin | defect | 17x17 square `rotate(45 12 12)`: tips at -1 and 25, clipped | 10.0, silent; `compactness.overflow` missed [silent] | apply the full `transform` (rotate, scale) to bboxes, or report "transform not understood" as not assessed | critical |
| icon.detail-stroke-1-5 | defect | good frame + plus, plus at 1.5 px: at 16 px it is one device px and reads lighter | 9.88, `polish.stroke_widths` fired (true positive) [smith: widths differ] | keep: one width is the family contract; the auto-fix (set 2) is right | warning |
| icon.thirteen-elements | defect | calendar with nine `h.01` dots, 13 elements; the dot rows (1 px gap) also fuse into bars at 16 px | 9.88, `medium.icon_elements` fired (true positive; this check had no probe) [smith: 13 strokes] | keep; a stroke counter must not treat `h.01` dots as sub-pixel detail (they render as 2 px round dots) | warning |
| icon.relative-path-commands | false_positive | the library page icon written with `m h l v` | **`content.none` critical** (0 shapes), 10.0 after the concurrent scoring change (was 8.88) [smith silent] | `geometry.path_to_points` matches lowercase commands but handles only `M H V L`; it also ignores implicit repeated coordinates after `L` and `A`/`C`/`Q` endpoints. Use `program.path_extent_points` for bboxes | critical (critic bug) |
| icon.marker-arrowhead | false_positive | external-link icon whose arrowhead is a `<marker>` | **`flow.diagonal`, `flow.short_shaft`** fired [smith silent] | skip `flow.*` for medium icon (they are listed under media `*`); an icon has no reading order | warning |
| icon.pill-toggle | false_positive | toggle switch: stadium track rx = h/2 | **`polish.corner_radius`** fired, 9.12; auto-fix would square the pill [smith: 31% coverage, "will vanish"] | cap rx relative to the shape (`rx <= min(w,h)/2`), and do not apply the clip-art veto to icons; the coverage rule needs a flat-metaphor exemption (minus, equals, trending, toggle) | warning |
| icon.scaled-group | false_positive | magnifier authored on a 48 grid in `<g transform="scale(0.5)">` | **`compactness.overflow`** critical, 8.25 [smith: safe margin] | bbox parser honours only `translate()`; apply scale or mark as not assessed | critical (critic bug) |
| icon.polyline-polygon | clean | trending-up icon with `<polyline>` + `<polygon>` | silent, 10.0 [smith: 31% coverage false alarm] | none (guard) | - |
| icon.viewbox24-size16 | clean | family magnifier at width/height 16, viewBox 24, with `<title>`/`<desc>` | silent, 10.0 [silent] | none (guard for the 16 px cold-eye copies) | - |
| teaching.animated-tokens-at-origin | false_positive | untouched `figtree animate` output | **`compactness.overflow` x2** (tokens are `<circle r=3>` with no cx/cy: bbox at -3,-3); a 10.0 figure scores 8.83 after animation. With a fourth token `topology.ungrouped` also fires (tokens count as blocks) | give tokens their path-start `cx/cy` with `transform-box:fill-box;transform-origin:center` (verified in Chromium: tokens stay on the path), or exclude `data-role=pulse` from shapes and blocks | critical (critic bug) |
| teaching.motion-backwards-pulse | gaming | `ft-travel` keyframes 100% → 0%: every token travels from arrowhead to tail | 10.0, static critic fooled (frame at 2.6 s: tokens near the heads moving back) | `proposed.motion.pulse_direction` | critical |
| teaching.motion-reveal-reversed | gaming | Output reveals first, Model, then Source; final frame identical to the clean figure | 10.0, fooled (frame at 0.3 s: only Output visible) | `proposed.motion.reveal_order` | warning |
| teaching.motion-control-faster | gaming | dashed control token: 296 px in 0.8 s (370 px/s) and as dark as data tokens (13 px/s) | 10.0, fooled | `proposed.motion.control_tempo` | warning |
| teaching.motion-no-reduced-motion | gaming | identical CSS without the `prefers-reduced-motion` block | 10.0, fooled (with `--force-prefers-reduced-motion` at 0.6 s only Source is visible; the untouched output shows the final state) | `proposed.motion.reduced_motion` | critical |
| teaching.motion-decorative-pulse | gaming | a token orbiting the Model block's border and the Output block blinking forever | 9.83, fooled (`topology.ungrouped` fires on the 4th token, a false positive) | `proposed.motion.decorative` | warning |

## Critic defects found on the way (not probes)

- `rx="50%"` on a rect raises `ValueError` in the corner-radius check and aborts the whole review
  (and would abort `figtree eval`), so it is documented rather than filed as a probe.
- `icon_structural_issues` compares `round(stroke_width, 1)` nowhere: a `stroke-width="2.04"`
  (a transform-scaled export) passes `QualityCritic` but fails the family rule.
- `animate.py:75` builds a `dash` attribute for control-edge shafts and never inserts it
  (line 78), and the draw-on CSS overrides `stroke-dasharray` anyway: while a control edge draws
  itself it is a solid line, indistinguishable from data until the real edge appears.
- The teaching critic treats pulse tokens (`<circle data-role="pulse">`) as blocks: four tokens
  on a three-block figure trip `topology.ungrouped`.

## Measurable motion checks (what to parse)

All of these read the `<style>` block of the animated SVG (or the sibling stylesheet) with a
small CSS tokenizer: `@keyframes NAME{...}` → per-keyframe property map; `#ID{...}` → declared
properties; `animation:` shorthand → (name, duration, timing, delay, iteration, direction) per
comma-separated entry; `@media (...)` → nested rules. They then join on element ids against
`load_program(svg)`.

| check | parse | rule |
|---|---|---|
| `motion.pulse_direction` | for each rule with `offset-path: path('D')`: the element id, `D`, its `ft-travel`-like keyframes (`offset-distance` at from/to), `animation-direction` | find the flow whose `d` (or `points_to_path(points)`) equals `D`; the offset-distance sequence must be non-decreasing over time (0% → 100%); `direction: reverse` or `alternate` on a token is a violation; a `D` equal to a flow's reversed point list is a violation |
| `motion.reveal_order` | every rule whose animation name's keyframes go opacity 0 → 1 (reveal), its delay, and the block/group it targets | order blocks by `(bbox.y // 64, bbox.x)` as `animate._order` does; Spearman rank correlation between that order and delays must be >= 0; additionally for every flow, delay(target group) >= delay(source group) |
| `motion.draw_after_endpoints` | rules on `ft-shaft-*` (stroke-dashoffset keyframes) with delay | delay(shaft) >= delay(source group) + reveal duration and >= delay(target group) + reveal duration |
| `motion.control_tempo` | per token: path length of `D` (Manhattan over `path_to_points`), duration, the token's fill; the flow's `data-flow` | speed = length/duration; max control speed <= min data speed; relative luminance of control fill > data fill; control tokens may not be larger (`r`) than data tokens |
| `motion.reduced_motion` | presence of `@media (prefers-reduced-motion: reduce)` and the rules inside it | every id animated outside the block must inside it get `animation: none` (or the universal rule) with its final values (`opacity: 1`, `stroke-dashoffset: 0`); every `[id^=ft-pulse]`/`[id^=ft-shaft]` must be `display: none` there; a missing block is critical |
| `motion.decorative` | every `offset-path` `D`; every `animation` entry's target element and iteration count; the animated properties of each keyframes block | each `D` must equal a flow's path (data-flow or marker-end) in forward order; `infinite`/`alternate` is allowed only on `data-role=pulse` tokens; blocks and labels may animate `opacity` once (reveal) and nothing else; shafts may animate `stroke-dashoffset` only; any other property (`transform`, `fill`, `stroke`, `r`, `filter`) is decoration |
| `motion.token_static_position` | each `data-role=pulse` element's `cx/cy` | must be on the first point of its `offset-path`, with `transform-box: fill-box; transform-origin: center` in its rule; this also keeps the static critic from reporting overflow |
| `motion.total_duration` | max(delay + duration) over non-infinite entries | <= the explainer's budget (e.g. 20 s) so the construction finishes before the captions do |

A rendered check complements these: capture frames at `t = delay(token) + 0.25 * duration` and
`+ 0.75 * duration`, locate the token (its fill colour) and verify the second position is farther
along the flow than the first; capture once with `--force-prefers-reduced-motion` at `t = 0.5 s`
and require the frame to equal the final frame.

## Eval summary

```
$ python -m figtree eval --rubric icon
23 probes, recall 0.312, precision 0.5, missed 11, false positives 5
  FAIL icon.crossing-asterisk (defect): missed ['proposed.icon.crossing_density']
  FAIL icon.marker-arrowhead (false_positive): false ['flow.diagonal', 'flow.short_shaft']
  FAIL icon.merge-at-16px (defect): missed ['proposed.icon.min_gap']
  FAIL icon.pill-toggle (false_positive): false ['polish.corner_radius'] overall 9.12
  FAIL icon.relative-path-commands (false_positive): false ['content.none']
  FAIL icon.rotated-into-margin (defect): missed ['compactness.overflow']
  FAIL icon.scaled-group (false_positive): false ['compactness.overflow'] overall 8.25
  FAIL icon.stroke-clipped (defect): missed ['compactness.overflow']

$ python -m figtree eval --rubric teaching      # seeds + this adversary's six teaching probes
27 probes, recall 0.808, precision 0.913, missed 5, false positives 2
  FAIL teaching.animated-tokens-at-origin (false_positive): false ['compactness.overflow'] overall 8.83
```

`teaching/` is shared with the other adversaries, so the plain `eval --rubric teaching` line
grows as they add probes; the numbers above are `evaluate(seed_probes() + [p for p in
load_probes(...) if p.source == "adversary-icon"], "teaching")`. The icon line is unaffected.

The 11 icon misses are 7 `proposed.*` checks on the gaming probes, 2 `proposed.*` checks on
defects the critic has no check for (`min_gap`, `crossing_density`), and 2 existing checks that
should have fired (`compactness.overflow` on stroke-clipped and rotated-into-margin); the 5 false
positives are real critic defects (two of them parser bugs). All five animated gaming probes
score >= 9.83: the static critic cannot see motion at all, and its one reaction to an animated
file is a false positive.
