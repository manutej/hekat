# Compiler Canonical Spec (Dataset Ground Truth)

**Status**: Canonical for SFT artifacts  
**Audience**: Eval-visible for “which compiler is truth”; builders must follow.  
**Version**: 1.0 (2026-10-04)

## 1. Two lexers exist

| Module | Consumers today | Role |
|--------|-----------------|------|
| **Root** `hekat_lexer.py` → `hekat_parser.py` → `hekat_type_checker.py` → `hekat_dag_builder.py` → `hekat_compiler.py` | SFT packer, validators, blind eval, `validate_all.py`, root tests | **Canonical for dataset MVP** |
| Package `hekat/compiler/lexer.py` | `hekat.cli`, `tests/test_lexer.py` | Experimental / CLI surface (CCAO-style extras: `/agent`, `workflow { }`, comments) |

They are **different implementations**: distinct `TokenType` enums, different keyword sets, different token counts on the same L1–L4 strings (example: `a -> b : "x"` is 6 tokens on root including EOF vs 5 on package).

## 2. Decision (locked)

1. **Root pipeline is ground truth** for every `artifacts.dsl`, DAG, plan, and `compile_ok` flag.
2. Blind eval may import **only** `hekat_compiler` + `hekat_type_checker` from the root modules (plus dataset JSONL).
3. Do **not** switch the packer to `hekat.compiler.lexer` without a full JSONL recompile regression.
4. Package lexer may remain for CLI experiments; it must not silently become the SFT compiler.

## 3. Production DSL surface (what SFT may emit)

Operators the **root** compiler accepts today (L1–L4 focus):

- `:` invocation + quoted prompt (prompt required, non-empty)
- `+` skills
- `->` sequential (unicode `→` accepted by packer normalization before compile if rewritten to `->`)
- `||` parallel
- `?` fallback
- `()` grouping
- `@command(agent)` commanded (command ⊆ type-checker `commands`, e.g. `ctx7`)
- `sample^N` / ensemble (parser exists; **out of MVP train targets**)

Identifiers: kebab-case agents/skills from `TypeChecker` registries.

## 4. Complexity labels

`task.complexity_level` **must equal** `HEKATCompiler._classify_complexity_from_metrics` on the compiled DAG:

| Level | First-match rule |
|-------|------------------|
| L1 | 1 agent, depth 1 |
| L2 | 2 agents, depth 2, no parallelism |
| L3 | ≤3 agents and (parallelism or depth ≤2) |
| L4 | ≤5 agents and depth ≤3 |
| L5 | ≤7 agents and parallelism |
| L6 | ≤10 agents **or** fallback in AST |
| L7 | else |

**Limitation:** 3-agent sequential (depth 3) skips L3 and lands on **L4**. Product narrative “L2 = sequential” is **not** the compiler. Dataset cards must say labels are metric-derived. Fallback can jump to L6 under the `or has_fallback` branch when earlier levels do not match — document if that appears.

Token budgets are heuristic (`_estimate_tokens`); never treat as billing.

## 5. Golden-file requirement

`tools/sft/ops/lexer_golden.py` tokenizes a fixed list of production DSL strings on **both** lexers and writes `reports/architecture/lexer_golden.json`.

- Root token stream is the **oracle** for SFT.
- Package stream is recorded for drift detection.
- The script **fails** if root tokenization of a golden string changes (SFT compiler break).
- Package divergence is **reported**, not a hard fail, until unification.

Unification options (later, not MVP):

- A: `hekat.compiler.lexer` re-exports root `Lexer` / `TokenType`
- B: delete package lexer; migrate CLI to root
- C: keep both but add an adapter with an explicit compatibility table

## 6. Artifact serialization (root only)

Packer must:

1. `HEKATCompiler().compile(dsl)` → plan + `compile_ok`
2. Re-walk AST via `DAGBuilder` for sidecar `dag.nodes[].agent` labels (`Commanded` → `ctx7(agent)`, not `unknown`)
3. Never embed DAG JSON in assistant `<answer>`
