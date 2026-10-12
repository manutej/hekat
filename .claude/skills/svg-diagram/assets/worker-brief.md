# Worker brief: score / repair one SVG (fill in the braces, delete the rest)

You are a FigTree repair worker. One file in, one command, at most 2 KB of JSON out. Never paste
SVG into your reply. Do not regenerate the figure; edit elements by id.

## Inputs
- Figure: `{ABS_PATH_TO_SVG}`
- Rubric: `{methodology|teaching|slide|data-figure|dashboard|icon}`
- Source text (optional, enables coverage/hallucination): `{ABS_PATH_TO_SOURCE_OR_none}`
- Output directory: `{ABS_OUT_DIR}`
- Round budget: `{N}`
- Decisions already taken (do not reopen): `{LIST_OR_none}`

## Do
1. Score: `python -m figtree score {SVG} --rubric {R} --json > {OUT}/score.before.json`
2. Read the rendered PNG if one exists (`{OUT}/r/round0.png` after step 3) and walk through
   `.claude/skills/svg-diagram/references/gotchas.md` (or `chart-gotchas.md`, `icon-gotchas.md`).
3. Write `{OUT}/edits.json` (one list per round) answering the critic's requests AND your eye
   findings. Shorten labels in the same round you raise fonts. Contradict an auto-fix only in a
   later round.
4. Refine: `python -m figtree refine {SVG} --rubric {R} -o {OUT}/refined.svg --trajectory {OUT}/t.json --edits {OUT}/edits.json --rounds {N} --render-dir {OUT}/r`
5. Stop when the stop reason is `no edits left` or a plateau, or when only design decisions remain.

## Return exactly this JSON (<= 2 KB), nothing else
```json
{"svg": "{OUT}/refined.svg", "trajectory": "{OUT}/t.json", "edits": "{OUT}/edits.json",
 "before": 0.0, "after": 0.0, "rounds": 0, "stop": "no edits left",
 "scores_after": {"text_quality": 10, "visual_polish": 10, "compactness": 8.5},
 "requests_open": [{"check": "compactness.aspect", "anchor": "svg", "decision": "banner by design, kept"}],
 "eye_findings": [{"what": "arrow f2 hugs Parser's top border", "fixed": true, "op": "set_attr d on f2"}],
 "diff_elements_per_round": [0, 7, 3]}
```
Trim `requests_open` and `eye_findings` to the 5 most important each. If a command fails, return
`{"error": "<first line of the traceback>", "command": "<the command>"}` and stop.
