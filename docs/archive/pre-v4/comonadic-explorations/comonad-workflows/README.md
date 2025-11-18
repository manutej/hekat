# Comonadic Queries: Practical Workflows Using Real Agents

**Status**: Comprehensive collection of 13 reusable comonadic query patterns
**Date**: 2025-10-23
**Purpose**: Abstract comonadic workflows paired with concrete examples using real Claude Code agents and workflows

---

## Overview

This folder contains **13 comonadic query patterns** derived from the hekat DSL and implemented using **real agents and workflows** from the Claude Code system. Each pattern represents a fundamental comonadic operation applied to LLM orchestration.

### What Is a Comonadic Query?

A **comonadic query** is an abstract workflow pattern that expresses:
- **Extract** (`↓`): Compress/focus on essential information
- **Duplicate** (`⟲`): Share context with multiple agents
- **Extend** (`→`): Apply transformations with full context awareness
- **Composition** (`·`): Chain operations maintaining comonadic laws

**Why These Matter**:
- **Memory efficient**: Extract compresses before distribute
- **Context-aware**: Each agent sees full historical context
- **Composable**: Patterns chain without impedance mismatch
- **Formally sound**: Respect comonad mathematical laws

---

## Quick Reference: The 13 Patterns

| # | Pattern | Comonadic Form | Primary Use Case |
|---|---------|---|---|
| 1 | **Perpetual Refinement** | `⟲ ∞ → extract:converge` | Iterative improvement with lazy evaluation |
| 2 | **Context Extraction** | `↓ → compress:cache` | Compress context while maintaining history |
| 3 | **Multi-Agent Broadcast** | `⟲ → {agents} → aggregate` | Distribute to parallel agents, then merge |
| 4 | **Self-Critique Loop** | `⟲ self → improve` | Agent reflects on own output iteratively |
| 5 | **Sequential Pipeline** | `→ → → sequence` | Chain agents, each sees full prior context |
| 6 | **Hierarchical Cascade** | `→ {*,*} → hierarchy` | Multi-stage parallel processing |
| 7 | **Bidirectional Window** | `↓ ◄► → attention` | Sliding focus maintaining bilateral context |
| 8 | **Research Synthesis** | `⟲ extract → validate → critique` | Deep research with iterative refinement |
| 9 | **Error Recovery Loop** | `⟲ backtrack → alternative` | Intelligent failure handling with context |
| 10 | **Consensus Formation** | `⟲ {experts} ◄► → weighted` | Multi-perspective analysis with balancing |
| 11 | **Streaming Aggregation** | `→ stream → fold:accumulate` | Process infinite streams with state |
| 12 | **Knowledge Validation** | `⟲ fact-check → cross-ref` | Iterative verification with dependency tracking |
| 13 | **Adaptive Orchestration** | `⟲ monitor → optimize` | Self-adjusting workflows based on metrics |

---

## Pattern Organization

Each pattern is documented in a dedicated markdown file with this structure:

```
PATTERN-NAME/
├── abstract.md          # Mathematical definition and comonadic form
├── agents-used.md       # Which real agents from ~/.claude/agents/ are involved
├── example-1.md         # First concrete implementation
├── example-2.md         # Second concrete implementation
├── example-3.md         # Third concrete implementation
└── composition.md       # How this pattern composes with others
```

### File Listing

- **1-perpetual-refinement.md** - Infinite improvement loops with convergence
- **2-context-extraction.md** - Compress context while preserving history
- **3-multi-agent-broadcast.md** - Parallel distribution with aggregation
- **4-self-critique-loop.md** - Reflexive improvement cycles
- **5-sequential-pipeline.md** - Linear agent composition
- **6-hierarchical-cascade.md** - Multi-tier parallel processing
- **7-bidirectional-window.md** - Attention mechanisms with full context
- **8-research-synthesis.md** - Deep research with iterative refinement
- **9-error-recovery-loop.md** - Intelligent fallback handling
- **10-consensus-formation.md** - Multi-agent consensus with weighting
- **11-streaming-aggregation.md** - Infinite stream processing
- **12-knowledge-validation.md** - Cross-referential fact checking
- **13-adaptive-orchestration.md** - Self-optimizing workflows

---

## Core Concepts

### The Comonadic Operators

| Operator | Name | Type | Meaning | Implementation |
|----------|------|------|---------|---|
| `↓` | Extract | `w a → a` | Focus/compress | `LLMContext.extract(compress_to: int)` |
| `⟲` | Duplicate | `w a → w (w a)` | Copy context to agents | `LLMContext.smart_duplicate(agents)` |
| `→` | Extend | `(w a → b) → w a → w b` | Apply with context | `LLMContext.extend(f, token_estimate)` |
| `◄►` | Zipper | Bilateral focus | Sliding window | `LLMContext.window(left, right)` |
| `{}` | Hyperedge | Multi-agent | Distribute to multiple | `[agent.extend(...) for agent in agents]` |
| `*` | Loop | Repetition | Until condition | `while condition: ctx = ctx.extend(...)` |
| `^` | Convergence | Termination | Stop at criterion | `if quality >= threshold: break` |

### Real Agents Used

These patterns leverage real agents from `~/.claude/agents/`:

- **debug-detective** - Root cause analysis and investigation
- **deep-researcher** - Comprehensive research and synthesis
- **practical-programmer** - Pragmatic code implementation
- **test-engineer** - Test creation and validation
- **frontend-architect** - Frontend design and architecture
- **api-architect** - API design and optimization
- **code-trimmer** - Code refactoring and cleanup
- **context7-doc-reviewer** - Documentation analysis
- **mercurio-orchestrator** - Multi-expert orchestration
- **docs-generator** - Documentation generation
- **deployment-orchestrator** - Deployment planning and execution
- **git-genius** - Git operations and workflows
- **project-orchestrator** - Project management and tracking

### Real Workflows Used

These patterns integrate with workflows from `~/.claude/workflows/`:

- **bug-investigation-fix** - Sequential debugging and fixing
- **research-to-documentation** - Research → synthesis → docs
- **frontend-feature-complete** - End-to-end feature development
- **code-refactoring-pipeline** - Multi-stage refactoring
- **mcp-integration-complete** - Integration workflow
- **api-development** - API design and implementation
- **linear-project-development** - Project-based development

---

## How to Use These Patterns

### Option 1: Pick a Pattern

```
1. Read the abstract.md to understand the comonadic structure
2. Check agents-used.md to see which agents are involved
3. Browse the 3 examples to find one matching your use case
4. Adapt the example to your specific needs
```

### Option 2: Compose Multiple Patterns

```
Research Synthesis = Pattern #8 (Research Synthesis)
                     + Pattern #10 (Consensus Formation)
                     + Pattern #12 (Knowledge Validation)

workflow = research | consensus | validate
```

### Option 3: Build a Custom Pattern

```
Use the template structure:
- Define comonadic form: (operators and composition)
- List agents needed
- Create 3 concrete examples
- Document composition rules
```

---

## Pattern Selection Guide

**Choose Pattern #1 (Perpetual Refinement) if**:
- You need iterative improvement until convergence
- Quality metrics determine when to stop
- Each iteration should preserve full context

**Choose Pattern #3 (Multi-Agent Broadcast) if**:
- You want parallel expert opinions
- Results need to be merged/aggregated
- Agents work independently on same context

**Choose Pattern #8 (Research Synthesis) if**:
- You need comprehensive research + documentation
- Multiple validation rounds desired
- Deep understanding required before synthesis

**Choose Pattern #10 (Consensus Formation) if**:
- Diverse expert opinions needed
- Opinions should be weighted by reliability
- Final decision requires negotiation

**Choose Pattern #12 (Knowledge Validation) if**:
- Claims need cross-referential fact-checking
- Trust scores should be tracked
- Dependencies between facts matter

---

## Mathematical Foundation

### Comonad Laws Satisfied

All patterns respect the three comonad laws:

1. **Left Counit**: `extract ∘ duplicate = id`
   - Extraction from duplicated context returns original

2. **Right Counit**: `fmap extract ∘ duplicate = id`
   - Duplicating then extracting from each layer returns original

3. **Coassociativity**: `fmap duplicate ∘ duplicate = duplicate ∘ duplicate`
   - Nested duplication is structurally coherent

### coKleisli Composition

All agent chains follow coKleisli composition:
```
(f <=< g) ctx = f (extend g ctx)
```

This ensures:
- Each agent accesses full context
- Context flows through the pipeline
- Operations are associative

---

## Token Budgeting

Each pattern includes token estimates for typical scenarios:

- **Perpetual Refinement**: 500-2K tokens per iteration
- **Multi-Agent Broadcast**: 3K × N agents (parallel)
- **Research Synthesis**: 5-10K for research, 2-5K for synthesis
- **Consensus Formation**: 2K × N experts (parallel)

See individual pattern files for detailed breakdowns.

---

## Real-World Applications

### Development Workflow
```
Pattern #8 (Research) → Pattern #6 (Cascade) → Pattern #4 (Self-Critique)
Research requirements → Design stages → Code review cycles
```

### Quality Assurance
```
Pattern #5 (Sequential) → Pattern #10 (Consensus) → Pattern #12 (Validation)
Test → Multiple expert review → Cross-check results
```

### Knowledge Management
```
Pattern #3 (Broadcast) → Pattern #10 (Consensus) → Pattern #12 (Validation)
Gather diverse perspectives → Merge opinions → Verify accuracy
```

### Continuous Improvement
```
Pattern #1 (Perpetual) → Pattern #4 (Self-Critique) → Pattern #9 (Recovery)
Iterate → Self-reflect → Handle failures gracefully
```

---

## Integration with hekat DSL

These patterns can be expressed in the hekat comonadic DSL:

```dsl
# Pattern 1: Perpetual Refinement
refine::(⟲ ∞):converge

# Pattern 3: Multi-Agent Broadcast
duplicate::{agent_A, agent_B, agent_C}:broadcast

# Pattern 8: Research Synthesis
collect[*]:converge
  | validate[fact,bias]:filter
  | critique>>improve^0.9
  | ^ final

# Pattern 10: Consensus Formation
copy[extract<3000>]expert1,expert2,expert3
  | consensus<>weighted
  | ^ decision
```

---

## Extending the Patterns

### Add Your Own Pattern

1. **Define the abstract form**:
   ```
   pattern_name::(comonadic operators):strategy
   ```

2. **List required agents**:
   - Which agents from ~/.claude/agents/
   - Which workflows from ~/.claude/workflows/

3. **Create 3 examples**:
   - Example 1: Simple case
   - Example 2: Complex case
   - Example 3: Edge case handling

4. **Document composition**:
   - How does it work with other patterns?
   - What are the counit laws implications?

### Submit a Pattern

To contribute a new comonadic query pattern:
1. Follow the template structure
2. Include mathematical formulation
3. Provide agent specifications
4. Add 3 tested examples
5. Document composition rules

---

## Quick Start

### Scenario 1: I want to refine code until it's perfect

→ Use **Pattern #1: Perpetual Refinement**
→ See `1-perpetual-refinement/example-1.md`

### Scenario 2: I want parallel expert analysis

→ Use **Pattern #10: Consensus Formation**
→ See `10-consensus-formation/example-2.md`

### Scenario 3: I want deep research with validation

→ Use **Pattern #8: Research Synthesis**
→ Then add **Pattern #12: Knowledge Validation**
→ See composition examples

### Scenario 4: I need to fix a broken process gracefully

→ Use **Pattern #9: Error Recovery Loop**
→ See `9-error-recovery-loop/example-3.md`

---

## File Structure

```
comonad-workflows/
├── README.md (this file)
├── 1-perpetual-refinement.md
├── 2-context-extraction.md
├── 3-multi-agent-broadcast.md
├── 4-self-critique-loop.md
├── 5-sequential-pipeline.md
├── 6-hierarchical-cascade.md
├── 7-bidirectional-window.md
├── 8-research-synthesis.md
├── 9-error-recovery-loop.md
├── 10-consensus-formation.md
├── 11-streaming-aggregation.md
├── 12-knowledge-validation.md
├── 13-adaptive-orchestration.md
└── COMPOSITION-GUIDE.md (how to combine patterns)
```

---

## Next Steps

1. **Explore a pattern** that matches your use case
2. **Read the abstract** to understand the comonadic structure
3. **Check agents used** to see what's involved
4. **Study an example** and adapt to your needs
5. **Compose with other patterns** for complex workflows

---

**Created**: 2025-10-23
**Status**: Complete with 13 abstract patterns and 39 concrete examples
**Next**: Deploy patterns to real Claude Code workflows

Start with **Pattern #1** (Perpetual Refinement) or jump to the pattern that solves your problem!
