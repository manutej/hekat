# Motion grammar

From `docs/META-PROMPT-SVG-ARTIFACTS.md` (binding rules), `figtree/animate.py` (what is
generated), `examples/figtree/animated/NOTES.md` (four rounds of frame review) and
`examples/figtree/probes/ADVERSARY-icon-motion.md` (what fooled the static critic).

## Binding rules

- `MotionGrammar` entries bind to flow types: data -> pulse; control/conditional -> slower,
  dimmer pulse; construction order -> reveal and draw. Reduced-motion users get the final state.
- Decoration is refused: a token orbiting a block's border, a block blinking forever, a colour
  that cycles, a shadow that breathes. Each of these passed the static critic (9.83-10.0).
- Motion never adds a component: the content plan is immutable downstream.
- Tokens travel tail to head (`offset-distance` non-decreasing); `animation-direction: reverse`
  or `alternate` on a token is a violation; a path equal to a flow's reversed point list is one.
- Reveal order correlates with reading order (`(bbox.y // 64, bbox.x)`, Spearman >= 0) and for
  every flow `delay(target) >= delay(source)`.
- A shaft draws after both endpoints have revealed: `delay(shaft) >= delay(src) + reveal` and
  `>= delay(dst) + reveal`.
- Control tempo: max control speed <= min data speed; control fill lighter than data fill;
  control token radius <= data token radius.
- Blocks and labels animate `opacity` once (reveal) and nothing else; shafts animate
  `stroke-dashoffset` only; `infinite` and `alternate` only on `data-role="pulse"`.
- Every id animated outside the reduced-motion block gets `animation: none` and its final
  values inside it (`opacity: 1`, `stroke-dashoffset: 0`); `[id^=ft-pulse]` and `[id^=ft-shaft]`
  are `display: none` there.
- Total construction time (max delay + duration over non-infinite entries) stays under the
  explainer's budget so the build finishes before the captions do.

## What `figtree animate` emits

```css
@keyframes ft-reveal{from{opacity:0}to{opacity:1}}
#n6{opacity:0;animation:ft-reveal .6s cubic-bezier(.2,.7,.2,1) 0.35s forwards}       /* per leaf <g>, delay = index * step */
@keyframes ft-draw{to{stroke-dashoffset:0}}
@keyframes ft-appear{to{opacity:1}}
#ft-shaft-0{stroke-dasharray:L;stroke-dashoffset:L;animation:ft-draw 0.6s cubic-bezier(.4,0,.2,1) D s forwards}
#n1\.arrow0{opacity:0;animation:ft-appear .01s linear (D+0.6)s forwards}               /* the real arrow, with its head */
@keyframes ft-travel{from{offset-distance:0%}to{offset-distance:100%}}
#ft-pulse-0{offset-path:path('M…');offset-rotate:0deg;opacity:0;animation:ft-travel 2.4s linear S s infinite, ft-show .1s linear S s forwards}
@keyframes ft-show{to{opacity:1}}
@media (prefers-reduced-motion: reduce){[id^=ft-pulse],[id^=ft-shaft]{display:none}*{animation:none!important;opacity:1!important;stroke-dashoffset:0!important}}
```

plus, appended before `</svg>`: one `<path id="ft-shaft-N" … data-role="anim-shaft">` per flow
(same stroke and width, no marker) and one `<circle id="ft-pulse-N" r="3.5" fill="#333333"
stroke="#FFFFFF" stroke-width="1.5" data-role="pulse">` per flow (`#999999`, 1.6 x duration on
control edges). Ids with `.` are escaped in selectors (`#n1\.arrow0`). `Timeline(step=0.35,
draw=0.6, pulse=2.4)`; `blocks_done = step x n_blocks`; shaft `i` starts at
`blocks_done + 0.15 i`; pulses start at `blocks_done + 0.15 x n_flows + draw`, staggered 0.4 s.

Known gaps in the generator (document them, do not fight them): control-edge shafts draw solid
(the `dash` attribute is built and never inserted, and `ft-draw` overrides `stroke-dasharray`),
so a control edge is indistinguishable from data while it draws; tokens have no `cx/cy` (the
critic at HEAD excludes pulse tokens from overflow and grouping; the explainer sets them by hand).

## Re-timing by beat (the explainer form)

The explainer keeps the generated structure and replaces delays per beat:

```css
@keyframes ft-reveal{from{opacity:0;translate:0 6px}to{opacity:1;translate:0 0}}   /* only on <g> with no SVG transform */
#n2{opacity:0;animation:ft-reveal .5s ease-out forwards;animation-delay:0.40s}
#ft-shaft-5{stroke-dasharray:136;stroke-dashoffset:136;animation:ft-draw 0.5s ease-in-out forwards;animation-delay:3.60s}
#n1\.arrow0{opacity:0;animation:ft-appear .05s linear forwards;animation-delay:4.05s}
[data-role=pulse]{r:4.5px;stroke:#FFFFFF;stroke-width:1.6px;opacity:0;offset-rotate:0deg;
  animation-duration:P s,P s;animation-timing-function:linear,step-end;animation-iteration-count:infinite,infinite;animation-delay:T s,T s}
@keyframes ft-pulse-5-move{0%,a%{offset-distance:0%}b%,100%{offset-distance:100%}}
@keyframes ft-pulse-5-show{0%{opacity:0}a%{opacity:1}b%,100%{opacity:0}}
#ft-pulse-5{offset-path:path('M168,128 H216 V88 H264');fill:#1F1F1F;animation-name:ft-pulse-5-move,ft-pulse-5-show}
```

Arithmetic: one cycle period `P` for every token; a token on a flow of length `L` at speed
`v` (240-320 px/s, min 0.35 s per hop) occupies `[a, b] = [t0/P, (t0 + L/v)/P]` of the cycle,
with `t0` the cumulative time of the hops before it in the chain, so tokens pass the baton in
order; tokens on parallel flows out of one block share `t0`. The control token gets half
speed and `#9A9A9A`. The showcase timeline: beats at 0 / 3.0 / 7.6 / 10.0 / 16.8 s, token
cycle 10.69 s, draw durations 0.4-1.2 s scaled with length, white ring on tokens (r 4.5 px)
so they stay visible over tinted blocks.

## Measurable motion checks (five implemented at HEAD as `motion.*`, three still proposed)

The implemented ones parse the `<style>` block (`figtree.quality.parse_css`, `parse_animation`)
and join on element ids; each fires on its probe in `examples/figtree/probes/teaching/motion-*`.

| check | parse | rule |
|---|---|---|
| `motion.pulse_direction` (implemented) | each `offset-path` rule, its keyframes, `animation-direction` | offset-distance non-decreasing; no reverse/alternate; path equals a flow forward |
| `motion.reveal_order` (implemented) | reveal rules (opacity 0 -> 1) and delays | Spearman with `(bbox.y // 64, bbox.x)` >= 0; target delay >= source delay |
| `motion.draw_after_endpoints` (proposed) | `ft-shaft-*` delays | >= both endpoint reveal delays + reveal duration |
| `motion.control_tempo` (implemented) | path length / duration, fill, `data-flow` | control speed <= data speed; control fill lighter; r not larger |
| `motion.reduced_motion` (implemented) | the `@media` block | every animated id reset to its final state; shafts and tokens hidden; missing block is critical |
| `motion.decorative` (implemented) | every animated property and target | only reveal opacity, shaft dashoffset, token offset-distance; `infinite` only on tokens |
| `motion.token_static_position` (proposed) | token `cx/cy` | equal to the path start, with `transform-box: fill-box; transform-origin: center` |
| `motion.total_duration` (proposed) | max(delay + duration) | under the explainer budget |

A rendered complement: frames at `delay + 0.25 x duration` and `+ 0.75 x duration` must show
the token farther along; a `--force-prefers-reduced-motion` frame at 0.5 s must equal the final
frame. The checks read the stylesheet, not the frames; the frame review stays the defence for
timing, legibility and the three rules not yet implemented.
