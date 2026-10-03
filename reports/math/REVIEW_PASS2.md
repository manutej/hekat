# Math / Metrics Review — Pass 2

**Reviewer role:** Cross-functional math/metrics review for HEKAT orchestration SFT.  
**Inputs:** `hekat_compiler.py` (`_classify_complexity_from_metrics`, `_estimate_tokens`), `reports/monitor/snapshot.json`, `datasets/hekat-orchestration-sft/data/{train,validation}.jsonl`.  
**Tooling:** `python tools/sft/ops/math_check.py` (run 2026-10-03).

---

## Executive summary

| Check | Result |
|-------|--------|
| `complexity_level` vs live recompile (full corpus n=52) | **0 mismatches** |
| Spot-check 15 stratified rows (seed=42) | **15/15 match** |
| `task.complexity_level` vs `execution_plan.complexity_level` | **Always equal** (spot-checked on full set) |
| Token budgets ≤ 0 | **None** (totals and per-phase) |
| `total_tokens` vs recompile | **0 drift** on all compile-ok rows |

Pilot snapshot (`snapshot.json`): 45 train + 7 validation, 52 compile-ok, levels L1=20, L2=1, L3=16, L4=15, **L5–L7 absent**.

**Verdict:** Labels and token fields are **compiler-consistent** for the current MVP corpus. Residual risk is **semantic** (what “L2” means to humans vs metrics), **distribution** (L2/L5+ sparsity), and **heuristic tokens** (not measured usage).

---

## 1) Complexity level vs compiler output

### Compiler rules (reference)

From `HEKATCompiler._classify_complexity_from_metrics` (ordered cascade on DAG metrics: `total_agents`, `execution_depth`, `has_parallelism`, `has_fallback`):

| Level | Condition (first match wins) |
|-------|------------------------------|
| L1 | 1 agent, depth 1 |
| L2 | 2 agents, depth 2, no parallelism |
| L3 | ≤3 agents and (parallelism **or** depth ≤2) |
| L4 | ≤5 agents and depth ≤3 |
| L5 | ≤7 agents and parallelism |
| L6 | ≤10 agents **or** fallback in AST |
| L7 | else |

Pattern type (`Sequential`, `Parallel`, …) is **not** an input to classification—only DAG metrics.

### Spot-check (15 rows)

Stratified sample (2 per pattern where possible, seed=42): all 15 IDs recompiled to the same level as `task.complexity_level` and stored `execution_plan.complexity_level`.

Representative rows:

| id | pattern | stored | recompile | agents | depth | parallel |
|----|---------|--------|-----------|--------|-------|----------|
| hekat-seq-002 | Sequential | L2 | L2 | 2 | 2 | no |
| hekat-seq-005 | Sequential | L4 | L4 | 3 | 3 | no |
| hekat-par-002 | Parallel | L3 | L3 | 3 | 1 | yes |
| hekat-mixed-002 | Mixed | L4 | L4 | 4 | 3 | yes |
| hekat-fallback-002 | Fallback | L3 | L3 | 3 | 1 | yes |
| hekat-cmd-001 | Commanded | L1 | L1 | 1 | 1 | no |

### Full-corpus check

Recompiled every row’s `artifacts.dsl` with the in-repo compiler: **52/52** agreement on `complexity_level` across `task`, `execution_plan`, and fresh compile.

**Conclusion:** For this release, `complexity_level` **always equals** compiler output. Training targets that echo `**level:**` in assistant `<answer>` blocks are aligned with artifacts.

---

## 2) Token budget sanity

### Heuristic (compiler)

Per phase (`_estimate_tokens`):

```
budget = 500 + 100×(agents in phase) + int(0.75×len(prompt)) + (200 if len(agents)>1 else 0)
```

`execution_plan.total_tokens` = **sum of phase budgets** (sequential phases add; parallel agents in one phase share one budget line but include the +200 parallel penalty once for that phase).

### Observed (n=52)

| Stat | Value |
|------|-------|
| min `total_tokens` | 637 |
| max `total_tokens` | 2289 |
| mean `total_tokens` | ~1208 |
| zero / negative totals | 0 |
| zero / negative phase `token_budget` | 0 |
| recompile `total_tokens` mismatch | 0 |

### Caveats (not bugs, but dataset-card material)

1. **Not measured tokens** — character-based prompt scaling (0.75×chars) is a rough stand-in for tokenizer behavior.
2. **No skill-aware surcharge** — `Skilled` rows use the same formula; skills do not add budget.
3. **Summed phases ≠ wall-clock cost** — parallel phases contribute one budget line each; summing across phases overstates concurrent work for scheduling narratives.
4. **Stable for SFT** — values are deterministic given DSL + compiler version; good for consistency, not for billing.

---

## 3) L2 sparsity and Sequential → L4

### L2 sparsity (quantified)

| Metric | Value |
|--------|-------|
| L2 rows (all patterns) | **1 / 52 (1.9%)** |
| Matches snapshot `levels.L2` | yes (1) |
| Patterns with any L2 | **Sequential only** (1 row) |

**Level × pattern crosstab (n=52):**

| Pattern | L1 | L2 | L3 | L4 |
|---------|----|----|----|-----|
| Simple | 8 | — | — | — |
| Skilled | 8 | — | — | — |
| Commanded | 4 | — | — | — |
| Sequential | — | 1 | — | 7 |
| Parallel | — | — | 8 | — |
| Fallback | — | — | 8 | — |
| Mixed | — | — | — | 8 |

L5, L6, L7: **0 rows** in pilot (no agent count >5, no fallback-driven L6 bump in practice except note below).

### Sequential → L4 (“surprise”)

| Metric | Value |
|--------|-------|
| Sequential rows | 8 |
| Sequential @ L4 | **7 (87.5%)** |
| Sequential @ L2 | **1 (12.5%)** — `hekat-seq-002` (2-agent chain) |

**Why 3-agent chains are L4, not L2 or L3:**

For `A -> B -> C`: `total_agents=3`, `execution_depth=3`, `has_parallelism=false`.

- **L2** fails: needs exactly 2 agents and depth 2.
- **L3** fails: needs `depth ≤ 2` when there is no parallelism (`agent_count ≤ 3` is true, but `depth ≤ 2` is false).
- **L4** matches: `agent_count ≤ 5` and `depth ≤ 3`.

Pilot sequential templates (`pilot_scenarios.json`): **7 of 8** `dsl_template` chains have **three** agents; only `seq-002` has two. That structural choice **explains** L2=1 and Sequential→L4=87.5% without label bugs.

**Product narrative gap:** If “Sequential pattern ⇒ L2” is implied in docs, the dataset and compiler **disagree** with that story. Correct statement: **“L2 ⇒ 2-agent linear DAG; most real sequential workflows in this pilot are 3-agent and compile to L4.”**

### Fallback note

Fallback rows are **L3** (3 alternatives, one parallel phase, depth 1), not L6—because L3 matches before the `has_fallback` L6 rule is reached. Fallback presence does not elevate level in this corpus.

---

## 4) LIMITATIONS — dataset card (copy-ready)

Use this block (or shorten) on the Hugging Face / internal dataset card:

1. **Synthetic MVP volume** — 52 examples (45 train / 7 val); not representative of production task diversity.
2. **Complexity is compiler-metric, not human difficulty** — `L1`–`L7` come from agent count, DAG depth, parallelism, and fallback flags; pattern name alone does not determine level.
3. **L2 and high levels underrepresented** — L2 is 1.9% of rows; **no L5–L7** examples in this release.
4. **Sequential workflows mostly label as L4** — 87.5% of Sequential pattern rows are L4 because templates use 3-agent chains; only 2-agent chains receive L2.
5. **Token budgets are heuristic estimates** — fixed base + per-agent + prompt character scaling; not tokenizer-accurate and not measured from model runs.
6. **Phase token sums are not wall-clock budgets** — parallel phases are budgeted per phase; summed `total_tokens` is a planning artifact, not concurrent spend.
7. **Skills do not affect token math** — Skilled DSL affects DAG node count (still one agent) and metadata only.
8. **Compiler version coupling** — `meta.hekat_compiler_version` / root pipeline; recompiling with a different classifier may change labels.
9. **Schema quality flag** — rows may show `quality.schema_valid: false` while `compile_valid: true`; math review does not override schema gates.
10. **Ensemble / `sample^N` and other advanced operators** — out of scope for pilot distribution; complexity rules for those shapes untested here.

---

## Recommendations (unchanged from Pass 1, confirmed)

1. **Keep** `task.complexity_level` compiler-aligned (current behavior is correct and consistent).
2. **Document** the Sequential/L4 coupling in the card and in any curriculum that teaches “levels.”
3. **Optional future work:** add `compiler_level` vs `semantic_level`; or add 2-agent sequential scenarios if L2 coverage is a training goal.
4. **Optional future work:** add L5–L7 scenarios (more agents, deep nesting, or fallback that survives to L6) before claiming full L1–L7 curriculum coverage.

---

## Appendix: `math_check.py` output

```
n_total=52
levels={'L1': 20, 'L2': 1, 'L3': 16, 'L4': 15}
complexity_mismatches=0
spot_check_15_ok=15/15
token_total_min=637 max=2289 mean=1208.0
token_total_nonpositive=0 phase_budget_nonpositive=0
token_drift_vs_recompile=0
L2_count=1 (1.9%)
sequential_n=8 L4=7 sequential_L4_rate=87.5%
```
