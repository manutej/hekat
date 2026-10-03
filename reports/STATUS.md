# STATUS — HEKAT SFT MVP (live)

**Branch:** `cursor/hekat-sft-dataset-mvp-6a6b`  
**PR:** not opened (by design)

## What shipped
| Lane | State |
|------|-------|
| SOP + checklist + memories | done |
| Dataset schema + card | done |
| Pilot JSONL | **52** compile-ok (45/7) |
| Blind eval | mvp_green |
| Adversarial | 8/8 catch |
| Monitor | no alarms |
| Math review | labels match compiler; L2 sparse |
| Arch review | firewall OK; dual-lexer deferred |
| Composer enrichment | 52/52 composer-sourced |
| PR steward | draft only |

## Checklist progress
Phases 0–3 complete. Phase 4 data gates complete except **orchestrator PR greenlight**.

## How to re-run gates
```bash
bash tools/sft/ops/run_all_gates.sh
python3 tools/sft/ops/math_check.py
```
