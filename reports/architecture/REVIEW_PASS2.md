# Architecture Review Pass 2 — HEKAT SFT MVP

**Role:** Senior developer / drift watcher (not blind task eval).  
**Date:** 2026-10-03  
**Scope:** `tools/sft/**`, `datasets/hekat-orchestration-sft/**`, eval↔build firewall, dual lexer, train-loss surface.

## Executive summary

The MVP scaffold is **coherent**: build lane packs rows, eval lane re-checks public artifacts, sidecar `artifacts.*` stays out of the default `messages` training surface. **No full DAG JSON is stuffed into assistant turns today** (~1.5k chars/turn; plan summary only).

Main risks are **semantic drift** (two lexer implementations), **eval contract gaps** (train split can greenlight exit; registry rule not enforced in eval), **trace homogeneity** (7 logic skeletons for 52 rows), and **duplicated tag/DSL helpers** across build/eval. None of these require a PR to remediate locally; they are process, test, and small-script fixes.

---

## `tools/sft/` structure (as inspected)

| Path | Lane | Role |
|------|------|------|
| `build/pack_record.py` | BUILD | Single packer: compile → DAG/plan sidecars → `messages` |
| `build/template_generator.py` | BUILD | Deterministic traces from `scenarios/pilot_scenarios.json` |
| `build/enrich_from_agent_jsonl.py` | BUILD | Merge Composer JSONL; fallback to templates |
| `build/validate_dataset.py` | BUILD (gate) | G1–G6 hard gates on shipped JSONL |
| `build/scenarios/pilot_scenarios.json` | BUILD **secret** | Scenario seeds + `dsl_template` — eval must not read |
| `eval/blind_eval.py` | EVAL | Scorecard; no build imports |
| `ops/monitor/snapshot.py` | MONITOR | Volume/pattern alarms + eval signal |
| `ops/adversarial/attack_suite.py` | ADVERSARIAL | Mutations via `pack_record` (build import OK here) |

**Observation:** Only `eval/` is firewall-critical. Ops lanes correctly import build utilities; that is not a violation of the SOP firewall (eval must not see generation secrets).

---

## Dataset (`datasets/hekat-orchestration-sft/`)

| Asset | Status |
|-------|--------|
| `schema/record.schema.json` | Strict MessagesList + sidecar shape; `additionalProperties: false` on core objects |
| `data/train.jsonl` | 45 rows, all `compile_ok` |
| `data/validation.jsonl` | 7 rows, stratified 1 per pattern |
| `README.md` | States TRL should train on `messages` only; artifacts for research/filtering |

**Measured assistant surface (52 rows):**

- Assistant content: mean ~1,540 chars; max ~1,646.
- `artifacts.dag` JSON: mean small (2–4 nodes); **0** rows embed DAG JSON in assistant text.
- **45/52** assistants include a short markdown plan summary (`**pattern:**`, `**phases:**`, etc.) inside `<answer>` — intentional per packer, not full `execution_plan` JSON.
- **Logic diversity:** 7 unique logic skeletons (≈ one per `pattern_type`); pseudocode varies mainly via embedded NL.

---

## Information firewall (eval ↔ build)

### What works

- `blind_eval.py` imports only `hekat_compiler` + dataset paths; **no** `tools.sft.build`, `pilot_scenarios.json`, or `BUILD_SPEC.md`.
- Thresholds are **hardcoded** in eval (mirror `PRODUCT_SPEC.md`) rather than importing builder docs.
- Build secrets live under `tools/sft/build/scenarios/` and `docs/sft/BUILD_SPEC.md` — outside eval module graph.

### Gaps / anti-patterns

| ID | Severity | Anti-pattern | Evidence | Recommended fix (no PR required) |
|----|----------|--------------|----------|----------------------------------|
| F1 | **High** | Exit code treats **train OR validation** as MVP green | `blind_eval.py` `green = val.get("mvp_green") or train.get("mvp_green")` | Gate exit code on **validation only**; keep train metrics in scorecard for diagnostics only. Aligns with `PRODUCT_SPEC.md` (“≥0.90 on **validation** split”). |
| F2 | **Medium** | Monitor alarm uses **train** `mvp_green`, not validation | `ops/monitor/snapshot.py` L43–44 | Switch alarm to `validation.mvp_green`; add separate `train_mvp_green` field for debug. |
| F3 | **Medium** | PRODUCT_SPEC hard gate **registry ⊆ agents** not implemented in blind eval | No `TypeChecker` in `tools/sft/eval/` | Add registry check in `eval_split` or document as builder-only via `validate_dataset.py` and add explicit gate G4 implementation (today stubbed). |
| F4 | **Low** | Firewall is comment-only until runtime check | Docstring “CI later” | **Applied:** `assert_information_firewall()` in `blind_eval.py` fails fast if `tools.sft.build` is already imported. Extend CI with `python -c` import-linter or grep gate. |
| F5 | **Low** | `sys.path.insert(ROOT)` widens import surface | Eval adds repo root | Acceptable for MVP; long-term package `hekat_compiler` as installable dep and drop path hack. |

---

## Dual lexer risk (`hekat_lexer.py` vs `hekat/compiler/lexer.py`)

| Consumer | Lexer |
|----------|--------|
| SFT packer, `HEKATCompiler`, dataset gates | **Root** `hekat_lexer.py` |
| `hekat` package, `hekat/cli.py`, `tests/test_lexer.py` | **`hekat.compiler.lexer`** |

**Severity: High (latent).** The two modules are **different implementations** (distinct `TokenType` enums, different keyword/syntax surface in package lexer). Pilot DSL samples tokenize on both for L1–L4 operators, but **token counts already differ** on simple sequential forms (root 6 vs package 5 tokens for `a -> b : "x"`).

**Impact if ignored:** CLI/docs/tests green while SFT/compiler reject the same string; or new syntax added only to package lexer ships in docs but never in training data compiler.

**Recommended fixes (no PR):**

1. Declare **root pipeline canonical** for dataset MVP (already implied by `DRIFT_NOTES.md`).
2. Add a **single golden-file test** module (even a script under `tools/sft/`) that runs N pilot DSL strings through both lexers + root `Parser` and fails on divergence.
3. Long-term: thin wrapper `hekat.compiler.lexer` re-exporting root lexer, or delete duplicate and migrate CLI.
4. Do **not** switch packer to package lexer without full regression on `data/*.jsonl`.

---

## Train loss vs DAG / artifact pollution

| Question | Finding |
|----------|---------|
| Is full DAG JSON in assistant content? | **No** (0/52). |
| Is `execution_plan` JSON in assistant? | **No** — only in `artifacts.execution_plan`. |
| What *is* in loss-bearing assistant text? | Full `<pseudocode>`, full `<logic>`, DSL fence + **4-line plan summary** in `<answer>`. |
| Could future edits regress? | **Yes** — `build_assistant_content()` is the single choke point; no schema cap on assistant length. |

| ID | Severity | Anti-pattern | Recommended fix |
|----|----------|--------------|-----------------|
| L1 | **Low (current)** / **High (if changed)** | Embedding `json.dumps(dag)` into `<answer>` | Add packer assert: `assert "execution_order" not in assistant` and/or max chars on `<answer>` body in `validate_dataset.py`. |
| L2 | **Medium** | Uniform `<logic>` templates dominate gradient | Composer enrichment (`enrich_from_agent_jsonl.py`); reject rows whose logic hash matches template bank. |
| L3 | **Low** | README says TRL uses `messages` only — no repo training script enforces mask | When adding TRL config, use `assistant_only` / turn mask; document in dataset card. |

**Sidecar duplication:** DAG is serialized twice in spirit (`compiler.compile` + `serialize_dag()` re-lex/parse in `pack_record.py`). Not a loss issue; minor **consistency** risk if paths diverge.

---

## Build / validate anti-patterns

| ID | Severity | Issue | Fix |
|----|----------|-------|-----|
| B1 | **Medium** | `validate_dataset.py` G4 registry loop is a **no-op** (`pass` only) | Implement agent/skill extraction from compile plan or AST; fail on unknown agents. |
| B2 | **Medium** | G5 dedup uses `content_hash` (nl+dsl) — OK but SOP cites `(nl_hash, dsl_hash)` pairs | Align naming or split hashes in `meta` for clearer dedup audits. |
| B3 | **Low** | `TAG_RE`, `normalize_dsl`, `answer_dsl` **triplicated** in packer, validator, eval | Extract `tools/sft/common/tags.py` (build+eval may share; eval must not import scenario data). |
| B4 | **Low** | `split_rows()` takes **first** `n_val` per pattern (deterministic, not shuffled) | Document seed or shuffle with fixed seed before split for reproducible but less biased val. |
| B5 | **Advisory** | Train count 45 &lt; SOP “≥50 train” wording | Checklist already notes 52 total; clarify gate as total compile-valid or bump train rows. |

---

## Adversarial / ops notes

- `attack_suite.py` correctly lives in ops and **may** import `pack_record` — not an eval firewall breach.
- Adversarial `strip_logic` mutates packed row in memory; ensure failures are not accidentally merged into `data/*.jsonl` (today writes only `reports/adversarial/report.json` — OK).

---

## Verdict

| Area | Grade | Note |
|------|-------|------|
| Layout build/eval/ops | **A** | Clear separation; single packer ground truth |
| Firewall | **B+** | No build imports in eval; exit-code and monitor still overweight train |
| Lexer drift | **C** | Two implementations; pilot overlap only |
| Loss / DAG hygiene | **A−** | Clean today; choke-point discipline needed |
| Trace quality | **C+** | Compiler-valid but template-heavy logic |

**Pass 2 recommendation:** Ship dataset MVP for internal SFT experiments **with eyes open** on template logic and dual lexer. Before Hub publish or external eval claims: fix **F1/F2**, implement **B1/F3**, add lexer golden tests, and land Composer diversity (checklist Phase 4).

---

## Changes applied in this review (local, no PR)

- `tools/sft/eval/blind_eval.py`: `assert_information_firewall()` — runtime check that `tools.sft.build` is not loaded when eval runs.

**Suggested next local edits (not applied — eval semantics):**

- Validation-only exit code (F1).
- Monitor validation alarm (F2).
- Registry gate in eval or complete G4 in validator (F3/B1).
