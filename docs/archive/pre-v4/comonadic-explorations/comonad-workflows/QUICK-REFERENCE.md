# Comonadic Patterns: Quick Reference Card

---

## The 13 Patterns at a Glance

### Tier 1: Core Patterns (Start Here)

| # | Pattern | Form | Agent | Cost | Use |
|---|---------|------|-------|------|-----|
| 1 | **Perpetual Refinement** | `⟲ ∞ → converge` | practical-programmer | 500-2K/iter | Iterate until quality threshold |
| 2 | **Context Extraction** | `↓ → compress` | code-trimmer | 200-500 | Compress before distribution |
| 3 | **Multi-Agent Broadcast** | `⟲ → {agents}` | [any] | 2-3K/agent | Parallel expert analysis |
| 4 | **Self-Critique Loop** | `⟲ self → improve` | debug-detective | 800-1.2K/iter | Agent improves own work |
| 5 | **Sequential Pipeline** | `→ → →` | [chained] | 1-2K/stage | Linear agent dependencies |

### Tier 2: Advanced Patterns

| # | Pattern | Form | Agent | Cost | Use |
|---|---------|------|-------|------|-----|
| 6 | **Hierarchical Cascade** | `→ {*,*} → hierarchy` | [multi-level] | 4-6K | Multi-tier parallel stages |
| 7 | **Bidirectional Window** | `◄► context ↔ history` | [any] | ~400/window | Sliding attention mechanism |
| 8 | **Research Synthesis** | `⟲ collect → validate → critique` | deep-researcher | 3-5K/cycle | Deep research with validation |
| 9 | **Error Recovery** | `try → catch → backtrack → alternative` | practical-programmer | 1-2K extra | Graceful failure handling |
| 10 | **Consensus Formation** | `⟲ {experts} → weighted → aggregate` | mercurio-orchestrator | 1.5-2K | Expert agreement with weighting |

### Tier 3: Specialized Patterns

| # | Pattern | Form | Agent | Cost | Use |
|---|---------|------|-------|------|-----|
| 11 | **Streaming Aggregation** | `stream → fold → checkpoint` | [any] | O(window) | Bounded-memory infinite streams |
| 12 | **Knowledge Validation** | `⟲ fact-check → cross-ref → verify` | context7-doc-reviewer | 500-1K/claim | Claim verification with deps |
| 13 | **Adaptive Orchestration** | `⟲ monitor → optimize → adapt` | [any] | 1K overhead | Self-optimizing workflows |

---

## Quick Selection Guide

**I want to...**

- **Generate better code in one pass**
  → Pattern 4 (Self-Critique) + Pattern 1 (Perpetual)

- **Get opinions from multiple experts**
  → Pattern 3 (Broadcast) + Pattern 10 (Consensus)

- **Process huge codebase efficiently**
  → Pattern 2 (Extract) → Pattern 3 (Broadcast)

- **Do deep research I can trust**
  → Pattern 8 (Research) + Pattern 12 (Validation) + Pattern 10 (Consensus)

- **Build production API**
  → Pattern 5 (Sequential) + Pattern 4 (Self-Critique) + Pattern 1 (Perpetual)

- **Analyze long document**
  → Pattern 7 (Window) + Pattern 11 (Streaming) to manage memory

- **Handle failures gracefully**
  → Pattern 9 (Error Recovery) + Pattern 3 (Broadcast alternatives)

- **Optimize my workflow over time**
  → Pattern 13 (Adaptive) + Pattern 4 (Self-Critique)

---

## Pattern Composition Quick Reference

### Extract Before Broadcast
```
Context (50K) → Extract (1-2K) → Broadcast to 3 agents
Cost: 7-8K (vs 150K+ if no extract)
```

### Iterative Improvement Loop
```
Generate → Self-Critique → Improve → Repeat until converged
Cost: 2-4K per cycle (usually 2-3 cycles)
```

### Multi-Expert Consensus
```
Question → Broadcast to experts → Consensus formation → Validation
Cost: 3-4K total (all parallel)
```

### Deep Research Foundation
```
Research → Extract findings → Fact-check → Expert consensus → Refine
Cost: 8-12K
Confidence: High (multiple validation layers)
```

---

## Comonad Operations Reference

| Operation | Symbol | Meaning | Example |
|-----------|--------|---------|---------|
| Extract | `↓` | Compress/focus | Summarize 50K context to 2K |
| Duplicate | `⟲` | Copy context | Send to multiple agents |
| Extend | `→` | Apply with context | Agent sees full history |
| Converge | `:converge` | Stop at threshold | Quality ≥ 0.95 → done |
| Zip | `◄►` | Bilateral focus | Sliding attention window |
| Broadcast | `{}` | Multi-way | {agent1, agent2, agent3} |
| Loop | `*` | Repeat | Until condition met |

---

## Token Budget Cheat Sheet

**For 200K Token Budget**:

| Scenario | Available | Typical Usage | Remaining |
|----------|-----------|---|---|
| Simple 1-agent task | 124K | 1-2K | 122K |
| 2-agent broadcast | 124K | 4-5K | 119K |
| 3-expert consensus | 124K | 6-8K | 116K |
| Deep research | 124K | 10-12K | 112K |
| Full pipeline | 124K | 18-25K | 99-106K |

**Key Rule**: Extract saves 80-90% of tokens in broadcast scenarios

---

## Comonad Law Verification Checklist

Every pattern satisfies these laws:

**Left Counit**: `extract(duplicate(ctx))` returns original
- Extracting from duplicated context = original context ✓

**Right Counit**: `fmap(extract)(duplicate(ctx))` returns original
- Structure preserved through duplication/extraction ✓

**Coassociativity**: `fmap(duplicate)(duplicate(ctx))` = `duplicate(duplicate(ctx))`
- Multiple duplication levels are coherent ✓

All 13 patterns respect these laws.

---

## Common Pitfalls & Fixes

| Pitfall | Fix | Pattern |
|---------|-----|---------|
| Broadcasting full context | Use Pattern 2 (Extract) first | Pattern 2 + 3 |
| Infinite loop | Add convergence metric | Pattern 1 |
| Too many agents | Use weighted consensus | Pattern 10 |
| Lost context history | Keep full history in context | All patterns |
| One agent failure | Add recovery fallback | Pattern 9 |
| Memory explosion | Use streaming windows | Pattern 11 |
| Slow optimization | Add adaptive selection | Pattern 13 |

---

## Real-World Examples

### Example 1: Code Review (5 minutes)
```
Pattern 2 (Extract codebase)
  + Pattern 3 (Broadcast to reviewers)
  + Pattern 10 (Consensus on quality)
Result: Multi-perspective code review, 4K tokens
```

### Example 2: Research Paper (30 minutes)
```
Pattern 8 (Research synthesis)
  + Pattern 12 (Validate claims)
  + Pattern 10 (Expert consensus)
  + Pattern 1 (Perpetual refinement)
Result: High-confidence research, 12K tokens
```

### Example 3: API Design (20 minutes)
```
Pattern 5 (Sequential design phases)
  + Pattern 4 (Self-critique each phase)
  + Pattern 1 (Perpetual improvement)
  + Pattern 12 (Consistency validation)
Result: Production-ready API, 8K tokens
```

---

## Decision Matrix: When to Use Each Pattern

```
Task Type          | Primary Pattern | Secondary | Tertiary
-------------------|-----------------|-----------|----------
Code generation    | 1 (Perpetual)   | 4 (Self)  | 5 (Seq)
Code review        | 3 (Broadcast)   | 2 (Extr)  | 10 (Cons)
Research           | 8 (Research)    | 12 (Val)  | 10 (Cons)
API design         | 5 (Seq)         | 4 (Self)  | 1 (Per)
Quality control    | 10 (Cons)       | 12 (Val)  | 13 (Adapt)
Long documents     | 7 (Window)      | 11 (Stream)| 2 (Extr)
Failure handling    | 9 (Recovery)    | 3 (BC)    | 13 (Adapt)
Streaming data      | 11 (Stream)     | 13 (Adapt)| 2 (Extr)
```

---

## Recommended Complexity Levels

**Level 1 - Beginner** (1-2 patterns):
- Pattern 1 + 4 (Generate, then self-critique)
- Pattern 3 + 2 (Extract, then broadcast)

**Level 2 - Intermediate** (3-4 patterns):
- Pattern 8 + 12 + 10 (Research, validate, consensus)
- Pattern 5 + 4 + 1 (Pipeline, self-critique, refine)

**Level 3 - Advanced** (5+ patterns):
- Full pipeline composition with error recovery
- Adaptive workflows that learn
- Streaming aggregation with staged processing

---

## File Organization

```
comonad-workflows/
├── README.md                 ← Start here
├── QUICK-REFERENCE.md        ← This file
├── 1-perpetual-refinement.md
├── 2-context-extraction.md
├── 3-multi-agent-broadcast.md
├── 4-self-critique-loop.md
├── 5-13-patterns.md         ← Patterns 5-13
└── COMPOSITION-GUIDE.md     ← How to combine patterns
```

---

## Next Steps

1. **Pick a pattern** matching your use case (see Quick Selection Guide)
2. **Read the full documentation** for that pattern
3. **Study the 3 examples** provided
4. **Try composing** with another pattern
5. **Deploy to real Claude Code workflow**
6. **Measure token savings** and quality improvements

---

**Status**: Complete quick reference for all 13 comonadic patterns
**Use**: As cheat sheet during workflow design
**Update**: As new patterns discovered

Created: 2025-10-23
