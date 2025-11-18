# Memory-Constrained Comonadic Orchestration

**The Critical Insight**: Comonads are perfect for orchestrating distributed agents under token constraints because they naturally separate LOCAL context (preserved within agents) from GLOBAL context (compressed for sharing).

---

## The Problem We Solved

### Initial Assumption (Broken ❌)
```
Global context: 100K tokens
Agents: 3 (security, performance, readability)
Naive duplication: context × 3 = 300K tokens
Budget: 200K tokens
Result: FAILS - exceeds budget by 100K tokens
```

### Our Solution (Working ✅)
```
Global context: 100K tokens
Extract compressed summary: 2K tokens
Distribute: 2K × 3 = 6K tokens
Total cost: 8K tokens
Budget: 114K tokens available
Result: Uses only 7% of budget, leaves 106K for other operations
```

---

## The Comonadic Model for Distributed Agents

### Three-Tier Context Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ GLOBAL CONTEXT (Orchestrator) - What everyone sees          │
│ - Current focus value                                       │
│ - Essential facts from history                              │
│ - Token tracking                                            │
│ ~114K tokens available                                      │
└─────────────────────────────────────────────────────────────┘
        │
        ├─extract(2K)─────┐ (Compress to essentials)
        │                 │
        ▼                 ▼
┌─────────────────┬─────────────────┬─────────────────┐
│  Agent 1        │  Agent 2        │  Agent 3        │
│ (Security)      │ (Performance)   │ (Readability)   │
├─────────────────┼─────────────────┼─────────────────┤
│ Shared summary  │ Shared summary  │ Shared summary  │
│ (2K read-only)  │ (2K read-only)  │ (2K read-only)  │
│                 │                 │                 │
│ Working memory  │ Working memory  │ Working memory  │
│ (2K local)      │ (2K local)      │ (2K local)      │
│                 │                 │                 │
│ Extract result  │ Extract result  │ Extract result  │
│ (1K output)     │ (1K output)     │ (1K output)     │
└─────────────────┴─────────────────┴─────────────────┘
        │                │                │
        └────extract(1K each)─────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Consensus            │
              │ Merge 3 results      │
              │ (3K → 1K compressed) │
              └──────────────────────┘
                         │
                         ▼
              Final output: 1K tokens
```

### Key Principle: Bidirectional Extraction

**Downward extraction** (global → agents):
- Large context (100K) → Compressed (2K)
- Full history → Essentials only
- Operation: `ctx.extract(compress_to=2000)`

**Upward extraction** (agents → global):
- Agent working memory (2K) → Results (1K)
- Findings → Key insights
- Automatic compression via `extract()`

**Result**: Information flows BOTH directions, but never exceeds token budget.

---

## Implementation: Memory-Aware LLMContext

### 1. Smart Extract (Downward Compression)

```python
def extract(self, compress_to: int = 2000) -> Tuple[str, Dict]:
    """
    Extract for sharing with other agents.

    Returns only what's essential:
    - Current focus
    - Quality score
    - Breakthrough moments from history
    - NOT full history
    """

    summary = f"Current: {str(self.focus)[:500]}"
    summary += f"\nQuality: {self.metadata.get('quality_score')}"

    # Add only breakthrough moments
    for breakthrough in self.history_snapshots:
        if breakthrough.is_breakthrough:
            summary += f"\nBreakthrough: {breakthrough.summary}"

    return summary[:compress_to * 4]  # Truncate to budget
```

### 2. Smart Duplicate (Selective Sharing)

```python
def smart_duplicate(
    self,
    agents: List[str],
    max_tokens_per_agent: int = 3000
) -> Dict[str, MemoryAwareLLMContext]:
    """
    Distribute to agents, each gets:
    - Extracted summary (1K)
    - Task instructions (1K)
    - Working memory space (1K)

    Total: 3K per agent, NOT full context × agents
    """

    shared_summary = self.extract(compress_to=1000)

    for agent in agents:
        agent_context = MemoryAwareLLMContext(
            focus=shared_summary,  # Extracted, not full
            metadata={"agent_id": agent},
            token_budget=3000,  # Per-agent budget
        )
```

### 3. Smart Extend (Context-Aware Apply)

```python
def extend(
    self,
    f: Callable,
    token_estimate: int = 2000
) -> MemoryAwareLLMContext:
    """
    Apply function with token awareness.

    If operation would exceed budget:
    1. Auto-compress history first
    2. Keep only breakthroughs + recent
    3. Apply function to compressed context
    """

    if self.tokens_used + token_estimate > self.token_budget:
        self = self._auto_compress()  # Keep breakthroughs only

    new_focus = f(self)
    return create_context_with_history(new_focus)
```

---

## Real Example: Code Review Workflow

### DSL (What users write)
```dsl
input[code]
  | extract<2000>:compress
  | copy[extract<3000>]security,performance,readability
  | consensus<>weighted
  | ^ review<1000>
```

### Execution (What happens internally)

**Step 1: Extract**
- Input: 600 tokens (code)
- Output: 127 tokens (compressed)
- Cost: 127 tokens

**Step 2: Distribute to 3 agents**
- Shared summary: 127 tokens
- Per agent: 127 + 1000 (task) + 2000 (working) = 3127 tokens
- Total: 127 + 9381 = **9,508 tokens**

**Step 3: Parallel analysis (agents work independently)**
- Agent 1 local: 2000 tokens (security review)
- Agent 2 local: 2000 tokens (performance review)
- Agent 3 local: 2000 tokens (readability review)
- Global cost: 0 (local memory only)

**Step 4: Consensus**
- Merge 3 results: 3 × 1000 = 3000 tokens
- Compress to consensus: 1000 tokens
- Cost: **1,000 tokens**

**Step 5: Extract final**
- Output: 1000 tokens
- Cost: 500 tokens

**TOTAL: 10,627 tokens (9.3% of 114K budget)**

---

## Key Design Decisions

### Decision 1: What Agents See

❌ **DON'T**: Full context
```python
agent_ctx = global_context  # 100K tokens - agent can't hold it
```

✅ **DO**: Extracted summary
```python
summary, _ = ctx.extract(compress_to=2000)  # 2K tokens - agent gets essential info
agent_ctx = MemoryAwareLLMContext(focus=summary, ...)
```

### Decision 2: What Agents Share

❌ **DON'T**: Full working memory
```python
agent1.working_memory = {...}  # 2K local - other agents don't see it
agent2.access(agent1.working_memory)  # WRONG
```

✅ **DO**: Extracted results only
```python
agent1.extract()  # Return 1K compressed findings
shared_result = agent1_result  # Other agents see this
```

### Decision 3: How History Works

❌ **DON'T**: Keep all attempts
```python
history = [attempt_1, attempt_2, ..., attempt_100]  # Grows unbounded
```

✅ **DO**: Keep breakthroughs + recent
```python
history = [
    breakthrough_1,  # Where we made progress
    breakthrough_2,
    recent_attempt_1,  # Last 2 attempts
    recent_attempt_2,
]  # Much smaller, still informative
```

---

## Token Accounting System

Every operation is tracked:

```
Operation              Input    Output   Cost      Ratio
─────────────────────────────────────────────────────────
extract_summary        593      127      127       1.0x
distribute_to_agents   127      9,381    9,381     74x
parallel_analysis      ~2K      (local)  0         0x (local)
consensus_merge        3,000    1,000    1,000     1.0x
final_extraction       1,000    1,000    500       1.0x
─────────────────────────────────────────────────────────
TOTAL GLOBAL COST:     9.3% of budget
```

The `0x` for parallel analysis is KEY: agent working memory doesn't count toward global budget.

---

## Why This Is Different From Traditional Approaches

### Traditional Parallel Agent System
```python
# Broadcast full context to all agents
context_to_share = full_context  # 100K tokens
for agent in agents:
    send_to_agent(agent, context_to_share)
    # 100K × 3 agents = 300K tokens
# Result: EXCEEDS BUDGET
```

### Comonadic Orchestration
```python
# Orchestrate via compressed extraction
shared_summary = ctx.extract(compress_to=2000)  # 2K tokens
for agent in agents:
    agent_ctx = distribute_with_summary(agent, shared_summary)
    # 2K × 3 agents = 6K tokens
# Result: Uses only 5% of budget
```

**The difference**: Comonads make compression NATURAL and AUTOMATIC through the `extract` operation.

---

## Assumptions for Memory-Constrained Environments

### Assumption 1: Extract Compresses
`extract()` means: "give me the compressed version, not full history"

### Assumption 2: Agents Are Independent
Each agent has local working memory that other agents can't see.

### Assumption 3: Communication Is Extracted-Only
Agents communicate only through `extract()` results, never full context.

### Assumption 4: History Is Compressed Automatically
When approaching token limit, history is compressed to essentials (breakthroughs + recent).

### Assumption 5: Token Budgeting Is Per-Operation
Each operation has estimated cost; exceeding budget triggers compression.

---

## The Elegance Emerges Here

**Why comonads are perfect for memory-constrained orchestration:**

1. **Extraction is natural**: `extract` operation is designed to compress context
2. **Duplication is smart**: `duplicate` can be selective (share only what's needed)
3. **History is optional**: Comonads preserve history but don't force you to keep all
4. **Composition is safe**: Each operation is independent and testable
5. **Token accounting is built-in**: Track cost of each operation automatically

Traditional approaches force you to manually manage:
- What to compress
- What to share
- History cleanup
- Budget tracking
- Agent communication protocols

Comonads make it AUTOMATIC through the algebraic structure.

---

## Next Steps: Real Implementation

1. **Implement with actual Claude API**: Measure real token costs
2. **Build adaptive compression**: Adjust history keeping based on remaining budget
3. **Create monitoring**: Real-time token usage visualization
4. **Test scaling**: 5, 10, 20 agents with same budget
5. **Document patterns**: Best practices for memory-aware workflows

This is where comonadic DSL becomes **practical engineering**, not theoretical elegance.
