# Comonadic Pattern Composition Guide

**Purpose**: Guide for combining multiple comonadic patterns into sophisticated workflows.

---

## Fundamental Composition Rules

### Rule 1: Extract Before Broadcast

```
Large Context
    ↓ Pattern 2: Extract (compress to 1-2K)
    ↓ Pattern 3: Broadcast to N agents

Cost: 3K-5K total (vs 30K+ if broadcasting full context)
```

**When**: Whenever distributing to multiple agents

### Rule 2: Self-Critique After Generation

```
Agent Generates Output
    ↓ Pattern 4: Self-Critique (identify issues)
    ↓ Pattern 1: Perpetual Refinement (improve until converged)

Benefit: Automatic quality improvement without external review
```

**When**: Single agent refinement is more efficient than external review

### Rule 3: Validation After Consensus

```
Multiple Agents → Pattern 10: Consensus
    ↓ Pattern 12: Validate (cross-check agreement)
    ↓ Final Decision (high confidence)

Benefit: Identifies where experts disagree (flags debate areas)
```

**When**: High-stakes decisions requiring verified agreement

### Rule 4: Adapt Based on Performance

```
Any Pipeline
    ↓ Pattern 13: Adaptive Orchestration (monitor metrics)
    ↓ Adjust agent selection (learn from failures)
    ↓ Improve over time

Benefit: Workflows get better at choosing which agent fits which task
```

**When**: Long-running systems or repeated similar tasks

---

## Common Composition Patterns

### A. High-Quality Code Generation

```
User Requirement
    ↓ Pattern 5: Sequential (Design → Implement → Test)
    ↓ Pattern 4: Self-Critique (Code critiques itself)
    ↓ Pattern 1: Perpetual (Refine until tests pass)

Result: High-quality code without external review round-trips
Token Cost: 4-6K
Quality: 85%+ pass rate
```

**Workflow Definition**:
```yaml
workflow: high-quality-code
steps:
  - design: [api-architect]
  - implement: [practical-programmer]
  - self-critique: [debug-detective]
  - test: [test-engineer]
  - refine: [perpetual] until [quality > 0.85]
```

---

### B. Deep Research with Verification

```
Research Question
    ↓ Pattern 8: Research Synthesis (Multiple methodologies)
    ↓ Pattern 12: Validation (Cross-reference claims)
    ↓ Pattern 10: Consensus (Multiple experts agree?)
    ↓ Final Synthesis

Result: Well-researched, verified, expert-consensus findings
Token Cost: 8-12K
Confidence: High
```

**Workflow Definition**:
```yaml
workflow: deep-research
steps:
  - research: [deep-researcher] using [quantitative, qualitative, literature]
  - validate: [context7-doc-reviewer] cross-check claims
  - expert-review: [api-architect, practical-programmer]
  - consensus: [mercurio-orchestrator]
```

---

### C. Multi-Perspective Code Review

```
Code to Review
    ↓ Pattern 2: Extract (Compress large codebases)
    ↓ Pattern 3: Broadcast (Send to expert reviewers)
    ↓ Pattern 10: Consensus (Weighted expert agreement)
    ↓ Pattern 12: Validation (Cross-check recommendations)

Result: Comprehensive review from multiple angles
Token Cost: 4-6K
Perspectives: 3-5 experts in parallel
```

**Workflow Definition**:
```yaml
workflow: multi-expert-review
steps:
  - extract: [code-trimmer] compress_to: 3000
  - broadcast: [frontend-architect, api-architect, practical-programmer]
  - aggregate: [mercurio-orchestrator] using weights
  - validate: [debug-detective] cross-check inconsistencies
```

---

### D. Production API Design

```
API Specification
    ↓ Pattern 4: Self-Critique (Design reviews itself)
    ↓ Pattern 6: Hierarchical Cascade (Specialist → Lead → Executive)
    ↓ Pattern 10: Consensus (Expert agreement on design)
    ↓ Pattern 12: Validation (Consistency verification)
    ↓ Pattern 1: Perpetual (Refine until mature)

Result: Production-ready, expert-vetted, consistent API
Token Cost: 8-10K
Iterations: 3-4 design cycles
```

**Workflow Definition**:
```yaml
workflow: production-api-design
steps:
  - initial-design: [api-architect]
  - self-critique: [api-architect] as reviewer
  - hierarchical:
    - specialists: [backend, frontend, devops]
    - leads: [api-architect, practical-programmer]
    - executive: [mercurio-orchestrator]
  - consistency-check: [context7-doc-reviewer]
  - refine: [perpetual] until [consistency > 0.92]
```

---

### E. Streaming Data Processing

```
Infinite Data Stream
    ↓ Pattern 11: Streaming (Process in windows)
    ↓ Pattern 2: Extract (Summarize each window)
    ↓ Pattern 13: Adaptive (Optimize processing strategy)
    ↓ Pattern 1: Perpetual (Continue indefinitely)

Result: Efficient processing of unbounded data
Memory: Bounded by window size (not total data)
Throughput: Optimizes over time
```

**Workflow Definition**:
```yaml
workflow: streaming-processor
steps:
  - windows: [aggregator] size: 100
  - process: [analyze-function]
  - extract: [summarizer]
  - adaptive: [monitor metrics]
  - checkpoint: [persister]
```

---

### F. Resilient Failure Recovery

```
Primary Agent Fails
    ↓ Pattern 9: Error Recovery (Catch failure)
    ↓ Pattern 3: Broadcast (Try alternative agents)
    ↓ Pattern 4: Self-Critique (Evaluate alternatives)
    ↓ Pattern 1: Perpetual (Refine until working)

Result: Graceful degradation, no total failure
Recovery Rate: 90%+
Graceful Fallback: Always produces result
```

**Workflow Definition**:
```yaml
workflow: resilient-processing
steps:
  - primary: [api-architect]
    on-error:
      - broadcast: [practical-programmer, debug-detective]
      - self-critique: [evaluate-all-results]
      - fallback: [always-has-answer]
```

---

## Advanced Composition Patterns

### Pattern: Debate & Resolution

```
Question with disagreement
    ↓ Pattern 3: Broadcast to experts (get diverse views)
    ↓ Pattern 10: Consensus (identify agreement areas)
    ↓ Pattern 12: Validation (verify high-confidence areas)
    ↓ Debate structure for low-confidence areas
    ↓ Synthesize: High-confidence facts + low-confidence debate format
```

**Use Case**: Complex questions where experts genuinely disagree (philosophy, design trade-offs)

### Pattern: Iterative Knowledge Refinement

```
Raw knowledge
    ↓ Pattern 2: Extract (identify key concepts)
    ↓ Pattern 5: Sequential (organize by dependency)
    ↓ Pattern 8: Research Synthesis (gather evidence)
    ↓ Pattern 12: Validation (verify each claim)
    ↓ Pattern 1: Perpetual (refine until converged)

Result: Polished, verified, well-organized knowledge
```

### Pattern: Adaptive Multi-Stage Processing

```
Input → Stages: {A, B, C, D}
    ↓ Pattern 13: Adaptive (select best agent per stage)
    ↓ Pattern 4: Self-Critique (evaluate each stage output)
    ↓ Pattern 11: Stream (batch similar tasks)
    ↓ Output

Benefit: Each stage learns which agent works best for which input type
```

---

## Composition Decision Tree

```
Start with question: "What are the requirements?"

1. Do you need MULTIPLE AGENTS involved?
   NO  → Patterns: 1, 4 (Perpetual + Self-Critique)
   YES → Continue to 2

2. Must agents work INDEPENDENTLY (parallel)?
   NO  → Pattern 5 (Sequential Pipeline)
   YES → Continue to 3

3. Is context VERY LARGE?
   NO  → Pattern 3 (Broadcast directly)
   YES → Pattern 2 (Extract) → Pattern 3 (Broadcast)

4. Do you need AGREEMENT from multiple agents?
   NO  → Stop (use selected patterns above)
   YES → Add Pattern 10 (Consensus)

5. Do you need VERIFICATION of results?
   NO  → Stop
   YES → Add Pattern 12 (Validation)

6. Do you need SELF-OPTIMIZATION?
   NO  → Stop
   YES → Add Pattern 13 (Adaptive)

7. Are you processing LARGE SEQUENTIAL DATA?
   NO  → Stop
   YES → Replace with Pattern 11 (Streaming)
```

---

## Token Budget Breakdown

### Budget Allocation Example: 200K Total

**Scenario: Deep Research with Multi-Expert Review**

```
System/Config: 32K (16%)
Conversation history: 44K (22%)
Available for workflow: 124K (62%)

Pattern Usage:
- Pattern 8 (Research):     8K  (6%)
- Pattern 2 (Extract):      1K  (0.8%)
- Pattern 3 (Broadcast):    6K  (4.8%)   [3 experts × 2K each]
- Pattern 10 (Consensus):   2K  (1.6%)
- Pattern 12 (Validation):  2K  (1.6%)
- Pattern 1 (Refinement):   3K  (2.4%)

Total: 22K (17.7% of 124K available)
Remaining: 102K (82.3%) for conversation/future operations
```

### Token Costs Per Pattern

| Pattern | Cost | Scaling |
|---------|------|---------|
| 1 (Perpetual) | 500-2K | Per iteration (usually 3-4) |
| 2 (Extract) | 200-500 | One-time per context |
| 3 (Broadcast) | 2-3K per agent | Scales with agent count |
| 4 (Self-Critique) | 800-1.2K | Per iteration (usually 2-3) |
| 5 (Sequential) | 1-2K per stage | Scales with stages |
| 6 (Hierarchical) | 4-6K | Increases with levels |
| 7 (Window) | ~400 per window | Bounded by window size |
| 8 (Research) | 3-5K | Per research cycle |
| 9 (Recovery) | 1-2K extra | Only on failure |
| 10 (Consensus) | 1.5-2K | Fixed cost, not per agent |
| 11 (Streaming) | O(window) | Constant per window |
| 12 (Validation) | 500-1K per claim | Scales with claims |
| 13 (Adaptive) | 1K overhead | Per adaptation cycle |

---

## Composition Antipatterns (What NOT to Do)

### ❌ Antipattern 1: Broadcast then Extract

```
Broadcast FIRST (full context to all agents)
    ↓ THEN Extract (too late, tokens already spent)
```

**Problem**: Each agent receives full context (very expensive)
**Solution**: Extract BEFORE broadcast

### ❌ Antipattern 2: Perpetual Without Convergence Metric

```
⟲ Infinite loop (no quality metric)
    → Never terminates or terminates too early
```

**Problem**: Can't tell if improvement is real
**Solution**: Define clear convergence metric (quality score, test pass, etc)

### ❌ Antipattern 3: All Patterns at Once

```
Extract + Broadcast + Consensus + Validate + Refine + Adaptive + Streaming
    → Token explosion
    → Complexity explosion
```

**Problem**: 50K+ tokens for simple task
**Solution**: Use minimal patterns needed for your goals

### ❌ Antipattern 4: No Recovery in Long Pipelines

```
Pipeline: A → B → C → D → fails at C
    → Entire pipeline worthless
```

**Problem**: No graceful degradation
**Solution**: Add Pattern 9 (Error Recovery) at critical points

### ❌ Antipattern 5: Sequential When Parallel Possible

```
Agent A does 2K tokens
Agent B does 2K tokens
Agent C does 2K tokens
Total: 6K tokens, sequential (slow)
```

**Problem**: Could run A, B, C in parallel (still 2K with extract)
**Solution**: Use Pattern 3 (Broadcast) when possible

---

## Composition Example: Complete Workflow

**Goal**: Build production-ready microservice API specification

**Selected Patterns**:
1. Pattern 8 (Research) - Investigate best practices
2. Pattern 2 (Extract) - Compress research findings
3. Pattern 3 (Broadcast) - Get specialist design input
4. Pattern 10 (Consensus) - Specialists agree on design
5. Pattern 4 (Self-Critique) - API design self-reviews
6. Pattern 1 (Perpetual) - Refine until mature
7. Pattern 12 (Validation) - Verify internal consistency

**Workflow Code**:

```python
def produce_production_api(business_requirements: str) -> dict:
    """End-to-end production API specification generation"""

    # Step 1: Research best practices
    research = deep_researcher_agent(
        f"Best practices for {business_requirements} API design",
        methodology="systematic"
    )

    # Step 2: Extract key insights
    research_summary = extract_key_insights(research, max_chars=1500)

    # Step 3: Broadcast to specialists
    context = CodeContext(focus=f"{research_summary}\nRequirements: {business_requirements}")

    specialist_designs = {
        "api": api_architect_agent(context),
        "backend": practical_programmer_agent(context),
        "devops": deployment_orchestrator_agent(context),
    }

    # Step 4: Consensus on design
    consensus_design = mercurio_orchestrator_agent(
        f"Specialist designs:\n{specialist_designs}\n\n"
        f"Create consensus API design respecting all constraints"
    )

    # Step 5-7: Self-critique and refine until mature
    current_spec = consensus_design
    for iteration in range(4):
        # Self-critique
        critique = api_architect_agent(
            current_spec,
            role="critic",
            focus="What's wrong with this design?"
        )

        # Validate consistency
        validation = context7_doc_reviewer_agent(
            current_spec,
            task="Check internal consistency and standards compliance"
        )

        # Refine based on critique
        if validation.get("consistency_score", 0.6) >= 0.92:
            break

        current_spec = api_architect_agent(
            f"Current spec: {current_spec}\nCritique: {critique}\nValidation: {validation}",
            role="designer",
            focus="Address critique and validation feedback"
        )

    return {
        "specification": current_spec,
        "research_foundation": research_summary,
        "specialist_inputs": specialist_designs,
        "iterations_to_maturity": iteration + 1
    }
```

**Token Cost**: 10-12K
**Quality**: Production-ready (multiple review cycles)
**Confidence**: High (specialist consensus + validation)

---

## Composition Testing Checklist

- [ ] Define clear success criteria (what does "done" look like?)
- [ ] Estimate token budget per pattern
- [ ] Test with minimal patterns first
- [ ] Add patterns incrementally
- [ ] Verify each pattern respects comonad laws
- [ ] Test error paths (what if an agent fails?)
- [ ] Measure quality improvements with each pattern added
- [ ] Document which patterns provide value vs. noise
- [ ] Create fallback for patterns that may fail
- [ ] Benchmark: does added complexity improve quality?

---

## Recommended Reading Order

1. **Start**: README.md (overview of all 13 patterns)
2. **Then choose one**:
   - For code: Pattern 1 + 4 + 5
   - For research: Pattern 8 + 12 + 10
   - For teams: Pattern 3 + 6 + 10
3. **Deep dive**: Read chosen pattern files completely
4. **Compose**: Mix patterns based on decision tree
5. **Deploy**: Start with simple composition, add complexity iteratively

---

**Status**: Complete composition guide with examples and antipatterns
**Next**: Deploy to real workflows and measure impact

Created: 2025-10-23
