# DRAFT PR (DO NOT OPEN YET)

**Branch**: `cursor/hekat-sft-dataset-mvp-6a6b`  
**Base**: `master`  
**Steward rule**: Keep this draft updated; open PR only after orchestrator greenlight.

## MVP status (2026-10-03)

| Area | Status |
|------|--------|
| Dataset rows | **79** compile-ok (66 train / 13 val), 7 patterns |
| Blind eval | **validation mvp_green** (exit gated on val only) + `registry_ok` |
| Adversarial | 8/8 caught |
| Monitor | `alarms=[]`; tracks `eval_mvp_green_validation` |
| Trace quality | **79/79** Composer-enriched (batch_a–d) |
| Arch F1–F3 | Applied (val-only green, monitor, registry G4) |

## Title
feat: HEKAT orchestration SFT dataset MVP (MessagesList + dual reasoning)

## Body

### Summary
- Adds HF-native MessagesList SFT dataset under `datasets/hekat-orchestration-sft/`
- Dual assistant reasoning: `<pseudocode>` → `<logic>` → `<answer>`
- Compiler artifacts (DAG + execution plan) as sidecars
- Blind eval firewall, adversarial suite, monitor snapshot
- SOP + measured checklist

### Evidence (current)
- Train/val: 66 / 13 (**79** compile-ok)
- Blind eval: validation mvp_green (`reports/eval/scorecard.json`)
- Adversarial: 8/8 (`reports/adversarial/report.json`)
- Monitor: no alarms
- Arch follow-ups F1–F3 landed

### Blockers before open
1. **Orchestrator greenlight** — do not open until explicit approval.
2. Optional: finish Composer enrichment for the 27 growth rows (batch_d).
3. Hub-ready card polish if publishing in the same PR.

### Test plan
- [ ] `bash tools/sft/ops/run_all_gates.sh`
- [ ] `python3 tools/sft/ops/math_check.py`

### Not in this PR yet
- Hub publish
- Package consolidation of root `hekat_*.py`
- Dual-lexer unification
