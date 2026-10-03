# Math / Metrics Reviewer Notes

**Role**: Verify complexity classification and token budgets are handled as well as possible; document limitations.  
**Status**: Pending first dataset snapshot.

## Scope
- Compiler `_classify_complexity_from_metrics` vs labeled `task.complexity_level`
- Token budget heuristics vs real usage (unknown in synthetic MVP)
- DAG phase counts vs operator nesting

## Limitations (known a priori)
1. Token estimates are **heuristic**, not measured LLM usage.
2. Complexity levels are **metric-derived**, not semantic difficulty.
3. Parallel token budgets currently **sum** phase estimates; may overcount vs true concurrent wall-cost.
4. Ensemble/`sample^N` math is out of MVP train distribution.

## Checklist for each release
- [ ] Spot-check 10 rows: level matches compiler output
- [ ] No negative / zero token budgets
- [ ] Document any pattern where level surprises (e.g. 3-agent sequence → L4)
