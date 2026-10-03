# AGENTS.md — HEKAT revival / SFT data MVP

## Mission
Revive HEKAT for **data curation**: MessagesList JSONL fine-tune dataset with dual reasoning (`<pseudocode>` + `<logic>`) and compiler artifacts (DSL, DAG, execution plan). Training focus is L1–L4 production track.

## Non-negotiables
- **No PR until comprehensively working** — commit + push on the feature branch only.
- **Blind eval segregation**: builders see build specs; eval sees only public product/schema specs — never generation prompts, scenario seeds, or adversarial recipes.
- **Composer 2.5** for sample-generation agent calls; instruct dual thinking styles.
- **Compiler ground truth**: root `hekat_compiler.py` pipeline must `compile_ok` for train rows.
- Commit at each meaningful milestone.

## Team roles (parallel)
| Role | Path | Job |
|------|------|-----|
| Builder | `tools/sft/build/` | Scenarios → DSL → traces → JSONL |
| Blind Eval | `tools/sft/eval/` | Spec-based scoring without build secrets |
| Adversarial | `tools/sft/ops/adversarial/` | Break samples; force repairs |
| Monitor | `tools/sft/ops/monitor/` | Metrics dashboard + drift alarms |
| Math reviewer | `reports/math/` | Token budgets, complexity math, limitations |
| Senior arch | `reports/architecture/` | Drift, anti-patterns (≠ task eval) |
| PR steward | `reports/pr/` | Draft PR body offline; **do not open PR** |

## Dataset contract (locked)
- Format: OpenAI/HF MessagesList JSONL
- Assistant order: `<pseudocode>` → `<logic>` → `<answer>`
- Sidecar: `task`, `artifacts`, `meta`
- Location: `datasets/hekat-orchestration-sft/`

## Authoritative refs
- `CORE.md` — three-track (ship L1–L4)
- Root compiler modules — ground truth for artifacts
- `docs/sft/SOP.md` — operating procedure
- `docs/sft/CHECKLIST.md` — measured phases
