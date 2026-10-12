# Capturing frames of an animated page

Headless Chromium drives CSS animations with `--virtual-time-budget=MS`: the page is loaded,
virtual time advances by MS milliseconds, then the screenshot is taken. This is how every
`frame-*.png` in `examples/figtree/animated/` was produced. The binary is the Playwright
headless shell the renderer (`figtree/render.py`) already locates; the flags are the renderer's
plus the virtual-time budget. Verified on this machine with the showcase explainer.

```bash
HS=$(ls /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell 2>/dev/null | head -1)
# full chromium instead: HS=$(which chromium); add --headless=new after "$HS"
PAGE="file://$PWD/examples/figtree/animated/index.html"     # absolute path; the SVG is inlined in the page
OUT=frames; mkdir -p "$OUT"

# frames at the beat starts and mid-beats (ms of virtual time)
for t in 800 2500 5000 9000 13000 18500 22500; do
  "$HS" --no-sandbox --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
        --window-size=960,620 --virtual-time-budget=$t \
        --screenshot="$OUT/frame-$t.png" "$PAGE"
done

# dark theme (the page honours ?theme=dark; --force-dark-mode would recolour the SVG too)
"$HS" --no-sandbox --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
      --window-size=960,620 --virtual-time-budget=18500 \
      --screenshot="$OUT/frame-dark-18500.png" "$PAGE?theme=dark"

# reduced-motion fallback: must equal the final frame, controls hidden, every caption lit
"$HS" --no-sandbox --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
      --window-size=960,620 --virtual-time-budget=500 --force-prefers-reduced-motion \
      --screenshot="$OUT/frame-reduced-motion.png" "$PAGE"
# the page's own switch renders the same fallback without the flag: "$PAGE?motion=reduce"

# phone width: no page-level horizontal scroll, captions stacked, figure scrolls inside its card
"$HS" --no-sandbox --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
      --window-size=390,900 --virtual-time-budget=9000 \
      --screenshot="$OUT/frame-phone-9000.png" "$PAGE"
```

Then look at each PNG (the `Read` tool shows images) and record, per frame, what is visible
and whether it matches the beat table.

## Rules learned the hard way

- A perpetual `requestAnimationFrame` loop in the page starves virtual time: every frame came
  back at 0.0 s with nothing revealed. Use a `setInterval` for any UI updater.
- `Animation.currentTime` reads 0 under virtual time even though timers run (verified: 31 ticks,
  `performance.now()` = 3011, `currentTime` = 0). The page must keep its own clock for the
  scrubber and the readout.
- A `<link>` to a web font blocks the budget on the network; use `@font-face src: local()` only.
- Opening the animated `.svg` directly renders an image document: `--virtual-time-budget` does
  not drive it (everything revealed, tokens at 0,0). Frames come from the HTML page.
- The window height must contain the caption strip (620 px for a 776 px-wide figure of aspect
  2.0); otherwise the captions fall below the viewport in every frame.
- Headless console errors: add `--enable-logging=stderr --v=0` and read stderr; the showcase
  checked "no script errors" this way.
- Static renders (no animation) use the same command without `--virtual-time-budget`; that is
  exactly what `figtree/render.py` runs, wrapping the SVG in a zero-margin page sized to the
  canvas (`--window-size=W,H`).

## Reading the frames: the checklist

| Frame | Expect |
|---|---|
| first beat (800 ms) | only the first block, mid-fade; caption 1 lit; clock 0.8 s |
| each beat start | the caption lights 0.1 s before the beat's first new element |
| mid-beat | the shaft mid-draw with no arrowhead yet; blocks it joins already visible |
| token frames | ringed tokens on the path, moving tail to head; parallel tokens side by side on a shared bus |
| control frame | the grey token visibly dimmer and slower than the black ones, on the dashed edge |
| dark | page dark, figure card white, legend swatches visible (use `currentColor`) |
| reduced motion | identical to the final frame, controls replaced by the note, no stray chrome |
| phone | captions stacked, figure keeps its 600 px minimum inside a scrolling card |
