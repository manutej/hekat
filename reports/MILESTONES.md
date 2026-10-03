# Milestones — HEKAT SFT MVP

## 2026-10-03 — Kickoff
- Branch: `cursor/hekat-sft-dataset-mvp-6a6b`
- Locked HF MessagesList schema with dual tags + artifact sidecars
- Wrote SOP, checklist, AGENTS.md, product/build specs
- Status: scaffolding in progress; no PR until MVP green

## 2026-10-03 — Phase 1–3 MVP plumbing green
- Generated **52** compile-ok rows (45 train / 7 val) across 7 patterns
- Blind eval **mvp_green** (pass_rate=1.0 both splits)
- Adversarial 3/3 caught; monitor alarms=[]
- Math: L2 sparse; sequential often metric-L4 — documented
- Arch: firewall OK; needs Composer diversity on traces/NL
- PR draft written — **not opened**
- Next: Composer-2.5 enrichment + minimal cleanup + push
