# Math Review Pass 1

## Observations from monitor snapshot
- Levels in pilot: L1=20, L2=1, L3=16, L4=15
- 3-agent sequential chains often classify as **L4** under compiler metrics (agent count + depth), not L2. This is consistent with `hekat_compiler._classify_complexity_from_metrics` but **surprising vs product narrative** ("L2 = sequential").
- Token budgets are always > 0 for compile-ok rows (spot-checked via generator).

## Limitations to document in dataset card
1. Complexity labels are compiler-metric labels, not human task difficulty.
2. Token totals are estimates; do not treat as billing truth.
3. L2 underrepresented (n=1) — distribution skew toward L1/L3/L4.

## Recommendations
- Either (a) relabel dataset `complexity_level` strictly from compiler (current), and teach users the metric meaning; or (b) add `semantic_level` separate from `compiler_level` later.
- For MVP keep compiler-aligned labels; note L2 sparsity in card.
