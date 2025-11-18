# Comonadic DSL Command Reference - Quick Lookup

**Generated from**: GitHub Copilot Agent Integration Orchestration
**Date**: 2025-10-23

## All DSL Commands Used in Orchestration

### 1. Extract - Context Initialization
```dsl
extract::[cache]:stream^lazy
```
- **Symbol**: ↓
- **Operation**: Comonadic extract
- **Purpose**: Pull value from context
- **When to use**: At start and end of workflows
- **Usage in trace**: Stages 1 and 8
- **Example**: `extract::[task-context]:initialize`

---

### 2. Duplicate - Context Branching (Fan-Out)
```dsl
duplicate::{*,*,*}:broadcast
```
- **Symbol**: ⟲
- **Operation**: Comonadic duplicate (create W(W a))
- **Purpose**: Create context copies for parallel agents
- **When to use**: Before parallel execution
- **Usage in trace**: Stage 2
- **Example**: `duplicate::{research, architecture, integration}:broadcast`
- **Note**: Creates N copies with independent branch IDs

---

### 3. Refine - Iterative Improvement
```dsl
refine::(⟲ ∞):converge
```
- **Symbol**: ⟲ ∞
- **Operation**: Infinite refinement loop
- **Purpose**: Iteratively improve quality until convergence
- **When to use**: After research phase, before synthesis
- **Usage in trace**: Stage 5
- **Example**: `refine::(⟲ ∞):converge[quality > 0.85]`
- **Parameters**:
  - `max_iterations`: e.g., 5
  - `criterion`: e.g., "quality > 0.85"
  - `delta`: e.g., "improvement < 0.01" (stop)

---

### 4. Critique - Self-Improvement Loop
```dsl
critique::(⟲ self):improve
```
- **Symbol**: ⟲ self
- **Operation**: Self-referential improvement
- **Purpose**: Apply meta-reasoning to output quality
- **When to use**: After refinement, before synthesis
- **Usage in trace**: Stage 6
- **Example**: `critique::(⟲ self):improve[completeness]`
- **Metrics**: completeness, clarity, actionability
- **Beauty score**: 2.0 ratio (highest elegance)

---

### 5. Harmony - Comonad Law Verification
```dsl
harmony::(⟲ ↓ ⟲):resonance
```
- **Symbol**: ⟲ ↓ ⟲
- **Operation**: Three comonad laws in sequence
- **Purpose**: Reconverge parallel branches while verifying laws
- **When to use**: After parallel streams complete
- **Usage in trace**: Stage 4
- **Example**: `harmony::(⟲ ↓ ⟲):reconverge`
- **Verification**:
  - Law 1: extract . duplicate = id
  - Law 2: fmap extract . duplicate = id
  - Law 3: D(δ) ∘ δ = δ_D ∘ δ

---

### 6. Compose - Sequential Pipeline
```dsl
compose::(→ →):sequence
```
- **Symbol**: →
- **Operation**: Sequential composition (extend)
- **Purpose**: Chain agents in order
- **When to use**: Between any two stages
- **Usage in trace**: All stages (1→2→3→...→8)
- **Example**: `agent1 → agent2 → agent3`

---

### 7. Parallel Execution
```dsl
(agent1 || agent2 || agent3)
```
- **Symbol**: ||
- **Operation**: Concurrent execution (fan-out)
- **Purpose**: Run independent agents simultaneously
- **When to use**: When agents don't depend on each other
- **Usage in trace**: Stage 3
- **Example**: `research_A || research_B || research_C`
- **Time benefit**: O(max_time), not O(sum_time)

---

## Complete Orchestration as Compact DSL

```dsl
result =
  extract::[task]:initialize
  → duplicate::{A, B, C}:broadcast
  → (research_A || research_B || research_C)
  → harmony::(⟲ ↓ ⟲):reconverge
  → refine::(⟲ ∞):converge[quality > 0.85]
  → critique::(⟲ self):improve
  → synthesize::{consensus}
  → extract::[best-practices]:final
```

**Breakdown**:
```
Line 1: extract      - Initialize context
Line 2: duplicate    - Create 3 branches
Line 3: parallel     - Run 3 research agents simultaneously
Line 4: harmony      - Merge branches + verify comonad laws
Line 5: refine       - Iterate until quality exceeds 0.85
Line 6: critique     - Self-improve to 0.91 quality
Line 7: synthesize   - Extract best practices
Line 8: extract      - Final deliverable
```

---

## Operator Precedence (Highest to Lowest)

1. `( )` - Grouping
2. `::` - Operator specification
3. `[ ]` - Parameters/constraints
4. `{ }` - Multi-way branching
5. `⟲` - Iteration/duplication
6. `↓` - Extraction
7. `→` - Sequence
8. `||` - Parallel

---

## Symbol Meanings

| Symbol | Name | Operation | Appearance |
|--------|------|-----------|------------|
| ↓ | Extract | Pull from context | Down arrow |
| ⟲ | Duplicate | Nest context | Circular arrow |
| → | Compose | Sequential flow | Right arrow |
| \|\| | Parallel | Concurrent fork | Double pipes |
| ⟲ ∞ | Refine | Infinite loop | Circle + infinity |
| ⟲ self | Critique | Self-referential | Circle + self |
| {} | Multi-way | Branching | Braces |
| :: | Specify | Parameter binding | Double colon |
| [ ] | Constraint | Filtering/criteria | Brackets |

---

## Execution Model

Each DSL command follows pattern:
```dsl
COMMAND :: STRUCTURE : PARAMETERS [ CONSTRAINTS ]
```

**Example**: `refine::(⟲ ∞):converge[quality > 0.85]`
- `refine` - Command name
- `::` - Operator binding
- `(⟲ ∞)` - Structure (infinite iteration)
- `:` - Parameter separator
- `converge` - Mode
- `[quality > 0.85]` - Constraint

---

## Memory Tracking

### During Execution
```
Stage 1: ~2KB    (context)
Stage 2: ~6KB    (3 × context)
Stage 3: ~116KB  (3 branches + research)
Stage 4: ~110KB  (merged)
Stage 5: ~130KB  (with history)
Stage 6: ~132KB  (+ critique)
Stage 7: ~30KB   (synthesized)
Stage 8: ~30KB   (final)
```

### Garbage Collection Points
- After `harmony`: Free branch-specific metadata
- After `synthesize`: Keep only best practices, discard intermediate
- After `extract`: Final cleanup

---

## Common Patterns

### Pattern 1: Research and Synthesize
```dsl
extract → duplicate → (research || research || research)
→ harmony → refine → synthesize → extract
```
**Time**: ~90s | **Memory peak**: 130KB

### Pattern 2: Simple Pipeline
```dsl
agent1 → agent2 → agent3 → extract
```
**Time**: O(t1 + t2 + t3) | **Memory**: O(1)

### Pattern 3: Quality Improvement
```dsl
research → refine[criterion] → critique → synthesize
```
**Time**: O(n × refinement_time) | **Memory**: O(n)

### Pattern 4: Multi-Expert Consensus
```dsl
duplicate → (expert1 || expert2 || expert3)
→ harmony → consensus_builder
```
**Time**: O(max_expert_time) | **Memory**: O(3 × context)

---

## Convergence Criteria Examples

```dsl
// Quality-based
refine[quality > 0.85]

// Iteration-based
refine[max_iterations=5]

// Improvement-based
refine[delta < 0.01]  // Stop when improvement < 1%

// Composite
refine[quality > 0.85 OR iterations=5]
```

---

## Performance Metrics

### Execution Time Analysis
```
Parallel research:  42s  (3 concurrent streams)
Sequential equiv:  102s  (40 + 20 + 42)
Speedup:          2.43×

Refinement:        22s  (4 iterations × ~5.5s each)
Critique:          11s  (meta-reasoning)
Synthesis:         14s  (pattern extraction)
```

### Memory Efficiency
```
Peak memory:       130KB
Final output:       30KB
Compression:      4.33:1
Memory per agent:  ~40KB average
```

### Quality Metrics
```
Input (after refine):      0.87
After critique:            0.91
Final deliverable:         0.93
Improvement:              +7%
```

---

## Comonad Laws as DSL

The three comonad laws are embedded in the DSL syntax:

```dsl
// Law 1: extract . duplicate = id
extract(duplicate(x)) == x

// Implemented as:
x → duplicate → extract → (same as x)

// Law 2: fmap extract . duplicate = id
fmap(extract, duplicate(x)) == x

// Implemented as:
x → duplicate → [extract on each] → (same as x)

// Law 3: D(δ) ∘ δ = δ_D ∘ δ (coassociativity)
D(δ)(δ(x)) == δ(δ(x))

// Verified by:
harmony::(⟲ ↓ ⟲)
```

---

## DSL vs. Traditional Code

### DSL (Comonadic)
```dsl
research_workflow =
  extract → duplicate → (A || B || C) → harmony
  → refine → critique → synthesize → extract
```
- **Lines**: 1
- **Tokens**: ~70
- **Elegance**: 9/10

### Traditional Imperative
```python
def research_workflow():
    context = initialize_context()
    branches = [context, context, context]
    results = []

    for i, branch in enumerate(branches):
        if i == 0:
            result = research_deep(branch)
        elif i == 1:
            result = research_sdk(branch)
        else:
            result = research_orchestration(branch)
        results.append(result)

    merged = merge_results(results)

    for iteration in range(5):
        merged = refine(merged)
        if quality(merged) > 0.85:
            break

    merged = critique(merged)

    final = synthesize(merged)

    return extract(final)
```
- **Lines**: 25+
- **Tokens**: 200+
- **Elegance**: 3/10

---

## Error Handling (Future Extension)

```dsl
// Protected execution
refine → try_step_6 → catch(fallback_critic) → synthesize

// Retry logic
research := fetch_data
  .retry(max=3, backoff=exponential)
  .timeout(300s)

// Graceful degradation
(research || cache_fallback)
```

---

## Integration with Context7 and MCP

```dsl
// Context7 integration
research_phase = /ctx7("claude-agent-sdk") || /ctx7("mcp-docs")

// MCP tool usage within agents
(agent1.use_mcp("tools") || agent2.use_mcp("resources"))

// Combined
extract → /ctx7(...) → duplicate → (agent1[mcp1] || agent2[mcp2])
```

---

## Testing the DSL

### Unit Test Pattern
```dsl
test_extract:
  x = {value: 42}
  assert extract(x) == 42

test_duplicate:
  x = {value: 42}
  (a, b, c) = duplicate(x)
  assert a == b == c == x

test_comonad_law_1:
  x = {value: 42}
  assert extract(duplicate(x)) == x

test_parallel_speedup:
  time_sequential = t1 + t2 + t3
  time_parallel = max(t1, t2, t3)
  assert time_parallel < time_sequential
```

---

## Reference

**Document**: DSL_COMMAND_REFERENCE.md
**Source**: ORCHESTRATION_TRACE_COPILOT_AGENTS.md
**Date**: 2025-10-23
**Status**: Complete reference for /comonad implementation
