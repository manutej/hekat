# Verdict schemas (what comes back from a worker or a workflow agent)

The orchestrator never receives markup. These are the shapes it does receive; the workflow
scripts enforce them with JSON Schema (`schema` option of `agent()`), workers are asked for them
in the brief's "report format".

## Score verdict (figtree-refine, scorer stage)

```json
{"overall": 9.19,
 "scores": {"semantic_coverage": null, "topology_accuracy": 10, "flow_readability": 9.3, "medium_fit": 7, "compactness": 8},
 "issues": [{"check_id": "compactness.blank_margin", "severity": "warning", "anchor": "svg", "fix": "shrink the canvas to content + margin"}],
 "requests": ["n4.arrow0: re-route to remove the crossing"]}
```
≤ 12 issues, critical first; `requests` are the content decisions a repairer must make.

## Repair verdict (figtree-refine, repairer stage)

```json
{"overall_before": 9.19, "overall_after": 9.86, "edits_applied": 7, "remaining_requests": [], "output_svg": "<out_dir>/round1.svg", "note": "widened n8, re-routed n4.arrow0"}
```

## Probe verdict (figtree-adversary)

```json
{"probes": [{"id": "teaching.gaming-2-edge-hug", "kind": "gaming", "expect_fire": ["flow.through_block"], "expect_silent": [], "rationale": "arrow along a block edge touches three boxes"}]}
```
Refuter: `{"refuted": false, "reason": "renders as described; the critic is silent"}` (majority of 3).

## Judge verdict (figtree-judge-panel, one lens)

```json
{"dimensions": {"faithfulness": {"score": 8, "why": "all five stages present; feedback edge missing"}}, "vetoes": [], "headline": "complete but the loop is not visible"}
```

## Icon review (figtree-icon-family)

```json
{"score": 9.5, "defects": [{"size": 16, "what": "handle fuses with the lens", "fix": "shorten the handle by 1px"}]}
```

## Digest unit (figtree-digest)

```json
{"id": "rmp-skill--3", "title": "Refine step", "svg": "<out>/rmp-skill--3.svg", "overall": 9.33, "status": "ok"}
```

## Handoff verdict (figtree-handoff)

```json
{"tests": {"passed": 204, "failed": 0}, "eval": {"probes": 110, "recall": 0.99, "precision": 1.0},
 "git": {"branch": "claude/figtree-generator", "clean": true, "ahead": 0},
 "open_items": [{"source": "probes/FOLD-REPORT.md", "item": "icon.mirrored-magnifier needs the judge"}],
 "status_md": "<path to the generated level-3 section>"}
```

## Worker final report (free text, ≤ 40 lines)

Files created/changed · numbers before/after · how it was validated · unfinished items. The
orchestrator checks the files exist and re-runs the numbers before trusting the report.
