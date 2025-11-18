# Memory-Aware Comonadic DSL Design

**Problem**: Current design assumes full context history can be preserved. With 200K token limit and parallel agents, this fails.

**Solution**: Context compression with smart extraction and staged sharing.

---

## The Real Constraint Analysis

### Token Budget Breakdown (200K limit)

```
Total available: 200,000 tokens
├── System prompt + tools: 32,000 (16%)
├── User configuration: 10,000 (5%)
├── Current conversation: 44,000 (22%)
├── Available for workflow: ~114,000 (57%) ← This is all we have
```

### The Parallel Agent Problem

Traditional (broken) approach:
```
Query: 5K tokens
duplicate[] to 3 agents
  -> Agent 1 gets 5K + 10K history = 15K
  -> Agent 2 gets 5K + 10K history = 15K
  -> Agent 3 gets 5K + 10K history = 15K
Total: 45K tokens for ONE operation
```

After 2-3 iterations, we've blown 135K+ tokens just on duplication. **This fails.**

---

## Memory-Aware Comonad Design

### Key Principle: Extraction as Compression

Instead of `extract()` returning full value, **memory-aware extraction returns COMPRESSED summary**:

```python
def extract(self) -> tuple[CompressedValue, int]:
    """
    Returns:
      - Compressed value (summary, key facts, essential data)
      - Token cost (how many tokens were used)
    """
```

### Three-Tier Context Model

#### Tier 1: Working Memory (Agent-Local)
- Current operation context only
- ~2-5K tokens
- **Never leaves the agent**
- Example: "I'm reviewing code for performance issues. Current code: [snippet]. My findings so far: [analysis]"

#### Tier 2: Extracted Summary (Shared)
- Compressed results from last operation
- ~1-2K tokens
- **Shared between agents**
- Example: "Code review completed. Performance bottleneck: DB query in loop. Fix: Batch queries. Confidence: 0.85"

#### Tier 3: Global History (Managed)
- Only essential facts and convergence data
- ~0.5-1K tokens
- **Centrally managed, not duplicated**
- Example: "Review 1: 0.82 quality. Review 2: 0.91 quality. Consensus decision: Refactor DB queries."

---

## Memory-Aware Comonadic Operations

### 1. Smart Extract (Compression)

```python
class MemoryAwareLLMContext:
    def extract(self, max_tokens: int = 2000) -> str:
        """
        Extract compressed summary that fits in token budget.

        Process:
        1. Get current focus value
        2. Compress history to essentials only
        3. Remove redundant information
        4. Ensure output <= max_tokens

        Returns: Compressed summary ready to share with other agents
        """
        # Keep current value (most important)
        summary = self.focus

        # Add only essential facts from history, not full history
        key_findings = self._compress_history(max_tokens)
        summary = f"{summary}\n\nKey findings: {key_findings}"

        return summary

    def _compress_history(self, budget: int) -> str:
        """Compress history to key facts only (1-2 sentences)."""
        if not self.history:
            return ""

        # Keep only:
        # - Quality scores (shows improvement)
        # - Turning points (where we changed approach)
        # - Final insights (what we learned)

        compressed = []
        for i, item in enumerate(self.history[-5:]):  # Last 5 only
            if i == 0:
                compressed.append(f"Started: {item[:50]}...")
            elif self.quality_improvements[i] > 0.15:  # Significant improvement
                compressed.append(f"Breakthrough: {item[:50]}... (quality +0.15)")
            if i == len(self.history) - 1:
                compressed.append(f"Current: {item[:50]}...")

        return " | ".join(compressed)
```

### 2. Smart Duplicate (Selective Sharing)

Instead of duplicating full context to each agent:

```python
def smart_duplicate(
    self,
    agents: List[str],
    max_tokens_per_agent: int = 3000
) -> Dict[str, MemoryAwareLLMContext]:
    """
    Distribute extracted context to agents, respecting token budget.

    Key insight: Each agent gets only what it needs to work, not full history.

    Returns:
      agent_name -> context (extracted summary + working space)
    """

    shared_summary = self.extract(max_tokens=1000)  # Shared summary

    result = {}
    for agent in agents:
        # Each agent gets:
        # 1. Extracted summary (1K tokens)
        # 2. Task-specific context (1K tokens)
        # 3. Working memory (1K tokens)
        # Total: 3K per agent, not full history

        agent_context = MemoryAwareLLMContext(
            focus=shared_summary,
            task_instructions=self.metadata.get(f"task_{agent}", ""),
            working_memory={},  # Agent fills this locally
            metadata={
                "agent_id": agent,
                "parent_context_id": self.id,
                "shared_summary_tokens": 1000,
            }
        )
        result[agent] = agent_context

    return result
```

### 3. Smart Extend (Context-Aware Apply)

```python
def extend(
    self,
    f: Callable[[str], str],
    token_budget: int = 5000
) -> 'MemoryAwareLLMContext':
    """
    Apply function with token awareness.

    Process:
    1. Check token cost before applying f
    2. If f would exceed budget, compress history first
    3. Apply f to compressed context
    4. Track token cost
    """

    # Estimate token cost
    estimated_cost = self._estimate_cost(f)

    if estimated_cost + self.total_tokens_used > token_budget:
        # Compress before applying
        self = self._compress()

    # Apply function to current focus
    new_focus = f(self.extract())

    return MemoryAwareLLMContext(
        focus=new_focus,
        history=self.history[-2:],  # Keep only last 2 steps
        metadata=self.metadata,
        total_tokens_used=self.total_tokens_used + estimated_cost
    )
```

---

## Memory-Aware DSL Workflow

### Example: Multi-Expert Code Review (Memory-Conscious)

```dsl
# Original (breaks with token limits):
# copy[]security,performance,readability | consensus<>weighted | ^ review

# Memory-aware version:
# Extract → copy[extract]security,performance,readability | compress & consensus<>weighted | ^ review
```

Breaking it down:

```
Step 1: extract (compress context)
  Input: Full code + context (10K tokens)
  Output: Compressed summary (2K tokens)
  Token cost: 2K

Step 2: copy[extract] to 3 agents
  Each agent gets: Compressed summary (2K) + task instructions (1K) = 3K per agent
  Total: 9K (instead of 30K if we duplicated full context)
  Token cost: 9K

Step 3: Agent 1 (Security Review) - runs independently
  Input: 3K summary
  Working memory: 2K (local analysis, not shared)
  Output: 1K compressed result
  Token cost: 2K (local only, doesn't impact global budget)

Step 4: Agent 2 (Performance Review) - parallel
  Same as Agent 1
  Token cost: 2K (local)

Step 5: Agent 3 (Readability Review) - parallel
  Same as Agent 1
  Token cost: 2K (local)

Step 6: compress & consensus
  Collect 3 agent results: 1K + 1K + 1K = 3K
  Compress to consensus: 1K
  Token cost: 1K

Step 7: extract (final output)
  Return: 1K compressed decision
  Token cost: 1K

TOTAL: 2K + 9K + 1K + 1K = 13K tokens
(vs 30K+ for naive duplication)
```

---

## Key Design Decisions

### Decision 1: What Gets Extracted?

**Not**: Full history and all attempts
**Yes**: Only essential information

```python
# What to extract:
- Current answer/decision
- Quality score
- Key insights (1-2 lines)
- Turning points where approach changed
- Confidence/uncertainty markers

# What NOT to extract:
- Full history of all attempts
- Intermediate reasoning steps
- All intermediate quality scores
- Failed approaches (unless lessons learned)
```

### Decision 2: Context Sharing Between Agents

**Model**: Each agent is independent with local working memory

```python
# Agent memory layout:
Agent_Context = {
    "shared_summary": 1K,      # From parent (read-only)
    "task_instructions": 1K,   # Task-specific (read-only)
    "working_memory": 2K,      # Agent's own analysis (local)
    "accumulated_cost": 2K,    # What agent has used
}

# Agent produces: 1K compressed result
# Agent never sees other agents' working memory
# Agents communicate only through extracted results
```

### Decision 3: History Management

**Approach**: Rolling window instead of full history

```python
# Instead of keeping all history:
history = [attempt_1, attempt_2, attempt_3, attempt_4, attempt_5, ...]

# Keep only sliding window:
history = [attempt_N-1, attempt_N]  # Last 2 steps
+ essential_facts = [breakthrough_moment, initial_insight]

# Compressed representation:
"Started: attempt_1 (quality 0.65) → Breakthrough at attempt_3 (quality 0.88) → Current: attempt_5 (quality 0.94)"
```

---

## Token Accounting System

Track tokens at each operation:

```python
class WorkflowTokenBudget:
    def __init__(self, total_budget: int = 114000):
        self.total = total_budget
        self.used = 0
        self.operations = []

    def log_operation(
        self,
        name: str,
        tokens_in: int,
        tokens_out: int,
        compression_ratio: float = 1.0
    ):
        """Log an operation's token usage."""
        cost = tokens_in * compression_ratio  # Compressed cost
        self.used += cost

        self.operations.append({
            "name": name,
            "input_tokens": tokens_in,
            "output_tokens": tokens_out,
            "cost": cost,
            "compression_ratio": compression_ratio,
            "total_used_so_far": self.used,
            "percent_budget": (self.used / self.total) * 100
        })

        if self.used > self.total * 0.9:
            print(f"WARNING: Using {self.percent_budget:.1f}% of token budget!")

    def remaining(self) -> int:
        return self.total - self.used
```

---

## Practical DSL Assumptions for Memory-Constrained Environment

### Assumption 1: Extraction Compresses
```dsl
extract (means: compress and summarize, not full history)
```

### Assumption 2: Duplication Uses Smart Extract
```dsl
copy[extract]agent1,agent2,agent3
(each agent gets 3K summary, not full context)
```

### Assumption 3: Agent Working Memory is Local
```dsl
agent1 analysis happens in agent1's memory
agent1 memory never seen by other agents
only agent1's extract[] result leaves the agent
```

### Assumption 4: Consensus is on Extracted Results
```dsl
consensus<>weighted (operates on 3×1K extracted results = 3K total)
(not 3×full_context which would be unaffordable)
```

### Assumption 5: History Compression is Automatic
```dsl
When context window pressure detected:
- Old attempts automatically pruned
- Only turning points and insights kept
- Rolling window of last N-2 attempts maintained
```

---

## DSL Syntax for Memory Management

Add explicit memory operations:

```dsl
# Force compression when approaching limit
compress:90% | continue_workflow

# Set per-agent token budget
copy[extract<3000>]agent1,agent2,agent3

# Log token usage
log-tokens | continue_workflow

# Specify which history to keep
keep-insights[breaking_points]:converge

# Abort if exceeding budget
abort-if-exceeds:100000
```

---

## Complete Memory-Aware Workflow Example

### Code Review with Token Tracking

```dsl
# Explicit memory-aware version
input[code]
  | extract<2000>:compress              # Step 1: Compress to 2K (if needed)
  | copy[extract<3000>]sec,perf,read    # Step 2: Distribute 3K each
  | log-tokens<15000>                   # Step 3: Record 15K used so far
  | consensus<>weighted                 # Step 4: Merge results (3K → 1K)
  | compress:50%                        # Step 5: Further compress if needed
  | ^ review<1000>                      # Step 6: Extract final 1K result
```

What this means:
1. Start with code (5K)
2. Compress if needed (→ 2K)
3. Distribute to 3 agents smartly (9K total)
4. Track at 15K checkpoint
5. Merge agent results (3K → 1K)
6. Further compress
7. Return 1K final result

**Total cost: ~15-17K tokens** (vs 30-40K naive approach)

---

## Why Comonads Still Win Here

Traditional parallel approach fails because:
- Needs to pass full context to each agent
- Context grows with each operation
- No built-in compression mechanism
- History management is manual

Comonadic approach wins because:
- `extract` naturally suggests compression
- `duplicate` can be "smart" (selective sharing)
- `extend` can include token awareness
- Full comonad structure supports partial information flow
- History compression is comonad operation (not external hack)

**Comonads were designed for this:** tracking local and global state with context preservation. Memory-constrained orchestration is a natural use case.

---

## Implementation Next Steps

1. Add `MemoryAwareLLMContext` class with token tracking
2. Implement smart duplicate/extract with compression
3. Create token accounting system
4. Build workflow with explicit memory management
5. Test with real Claude API calls (measure token costs)
6. Compare: naive vs memory-aware approach

This turns "comonadic DSL" from theoretical elegance into practical engineering solution for real-world token constraints.
