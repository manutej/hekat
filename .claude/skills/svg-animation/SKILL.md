---
name: svg-animation
description: Animate an editable SVG figure into an explainer with meaning-bound motion (reveal, draw, pulse, morph, motion path) and build the self-contained HTML player with replay, pause, scrubber and caption strip. Use when someone says "animate this figure", "make the diagram build itself", "show what flows where", "a token travelling the pipeline", "an animated explainer", "explainer with captions / a scrubber", "capture frames of the animation", "the animation jumps / the arrowheads float / reduced motion", or wants `python -m figtree animate` output checked frame by frame. Covers the motion grammar, why reveals are opacity-only, shaft copies for draw-on, one clock, prefers-reduced-motion, and virtual-time frame capture with headless Chromium. Not for Lottie, GSAP or React animation libraries.
---

# SVG animation: motion that means something

Animate only what carries meaning. The grammar is small and each entry is bound to a flow
type or to construction order; everything else is decoration and is refused. The critic
parses the animation CSS at HEAD (`motion.pulse_direction`, `motion.reveal_order`,
`motion.control_tempo`, `motion.reduced_motion`, `motion.decorative`), but it reads the
stylesheet, not the screen, so motion is verified by **frames**: capture at known virtual times
and look.

## Motion grammar (bound to meaning)

| Motion | Means | Implementation (`figtree/animate.py`) |
|---|---|---|
| **reveal** | construction order: the figure builds itself the way the recursion does (leaf blocks by row then x) | `opacity 0 -> 1`, `.6s cubic-bezier(.2,.7,.2,1)`, delay = index x `step` (0.35 s) on the leaf `<g>` |
| **draw** | a connector exists once both endpoints do | a marker-less copy `#ft-shaft-N` (`data-role="anim-shaft"`) animates `stroke-dashoffset` from the path length to 0 over 0.6 s; the real arrow (with its head) appears at the end (`ft-appear`) |
| **pulse** | what moves where: a token travels every data flow | `<circle id="ft-pulse-N" r="3.5" data-role="pulse">` with `offset-path: path('…')`, `offset-distance 0% -> 100%`, 2.4 s, infinite |
| control pulse | a control/feedback edge is slower and dimmer | `data-flow="control|conditional"`: 1.6 x duration, fill `#999999` |
| **morph** | a transition the reader can name (A becomes B) | same-command-count paths, `d` interpolated; not generated, hand-authored |
| **motion path** | a specific object follows a specific route | `offset-path` on the object; only along a flow the figure draws |

Rules the probes made explicit (`references/motion-grammar.md`): tokens travel tail to head;
blocks reveal in flow order (target after source); shafts draw after both endpoints revealed;
control tokens never faster or darker than data tokens; blocks and labels animate `opacity`
once and nothing else; nothing loops except pulse tokens; a `prefers-reduced-motion` block
shows the final state.

## Build

```bash
python -m figtree animate fig.svg -o fig.animated.svg                 # standalone SVG, <style> inside
python -m figtree animate fig.svg -o fig.animated.svg --css fig.css   # page form: SVG + separate stylesheet
python -m figtree animate fig.svg --modes reveal,draw --step 0.5      # subset, slower reveal
```

The figure must be a FigTree program: blocks with `data-role="block"` inside their leaf `<g>`,
flows with `data-flow` or `marker-end` and parseable `d` (`M H V L`; polylines are invisible to
the animator as to the critic). Timings are derived from the program, so the timeline is
deterministic and the total is `blocks x step + flows x 0.15 + draw (+ pulse)`.

## The four things that went wrong and the fixes that hold

1. **Reveals are opacity-only.** A CSS `transform`/`translate` on an SVG `<g>` *replaces* the
   group's own `transform="translate()"`: the block jumps to its container's corner. The
   explainer re-timed CSS uses `translate: 0 6px` only on groups without an SVG transform.
2. **Draw-on uses shaft copies.** A marker-ended path with a hidden shaft still paints its
   arrowhead: a floating triangle during draw-on. The shaft copy draws, then the real arrow
   with its head appears in one frame.
3. **One clock.** Captions, scrubber and figure share one timeline: caption `--on`/`--off`
   delays equal the figure's delays, the page keeps its own `performance.now()` clock (headless
   Chromium reports `Animation.currentTime` as 0 under virtual time), and the updater is a
   100 ms `setInterval`, because a perpetual `requestAnimationFrame` loop starves headless
   virtual time (every frame came back at 0.0 s).
4. **Reduced motion shows the final state.** `@media (prefers-reduced-motion: reduce)` sets
   `animation: none`, `opacity: 1`, `stroke-dashoffset: 0`, hides shafts and tokens; the page
   mirrors it with `?motion=reduce` so the fallback can be rendered. Hide chrome with
   `visibility`, not opacity (the fallback's `opacity: 1 !important` revealed an empty chip).

Also: a `<link>` to a web font stalls virtual time (the frame waits on the network); use
`@font-face { src: local(...) }` only, so a machine without the font falls through. Give pulse
tokens their path-start `cx`/`cy` (and `transform-box: fill-box; transform-origin: center`) so a
token sits on its path before its animation starts; `animate.py` leaves tokens at the origin,
the explainer sets them by hand, and the critic at HEAD no longer reports them as overflow
(probe `teaching.animated-tokens-at-origin` is silent).

## The explainer page

Start from `assets/explainer.template.html`: header with title and legend (data flow, control,
token), the figure card with the inlined animated SVG and a hover id chip (editable output),
controls (Pause/Play, Replay, scrubber with beat ticks, clock), a caption strip of 3-5 beats
with `--on`/`--off` per caption, `?theme=dark|light` and `?motion=reduce` switches, keyboard
space/R. Keep captions to 16-22 words for beats of 3-7 s; start a beat's first new element
0.1 s after its caption lights; cap the SVG width so the caption strip stays inside a 620 px
viewport. `assets/animation.template.css` is the generated stylesheet shape to re-time by beat.

Beat planning: list the beats, assign each a start time, then set every element's delay inside
its beat in flow order; tokens start after the last draw completes, share one cycle period,
and hold at 0 % / 100 % so the chain stays in order (speed 240-320 px/s, >= 0.35 s per hop).

## Verify with frames

`references/capture-frames.md` has the exact headless_shell commands. Capture at the beat
starts and mid-beats (800, 2500, 5000, 9000, 13000, 18500, 22500 ms were the showcase set),
once with `?theme=dark`, once with `--force-prefers-reduced-motion`, and once at phone width.
Then look: is the order right? is anything revealed before its source? do tokens sit on the
path and move tail to head? is the control token dimmer and slower? does the reduced-motion
frame equal the final frame? are captions readable in the time they are lit? Write the round's
findings and changes as a table (`examples/figtree/animated/NOTES.md` is the form).

A `.svg` opened directly is an image document: `--virtual-time-budget` does not drive it. Frames
come from the HTML page.

## References and assets

- `references/motion-grammar.md`: the binding rules, the generated CSS, the timeline arithmetic, and the measurable motion checks proposed by the adversary.
- `references/capture-frames.md`: headless Chromium commands for virtual-time frames, dark theme, reduced motion, phone width.
- `assets/animation.template.css`: the stylesheet shape `figtree animate` emits, with placeholders to re-time.
- `assets/explainer.template.html`: the player page with placeholders for title, SVG, CSS, captions and timeline constants.
