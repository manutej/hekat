# PRODUCT SPEC — HEKAT Orchestration SFT (Eval-Visible)

**Audience**: Blind evaluators, monitors, math/arch reviewers.  
**Must not contain**: generation prompts, scenario seeds, adversarial recipes, or builder internals.

## Purpose
Train models to map natural-language orchestration intents to valid HEKAT DSL queries, with dual structured reasoning and a clear final answer.

## Output contract (assistant)
Exactly this order, all non-empty:

1. `<pseudocode>...</pseudocode>` — imperative sketch using coding-like steps  
2. `<logic>...</logic>` — ordered program-like reasoning (`fn`, `if`, `Parallel`, `Sequential`, `assert`, etc.)  
3. `<answer>...</answer>` — final HEKAT DSL in a fenced `hekat` block, plus short pattern/level summary  

## Input contract (user)
A natural-language task describing an agent orchestration need (design, implement, test, research, fallback, etc.).

## Record shape (public)
Each JSONL row:

- `id` (string)
- `messages` (list of `{role, content}` with system/user/assistant)
- `task.natural_language`, `task.pattern_type`, `task.complexity_level`
- `artifacts.dsl` (string), `artifacts.compile_ok` (bool)
- `artifacts.dag`, `artifacts.execution_plan` (objects; may be inspected for consistency)
- `meta.quality.*` booleans

## Valid DSL surface (L1–L4 production)
Operators: `:`, `+`, `->` / `→`, `||`, `?`, parentheses for grouping.  
Agents/skills/commands must exist in the public registry snapshot shipped with the dataset card.  
Complexity labels L1–L4 should be consistent with compiler metrics when `compile_ok`.

## Hard acceptance (eval)
A row **passes** iff:

1. Schema-valid  
2. All three XML tags present and non-empty  
3. `artifacts.compile_ok` is true and re-compiling `artifacts.dsl` succeeds  
4. DSL agents ⊆ registry  
5. `<answer>` DSL matches `artifacts.dsl` (normalized whitespace)

## Blind eval score thresholds (MVP)
- **Pass rate** ≥ 0.90 on validation split  
- **Tag completeness** = 1.0  
- **Compile recheck** ≥ 0.95  
- **DSL/answer match** ≥ 0.95  

## Out of scope for MVP
L6–L7 research monads, TUI agent, Query Builder hotkeys, consciousness YAML learning.
