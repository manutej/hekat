# HEKAT Dual-Track Reasoning Spec

**Status**: Canonical for SFT traces  
**Audience**: Eval-visible. Builders, eval, math, and architecture all share this contract.  
**Version**: 1.0 (2026-10-04)

## 1. Problem

Freeform chain-of-thought trains models to *talk through* a plan. HEKAT plans are **graphs**: sequential `->`, parallel `||`, fallback `?`, skills `+`, commands `@`. Prose CoT does not force the network to hold those operators as control flow.

We use a **dual-track** scratchpad, then a locked answer:

1. `<pseudocode>` — imperative sketch (human-readable steps)
2. `<logic>` — the *same* plan rewritten as coding constructs (typed control flow)
3. `<answer>` — HEKAT DSL + short summary

The dual track is deliberate: two encodings of one plan, not two different plans.

## 2. Related work (what we are *not*)

| Family | What it does | HEKAT difference |
|--------|----------------|------------------|
| CoT (Wei 2022) | Natural-language steps | We ban prose-only traces in `<logic>` |
| PAL / PoT (Gao 2023, Chen 2023) | LLM writes **executable** code; interpreter computes | `<logic>` is **not executed**. Compiler ground truth is the DSL, not the logic program |
| Chain of Code (Li 2024) | Mix executable code + LM-emulated semantic calls | We mix **two non-executed encodings** (imperative + control-flow), then compile DSL |
| Logic-of-Thought (NAACL 2025) | Inject propositional logic into context | We inject **orchestration AST constructors**, not FOL |
| HoT XML highlights (2025) | XML around facts | We use XML as **lane separators**, not fact highlighters |
| HF / TRL `<think>` | Single messy scratchpad in assistant content | We keep traces **in assistant `content`** (TRL-compatible) but **split into two structured lanes** before `<answer>` |
| `reasoning_content` columns | Separate field some Hub datasets use | We do **not** rely on `reasoning_content`; TRL SFTTrainer example still embeds tags in `content` |

**Novelty claim (narrow):** dual *ordered* encodings of the same orchestration plan — first imperative, then constructor/control-flow — with compiler-validated DSL as the only executable artifact.

## 3. Assistant grammar

```
assistant := pseudocode_block logic_block answer_block
pseudocode_block := "<pseudocode>" WS body WS "</pseudocode>"
logic_block      := "<logic>" WS body WS "</logic>"
answer_block     := "<answer>" WS fence WS summary WS "</answer>"
fence            := "```hekat" NL dsl NL "```"
```

Rules:

- Order is **strict**: pseudocode → logic → answer. Extra text outside the three blocks is discouraged; eval currently checks presence, not exclusivity (future hard gate).
- Bodies must be non-empty after strip.
- Tags are case-insensitive; writers should emit lowercase.
- No nesting of these three tags.

## 4. `<pseudocode>` lane

**Purpose:** fast, linear intent capture.

Required shape (recommended, not regex-hard yet):

```
GOAL = <short_name>
STEPS:
  1. ...
  2. ...
RETURN dsl
```

Allowed: assignment, numbered steps, comments, agent names from the registry.  
Disallowed as the *only* content: a copy of the DSL string with no steps.

## 5. `<logic>` lane (coding constructs)

**Purpose:** force an ordered, type-shaped walk over the same plan.

The body **must** look like a program, not a paragraph. Required:

1. At least one function binding: `fn plan` or `def plan` or `fn compose`
2. At least one constructor **or** control-flow keyword from the table below
3. At least one `assert` (typecheck, arity, or registry)

### Constructor vocabulary (orchestration AST)

| Construct | Maps to DSL |
|-----------|-------------|
| `Agent(name)` / `Simple(name)` | identifier |
| `Skilled(agent, skills)` | `agent + skill + …` |
| `Sequential([...])` | `a -> b -> c` |
| `Parallel([...])` | `(a \|\| b \|\| c)` |
| `Fallback([...])` | `a ? b ? c` |
| `Commanded(cmd, [agent])` | `@cmd(agent)` |
| `with_prompt(task)` | `: "…"` |

### Control-flow vocabulary

`if` / `elif` / `else`, `for`, `return`, `assert`, `raise`.

### Example (valid)

```
fn plan(task: str) -> DslQuery:
  if needs_research(task):
    head = Agent("deep-researcher")
  else:
    head = Agent("api-architect")
  mid = Parallel([Agent("api-architect"), Agent("debug-detective")])
  dsl = Sequential([head, mid, Agent("practical-programmer")]).with_prompt(task)
  assert typecheck(dsl).valid
  return dsl
```

### Invalid

- Prose: “First we research, then we design in parallel…”
- DSL dump with no `fn`/`assert`
- A different plan than `<pseudocode>` (alignment violation)

## 6. Alignment (same plan, two encodings)

Both lanes must describe the **same** operator skeleton:

- Same pattern family (Simple / Skilled / Sequential / Parallel / Mixed / Fallback / Commanded)
- Same primary agents (set equality, order may be described differently)
- `<answer>` DSL is the compilation of that skeleton

MVP eval hard-gates tag presence + compile + DSL match. Alignment and construct vocabulary are **soft gates** (`logic_style_ok`) until a checker is promoted.

## 7. `<answer>` lane

Must contain a fenced `hekat` block whose body **equals** `artifacts.dsl` after whitespace/`→`→`->` normalization.

Optional 2–6 line summary (`pattern`, `level`, `phases`, `total_tokens`).  
**Forbidden:** full DAG JSON, `execution_order`, or `execution_plan` dumps (train-loss pollution).

## 8. Training surface

- Loss-bearing: `messages[*].content` only (HF MessagesList / TRL chat template).
- Sidecar `artifacts.*` is research/filter metadata, not chat tokens.
- Do not convert traces into a `reasoning_content` field unless a future Hub config is added; if added, it must be a *copy* of the two XML lanes, not a replacement.

## 9. Soft vs hard gates

| Check | Gate |
|-------|------|
| Three tags present, non-empty | Hard (G2) |
| Answer DSL = artifacts.dsl | Hard |
| DSL compiles on **root** compiler | Hard (G3) |
| Registry ⊆ type-checker | Hard (G4) |
| `<logic>` has `fn`/`def` + constructor/control + `assert` | Soft → promote after checker lands |
| Pseudocode/logic agent-set alignment | Soft |
| No DAG JSON in assistant | Soft (packer assert recommended) |
