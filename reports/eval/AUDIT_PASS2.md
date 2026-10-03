# HEKAT SFT — Independent Blind Eval Audit (Pass 2)

**Auditor role:** Independent blind eval (information firewall enforced)  
**Date:** 2026-10-03 (UTC)  
**Harness:** `python3 /workspace/tools/sft/eval/blind_eval.py`  
**Spec:** `/workspace/docs/sft/PRODUCT_SPEC.md`

## Executive verdict

| Gate | Result |
|------|--------|
| Validation MVP thresholds (`mvp_green`) | **PASS** |
| Automated `fail_ids` (validation) | **None** |
| Manual spot-check (5 rows) | **PASS** (tags + DSL/answer alignment) |

Validation split meets all four numeric thresholds at 1.0. No concrete failing row IDs under the blind harness definition of pass.

---

## Re-run metrics (scorecard)

Written to `reports/eval/scorecard.json`.

### Thresholds (PRODUCT_SPEC MVP)

| Metric | Required | Validation | Train |
|--------|----------|------------|-------|
| `pass_rate` | ≥ 0.90 | **1.0** (7/7) | 1.0 (45/45) |
| `tag_completeness` | = 1.0 | **1.0** | 1.0 |
| `compile_recheck` | ≥ 0.95 | **1.0** | 1.0 |
| `dsl_answer_match` | ≥ 0.95 | **1.0** | 1.0 |

Validation `pass_by_pattern`: Simple, Skilled, Sequential, Parallel, Mixed, Fallback, Commanded — 1 each.

Train note (informational only; not gating this audit): same perfect metrics; not manually spot-checked in this pass.

---

## Manual spot-check (5 validation rows)

Sampled for pattern diversity: Simple, Sequential, Mixed, Fallback, Commanded.

| `id` | Tag order (`pseudocode` → `logic` → `answer`) | Answer DSL = `artifacts.dsl` | Re-compile (via harness logic) | Notes |
|------|-----------------------------------------------|--------------------------------|--------------------------------|-------|
| `hekat-simple-000` | OK | OK | OK | L1 Simple; prompt echoes NL |
| `hekat-seq-000` | OK | OK | OK | L4 three-agent chain; DAG depth matches DSL |
| `hekat-mixed-000` | OK | OK | OK | Fan-out/grouping consistent with sidecar DAG |
| `hekat-fallback-000` | OK | OK | OK | `?` chain; `has_fallback` in plan metadata |
| `hekat-cmd-000` | OK | OK | OK | `@ctx7(...)` compiles; sidecar DAG lists agent `"unknown"` (artifact inconsistency, not harness fail) |

Additional checks on spot rows:

- All three XML regions non-empty; fenced `hekat` block present in `<answer>`.
- `task.pattern_type` / complexity in answer summary align with `artifacts.execution_plan` for checked rows.
- JSON Schema (`record.schema.json`) validates all 7 validation records (independent of stale `meta.quality.schema_valid: false` flags).

---

## PRODUCT_SPEC hard acceptance vs harness

The blind harness pass predicate requires: tags OK, `artifacts.compile_ok`, re-compile success, and normalized answer DSL match. It does **not** enforce tag **ordering** (only presence), registry extraction as a separate check (compile path validates agents), or JSON Schema.

Under the **full** PRODUCT_SPEC hard-acceptance list, spot-checked rows still satisfy compile, answer/artifact DSL match, and schema when validated externally. No validation `id` failed the harness; therefore **no failing ids to list**.

---

## Qualitative issues (non-blocking for MVP thresholds)

1. **Template-heavy reasoning** — `<pseudocode>` and `<logic>` share the same multi-branch `if pattern == ...` skeleton on every row; only the trailing concrete comment differs. Low pedagogical diversity for SFT.
2. **Weak / synthetic NL** — User turns are placeholder-like (`"Sequential workflow 0"`, `"Parallel exploration 0"`) with little orchestration intent signal; prompts often duplicate into the DSL string verbatim.
3. **Stale quality metadata** — Every validation row has `meta.quality.schema_valid: false` while records validate against `schema/record.schema.json`; undermines trust in sidecar quality flags.
4. **Artifact fidelity edge case** — `hekat-cmd-000`: `artifacts.dag.nodes[0].agent` is `"unknown"` while `execution_plan` names `ctx7(api-architect)`; DSL and compile are fine, but DAG sidecar is misleading for downstream filters.
5. **Dataset card alignment** — README already warns of synthetic repetition and L2 sparsity; validation set is one row per pattern (n=7), so threshold headroom is wide but coverage is thin.

---

## Failing row IDs (concrete harness failures)

*(none — validation `fail_ids: []`)*

---

## Auditor constraints observed

- Did not read `tools/sft/build/**`, `BUILD_SPEC.md`, enrichment prompts, or adversarial recipes.
- Did not modify train or validation JSONL.
- No PR opened.
