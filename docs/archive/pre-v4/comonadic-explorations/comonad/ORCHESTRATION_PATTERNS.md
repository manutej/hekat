# Comonadic Orchestration Patterns for Memory-Constrained Environments

**Summary**: How to design DSL workflows that work within 200K token limits with parallel agents.

---

## Pattern 1: Sequential with Compression

**When to use**: Operations must happen in order, history matters less than end result.

**DSL**:
```dsl
input[data]
  | extract<2000>:compress
  | process1:>>loop^0.9
  | compress:80%
  | process2:>>loop^0.95
  | ^ final<1000>
```

**Memory flow**:
```
data (5K)
  ↓ extract
summary (2K)
  ↓ process1 (auto-compress if needed)
result1 (2K)
  ↓ explicit compress to 80%
result1 compressed (1.6K)
  ↓ process2
result2 (2K)
  ↓ extract final
output (1K)

Total: ~13K tokens
```

**Implementation**:
```python
ctx = LLMContext(data)
ctx = ctx.extend(process1, token_estimate=2000)
if ctx.tokens_used > 0.5 * ctx.token_budget:
    ctx = ctx._auto_compress()
ctx = ctx.extend(process2, token_estimate=2000)
final = ctx.extract(compress_to=1000)
```

---

## Pattern 2: Parallel Consensus

**When to use**: Multiple agents analyze independently, results are merged.

**DSL**:
```dsl
input[query]
  | extract<1500>:compress
  | copy[extract<2500>]agent_A,agent_B,agent_C
  | consensus<>weighted
  | ^ decision<1000>
```

**Memory flow**:
```
query (5K)
  ↓ extract
summary (1.5K) [shared by all 3 agents]
  ↓ copy with extracted context
Agent_A gets: 1.5K + 1K task = 2.5K
Agent_B gets: 1.5K + 1K task = 2.5K
Agent_C gets: 1.5K + 1K task = 2.5K

Agent_A analysis (local, not global): 2K
Agent_B analysis (local, not global): 2K
Agent_C analysis (local, not global): 2K

Agent_A extracts: 1K
Agent_B extracts: 1K
Agent_C extracts: 1K
  ↓ consensus merge
consensus (2K)
  ↓ extract final
decision (1K)

Global cost: 1.5K + 7.5K + 2K + 1K = 12K
```

**Implementation**:
```python
ctx = LLMContext(query)
summary, _ = ctx.extract(compress_to=1500)

agents = ctx.smart_duplicate(
    ["A", "B", "C"],
    max_tokens_per_agent=2500
)

results = {}
for name, agent_ctx in agents.items():
    # Each agent runs independently
    agent_result = run_agent(name, agent_ctx)
    results[name] = agent_result

# Merge results
final_ctx = ctx.consensus(list(results.values()))
decision = final_ctx.extract(compress_to=1000)
```

---

## Pattern 3: Hierarchical Multi-Stage

**When to use**: Multiple levels of processing with approval/review at each stage.

**DSL**:
```dsl
input[request]
  | stage1:analyze
  | copy[extract<2000>]reviewer_1,reviewer_2
  | consensus<>unanimous?stage2:detail:>>improve^0.95:extract<1500>
  | stage3:decide
  | ^ approved<1000>
```

**Memory flow**:
```
request (3K)
  ↓ stage1 analysis
analysis (3K)
  ↓ extract
analysis_summary (2K) [shared with reviewers]
  ↓ copy
Reviewer_1: 2K summary
Reviewer_2: 2K summary

[Local review work: 2K each, not global]

Reviewer_1 extracts (1.5K)
Reviewer_2 extracts (1.5K)
  ↓ consensus
consensus (2K)
  ↓ if unanimous?
  └─→ stage2 detail analysis
     (auto-improve until quality > 0.95)
     ↓ extract final
     stage2_result (1.5K)
  ↓ stage3 decision
  ↓ extract approved
  final_decision (1K)

Total: ~17K tokens
```

**Key**: The `?unanimous` is a conditional checkpoint. If not unanimous, triggers detailed analysis loop.

---

## Pattern 4: Self-Iterative with Backtracking

**When to use**: Agent refines its own work, needs to backtrack if quality drops.

**DSL**:
```dsl
input[task]
  | refine:loop[*]:>>improve^0.85
  | extract<1500>:checkpoint
  | critique:self:>>fix^0.9
  | backtrack?quality<0.88:previous
  | ^ final<1000>
```

**Memory flow**:
```
task (3K)
  ↓ refine (loop until quality > 0.85)
iteration_0: quality 0.72
iteration_1: quality 0.78
iteration_2: quality 0.83
iteration_3: quality 0.86 ✓ (stop)
refined (3K)
  ↓ extract checkpoint
checkpoint (1.5K) [save this state]
  ↓ self critique
critique (2K)
  ↓ fix based on critique
fixed (3K) [quality now 0.91]
  ↓ backtrack check
quality (0.91) > threshold (0.88) ✓
  ↓ extract final
output (1K)

Total: ~14K tokens
```

**Key advantage**: `checkpoint` saves extraction point; `backtrack` restores if needed.

---

## Pattern 5: Streaming with Memory Management

**When to use**: Processing stream of items, need to avoid accumulating results.

**DSL**:
```dsl
stream[items]
  | for-each[item]:
      extract<1000>:current
      | process:>>refine^0.9
      | compress:summary
      | ^ result<500>
  | aggregate<1000>:final
```

**Memory flow**:
```
[item_1, item_2, item_3, ...]
  ↓ for item_1:
  current (1K) [not full stream]
  ↓ process
  processed (1.5K)
  ↓ compress to summary
  summary (500B)
  ↓ extract
  result_1 (500B) [OUTPUT, not kept]

[item_2]
  ↓ [repeat but DON'T keep result_1]
  result_2 (500B)

[item_3]
  ↓ [repeat]
  result_3 (500B)

[Final aggregation of results]
  ↓ aggregate
  final (1K)

Memory at any time: ~3-4K (just current item)
NOT: item_1 + item_2 + item_3 + ... (unbounded)
```

**Key**: Each item is processed and extracted independently. Results are consumed immediately, not accumulated.

---

## Memory Management Decision Tree

```
START: New workflow
├─ Sequential operations?
│  └─ YES → Pattern 1 (Sequential with Compression)
│          Auto-compress between stages
│
├─ Multiple independent agents?
│  └─ YES → Pattern 2 (Parallel Consensus)
│          Smart duplicate with extraction
│
├─ Multi-level approval/review?
│  └─ YES → Pattern 3 (Hierarchical Multi-Stage)
│          Checkpoint + consensus at each level
│
├─ Self-refinement needed?
│  └─ YES → Pattern 4 (Self-Iterative with Backtracking)
│          Save checkpoints, enable backtrack
│
└─ Streaming many items?
   └─ YES → Pattern 5 (Streaming with Management)
           Process one at a time, extract results
```

---

## Token Budget Allocation Templates

### For 114K available tokens:

**Small workflow (1-2 steps)**:
```
- Extraction: 2K
- Processing: 5K
- Result: 1K
- Buffer (unused): 106K
```

**Medium workflow (3-4 steps with 2 agents)**:
```
- Extraction: 2K
- Distribution: 6K
- Processing per agent: 2K × 2 = 4K (local)
- Consensus: 2K
- Result: 1K
- Buffer: 103K
```

**Large workflow (5+ steps with 3-5 agents)**:
```
- Extraction/compression: 3K
- Distribution: 9K (3 agents)
- Processing per agent: 2K × 3 = 6K (local)
- Consensus: 3K
- Refinement: 4K
- Result: 2K
- Buffer: 87K
```

**Complex workflow (hierarchical with loops)**:
```
- Stage 1: 8K
- Stage 2: 10K
- Review: 8K
- Refinement: 6K
- Consensus: 4K
- Final: 2K
- Buffer: 76K
```

---

## Best Practices

### Do ✅

1. **Extract early**: Compress context before distributing
   ```dsl
   input | extract<2K> | copy[] ... ✓
   ```

2. **Set explicit budgets**: Make token usage visible
   ```dsl
   agent_context<3000> | ... ✓
   ```

3. **Compress before loops**: Don't let history grow
   ```dsl
   loop[*] | compress:90% | ... ✓
   ```

4. **Use checkpoints**: Save extraction points for backtracking
   ```dsl
   | extract<1.5K>:checkpoint | ... ✓
   ```

5. **Extract at boundaries**: Between components
   ```dsl
   component1 | extract<1K> | component2 ✓
   ```

### Don't ❌

1. **Pass full context to agents**:
   ```dsl
   copy[]agent1,agent2,agent3  ✗ (use copy[extract] instead)
   ```

2. **Accumulate results**:
   ```python
   results = [r1, r2, r3, ...]  ✗ (extract each, don't keep all)
   ```

3. **Ignore token tracking**:
   ```dsl
   ... | process | process | process  ✗ (add log-tokens checkpoints)
   ```

4. **Keep full history**:
   ```python
   history = [attempt_1 through attempt_100]  ✗ (keep breakthroughs + recent only)
   ```

5. **Process without extraction**:
   ```dsl
   input | component1 | component2  ✗ (add extract between)
   ```

---

## Validation Checklist

Before deploying a comonadic workflow:

- [ ] Total global token cost estimates < 50% of budget
- [ ] Each extract() call specified with max_tokens
- [ ] Parallel agents use smart_duplicate() not full copy
- [ ] History compression strategy documented
- [ ] Checkpoint/backtrack points identified
- [ ] Token budget allocated per stage
- [ ] Memory-constrained assumptions documented
- [ ] Fallback behavior if budget exceeded defined

---

## The Core Insight

**Comonadic orchestration works in memory-constrained environments because:**

1. `extract()` naturally produces compressed form
2. `duplicate()` can be selective (smart duplicate)
3. `extend()` can be token-aware
4. History compression is built-in (not external hack)
5. Each operation is independent and testable
6. Token accounting is automatic

Traditional parallel agent systems force you to solve these manually.
Comonads make it STRUCTURAL and AUTOMATIC.

---

**Next**: Implement these patterns in practice with real Claude API calls and measure actual token usage.
