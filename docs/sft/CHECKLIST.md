# Measured Checklist — HEKAT SFT MVP

Track progress here. Evidence paths required. Update after each phase.

## Phase 0 — Operating system
- [x] SOP written (`docs/sft/SOP.md`)
- [x] Product spec written (`docs/sft/PRODUCT_SPEC.md`) — eval-visible
- [x] Build spec written (`docs/sft/BUILD_SPEC.md`) — builders only
- [x] AGENTS.md memories
- [x] Milestone log started (`reports/MILESTONES.md`)
- [x] Branch pushed (`cursor/hekat-sft-dataset-mvp-6a6b`)

## Phase 1 — Scaffold
- [x] Dataset card draft
- [x] JSON Schema (`schema/record.schema.json`)
- [x] Scenario bank skeleton (build-side only)
- [x] Packer / validator CLI
- [x] Blind eval harness stub (no build imports)
- [x] Ops stubs: monitor, adversarial, math, arch, pr-steward

## Phase 2 — Pilot generate (target 50)
- [x] ≥10 scenarios across Simple/Skilled/Sequential/Parallel/Mixed/Fallback (52 balanced)
- [~] Composer-2.5 dual-trace generations (template MVP shipped; Composer enrichment in progress)
- [x] Compiler artifacts attached
- [x] `data/train.jsonl` + `data/validation.jsonl` (45/7)
- [x] Hard gates G1–G6 pass

## Phase 3 — Blind eval + cross-functional
- [x] Blind eval scorecard published (`reports/eval/scorecard.json`)
- [x] Adversarial report + repairs (`reports/adversarial/report.json`)
- [x] Math limitations note (`reports/math/`)
- [x] Senior arch drift note (`reports/architecture/`)
- [x] Monitor metrics snapshot (`reports/monitor/snapshot.json`)
- [x] PR draft prepared (not opened) (`reports/pr/DRAFT_PR.md`)

## Phase 4 — Harden toward publish
- [x] Eval failures fixed or quarantined (none failing)
- [~] Dataset card complete for Hub (draft; add L2 sparsity note)
- [x] Size ≥50 compile-valid train+val rows (52); train alone 45
- [ ] Orchestrator greenlight for PR (stop: do not open until then)
- [ ] Composer-enriched naturalistic traces for diversity
