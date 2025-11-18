# HEKAT Query Builder: Complete Specification

**Status**: Unified Design (Hekat-Agent + Mercurio-Orchestrator Convergence)
**Date**: 2025-10-27
**Authors**: Hekat-Agent, Mercurio-Orchestrator, Claude Code
**Version**: 1.0 (Production Ready)

---

## Overview

The HEKAT Query Builder is a **complexity-aware, token-disciplined orchestration system** that enables users to request multi-agent workflows at varying levels of sophistication (L1-L7). It combines:

- **Comonadic memory-aware context distribution** (from hekat/comonad project)
- **Dynamic query selection** based on consciousness patterns (historical learning)
- **Progressive disclosure hotkey system** (simple to advanced)
- **Real-time token tracking** with task-relay checkpoint discipline
- **Smart fallback mechanisms** when resources are constrained

---

## Part 1: Complexity Levels (L1-L7)

### Design Philosophy

Each level maps to a **comonadic orchestration pattern** (from ORCHESTRATION_PATTERNS.md):
- **Sequential**: One agent after another (L1, L2, L3)
- **Parallel Consensus**: Multiple agents in parallel, merge results (L4)
- **Hierarchical**: Multi-stage with approval gates (L5)
- **Iterative**: Feedback loops with refinement (L6)
- **Streaming + Hierarchical + Parallel Combined**: Full ensemble (L7)

Each level has:
- **Agent count & coordination model**
- **Token budget** (proportional to comonad examples)
- **Context distribution** (extract/duplicate/consensus costs)
- **Hotkey paradigm** (single key, combo, dynamic)
- **Trigger conditions** (what user inputs trigger this level)
- **Real DSL example**

---

### L1: Ultra-Fast Single-Hop

**Pattern**: Sequential (minimal)
**Agents**: 1 (no coordination)
**Complexity**: Ultra-simple, scoped question

**Token Budget**: 600-1200 tokens
- Base query context: 100 tokens
- Agent setup/dispatch: 150 tokens
- Agent execution: 300-700 tokens
- Output extraction: 50-100 tokens

**Context Distribution**:
- Query → Agent-Local scope only
- No extraction needed (context small enough)
- Agent works independently

**Hotkey Paradigm**: Single mnemonic key
```
[R] Research     [D] Debug      [T] Test       [B] Build
[F] Frontend     [I] Implement  [A] Analyze    [C] Code-review
```

**Trigger Conditions**:
```yaml
Keywords:
  - "explain ...", "understand ...", "what is ..."
  - "debug ...", "fix ..." (quick diagnostic)
  - "list ...", "show ...", "tell me ..."

Agent count: 1
Execution: Immediate, no synthesis
Token available: >600
```

**Real DSL Example**:
```
deep-researcher : "explain how PostgreSQL indexes work"
```

**Output**: Direct answer from single agent, no processing

---

### L2: Fast Simple-Chain

**Pattern**: Sequential with compression (2 agents)
**Agents**: 2 in sequence (A → B)
**Complexity**: Two-step workflow

**Token Budget**: 1500-3000 tokens
- Query context: 200 tokens
- Agent A dispatch + execution: 600-800 tokens
- Extract A output: 200-300 tokens
- Agent B dispatch + execution: 500-900 tokens
- Merge/format output: 100-200 tokens

**Context Distribution**:
```
Global context (200)
  ↓ extract() to A-Local (500)
Agent A executes independently
  ↓ output → extract() (300)
Agent B receives: 300 token summary + task
Agent B executes
  ↓ extract final output (200)
```

**Hotkey Paradigm**: Single key (or chained [A>B])
```
[D] Document    [F] Fix        [B] Build       [R] Report
```

**Trigger Conditions**:
```yaml
Keywords:
  - "design then implement", "fix and test", "research and document"
  - Two-step patterns ("X then Y")

Pattern: A → B sequential
Agents: 2 in sequence
Token available: >1500
```

**Real DSL Example**:
```
deep-researcher -> docs-generator : "research FastAPI patterns and create documentation"
```

**Output**: Agent B's synthesized result of A's work

---

### L3: Balanced Sequential

**Pattern**: Sequential with staged compression (3 agents)
**Agents**: 3 in sequence (A → B → C)
**Complexity**: Standard feature development workflow

**Token Budget**: 2500-4500 tokens
- Query context: 300 tokens
- Agent A: 600 tokens (design)
- Extract: 200 tokens
- Agent B: 700 tokens (implementation)
- Extract: 300 tokens
- Agent C: 400 tokens (testing)
- Final extraction: 200 tokens

**Context Distribution**:
```
Global (300)
  ↓ extract → A-Local (500)
A design output
  ↓ extract (300) → B-Local (1000)
B implementation output
  ↓ extract (300) → C-Local (1200)
C testing/review output
  ↓ extract final (200)
Total: ~3.5K tokens (matches comonad Pattern 1 scaling)
```

**Hotkey Paradigm**: Single key (or chain [D>I>T])
```
[A] Architect   [E] Endpoint   [I] Implement   [T] Test
```

**Trigger Conditions**:
```yaml
Keywords:
  - "build feature", "create endpoint", "develop function"
  - Three-phase workflows (design → implement → test)
  - Standard TDD approaches

Pattern: A → B → C sequential
Agents: 3 in sequence
Token available: >2500
```

**Real DSL Example**:
```
api-architect -> practical-programmer -> test-engineer : "build authentication endpoint with full test coverage"
```

**Output**: Agent C's final review/test results, with implementation preserved

---

### L4: Parallel Consensus (Light)

**Pattern**: Parallel Consensus (comonad Pattern 2)
**Agents**: 2-3 agents in parallel
**Complexity**: Multi-perspective analysis

**Token Budget**: 3000-6000 tokens
- Query context: 400 tokens
- smart_duplicate(): 600 tokens (extraction + distribution)
- Agent A execution (local): 1200 tokens
- Agent B execution (local): 1200 tokens
- Agent C execution (local): 1200 tokens (optional)
- Consensus merge: 1200 tokens
- Final extraction: 200 tokens

**Context Distribution**:
```
Global context (400)
  ↓ extract() (600)
Compressed summary (400)
  ↓ smart_duplicate() to 3 agents
Each agent gets:
  - Shared summary: 400 tokens (read-only)
  - Task instructions: 200 tokens
  - Working space: 600 tokens
  Total per agent: 1200 tokens (independent, not counted globally)

Parallel execution (no global cost)
  ↓ consensus merge
Agent outputs unified (1200 tokens)
  ↓ extract final
Decision (200 tokens)

Global total: 400 + 600 + 1200 + 200 = 2.4K
(vs 3.6K if agents got full context—60% savings!)
```

**Hotkey Paradigm**: Combo key or complexity selector
```
[P] Parallel (quick)   OR   [Ctrl+P] (L4 selector)
[P:R||D||A] (explicit agents: Research || Design || Analyze)
```

**Trigger Conditions**:
```yaml
Keywords:
  - "compare", "evaluate", "analyze options", "get multiple perspectives"
  - "design" (multiple design approaches)
  - "audit", "review", "security check" (multiple viewpoints)

Pattern: Parallel (||) with consensus
Agents: 2-3 independent
Execution: Parallel, then merge
Token available: >3000
```

**Real DSL Example**:
```
(deep-researcher || api-architect || claude-sdk-expert) : "evaluate which SDK (anthropic, openai, together) for multi-agent system"
```

**Output**: Weighted consensus decision with confidence scores

---

### L5: Hierarchical Multi-Stage

**Pattern**: Hierarchical (comonad Pattern 3)
**Agents**: 4-5 in hierarchical stages
**Complexity**: System architecture with approval gates

**Token Budget**: 5500-9000 tokens
- Query context: 500 tokens
- Stage 1: Parallel research (2-3 agents, local): 2000 tokens combined
- Stage 1 extraction + merge: 800 tokens
- Supervisor agent (orchestrator): 1500 tokens
- Stage 2: Parallel implementation (2-3 agents, local): 2000 tokens combined
- Final orchestration: 500 tokens

**Context Distribution**:
```
Global context (500)
  ↓ extract for Stage 1 (600)
Stage 1 agents (parallel):
  - Research Agent A: 1000 tokens (local)
  - Research Agent B: 1000 tokens (local)
  ↓ extract outputs (800)
Merged findings (800)
  ↓ Supervisor (Project Orchestrator)
Supervision/decision: 1500 tokens
  ↓ extract for Stage 2 (600)
Stage 2 agents (parallel):
  - Implementation Agent A: 1000 tokens (local)
  - Implementation Agent B: 1000 tokens (local)
  ↓ final extraction (500)
Final decision: 500 tokens

Global total: 500 + 600 + 800 + 1500 + 600 + 500 = 4.5K
(hierarchical structure = efficient multi-stage processing)
```

**Hotkey Paradigm**: Combo key or complexity selector
```
[H] Hierarchical   OR   [Ctrl+H] (L5 selector)
[H:R+D→O] (explicit: Research+Design → Orchestrate)
```

**Trigger Conditions**:
```yaml
Keywords:
  - "architect", "design system", "plan infrastructure"
  - "full microservice", "complete platform"
  - "with approval", "gated decision"

Pattern: Multi-stage with approval
Agents: 4-5 hierarchical
Execution: Stage 1 (parallel) → Supervisor → Stage 2 (parallel)
Token available: >5500
```

**Real DSL Example**:
```
[deep-researcher + api-architect] -> project-orchestrator -> (practical-programmer || deployment-orchestrator) : "design microservices architecture for SaaS platform"
```

**Output**: Final orchestrated plan with validation from supervisor

---

### L6: Deep Iterative Refinement

**Pattern**: Iterative with feedback (comonad Pattern 4)
**Agents**: 4-6 with refinement cycles
**Complexity**: Problem requiring iteration, testing, refinement

**Token Budget**: 8000-12000 tokens
- Query context: 600 tokens
- Iteration 1: A → B → C (3000 tokens)
  - Agent A: 800 tokens
  - Extract: 200 tokens
  - Agent B: 900 tokens
  - Extract: 200 tokens
  - Agent C (test): 700 tokens
  - Extract: 200 tokens
- Iteration 2: feedback + refinement (2500 tokens)
  - Accumulated context: 500 tokens
  - Agent A refined: 700 tokens
  - Agent B refined: 800 tokens
  - Agent C retest: 500 tokens
- Iteration 3: final validation (1500 tokens)
  - Agent A final: 600 tokens
  - Agent B final: 600 tokens
  - Agent C final: 300 tokens
- Final extraction: 300 tokens

**Context Distribution**:
```
Global context (600)
  ↓ Iteration 1
    A → extract (200) → B → extract (200) → C → extract (200)
    Iter1 cost: 3000 tokens
  ↓ Iteration 2 (feedback loop)
    Accumulated summary: 500 tokens
    A refined → B refined → C retest
    Iter2 cost: 2500 tokens
  ↓ Iteration 3 (convergence check)
    Confidence check + final refine
    Iter3 cost: 1500 tokens
  ↓ Final extraction (300)

Total: 600 + 3000 + 2500 + 1500 + 300 = 7.9K tokens
(iterative overhead is cost of convergence)
```

**Hotkey Paradigm**: Combo key or complexity selector
```
[I] Iterative   OR   [Ctrl+I] (L6 selector)
[I:D→P→T→repeat] (explicit: Debug → Program → Test → Repeat)
```

**Trigger Conditions**:
```yaml
Keywords:
  - "fix with tests", "iterate until", "refine until working"
  - "bug fix" with complexity hints
  - "test-driven", "TDD", "red-green-refactor"

Pattern: Iterative with feedback
Agents: 4-6 in refinement loops
Execution: Multi-iteration cycles
Token available: >8000
```

**Real DSL Example**:
```
iterate(debug-detective -> practical-programmer -> test-engineer, until=tests_pass) : "fix production memory leak with full test coverage"
```

**Output**: Converged solution with passing tests, iteration count, refinement history

---

### L7: Full Ensemble Synthesis

**Pattern**: Streaming + Hierarchical + Parallel Combined
**Agents**: 7+ with complex orchestration
**Complexity**: Multi-dimensional, full-stack from scratch

**Token Budget**: 12000-22000 tokens
- Query context: 800 tokens
- Stage 1: Parallel research (4 agents, local): 3500 tokens
  - deep-researcher: 900 tokens
  - api-architect: 900 tokens
  - frontend-architect: 900 tokens
  - claude-sdk-expert: 800 tokens
- Extract + merge: 1200 tokens
- Stage 2: Synthesis (mercurio-orchestrator): 4000 tokens
- Extract synthesis: 800 tokens
- Stage 3: Parallel implementation (3 agents, local): 2500 tokens
  - practical-programmer: 900 tokens
  - deployment-orchestrator: 800 tokens
  - docs-generator: 800 tokens
- Extract + merge: 800 tokens
- Stage 4: Final orchestration (project-orchestrator): 2000 tokens
- Streaming updates: 500 tokens

**Context Distribution**:
```
Global context (800)
  ↓ extract for Stage 1 (1000)
Stage 1 agents (parallel):
  - deep-researcher: 900 (local)
  - api-architect: 900 (local)
  - frontend-architect: 900 (local)
  - claude-sdk-expert: 800 (local)
  ↓ extract + consensus (1200)
Research synthesis: 1200
  ↓ mercurio-orchestrator
Synthesis: 4000 tokens (integrate all perspectives)
  ↓ extract for Stage 3 (800)
Stage 3 agents (parallel):
  - practical-programmer: 900 (local)
  - deployment-orchestrator: 800 (local)
  - docs-generator: 800 (local)
  ↓ extract + merge (800)
Implementation: 800
  ↓ project-orchestrator
Final orchestration: 2000 tokens
  ↓ streaming updates (500)

Global total: 800 + 1000 + 1200 + 4000 + 800 + 800 + 2000 + 500 = 11.1K
(parallel execution + smart extraction = scale to 7+ agents)
```

**Hotkey Paradigm**: Ensemble selector
```
[E] Ensemble   OR   [Ctrl+E] (L7 selector)
[E:P→S→I→O] (explicit: Parallel research → Synthesize → Implement → Orchestrate)
```

**Trigger Conditions**:
```yaml
Keywords:
  - "design and implement", "build platform", "complete solution"
  - "production", "enterprise", "scalable"
  - "from scratch", "greenfield"

Pattern: Parallel research + synthesis + parallel implementation
Agents: 7+ complex orchestration
Execution: Stage 1 parallel → Stage 2 sequential → Stage 3 parallel → Stage 4 final
Token available: >12000
```

**Real DSL Example**:
```
sample^3(deep-researcher, api-architect, frontend-architect) ;
mercurio-orchestrator[consensus] ;
(practical-programmer || deployment-orchestrator || docs-generator) ;
project-orchestrator[final-synthesis] :
"design and implement production-ready multi-tenant SaaS platform with full documentation"
```

**Output**: Complete architecture, implementation plan, deployment guide, documentation

---

## Part 2: Hotkey System (TIER Architecture)

### Design Principle

**Progressive Disclosure**: Users start with simple single-key shortcuts (TIER 1), graduate to complexity selectors (TIER 2), and can use advanced combos (TIER 3) as needed.

### TIER 1: Quick Access (Always Available)

Single-letter mnemonics for immediate use. No modifiers needed.

```
┌─────────────────────────────────────────────────────────┐
│ TIER 1: Quick Access Single Keys                         │
├─────────────────────────────────────────────────────────┤
│ [R]esearch    [D]esign/Debug  [T]est      [B]uild        │
│ [F]rontend    [I]mplement     [O]rchestrate [S]ynthesize │
│ [C]ode-review [P]arallel      [V]erify    [A]nalyze      │
│                                                          │
│ Usage: Just press key in /hekat prompt                  │
│ Example: /hekat [R] "explain JWT"                       │
│ → Triggers: deep-researcher                             │
└─────────────────────────────────────────────────────────┘
```

**Semantic Mapping**:
- `[R]` Research → deep-researcher (learning, analysis)
- `[D]` Design/Debug → api-architect, debug-detective (architecture, troubleshooting)
- `[T]` Test → test-engineer (quality assurance)
- `[B]` Build → practical-programmer (implementation)
- `[F]` Frontend → frontend-architect (UI/UX)
- `[I]` Implement → practical-programmer (primary implementation)
- `[O]` Orchestrate → project-orchestrator (coordination, tracking)
- `[S]` Synthesize → mercurio-orchestrator (integration, synthesis)
- `[C]` Code-review → debug-detective, test-engineer (quality review)
- `[P]` Parallel → invoke L4 (multi-perspective)
- `[V]` Verify → test-engineer (validation)
- `[A]` Analyze → deep-researcher, debug-detective (investigation)

**Discovery**:
```
CLI Help:
/hekat --help

Shows:
TIER 1 Quick Keys: [R]esearch [D]esign [T]est [B]uild [F]rontend [I]mplement...
TIER 2 Complexity: Hold Ctrl for levels ([Ctrl+P] L4, [Ctrl+H] L5, etc.)
TIER 3 Chains:    Combine keys ([R>D>I], [P:R||D||A])

Hint: Start with single keys, graduate to Ctrl-modifiers
```

---

### TIER 2: Complexity Selectors (Hold Ctrl)

When user wants specific complexity level, use Ctrl modifier:

```
┌──────────────────────────────────────────────────────┐
│ TIER 2: Complexity Selectors (Hold Ctrl)              │
├──────────────────────────────────────────────────────┤
│ [Ctrl+P] → L4 Parallel Consensus (multi-perspective)  │
│ [Ctrl+H] → L5 Hierarchical (architecture with gates)  │
│ [Ctrl+I] → L6 Iterative (refinement loops)            │
│ [Ctrl+E] → L7 Ensemble (full orchestration)           │
│                                                       │
│ Usage: Hold Ctrl while pressing key                  │
│ Example: /hekat [Ctrl+H] "design microservices"      │
│ → Forces: L5 Hierarchical (4-5 agents)               │
└──────────────────────────────────────────────────────┘
```

**Force Level Override**:
```
User types: /hekat [Ctrl+H] "quick question"
System detects: Level too high for query
Response: "L5 requires ~7K tokens for 'quick question'.
           Use [Ctrl+D] L3 (~4K) instead? Or continue? [Y/N]"
```

---

### TIER 3: Agent Chains (Combo Patterns)

Advanced users can specify agent chains directly:

```
┌──────────────────────────────────────────────────────────┐
│ TIER 3: Agent Chain Patterns                             │
├──────────────────────────────────────────────────────────┤
│ Sequential:  [R>D>I]   (Research → Design → Implement)   │
│              [D>I>T]   (Design → Implement → Test)       │
│              [B>R>T]   (Build → Refactor → Test)         │
│                                                           │
│ Parallel:    [P:R||D||A]   (Research || Design || Analyze) │
│              [C:P||P||V]    (Code-review in parallel)     │
│                                                           │
│ Complex:     [H:R+D→O]   (Hierarchical: Research+Design → │
│                           Orchestrate)                    │
│              [I:D→P→T]   (Iterative: Debug → Program →   │
│                           Test)                          │
│                                                           │
│ Usage: Type pattern in /hekat prompt                    │
│ Example: /hekat [R>D>I] "build authentication"          │
│ → Uses: L3 Sequential (deep-researcher → api-architect  │
│          → practical-programmer)                         │
└──────────────────────────────────────────────────────────┘
```

**Chain Syntax**:
- `→` (arrow): Sequential (one after another)
- `||` (parallel): Concurrent execution
- `+` (plus): Start together then merge
- `:` (colon): Labeled group (e.g., `H:` for Hierarchical)

---

### Hotkey Matrix by Complexity Level

```yaml
L1_ULTRA_FAST:
  Quick: [R], [D], [T]
  Explicit: @L1 <query>

L2_FAST_CHAIN:
  Quick: [D], [F], [B]
  Chains: [R>D], [D>I], [B>T]
  Explicit: @L2 <query>

L3_BALANCED:
  Quick: [A], [E], [I]
  Chains: [D>I>T], [R>D>I], [B>R>T]
  Explicit: @L3 <query>

L4_PARALLEL:
  Key: [P] or [Ctrl+P]
  Chains: [P:R||D||A], [C:Security||Performance||Read]
  Explicit: @L4 <query>

L5_HIERARCHICAL:
  Key: [H] or [Ctrl+H]
  Chains: [H:R+D→O], [H:Research+Design→Supervise→Implement]
  Explicit: @L5 <query>

L6_ITERATIVE:
  Key: [I] or [Ctrl+I]
  Chains: [I:D→P→T→repeat], [I:Debug→Fix→Test→Verify]
  Explicit: @L6 <query>

L7_ENSEMBLE:
  Key: [E] or [Ctrl+E]
  Chains: [E:P→S→I→O], [E:Parallel→Synthesize→Implement→Orchestrate]
  Explicit: @L7 <query>
```

---

## Part 3: Smart Query Selection & DSL Parser

### Input Parsing Algorithm

User provides: `/hekat <hotkey or query>`

**Step 1: Detect Input Type**
```
If starts with @L[1-7]:        → Explicit level override
If starts with [symbol]:        → Hotkey input
If contains -> || + :          → DSL syntax
Else:                           → Natural language query
```

**Step 2: Classify to Complexity Level**

For natural language queries, run classification algorithm:

```python
def classify_complexity(query: str, history: Dict, tokens_available: int) -> int:
    """
    Classify query to complexity level 1-7
    """
    # A. Keyword-based classification
    keywords_L1 = {"explain", "understand", "what", "how", "tell me", "show me"}
    keywords_L2 = {"then", "and then", "fix and", "design and", "document"}
    keywords_L4 = {"compare", "evaluate", "pros and cons", "options", "perspectives"}
    keywords_L5 = {"architect", "design system", "microservice", "infrastructure"}
    keywords_L6 = {"debug", "fix", "iterate", "until", "converge", "refine"}
    keywords_L7 = {"build", "complete", "from scratch", "full platform", "production"}

    if any(kw in query.lower() for kw in keywords_L7):
        base_level = 7
    elif any(kw in query.lower() for kw in keywords_L6):
        base_level = 6
    elif any(kw in query.lower() for kw in keywords_L5):
        base_level = 5
    elif any(kw in query.lower() for kw in keywords_L4):
        base_level = 4
    elif any(kw in query.lower() for kw in keywords_L2):
        base_level = 2
    elif any(kw in query.lower() for kw in keywords_L1):
        base_level = 1
    else:
        base_level = 3  # default balanced

    # B. Consciousness pattern matching
    similar_queries = find_similar_in_history(query, history, threshold=0.8)
    if similar_queries:
        # Use historical success level
        best_match = max(similar_queries, key=lambda q: q.success_rate)
        if best_match.success_rate > 0.9:
            base_level = best_match.level

    # C. Token budget constraint
    TOKEN_BUDGETS = {
        1: (600, 1200),
        2: (1500, 3000),
        3: (2500, 4500),
        4: (3000, 6000),
        5: (5500, 9000),
        6: (8000, 12000),
        7: (12000, 22000),
    }

    while base_level > 1 and TOKEN_BUDGETS[base_level][0] > tokens_available:
        base_level -= 1

    return base_level
```

**Step 3: Suggest Complexity Level**

```
Query: "design and implement authentication"
Base level: L3 (keyword: "implement")
History match: Similar query succeeded at L5 (87% success)
Tokens available: 9000

SUGGESTION:
"Similar to your 'user profile feature' (L5 Hierarchical, 87% success).
Use L5 (~7K tokens) for comprehensive design? [Y] [N] [Pick L1-7] [?]"

Default: [Y] uses historical success level
```

---

### Smart DSL Parser

Users can write DSL syntax directly for clarity:

**Implicit Level Detection** (parser infers level from syntax structure):

```yaml
SYNTAX_PATTERNS:
  L1: agent : "prompt"
      Example: deep-researcher : "explain JWT"

  L2: A -> B : "prompt"
      Example: api-architect -> docs-generator : "design then document"

  L3: A -> B -> C : "prompt"
      Example: api-architect -> practical-programmer -> test-engineer : "build auth"

  L4: (A || B || C) : "prompt"
      Example: (deep-researcher || api-architect || claude-sdk-expert) : "compare SDKs"

  L5: supervisor[A -> (B || C)] : "prompt"
      Example: project-orchestrator[(api-architect -> (practical-programmer || deployment-orchestrator))] : "microservice design"

  L6: iterate(A -> B -> C, until=condition) : "prompt"
      Example: iterate(debug-detective -> practical-programmer -> test-engineer, until=tests_pass) : "fix bug"

  L7: sample^3(A, B, C) ; mercurio[consensus] ; (D || E || F) : "prompt"
      Example: sample^3(deep-researcher, api-architect, frontend-architect) ; mercurio[consensus] ; (practical-programmer || deployment-orchestrator) : "platform design"
```

**Explicit Override** (force specific level):

```yaml
@L5 "quick question"
@L7 design system
@L4 (research || implement)

Example:
/hekat @L5 "explain database indexing"
→ Forces L5 Hierarchical for this query (may waste tokens, warns user)
```

**Parser Rules** (precedence):

```python
def parse_dsl_and_classify(input_str: str) -> Tuple[int, str]:
    """
    Parse DSL syntax and return (level, query)
    """
    # Rule 1: Explicit @L override
    if input_str.startswith("@L"):
        level = int(input_str[2])  # @L5 → 5
        query = input_str[4:]
        return level, query, "explicit"

    # Rule 2: Count operators to infer level
    arrow_count = input_str.count("->")
    parallel_count = input_str.count("||")
    iterate_count = input_str.count("iterate(")
    sample_count = input_str.count("sample^")

    if sample_count > 0 or "mercurio" in input_str:
        level = 7
    elif iterate_count > 0:
        level = 6
    elif "supervisor" in input_str or "[" in input_str:
        level = 5
    elif parallel_count > 0:
        level = 4
    elif arrow_count >= 2:
        level = 3
    elif arrow_count == 1:
        level = 2
    else:
        level = 1

    return level, input_str, "implicit"
```

---

## Part 4: Token Tracking & Display

### Task-Relay Checkpoint Format

Every /hekat invocation logs phases with token accounting:

```yaml
CHECKPOINT_LOG:
  timestamp: 2025-10-27T15:45:32Z
  query: "design auth system"

  Phase_1_Input_Parsing:
    status: complete
    pre_tokens: 45000
    post_tokens: 45487
    delta: +487
    variance: +0.00% (expected: ~500)

  Phase_2_Query_Selection:
    status: complete
    pre_tokens: 45487
    post_tokens: 46379
    delta: +892
    variance: +0.04% (expected: ~900)

  Phase_3_Complexity_Classification:
    status: complete
    pre_tokens: 46379
    post_tokens: 46487
    delta: +108
    variance: -0.78% (expected: ~300)
    note: "Used consciousness pattern match (cached result)"

  Phase_4_Hotkey_Generation:
    status: complete
    pre_tokens: 46487
    post_tokens: 46994
    delta: +507
    variance: +0.07% (expected: ~500)

  Phase_5_Display_Formatting:
    status: complete
    pre_tokens: 46994
    post_tokens: 47297
    delta: +303
    variance: +0.02% (expected: ~300)

SUMMARY:
  total_hekat_overhead: 2297 tokens (hekat selection + display)
  selected_level: L5 Hierarchical
  estimated_execution: 7200 tokens
  total_projected: 9497 tokens
  budget_remaining: 40503 / 50000
  variance: +2.3% ⚠️ (investigate Phase 2 spike)
  status: ✅ PROCEED (40K+ remaining for execution)
```

### CLI Display Formats

**DEFAULT (Clean, user-friendly)**:
```
/hekat "design auth system"

→ Selected: L5 Hierarchical (Est: 7200 tokens) ✅
  Agents: [api-architect + deep-researcher] → project-orchestrator → [practical-programmer || deployment-orchestrator]
  Hotkey: [Ctrl+H]

  Ready to execute? [Y/N] [Show details] [Pick different level]
```

**VERBOSE (--verbose flag)**:
```
/hekat --verbose "design auth system"

PHASE BREAKDOWN:
  Phase 1: Input Parsing         [+487 tokens] ✅
  Phase 2: Query Selection       [+892 tokens] ✅
  Phase 3: Complexity Classify   [+108 tokens] ✅ (cached)
  Phase 4: Hotkey Generation     [+507 tokens] ✅
  Phase 5: Display Format        [+303 tokens] ✅
  ─────────────────────────────────────────
  Overhead: 2297 tokens

EXECUTION ESTIMATE:
  Level: L5 Hierarchical
  Agents: 4-5 agents, hierarchical
  Token budget: 7200 (range: 5500-9000)
  Variance target: ±5%

TOKEN BUDGET:
  Available: 50000
  Overhead: 2297
  Execution: 7200
  Total: 9497
  Remaining: 40503
  Status: ✅ PROCEED
```

**ERROR (Variance > ±20% or constraint violation)**:
```
/hekat --verbose "design complete platform"

⚠️ TOKEN CONSTRAINT VIOLATION
  Selected: L7 Ensemble
  Estimated tokens: 18000
  Available: 9500
  Deficit: -8500 tokens

OPTIONS:
  [5] Use L5 Hierarchical (7-8K, ~85% of requested depth) - RECOMMENDED
  [6] Use L6 Iterative (9-10K, tight fit)
  [4] Use L4 Parallel (4-5K, conservative)
  [C] Continue anyway (may truncate or degrade)
  [X] Cancel

Your choice: _
```

**STREAMING (During execution)**:
```
/hekat "design auth system"

Executing L5 Hierarchical [████████░░░░] 65%

Phase 1: Research [COMPLETE] 2341 tokens
Phase 2: Synthesis [RUNNING...] +1200 tokens (est)
Phase 3: Implementation [PENDING]

Current cost: 3541 / 7200 budget
Remaining: 3659 tokens
Status: ✅ ON TRACK
```

---

## Part 5: Consciousness Integration

### What Gets Tracked

```yaml
CONSCIOUSNESS_PATTERN:
  query_context: "design auth system"
  selected_level: 5
  agents_used: [api-architect, deep-researcher, practical-programmer]
  tokens_estimated: 7200
  tokens_actual: 7189
  variance: -0.15%
  execution_time: 240 seconds
  user_satisfaction: "good"  # implicit from next query timing
  success_indicator: true
  timestamp: 2025-10-27T15:45:32Z
```

### Pattern Matching Algorithm

```python
def find_similar_pattern(new_query: str, history: List[Consciousness]) -> Optional[Consciousness]:
    """
    Find similar past queries to suggest level
    """
    best_match = None
    best_score = 0.7  # minimum threshold

    for past in history:
        # Semantic similarity (simplified)
        similarity = compute_similarity(new_query, past.query_context)

        # Success rate weight
        success_weight = past.success_rate  # 0-1

        # Recent bonus (recent patterns more relevant)
        recency = 1.0 if past.timestamp > now() - timedelta(days=7) else 0.8

        score = similarity * success_weight * recency

        if score > best_score:
            best_score = score
            best_match = past

    return best_match
```

### Learning Loop

```yaml
LEARNING_CYCLE:
  1. User makes query → system suggests level based on history
  2. User accepts or overrides
  3. Execution completes → log success/failure
  4. Pattern added to consciousness
  5. Next similar query → better suggestion (higher confidence)

PATTERN_IMPROVEMENT:
  Sample_count: 1-2     → Low confidence (0.5-0.6), ask user
  Sample_count: 3-5     → Medium confidence (0.7-0.8), suggest
  Sample_count: 5+      → High confidence (0.9+), recommend strongly
  Success_rate: <0.7    → Downgrade confidence
  Success_rate: >0.9    → Upgrade confidence
```

---

## Part 6: Fallback Mechanisms

### Insufficient Token Budget

**Scenario**: User requests L7 (18K tokens) but only 10K available

**Response**:
```
You requested L7 Ensemble (needs ~18K tokens)
Available: 10,000 tokens | Deficit: -8,000 tokens

FALLBACK OPTIONS:
[5] Use L5 Hierarchical (7-8K tokens) ⭐ RECOMMENDED
     → Full design phase with approval gates
     → Missing: parallel implementation agents
     → Projected success: 89% vs 97% for L7

[6] Use L6 Iterative (9-10K tokens) [TIGHT FIT]
     → Iterative refinement approach
     → Good for bugs, less good for architecture
     → Projected success: 72% vs 97% for L7

[4] Use L4 Parallel (4-5K tokens) [CONSERVATIVE]
     → Multi-perspective analysis only
     → No implementation planning
     → Projected success: 54% vs 97% for L7

[C] Continue with L7 anyway
     → May truncate results or degrade quality
     → Not recommended

[X] Cancel this query

Your choice [5]:
```

**Smart Default**: System selects [5] (next-best level) if user doesn't respond in 30 seconds

### Agent Unavailability

**Scenario**: Requested agent is not available (e.g., hekat-agent during initial setup)

**Response**:
```
Agent 'hekat-agent' not available
Fallback chain:
  L5 (api-architect + deep-researcher → project-orchestrator) → [✓ Available]

Using: L5 with available agents
Missing agent: hekat-agent (not critical for this level)
Projected impact: +10% tokens (alternate agent may be less efficient)

Continue? [Y/N]
```

### Context Size Explosion

**Scenario**: Query generates unexpectedly large intermediate results

**Response**:
```
⚠️ CONTEXT SIZE SPIKE DETECTED
Phase 3 generated 4800 tokens (expected: 2000)
Remaining budget: 2100 tokens

FALLBACK:
[A] Auto-compress Phase 3 results (using extract + comonad patterns)
    → Compress to 1200 tokens (save 3600)
    → Continue with Phase 4-5
    → Small quality loss (5-10%)

[B] Stop after Phase 3 and return current results
    → Partial solution available now
    → Can resume later with fresh budget

[C] Continue without compression (risk budget overrun)

Your choice [A]:
```

---

## Part 7: Integration with Existing Claude Code

### `/hekat` Command

Location: `~/.claude/commands/hekat.md`

```markdown
---
name: hekat
description: HEKAT Query Builder - complexity-aware multi-agent orchestration (L1-L7)
---

# HEKAT Query Builder

## Usage

```bash
/hekat <query>                    # Auto-detect complexity
/hekat @L5 <query>               # Force specific level
/hekat [hotkey] <query>          # Use hotkey (e.g., [R], [D], [P:R||D||A])
/hekat --verbose <query>         # Show detailed token tracking
/hekat --dry-run <query>         # Show execution plan without running
/hekat --help                    # Show hotkey reference
```

## Quick Examples

```bash
/hekat [R] "explain JWT authentication"
→ L1: Single research agent

/hekat "design and implement API endpoint"
→ L3: Research → Design → Implement

/hekat [P] "compare FastAPI vs Express"
→ L4: Parallel consensus (multiple perspectives)

/hekat @L7 "build scalable microservices platform"
→ L7: Full ensemble with research + synthesis + implementation
```

## Hotkey Reference

TIER 1 (Single keys): [R]esearch [D]esign [T]est [B]uild [F]rontend [I]mplement [O]rchestrate [S]ynthesize

TIER 2 (Ctrl modifiers): [Ctrl+P] L4, [Ctrl+H] L5, [Ctrl+I] L6, [Ctrl+E] L7

TIER 3 (Chains): [R>D>I] Sequential, [P:R||D||A] Parallel, [H:R+D→O] Hierarchical
```

### `hekat` Skill

Location: `~/.claude/skills/hekat/SKILL.md`

```markdown
---
name: hekat
description: HEKAT Query Builder - select optimal agent composition for any task (L1-L7 complexity)
---

# HEKAT Query Builder

## When to Use This Skill

- Need to determine right level of agent orchestration for a task
- Want to optimize token usage while maintaining quality
- Need consciousness patterns to improve over time
- Want to see task-relay token tracking for every query

## Quick Start

```
/hekat "your task or question"
→ Auto-selects complexity level (L1-L7)
→ Shows estimated tokens and execution plan
→ Executes with task-relay checkpoints
```

## Complexity Levels Reference

| Level | Pattern | Agents | Tokens | Use Case |
|-------|---------|--------|--------|----------|
| L1 | Single | 1 | 600-1200 | Quick explanation |
| L2 | Chain | 2 | 1500-3000 | Two-step workflow |
| L3 | Sequential | 3 | 2500-4500 | Feature development |
| L4 | Parallel | 2-3 | 3000-6000 | Multi-perspective |
| L5 | Hierarchical | 4-5 | 5500-9000 | Architecture design |
| L6 | Iterative | 4-6 | 8000-12000 | Refinement loops |
| L7 | Ensemble | 7+ | 12000-22000 | Full-stack projects |

## Common Hotkeys

[R] Research, [D] Design, [T] Test, [I] Implement
[P] Parallel, [H] Hierarchical, [E] Ensemble
[R>D>I] Sequential chain, [P:R||D||A] Parallel research/design/analyze
```

### `hekat` Agent

Location: `~/.claude/agents/hekat-agent/agent.yaml`

```yaml
name: hekat-agent
description: HEKAT domain expert - analyzes queries, suggests complexity levels, optimizes agent composition
model: claude-sonnet

capabilities:
  - complexity_classification: Map natural language to L1-L7
  - pattern_matching: Find similar past queries in consciousness
  - hotkey_suggestion: Recommend single-key or combo hotkeys
  - token_budgeting: Estimate tokens per phase
  - dsl_parsing: Understand DSL syntax
  - consciousness_management: Learn from query history

use_cases:
  - User makes query → hekat-agent classifies to level
  - User wants to understand why level was chosen → explain with reasoning
  - New DSL syntax → parse and infer level
  - Historical pattern → suggest based on past success
  - Token constraint → recommend fallback level
```

### Consciousness Storage

Location: `~/.claude/hekat-consciousness.yaml`

```yaml
hekat_consciousness:
  version: 1.0
  last_updated: 2025-10-27T15:45:32Z

  invocations:
    - id: inv_001
      timestamp: 2025-10-27T14:30:00Z
      input_query: "explain JWT authentication"
      detected_level: 1
      user_override: false
      agents_executed: [deep-researcher]
      tokens_estimated: 900
      tokens_actual: 847
      variance: -5.9%
      success_indicator: true
      execution_time: 23s

    - id: inv_002
      timestamp: 2025-10-27T15:15:00Z
      input_query: "design auth system"
      detected_level: 5
      consciousness_match: "auth" (89% similarity, L5, 0.94 success)
      user_override: false
      agents_executed: [api-architect, deep-researcher, project-orchestrator, practical-programmer]
      tokens_estimated: 7200
      tokens_actual: 7189
      variance: -0.15%
      success_indicator: true
      execution_time: 240s

  consciousness_patterns:
    auth_feature:
      pattern: "design * auth"
      default_level: 5
      sample_count: 12
      success_rate: 0.94
      last_used: 2025-10-27T15:15:00Z
      recommended_agents: [api-architect, deep-researcher, project-orchestrator, practical-programmer]

    quick_explanation:
      pattern: "explain *"
      default_level: 1
      sample_count: 34
      success_rate: 0.99
      last_used: 2025-10-27T14:30:00Z
      recommended_agents: [deep-researcher]
```

---

## Summary

The HEKAT Query Builder is a **production-ready system** that:

✅ **Maps user intent to agent complexity** (L1-L7)
✅ **Tracks tokens rigorously** with task-relay checkpoints
✅ **Suggests hotkeys** for fast execution
✅ **Learns from history** via consciousness patterns
✅ **Falls back gracefully** when constrained
✅ **Integrates with Claude Code** (command, skill, agent)

**Status**: Ready for implementation and iteration.
