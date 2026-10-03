# DRAFT PR (DO NOT OPEN YET)

**Branch**: `cursor/hekat-sft-dataset-mvp-6a6b`  
**Base**: `master`  
**Steward rule**: Keep this draft updated; open PR only after orchestrator greenlight.

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
- Train/val: 45 / 7 (52 compile-ok)
- Blind eval: mvp_green on both splits
- Adversarial: 3/3 caught
- Monitor: no alarms

### Test plan
- [ ] `python3 tools/sft/build/template_generator.py`
- [ ] `python3 tools/sft/build/validate_dataset.py`
- [ ] `python3 tools/sft/eval/blind_eval.py`
- [ ] `python3 tools/sft/ops/adversarial/attack_suite.py`
- [ ] `python3 tools/sft/ops/monitor/snapshot.py`

### Not in this PR yet
- Hub publish
- Deep repo archive cleanup
- Package consolidation of root `hekat_*.py`
