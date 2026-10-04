# STATUS — HEKAT SFT MVP (live)

**Branch:** `cursor/hekat-sft-dataset-mvp-6a6b`  
**PR:** not opened (by design)

## What shipped
| Lane | State |
|------|-------|
| SOP + checklist + memories | done |
| Dataset schema + card | done |
| Pilot JSONL | **79** compile-ok (66/13); **79/79** composer-sourced (batch_a–d) |
| Blind eval | validation mvp_green (+ registry_ok); exit gated on val only |
| Adversarial | 8/8 catch |
| Monitor | no alarms |
| Math review | labels match compiler; L2 sparse |
| Arch review | firewall OK; dual-lexer **specced** (root oracle; package 7/7 divergent) |
| Dual-track spec | `docs/sft/DUAL_REASONING_SPEC.md` + research notes |
| Composer enrichment | 79/79 composer-sourced |
| PR steward | draft only |

## Checklist progress
Phases 0–3 complete. Phase 4 data gates complete except **orchestrator PR greenlight**.

## How to re-run gates
```bash
bash tools/sft/ops/run_all_gates.sh
python3 tools/sft/ops/math_check.py
```
