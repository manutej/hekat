# DRAFT PR (DO NOT OPEN YET)

**Branch**: `cursor/hekat-sft-dataset-mvp-6a6b`  
**Base**: `master`  
**Steward rule**: Keep this draft updated; open PR only after orchestrator greenlight.

## MVP status (2026-10-03)

| Area | Status |
|------|--------|
| Dataset rows | **52** compile-ok (45 train / 7 val), 7 patterns |
| Blind eval | **mvp_green** — pass_rate=1.0 on train and val |
| Adversarial | 3/3 caught |
| Monitor | `alarms=[]` (`reports/monitor/snapshot.json`) |
| Trace quality | **Composer-2.5 enrichment in flight** (template MVP on disk; diversity/NL still pending) |

Plumbing (pack, validate, blind eval firewall, ops snapshots) is green. This draft tracks a **template-quality MVP** until enrichment lands and the orchestrator approves opening.

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
- Train/val: 45 / 7 (**52** compile-ok)
- Blind eval: **mvp_green** on both splits (`reports/eval/scorecard.json`)
- Adversarial: 3/3 caught (`reports/adversarial/report.json`)
- Monitor: no alarms
- Enrichment: `tools/sft/build/enrich_from_agent_jsonl.py` + Composer agent JSONL — **in progress** (not yet merged into published rows for diversity gate)

### Blockers before open
1. **Orchestrator greenlight** — PR steward must not open until explicit approval (`docs/sft/CHECKLIST.md` Phase 4).
2. **Composer-2.5 enrichment** — dual-trace / naturalistic NL diversity (see `reports/architecture/REVIEW_PASS1.md`); template-only traces remain a known limitation until enrichment completes or is explicitly accepted.
3. **Branch pushed** — remote branch sync before open (checklist Phase 0).
4. **Hub-ready dataset card** — draft card; finalize L2 sparsity and post-enrichment row notes before publish (out of scope for first PR unless required by greenlight).

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
