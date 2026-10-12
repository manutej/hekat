# Judge calibration

Implementation: `figtree/judge.py` (`judge`, `calibrate`), driven by `python -m figtree judge`.

## The judge

- Renders the SVG to PNG (`figtree/render.py`: Chromium headless shell, rsvg-convert or
  cairosvg), then runs `claude -p` with `--json-schema`, `--tools Read --allowedTools Read`,
  `--no-session-persistence`, `--add-dir <render dir>` on the session's own OAuth login
  (no API key). Cost is reported per call (`total_cost_usd`, about 3 cents a figure).
- Prompt: the medium and its description, "read the image file at <png>", the source text when
  given (authority for coverage and hallucination; without it those two are scored "from
  internal consistency only"), the eight dimensions with their judge question and 1-10 anchors
  (`rubric_spec.JUDGE_QUESTIONS`, `ANCHORS`), the veto rules, and a 6000-character SVG excerpt
  for element-level evidence.
- System prompt: use the full range (5 mediocre, 1-2 broken, 9-10 reserved), judge as rendered,
  cite concrete visual evidence, 1-4 diagnostic tags, a veto caps the dimension at 4, do not
  reward attractive figures that are wrong.
- Schema: `{scores: {dim: {score 1-10, justification, tags[]}}, vetoes[], overall_comment}`;
  `overall` is the plain mean of the eight scores (no weights, no n/a).

```bash
python -m figtree judge FIG.svg --rubric slide --source src.md --report judge.json
```

## Calibration

```bash
python -m figtree judge --calibrate set.json --report calibration.json
# set.json: [{"name": "bar-chart before", "svg": "path.svg", "rubric": "data-figure", "source": "optional.md"}, ...]
```

For each item: `QualityCritic(rubric).review(svg, source)` and `judge(...)`; the row holds
measured and judged per dimension, both overalls and the gap (judged - measured). Findings:

| kind | condition | meaning |
|---|---|---|
| rubric blind spot | measured >= 9 and judged <= 6 | the rubric has no signal for what the judge saw (or the judge is wrong: check the PNG) |
| rule to reconsider | measured <= 6 and judged >= 9 | a check penalised something the medium accepts |

`mean_gap` is the mean of overall gaps; `cost_usd` the sum. The showcase renders the table and
the findings list.

## Bundled result (`examples/figtree/eval/calibration.json`)

14 figures: the four teaching artifacts before and after refinement, the icon before and
after, the three rule-grounded methodology figures and the Claude-grounded one. Mean gap
-2.65, 33 blind spots, 0 rules to reconsider, $0.471.

| figure | rubric | measured | judged | gap |
|---|---|---|---|---|
| bar-chart before / after | data-figure | 6.12 / 9.83 | 4.25 / 6.12 | -1.87 / -3.71 |
| slide-pipeline before / after | slide | 6.83 / 9.67 | 4.00 / 6.75 | -2.83 / -2.92 |
| dashboard-tiles before / after | dashboard | 5.80 / 9.70 | 5.25 / 7.75 | -0.55 / -1.95 |
| trajectory-chart before / after | data-figure | 6.05 / 10.0 | 4.75 / 7.50 | -1.30 / -2.50 |
| process-icon before / after | icon | 7.88 / 8.25 | 3.62 / 3.62 | -4.26 / -4.63 |
| figtree-spec / transformer / rmp-skill | methodology | 8.84 / 8.44 / 9.40 | 5.88 / 6.00 / 7.38 | -2.96 / -2.44 / -2.02 |
| figtree-spec (Claude-grounded) | methodology | 8.29 | 5.12 | -3.17 |

What the blind spots say, read across the set:
- `topology_accuracy` and `flow_readability` are 10.0 on every chart and tile (no arrows, no
  containers, nothing to measure) while the judge scores 5-6: on those media the critic should
  report them as not assessed, or the judge question should be medium-specific.
- `compactness` is 10.0 on most figures the judge puts at 5-6: the critic sees margins and
  detours, the judge sees uneven density and oversized canvases.
- `text_quality` 10.0 on the icon with text in it: the icon rubric's text checks never run on
  `text_quality` (the text-in-icon issue lands on `medium_fit`), so the dimension reads clean.
- The refinement gain is real but smaller to the judge (+1.9 to +2.8 judged vs +2.6 to +4.0
  measured): the mechanical fixes clear the measurable defects, the design decisions the judge
  wants (hierarchy, density, a real finding) are the requests the loop hands back.
- The judge and the critic agree on direction for every pair (after > before), so the loop is
  not optimising the wrong thing; it is optimising a subset of the right thing.

## Using it

- Run the judge on anything whose measured score is >= 9 before claiming it is done; the
  showcase's design round went paper-register judged 5.88 -> teaching-register round 3 judged
  higher only after four changes the critic never asked for (preset, barycenter ordering, lane
  allocation, row balancing).
- Keep the set small and fixed so gaps are comparable across rubric changes; add a figure when
  a probe shows a new blind spot.
- Report cost; the judge is the expensive evaluator.
- The `figtree-judge-panel` workflow runs three judges with distinct lenses (faithfulness to
  source, readability at a glance, aesthetics and medium fit) and synthesises a ranking when
  one judgement is not defensible enough.
