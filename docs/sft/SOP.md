# HEKAT SFT Data MVP — Standard Operating Procedure

**Status**: Active  
**Branch**: `cursor/hekat-sft-dataset-mvp-6a6b`  
**Goal**: Publishable HF-native MessagesList dataset with dual-style reasoning + compiler artifacts.

## 1. Principles

1. **Publish or perish** — ship a validated pilot before expanding.
2. **Multithreaded** — build, blind eval, adversarial, monitor, math, arch run in parallel lanes.
3. **Information firewall** — Eval never reads `tools/sft/build/` generation secrets (prompts, scenario seeds, adversarial recipes). Eval may only use:
   - `datasets/hekat-orchestration-sft/schema/`
   - `datasets/hekat-orchestration-sft/README.md` (card)
   - `docs/sft/PRODUCT_SPEC.md`
   - Compiler public behavior (compile succeeds / fails)
4. **Ground truth** — train rows require `artifacts.compile_ok == true`.
5. **Commits per phase** — no GitHub PR until MVP checklist is green.
6. **Dual thinking** — every assistant turn contains `<pseudocode>`, `<logic>`, `<answer>` in that order.

## 2. Lanes

```
BUILD ──► JSONL ──► MONITOR
  │                   ▲
  ▼                   │
ADVERSARIAL ──► repair loop
  │
EVAL (blind) ──► scorecard ──► BUILD backlog
MATH / ARCH ──► reports (advisory, not gate alone)
PR STEWARD ──► draft only (no open PR)
```

## 3. Phase loop

For each phase in `CHECKLIST.md`:

1. Assign owners (agents).
2. Execute work; write artifacts under agreed paths.
3. Update checklist `[x]` with evidence paths.
4. Append 3–6 lines to `reports/MILESTONES.md`.
5. `git add` / `commit` / `push` branch.
6. Do **not** open a PR.

## 4. Quality gates (hard)

| Gate | Rule |
|------|------|
| G1 Schema | JSON Schema validate each row |
| G2 Tags | All three XML blocks present, non-empty |
| G3 Compile | `HEKATCompiler.compile(dsl)` succeeds |
| G4 Registry | Agents/skills/commands ⊆ type-checker sets |
| G5 Dedup | Unique `(nl_hash, dsl_hash)` |
| G6 Split | Stratified by `pattern_type` × `complexity_level` |

## 5. Soft gates (advisory)

- Math: token budgets plausible; complexity labels match compiler metrics; document limitations.
- Arch: no dual-pipeline drift; no stuffing train loss with huge DAGs; no Alpaca regression.
- Adversarial: ≥1 failure class fixed per cycle or documented wontfix.

## 6. Stop line for PR

PR steward may open a PR **only** when:

- Pilot ≥50 train rows compile-valid
- Blind eval score ≥ threshold in `PRODUCT_SPEC.md`
- Checklist Phase 0–3 complete
- Human/orchestrator explicitly says “open PR”
