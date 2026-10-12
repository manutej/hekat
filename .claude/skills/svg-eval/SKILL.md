---
name: svg-eval
description: Evaluate the FigTree evaluators by writing adversarial probes against a rubric, measure each check's recall and precision with `python -m figtree eval`, run the image judge and calibrate it against the measured scores, and decide when a gaming probe becomes a rule. Use when someone says "is the critic right?", "the score is 10 but the figure is bad", "write probes", "adversary", "harden the rubric", "false positive", "recall and precision of the checks", "judge this figure", "calibrate the judge", "blind spot", "add a check", or when a new medium or rubric is being introduced. Also use before trusting any `figtree score` number in a report. Not for building figures (svg-diagram, svg-data-figure, svg-icon).
---

# Evaluating the evaluators

A rubric is an artifact too, so it gets the same loop: publish the spec, attack it with
probes, measure recall and precision per check, read the gaps against an image judge, promote
what the probes prove into checks or veto rules, repeat. A check without a probe is unproven;
a gaming probe that stays gaming means the judge is the only defence and the showcase says so;
a false-positive probe that fires means the rule is wrong for that medium, not the figure.

## Probe kinds

| kind | what it is | passes when |
|---|---|---|
| `defect` | a minimal figure with one known defect | every `expect_fire` check fires and no `expect_silent` check does |
| `clean` | a correct figure (regression guard) | nothing in `expect_silent` fires |
| `gaming` | a bad figure that satisfies every measurable check | the critic scores >= 9.0 (fooled by definition); `expect_fire` names the `proposed.*` check that should exist |
| `false_positive` | a correct figure the critic wrongly flags | nothing in `expect_silent` fires (it fails until the rule is fixed) |

A probe is `examples/figtree/probes/<rubric>/<slug>.svg` + `<slug>.json` (schema in
`references/probe-schema.md`; template in `assets/probe.template.json`). Seed probes are
generated in `figtree/probes.py` (21 teaching, 3 data-figure, 4 icon, 2 slide). Check ids come
from `figtree/rubric_spec.py:CHECKS`; a check that does not exist yet is `proposed.<area>.<name>`.

## The eval loop

```bash
python -m figtree eval --specs examples/figtree/rubrics          # publish the spec (JSON per rubric)
python -m figtree eval --rubric teaching                          # recall, precision, failing probes, checks without probes
python -m figtree eval --rubric data-figure --report eval.json    # exit 1 while any probe fails
```

Read the summary as: `recall` = caught / expected fires (misses include `proposed.*`
expectations, which is the point, and a probe JSON that still expects `proposed.x` after the
real check `chart.x` landed stays a miss until renamed, so `eval` doubles as the rename list);
`precision` = caught / (caught + false positives);
`missed` lists what should have fired; `false_positives` what should not have. Then write the
adversary table (`assets/adversary-brief.md` has the columns): id, kind, what a cold reader
sees, what the critic did, proposed check or rule change, severity.

Attack with a lens per adversary: **gaming** (satisfy every check, mislead the reader),
**false positive** (library exports, legitimate layouts the rules reject), **miss** (a defect
an existing check should catch but does not: inheritance, transforms, polylines, paths),
**clean control** (a textbook figure). Render every probe before filing it; a probe that does
not look like what its rationale claims is refuted.

## When a gaming probe becomes a rule

1. The probe renders as claimed and three refuters cannot show otherwise.
2. The signal is computable from ids and attributes already in the program (`bar_axis_zero`:
   lowest y tick under bars reads 0; `legend_swatch_colour`: every swatch fill equals a mark's
   colour; `axis_units`: a parenthesised unit, `%`, or an explicit unitless marker).
3. A clean probe shows the rule stays silent on a correct figure of the same medium.
4. Then it is added to `CHECKS` with id, dimension, severity, signal, `mechanical` and a
   `pattern` over the critic's message, the critic emits that message, and the probe's
   `expect_fire` drops the `proposed.` prefix. If no signal exists (metaphor orientation,
   backwards semantics, misleading grouping), it becomes a judge question in `VETOES` or
   `JUDGE_QUESTIONS` and the showcase lists it under "what still fools the measurable critic".

Do not add a rule from one probe that only the author can see at 16 px; the cold-eye finding
goes to the medium's gotchas and the judge.

## The image judge and calibration

```bash
python -m figtree judge FIG.svg --rubric teaching [--source SRC.md] --report judge.json
python -m figtree judge --calibrate examples/figtree/eval/calibration-set.json --report calibration.json
```

The judge renders the PNG and asks Claude (through the Claude Code CLI on this session's
login, `Read` tool only, JSON schema enforced) for a 1-10 score, a justification and tags per
dimension, applying the vetoes (a veto caps a dimension at 4). It uses the full range: 5 is
mediocre, 9-10 reserved. Calibration runs judge and critic over a set and reports per figure
the gap (judged minus measured) and two kinds of finding: **rubric blind spot** (measured >= 9,
judged <= 6) and **rule to reconsider** (measured <= 6, judged >= 9). `references/calibration.md`
has the bundled result: mean gap -2.65 over 14 figures, 33 blind spots, 0 rules to reconsider,
$0.47.

Read a blind spot as "the rubric has no signal for this dimension on this medium" (topology
and flow on charts, compactness everywhere, text quality on an icon with text) before reading
it as "the judge is harsh". A judged 3 on `visual_polish` for a 10.0 slide is the judge seeing
the 12 px grey labels the critic measured as fine before refinement.

## Delegation

An adversary subagent gets one rubric, one lens, the probe directory and the brief; it returns
the probe ids it wrote and the eval line, never SVG. A refuter gets one probe path and returns
`{"id", "refuted": bool, "why"}`. The `figtree-adversary` workflow wires this up
(3 refuters per probe, refuted probes deleted, eval before and after).

## References and assets

- `references/probe-schema.md`: the JSON fields, naming, the seed probe builders, how `evaluate()` scores a probe.
- `references/calibration.md`: judge prompt shape, schema, the calibration format and the bundled results.
- `assets/probe.template.json`: a probe metadata file to copy.
- `assets/adversary-brief.md`: the brief for an adversary or refuter subagent and the table they return.
