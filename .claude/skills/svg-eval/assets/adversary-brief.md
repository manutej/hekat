# Adversary brief (one rubric, one lens)

You attack the measurable critic `figtree score --rubric {RUBRIC}` so its checks get better.
Spec: `python -m figtree eval --specs {SPEC_DIR}` then read `{SPEC_DIR}/{RUBRIC}.json`.
Existing probes: `examples/figtree/probes/{RUBRIC}/` and the tables in
`examples/figtree/probes/ADVERSARY-*.md` (do not duplicate them).
Eye checks that already exist: `.claude/skills/svg-*/references/*gotchas.md`.

Lens (one of): `gaming` = a figure that satisfies every check and misleads a reader;
`false_positive` = a correct figure (library export, legitimate layout) the critic flags;
`miss` = a defect an existing check should catch but does not (inheritance, transforms, paths,
polylines, hosts); `clean` = a textbook figure as a regression guard.

## Do
1. Write {N} probes as `{PROBE_DIR}/{RUBRIC}/<slug>.svg` + `<slug>.json`
   (`.claude/skills/svg-eval/assets/probe.template.json`). House style, ids on every element.
2. Render each (`python -m figtree refine P.svg --rubric {RUBRIC} --rounds 0 --render-dir r/`
   or the headless command in `svg-animation/references/capture-frames.md`) and confirm it
   shows what the rationale claims. Delete it if not.
3. Score each: `python -m figtree score P.svg --rubric {RUBRIC}` and record the overall and
   what fired.
4. Run `python -m figtree eval --rubric {RUBRIC}` and copy the summary line.

## Return (<= 2 KB JSON, no SVG)
```json
{"rubric": "{RUBRIC}", "lens": "gaming", "eval_line": "52 probes, recall 0.542, precision 0.765, missed 22, false positives 8",
 "probes": [
  {"id": "teaching.edge_hugging_arrow", "kind": "gaming", "sees": "one arrow touching three boxes along Parser's top border",
   "critic": "silent, 10.0", "proposed": "flow.through_block: inflate block boxes by a halo >= 4px; count collinear-with-edge as a hit",
   "severity": "veto (occlusion)"}
 ]}
```

# Refuter brief (one probe)

Probe: `{PROBE_SVG}` with `{PROBE_JSON}`. Render it and read the rationale. Your job is to show
the probe does **not** demonstrate its claim: the defect is not visible as described, the
"correct" figure is not correct, the proposed signal would also fire on the clean control, or
the check it names already fires. Return `{"id": "...", "refuted": true|false, "why": "<= 2 sentences"}`.
Majority of three refuters rules; refuted probes are deleted.
