# DSL Symbolic Visual Guide

**Quick Reference for Claude Code Agent Orchestration**

---

## 🎯 Core Symbols

```
●  Agent          ┃  Operator      ═══  State/Context
◐  Skill          │  Data flow     ···  Optional path
▣  Command        ┊  Async          ━━  Synchronization barrier
⬡  Workflow       ╱  Conditional    ⟿   Loop/iteration
```

---

## Operators at a Glance

```
→   Sequential    A → B → C

║   Parallel     A ║ B ║ C

⊕   Combination   A ⊕ skill₁ ⊕ skill₂

:   Binding       agent : "task"

=   Assignment    param = value

?   Conditional   A → ? → B | C

*   Iteration     (A → B)*

⟲   Retry         A ⟲³ → fallback
```

---

## Level 1: Single Invocation

```
●──────┐
│ task │
└──┬───┘
   ↓
 result
```

**Example**: `api-architect : "design API"`

---

## Level 2: Binary Operations

### Sequential (→)
```
●─────●─────●
A  →  B  →  C

t₁    t₂    t₃
Total: t₁ + t₂ + t₃
```

### Parallel (║)
```
     ┌───●───┐
     │   A   │
     ├───●───┤
     │   B   │
     └───●───┘
       max(tₐ, tᵦ)
```

### Combination (⊕)
```
●  ⊕  ◐  ⊕  ◐
agent + skill₁ + skill₂
   = enhanced_agent
```

---

## Level 3: Parallel Streams

```
        ┏━━━━━┓
        ┃input┃
        ┗━┯━━━┛
    ┌─────┼─────┬─────┐
    │     │     │     │
    ▼     ▼     ▼     ▼
  ●───  ●───  ●───  ●───
  S₁    S₂    S₃    S₄
  │     │     │     │
  └─────┼─────┴─────┘
      ━━┷━━ (barrier)
        │
        ▼
     merge
```

**Example**: `(A ║ B ║ C) : task`

---

## Level 4: Complex Orchestration

### Fan-Out / Fan-In
```
       ●
      ╱│╲
     ╱ │ ╲
    ●  ●  ●
    │  │  │
    └──┼──┘
       ●
```

### Conditional Branch
```
    ●
    │
    ?
   ╱ ╲
  ●   ●
  Y   N
```

### Error Handling
```
●──→ ⟲³ ──→ ●
│          fallback
└──✗───────→ ●
```

### Nested Parallel
```
●─────┬─────┐
      │     │
    (●→●) (●→●)
      │     │
      └──●──┘
```

---

## Level 5: Workflow Composition

### Named Workflow
```
┏━━━━━━━━━━━━━━┓
┃ workflow W   ┃
┠──────────────┨
┃ ●→(●║●)→●    ┃
┗━━━━━━━━━━━━━━┛
      ↓
    W(params)
```

### Map-Reduce
```
[●,●,●,●]
    │ map
 ┌──┼──┐
 ●  ●  ●  (parallel)
 │  │  │
 └──┼──┘
    │ reduce
    ●
```

### Context Sharing
```
    ═══ ctx
     │
●────┼────●────┼────●
A   ctx   B   ctx   C
     (shared context)
```

---

## Level 6: Meta-Programming

### Functor
```
Workflow⟨A⟩
     │
   fmap(f)
     │
     ▼
Workflow⟨B⟩
```

### Applicative
```
  ●     ●     ●
  │     │     │
  └─────┼─────┘
     <*>
      │
      ●
```

### Monad
```
do {
  a ← ●
  b ← ●(a)
  c ← ●(b)
  return c
}
```

### Workflow Generator
```
meta⟨T⟩ → ⬡
    │
    ├─→ ⬡⟨User⟩
    ├─→ ⬡⟨Product⟩
    └─→ ⬡⟨Order⟩
```

---

## Composition Patterns

### Pipeline
```
●──→●──→●──→●
   linear flow
```

### Diamond
```
    ●
   ╱ ╲
  ●   ●
   ╲ ╱
    ●
```

### Star (Hub-Spoke)
```
    ●
   ╱│╲╲
  ● ● ● ●
```

### Tree
```
      ●
    ╱   ╲
   ●     ●
  ╱ ╲   ╱ ╲
 ●   ● ●   ●
```

### Mesh
```
 ●─●─●
 │╳│╳│
 ●─●─●
```

---

## Time & Token Diagrams

### Sequential
```
●────●────●────●
t₁   t₂   t₃   t₄
━━━━━━━━━━━━━━━━
Total: Σ(tᵢ)
Tokens: Σ(tokᵢ)
```

### Parallel
```
●────│
●────│  max(t)
●────│
━━━━━━
Total: max(tᵢ) + merge
Tokens: max(tokᵢ) + overhead
```

### Hybrid
```
●───→ ●───┐
      │   ├──→ ●
●───→ ●───┘
━━━━━━━━━━━━━━━
Total: seq + max(par)
```

---

## State Transitions

### Simple
```
S₀ → [●] → S₁
```

### Fork/Join
```
      S₀
    ╱  │  ╲
   ●   ●   ●
    ╲  │  ╱
      S₁
```

### Conditional
```
S₀ → ? → S₁
     └─→ S₂
```

### Loop
```
S₀ → ● ⟲ S₀
     ↓
     S₁
```

---

## Error Patterns

### Retry
```
●──✗──⟲──●──✗──⟲──●──✗──→ fallback
1st   retry  2nd   retry  3rd
```

### Circuit Breaker
```
CLOSED ──failures──→ OPEN
  ↑                    │
  │                 timeout
  │                    ↓
  └──success── HALF_OPEN
```

### Graceful Degradation
```
primary ──✗──→ cached ──✗──→ default
   ●             ●              ●
```

---

## Resource Constraints

### Budget Limit
```
[●][●][●]  budget: 50K
 ▲  ▲  ▲
 │  │  └─ waiting (insufficient budget)
 │  └──── running (20K)
 └─────── running (30K)
```

### Concurrency Limit
```
Running: [●][●]  (2/2 max)
Queued:  [●][●][●]
```

### Timeout
```
●────────────────⏱──✗
     30 min limit
```

---

## DAG Patterns

### Linear DAG
```
●→●→●→●
 Depth: 4
 Width: 1
```

### Balanced Tree DAG
```
       ●
     ╱   ╲
    ●     ●
   ╱ ╲   ╱ ╲
  ●   ● ●   ●
Depth: 3
Width: 4
```

### Layered DAG
```
Layer 0:  ●  ●  ●
          │╲ ╱│ ╱
Layer 1:  ● ● ●
          │ ╳ │
Layer 2:  ● ●
          │╱
Layer 3:  ●
```

---

## Type Signatures

### Sequential
```
●ᴬ → ●ᴮ : A → B → workflow⟨A,B⟩
```

### Parallel
```
●ᴬ ║ ●ᴬ : A → (B,C) → workflow⟨A,(B,C)⟩
```

### Generic
```
⬡⟨T⟩ : ∀T. T → Result⟨T⟩
```

---

## Quick Pattern Lookup

| Pattern | Symbol | Use When |
|---------|--------|----------|
| Pipeline | `●→●→●` | Dependent steps |
| Fan-out | `●╱│╲●` | Independent parallel |
| Conditional | `●?●` | Runtime decisions |
| Loop | `●⟲●` | Retry/iterate |
| Map-reduce | `[●]→●` | Collection processing |
| Context share | `●═●` | Shared resources |
| Fallback | `●+●` | Error recovery |
| Barrier | `━━` | Synchronization |

---

## Common Compositions

### Research Pipeline
```
●──→(●║●║●)──→●
research  parallel  synthesize
         analysts
```

### CI/CD
```
●→●→?→●→●
build  ╲
test    deploy
check  ╱
       rollback
```

### Data Processing
```
[●,●,●,●]
    │ split
  ●║●║●  transform
    │ reduce
    ●  aggregate
```

### Microservice Deploy
```
     ●
   ╱ │ ╲
  ● ● ● ●  build services
   ╲ │ ╱
     ●    integrate
     │
     ?    health check
    ╱ ╲
   ●   ●  deploy / rollback
```

---

## Legend Summary

```
SHAPES              CONNECTIONS         MODIFIERS
──────              ───────────         ─────────
●  Agent            →  Sequential       ⟲  Retry
◐  Skill            ║  Parallel         ?  Conditional
▣  Command          ═  State/Context    *  Iteration
⬡  Workflow         ┊  Async flow       ✗  Error/Failure
                    ╱  Branch           ⏱  Timeout
                    ━  Barrier          ╳  Intersection
```

---

## Complexity Quick Reference

```
L1:  ●           (5K tok, 5 min)

L2:  ●→●         (15K tok, 10 min)
     ●║●

L3:  ●║●║●       (50K tok, 30 min)

L4:  ●→(●║●)→?   (100K tok, 60 min)

L5:  ⬡(●→●║●)    (200K tok, 2 hr)

L6:  meta⟨T⟩     (500K+ tok, 4+ hr)
```

---

## Execution Model

```
INPUT
  │
  ▼
PARSE ──→ AST
  │
  ▼
TYPE CHECK
  │
  ▼
BUILD DAG
  │
  ▼
STRATIFY
  │
  ▼
┌───────────┐
│ Level 0   │ ●  ●  ●  ●  (parallel)
├───────────┤ ━━━━━━━━━━━ (barrier)
│ Level 1   │ ●  ●        (parallel)
├───────────┤ ━━━━━━━━━━━
│ Level 2   │ ●           (single)
└───────────┘
  │
  ▼
RESULT
```

---

## Mathematical Foundations

```
CATEGORY THEORY         GRAPH THEORY
───────────────         ────────────
● → ● : morphism        V = {agents}
id → ● = ●              E = {dependencies}
(f∘g)∘h = f∘(g∘h)       DAG = (V, E)

MONOID                  TOPOLOGICAL SORT
──────                  ────────────────
● ⊕ ● : composition     in-degree → 0
● ⊕ ∅ = ●                    ↓
(●⊕●)⊕● = ●⊕(●⊕●)        schedule
                              ↓
FUNCTOR                    execute
───────                        ↓
fmap: (a→b)→(F a→F b)      result
F(g∘f) = F(g)∘F(f)
```

---

**End of Symbolic Visual Guide**

*Use this as a quick reference alongside the comprehensive documentation*
