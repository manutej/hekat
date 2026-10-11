# FigTree animated explainer: render/critique loop notes

Files in this directory:

| File | What it is |
|---|---|
| `figtree-spec.svg` | `python -m figtree generate examples/figtree/figtree-spec.md --icons --shapes --max-aspect 2.4 --no-render` (14 nodes, 9 components, 9 flows, 1 residual, editability PASS diff=1) |
| `figtree-spec.animated.svg`, `figtree-spec.animation.css` | `python -m figtree animate` on the generated figure (standalone SVG + separate stylesheet) |
| `figtree-spec.refined.svg`, `figtree-spec.trajectory.json` | `python -m figtree refine --rubric teaching`: one mechanical round, labels 12 → 14 px, score 8.25 → 9.75 |
| `figtree-spec.refined.animated.svg`, `figtree-spec.refined.animation.css` | `animate` on the refined figure; this is what `index.html` inlines |
| `index.html` | the self-contained explainer (SVG inlined, stylesheet in `<style>`, no external resources; the only URL in the file is the SVG namespace) |
| `frame-*.png` | headless-Chromium frames at virtual times, round 3 (final) |

## Score (`python -m figtree score examples/figtree/animated/figtree-spec.svg --rubric teaching`)

```
teaching: overall 8.25
  semantic_coverage        n/a
  hallucination_control    n/a
  topology_accuracy      10.00
  flow_readability       10.00
  text_quality            1.00
  visual_polish          10.00
  medium_fit             10.00
  compactness             8.50
  [warning] compactness: canvas aspect 2.54 outside the teaching material range 1.0-2.4 (banner or tower shape) -> re-flow the layout into rows so the figure is closer to the medium's aspect (request)
  [warning] text_quality: n6.label font size 12px below the teaching material minimum 14px -> raise font size to at least 14px (auto)
  ... (same warning for n7.label .. n14.label, nine labels in all)
```

After `refine --rubric teaching` (`figtree-spec.refined.svg`): **overall 9.75**, text_quality 10.00; the one
request left is the 2.54 aspect, a layout decision (`--max-aspect 2.4` still folds to two rows of
this width), so it was left to the generator rather than edited by hand. The page inlines the
refined figure because its 14 px labels are what a teaching page needs.

## Timeline of the page (one clock for figure and captions)

Motion grammar as in `docs/META-PROMPT-SVG-ARTIFACTS.md`: reveal = construction order (containers
appear with their first block), draw = connectors, after both endpoints exist (a marker-less
`ft-shaft-N` draws itself, then the real arrow with its head appears), pulse = a token travelling a
data flow; the dashed control edge `re-validate invariants → render` gets a slower (half speed)
and dimmer (#9A9A9A) token. Nothing else moves.

| Beat | Starts | What happens in the figure |
|---|---|---|
| 1 Grounding | 0.0 s | container n2 (0.3), Grounder (0.6) |
| 2 Recursive construction | 3.0 s | Generator (3.1), container n3 (3.7), Decompose children (3.9), Generator → Decompose drawn (4.4), recursive tree (5.2), Grounder → recursive tree drawn (5.7) |
| 3 Merge | 7.6 s | container n4 (7.8), Merge (8.0), Decompose → Merge drawn over 1.0 s (8.5) |
| 4 Render–critic loop | 10.6 s | Critic (10.8), Merge → Critic (11.2), tree → Critic (11.5), container n5 (12.2), Worker (12.4), Critic → Worker (12.8), re-validate (13.3), Worker → re-validate (13.7), render (14.2), dashed control edge (14.6), render → Critic feedback over 1.0 s (15.4) |
| 5 Editable output | 17.0 s | tokens start; one 9.92 s cycle: Grounder/Generator tokens → Decompose/tree tokens (the long bus to Merge and the drop to Critic) → Merge → Critic → Worker → re-validate → (control, slow, grey) render → feedback back to Critic → rest → repeat |

Token speed is 240 px/s of path length (minimum 0.35 s per hop), so a token on the 680 px bus takes
2.8 s and a 24 px hop takes 0.35 s; the per-token keyframes hold at 0 % and 100 % so every token
shares the same cycle period and the chain stays in order.

The caption strip is highlighted with the same CSS delays (`--on`/`--off` per caption). Replay,
pause, a scrubber and clickable captions seek every animation through the Web Animations API
(`Animation.currentTime`); the page keeps its own clock from `performance.now()`.
`?theme=dark|light` forces a theme, `?motion=reduce` previews the reduced-motion fallback (the
media query is also honoured): final state, shafts and tokens hidden, all captions lit, controls
hidden.

## Round 1

Frames: 800, 2500, 5000, 9000, 12000, 16000, 20000 ms at 960×620.

**What the first frames showed.** Every frame identical: a blank white card, clock at 0.0 s, only
caption 1 lit. The same page with the `<script>` removed animated correctly (at 3 s: Grounder and
Generator revealed, caption 2 lit), so the script was the cause: a perpetual `requestAnimationFrame`
loop that updated the scrubber starved headless Chromium's virtual-time clock. **Change:** the
updater became a 100 ms `setInterval`.

Separately, the raw `figtree-spec.refined.animated.svg` opened directly as a `.svg` renders as an
image document, so `--virtual-time-budget` does not drive it (fully revealed at every time, tokens
sitting at 0,0). Not a page defect; frames must come from the HTML page.

**Re-rendered frames.** 800: Grounder mid-fade inside its container. 2500: Grounder only, caption 2
already lit (beat started at 2.4 s, first new block at 2.6 s). 5000: Generator → Decompose drawn,
recursive tree in, Grounder → tree not yet. 9000: Merge and the long bus from Decompose drawn,
caption 4 lit. 12000: Critic, Worker, re-validate, their arrows. 16000: two black tokens side by
side on the shared bus (Decompose → Merge and tree → Critic). 20000: the grey control token
between re-validate and render, clearly dimmer than the data tokens. Tokens sit above the blocks
(the pulse circles are the last children of the SVG), r = 4.5 px reads at this scale.

**Defects seen.** (a) Clock and scrubber frozen at "0.0 s" in every frame although the animation
advanced: `Animation.currentTime` reads 0 under headless virtual time even though timers run
(verified with a counter page: 31 ticks, `performance.now()` = 3011, `currentTime` = 0).
(b) Captions were ~30 words for beats of 2.4–4 s: unreadable in time. (c) "2 · RECURSIVE
CONSTRUCTION" wrapped to two lines and pushed its body out of line with the other captions.
(d) Caption 2 lit 0.2 s before anything new appeared.

**Changes for round 2.** Page keeps its own clock (`performance.now()` with pause/seek
bookkeeping) instead of reading animation time back; captions cut to 16–22 words and beats
stretched to 0 / 3.0 / 7.6 / 10.6 / 17.0 s (first new element 0.1 s after each caption lights);
caption titles sentence case; added `?theme=` and `?motion=reduce` switches (mirrored in CSS) so
the dark theme and the reduced-motion fallback can be rendered as frames.

## Round 2

Frames: 800, 2500, 5000, 9000, 13000, 18500, 22500 ms; `frame-dark-18500.png`; `frame-reduced-motion.png`.

**What the frames showed.** Clock and scrubber now track (0.8 → 22.5 s) and the thumb sits on the
beat ticks. 5000: Generator → Decompose drawn with its head, caption 2 lit. 9000: Merge in and
the long bus mid-draw, caption 3 lit. 13000: Critic, Worker, Critic → Worker mid-draw, caption 4.
18500: tokens on the bus, caption 5. 22500: grey control token. Dark: page dark, figure card white,
captions legible. Reduced motion: final state, all five captions lit, controls replaced by the note.

**Defects seen.** (a) Caption 2's title truncated to "2 · Recursive constructi…" (the nowrap +
ellipsis I had added). (b) In the dark frame the legend swatches (#333 arrows) nearly vanished
against the dark header. (c) In the reduced-motion frame a small empty grey pill sat at the top
right of the figure card: the hover id chip, revealed by the fallback's `opacity:1 !important`.

**Changes for round 3.** Titles 12 px, wrapping allowed, no ellipsis, caption gap 8 → 6 px and
padding 8 → 7 px so the longest title fits on one line; legend swatches use `currentColor`
(page foreground); the id chip is hidden with `visibility`, not opacity.

## Round 3 (final)

Frames re-rendered at the same times plus a 390 px-wide check. All five titles on one line and the
bodies aligned; legend visible in both themes; no stray chip in the reduced-motion frame; at phone
width the figure keeps a 600 px minimum and scrolls inside its card (no page-level horizontal
scroll) and the captions stack. Headless console reports no script errors. No further edits.

**Residuals that belong to the figure, not the page:** the Grounder → recursive tree and
Generator → Decompose arrows share the vertical segment at x = 216 between the two containers, so
the two crossing flows look fused for 48 px; and the 2.54 aspect request above. Both are generator
layout decisions and were left as the generator produced them.
