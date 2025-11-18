# HEKAT Query Builder: Implementation Roadmap

**Status**: Specification Complete → Implementation Phase
**Date**: 2025-10-27
**Version**: 1.0

---

## Overview

This roadmap details the path from unified specification (QUERY_BUILDER_SPECIFICATION.md) to production-ready system. It identifies **concrete next steps** that enable you to modify skills, agents, and commands with full context.

---

## Phase 1: Foundation (Immediate - This Week)

### Goal: Create callable components with correct file structure

**What gets built**: Command, Skill, Agent definitions that can be invoked, even if not fully functional yet.

---

### 1.1 Create `/hekat` Command

**File**: `~/.claude/commands/hekat.md`

**Content**: Minimal command definition

```markdown
---
name: hekat
description: HEKAT Query Builder - complexity-aware orchestration (L1-L7)
---

# /hekat Command

## Usage

/hekat <query>              # Auto-detect complexity
/hekat @L5 <query>         # Force level
/hekat --verbose <query>   # Show token tracking
/hekat --help              # Show hotkeys

## Quick Examples

/hekat "explain JWT"                    → L1 single research agent
/hekat "design auth endpoint"           → L3 design → implement → test
/hekat [P] "compare API frameworks"     → L4 parallel consensus
/hekat @L7 "build microservices"       → L7 full ensemble

## Current Status

🚀 TIER 1 command: Basic query input accepted
⏳ TIER 2: Complexity classification (in progress)
⏳ TIER 3: Token tracking display (in progress)
⏳ TIER 4: Consciousness pattern integration (planned)

See: QUERY_BUILDER_SPECIFICATION.md for full details
```

**Action Items**:
- [ ] Create file in `~/.claude/commands/hekat.md`
- [ ] Make `/hekat` callable (test: `/hekat --help` works)
- [ ] Run `/actualize`

**Deliverable**: Users can run `/hekat` (even if it just echoes back the query)

---

### 1.2 Create `hekat` Skill

**File**: `~/.claude/skills/hekat/SKILL.md`

**Content**: Skill with progressive disclosure

```markdown
---
name: hekat
description: HEKAT Query Builder - select optimal agent composition (L1-L7)
---

# HEKAT Query Builder Skill

## When to Use

- Need to select right complexity level for a task
- Want to understand why a certain agent composition was chosen
- Uncertain about token budget for a query
- Want to leverage consciousness patterns (historical learning)

## Core Concepts

### Complexity Levels (L1-L7)

Each level combines different numbers of agents with specific orchestration patterns:

**L1-L3**: Sequential (one agent after another)
- L1: Single agent (~600 tokens)
- L2: Two agents in sequence (~2000 tokens)
- L3: Three agents in sequence (~3500 tokens)

**L4-L5**: Parallel + Hierarchical (multiple agents coordinating)
- L4: Parallel consensus (2-3 agents, ~4000 tokens)
- L5: Hierarchical with approval gates (4-5 agents, ~7000 tokens)

**L6-L7**: Iterative + Ensemble (complex coordination)
- L6: Iterative refinement loops (4-6 agents, ~10000 tokens)
- L7: Full ensemble orchestration (7+ agents, ~18000 tokens)

### Token Budget Management

Each level has estimated token cost:
```
L1:  600-1200      (single agent, minimal context)
L2:  1500-3000     (two agents, extract costs)
L3:  2500-4500     (three agents, staged extraction)
L4:  3000-6000     (parallel with smart_duplicate)
L5:  5500-9000     (hierarchical multi-stage)
L6:  8000-12000    (iterative refinement)
L7:  12000-22000   (ensemble + synthesis)
```

### Hotkey Tiers

**TIER 1**: Single-key quick access
- [R] Research, [D] Design, [T] Test, [B] Build, [F] Frontend, [I] Implement

**TIER 2**: Complexity selectors (hold Ctrl)
- [Ctrl+P] L4, [Ctrl+H] L5, [Ctrl+I] L6, [Ctrl+E] L7

**TIER 3**: Agent chains
- [R>D>I] Sequential, [P:R||D||A] Parallel, [H:R+D→O] Hierarchical

## Quick Start

### Single Agent (L1)
```
/hekat [R] "explain PostgreSQL indexing"
→ deep-researcher explains concept
```

### Two-Step Workflow (L2)
```
/hekat "design API then document it"
→ api-architect designs, docs-generator documents
```

### Full Feature Development (L3)
```
/hekat [D>I>T] "build authentication"
→ api-architect → practical-programmer → test-engineer
```

### Multi-Perspective (L4)
```
/hekat [P] "evaluate FastAPI vs Express"
→ (deep-researcher || api-architect || claude-sdk-expert) analyzes options
```

### System Architecture (L5)
```
/hekat @L5 "design microservices platform"
→ Research + Design → Project Orchestrator → Implementation
```

## Advanced Patterns

### Token Tracking
```
/hekat --verbose "your query"
→ Shows phase-by-phase token consumption with variance
```

### DSL Syntax
```
/hekat "agent1 -> agent2 -> agent3 : query"
→ Parser infers L3 from two arrows
```

### Consciousness Patterns
```
/hekat "design auth"
→ System finds similar past query (87% match, L5, 0.94 success)
→ Suggests L5 for this query
```

### Fallback When Budget Tight
```
/hekat "build full platform"
→ Requested L7 (18K tokens), available 10K
→ System offers L5 (7K) as best alternative
```

## Use Cases by Situation

| Situation | Example | Recommended Level |
|-----------|---------|-------------------|
| Quick explanation | "What is JWT?" | L1 [R] |
| Design then build | "Design API endpoint" | L3 [D>I>T] |
| Compare options | "PostgreSQL vs MongoDB" | L4 [P] |
| Architecture | "Design microservices" | L5 [H] |
| Bug fix with tests | "Fix memory leak" | L6 [I] |
| Full project | "Build SaaS platform" | L7 [E] |

## Token Budgeting Example

Query: "Build authentication system"
System inference:
- Keywords: "build", "system" → base level L5
- Token available: 15000 → sufficient for L5
- Consciousness: Similar "auth design" query succeeded at L5 → confirm L5
- Estimated: 7200 tokens, actual range 5500-9000

Display:
```
Selected: L5 Hierarchical
Agents: api-architect + deep-researcher → project-orchestrator → practical-programmer
Tokens: Est 7200 | Budget 15000 | Variance ±5%
Status: ✅ Ready to execute
```

## Architecture Reference

See QUERY_BUILDER_SPECIFICATION.md for:
- Complete L1-L7 definitions with agents per level
- Full hotkey matrix (TIER 1-3)
- Smart DSL parser rules
- Token tracking display formats
- Consciousness pattern schema
- Fallback mechanisms
```

**Action Items**:
- [ ] Create directory `~/.claude/skills/hekat/`
- [ ] Create file `SKILL.md` with content above
- [ ] Optional: Create `EXAMPLES.md` with 10+ real-world queries
- [ ] Run `/actualize`

**Deliverable**: Skill is discoverable and explains L1-L7 system

---

### 1.3 Create `hekat-agent` Agent Definition

**File**: `~/.claude/agents/hekat-agent/agent.yaml`

**Content**: Agent configuration

```yaml
name: hekat-agent
displayName: HEKAT Query Builder Expert
description: |
  Analyzes user queries, classifies complexity (L1-L7),
  suggests hotkeys, estimates tokens, manages consciousness patterns

model: claude-sonnet
color: purple

capabilities:
  - complexity_classification: "Map natural language queries to L1-L7"
  - pattern_matching: "Find similar queries in consciousness history"
  - hotkey_suggestion: "Recommend single-key or combo hotkeys"
  - token_estimation: "Estimate tokens per phase of execution"
  - dsl_parsing: "Parse and validate DSL syntax"
  - consciousness_management: "Track and learn from query history"
  - fallback_planning: "Suggest lower complexity levels when constrained"

primary_role: "Complexity advisor - helps users find right level for their task"

use_cases:
  - User asks question → hekat-agent classifies to L1-L7
  - "Why L5?" → hekat-agent explains reasoning
  - DSL query → hekat-agent validates and infers level
  - Token constraint → hekat-agent suggests best fallback
  - Historical pattern → hekat-agent suggests based on past success

expertise_areas:
  - Comonadic orchestration patterns (extract, smart_duplicate, consensus)
  - Task-relay token discipline and accounting
  - Consciousness pattern learning and matching
  - DSL parsing and syntax inference
  - Fallback mechanism design

file_structure:
  - agent.yaml: This configuration
  - AGENT.md: Usage guide
  - reference.md: Detailed token budget breakdown (optional)

integration:
  - Works with: `/hekat` command
  - Uses: consciousness patterns (~/.claude/hekat-consciousness.yaml)
  - Outputs: Complexity level, hotkey, execution plan
  - Logs: Query invocations to consciousness history

invocation_example: |
  Task tool with subagent_type: "hekat-agent"
  Prompt: "Classify this query and suggest optimal complexity level with hotkey"
```

**Action Items**:
- [ ] Create directory `~/.claude/agents/hekat-agent/`
- [ ] Create `agent.yaml` with configuration
- [ ] Create `AGENT.md` with usage guide
- [ ] Sync to project `.claude/agents/` if needed
- [ ] Run `/actualize`

**Deliverable**: Agent is discoverable and can be invoked via Task tool

---

### 1.4 Create Consciousness Storage File

**File**: `~/.claude/hekat-consciousness.yaml`

**Content**: Initial empty consciousness with schema

```yaml
# HEKAT Consciousness Pattern Store
# Tracks query invocations, success rates, agent compositions
# Used by hekat-agent to suggest complexity levels

metadata:
  version: 1.0
  created: 2025-10-27
  last_updated: 2025-10-27
  total_invocations: 0
  total_patterns: 0

invocations: []
# Will be populated as users run /hekat queries
# Schema per invocation:
#   - id: unique invocation ID
#   - timestamp: when query was run
#   - input_query: what user asked
#   - detected_level: what level was chosen (1-7)
#   - agents_executed: which agents were used
#   - tokens_estimated: predicted tokens
#   - tokens_actual: real token consumption
#   - variance: (actual - estimated) / estimated
#   - success_indicator: did query succeed
#   - execution_time: wall-clock time
#   - user_override: did user override auto-detected level

consciousness_patterns: {}
# Patterns learned from invocation history
# Schema per pattern:
#   pattern_name:
#     pattern_text: "design * system"
#     default_level: 5
#     sample_count: number of matching historical queries
#     success_rate: % of queries at this level succeeding
#     last_used: timestamp of most recent match
#     recommended_agents: [list of agents effective at this level]
#     token_range: [min, max] typical tokens for this pattern
```

**Action Items**:
- [ ] Create file `~/.claude/hekat-consciousness.yaml`
- [ ] Initialize with schema above
- [ ] Ensure file is readable/writable

**Deliverable**: Consciousness storage is ready for population

---

### 1.5 Sync to Project

**Action Items**:
- [ ] Copy `~/.claude/commands/hekat.md` → `./LUXOR/.claude/commands/hekat.md`
- [ ] Copy `~/.claude/skills/hekat/` → `./LUXOR/.claude/skills/hekat/`
- [ ] Copy `~/.claude/agents/hekat-agent/` → `./LUXOR/.claude/agents/hekat-agent/`

---

### 1.6 Run Actualization

**Action**:
```bash
/actualize
```

**Expected Output**:
```
Actualization Status:
  Commands: 42 → 43 (+1: hekat)
  Skills: 75 → 76 (+1: hekat)
  Agents: 34 → 35 (+1: hekat-agent)

  Synced: ~/.claude ↔ LUXOR/.claude
  Timestamp: 2025-10-27T15:45:32Z
  Status: ✅ All systems synchronized
```

**Deliverable**: Command, Skill, Agent are registered and invocable

---

## Phase 2: Core Implementation (1-2 Weeks)

### Goal: Make `/hekat` functional with complexity classification and hotkey suggestion

---

### 2.1 Implement Complexity Classification

**What**: Parse user input and classify to L1-L7

**Where**: `/hekat` command implementation OR hekat-agent invocation

**Implementation approach**:

```python
# Pseudocode for /hekat command

def hekat_classify(user_input: str, available_tokens: int) -> dict:
    """
    Classify query to complexity level
    Returns: {level: 1-7, confidence: 0-1, reasoning: str, hotkey: str}
    """

    # Step 1: Check for explicit level override (@L5)
    if user_input.startswith("@L"):
        level = int(user_input[2])
        return {
            "level": level,
            "confidence": 1.0,
            "method": "explicit",
            "reasoning": f"User explicitly requested L{level}"
        }

    # Step 2: Check for hotkey input ([R], [D], [P], etc.)
    if user_input.startswith("[") and user_input.count("]") > 0:
        hotkey = extract_hotkey(user_input)
        level = map_hotkey_to_level(hotkey)
        return {
            "level": level,
            "confidence": 0.95,
            "method": "hotkey",
            "reasoning": f"Hotkey {hotkey} maps to L{level}",
            "hotkey": hotkey
        }

    # Step 3: Keyword classification
    query_text = user_input.lower()
    keyword_level = classify_by_keywords(query_text)

    # Step 4: Look up consciousness patterns
    matching_pattern = find_matching_pattern(query_text)
    if matching_pattern and matching_pattern.success_rate > 0.85:
        pattern_level = matching_pattern.default_level
        pattern_confidence = matching_pattern.success_rate
    else:
        pattern_level = keyword_level
        pattern_confidence = 0.6

    # Step 5: Check token budget
    final_level = pattern_level
    while TOKEN_BUDGETS[final_level].min > available_tokens:
        final_level -= 1

    return {
        "level": final_level,
        "confidence": pattern_confidence,
        "method": "keyword + consciousness",
        "reasoning": f"Keywords suggest L{keyword_level}, consciousness suggests L{pattern_level}, tokens allow L{final_level}",
        "consciousness_match": matching_pattern.name if matching_pattern else None
    }
```

**Testing**:
- [ ] Test with L1 queries: "explain X" → L1
- [ ] Test with L2 queries: "design and build" → L2
- [ ] Test with L4 queries: "compare options" → L4
- [ ] Test with L7 queries: "build platform from scratch" → L7
- [ ] Test token constraint: Request L7 with 5K tokens → fallback to L5
- [ ] Test hotkey input: [R] → L1, [P] → L4, etc.
- [ ] Test consciousness: Second "auth design" query suggests L5

**Deliverable**: User runs `/hekat "query"` → System suggests L1-L7 with reasoning

---

### 2.2 Implement Hotkey Matrix

**What**: Map hotkeys to agent compositions

**Where**: Hotkey configuration file or hardcoded in command

**Data structure**:

```yaml
hotkey_matrix:
  tier_1:  # Single keys
    R: {agents: [deep-researcher], level: 1, description: "Research/explain"}
    D: {agents: [api-architect, debug-detective], level: "1-5", description: "Design/debug"}
    T: {agents: [test-engineer], level: 1, description: "Test/verify"}
    B: {agents: [practical-programmer], level: 2, description: "Build/implement"}
    F: {agents: [frontend-architect], level: 2, description: "Frontend development"}
    I: {agents: [practical-programmer], level: 2, description: "Implement"}
    O: {agents: [project-orchestrator], level: 5, description: "Orchestrate"}
    S: {agents: [mercurio-orchestrator], level: 6, description: "Synthesize"}
    C: {agents: [debug-detective, test-engineer], level: 3, description: "Code review"}
    P: {agents: "parallel", level: 4, description: "Parallel analysis"}
    V: {agents: [test-engineer], level: 1, description: "Verify"}
    A: {agents: [deep-researcher, debug-detective], level: 1, description: "Analyze"}

  tier_2:  # Ctrl-modifiers for levels
    Ctrl+P: {level: 4, description: "L4 Parallel Consensus"}
    Ctrl+H: {level: 5, description: "L5 Hierarchical"}
    Ctrl+I: {level: 6, description: "L6 Iterative"}
    Ctrl+E: {level: 7, description: "L7 Ensemble"}

  tier_3:  # Agent chains
    R>D>I: {agents: [deep-researcher, api-architect, practical-programmer], level: 3}
    D>I>T: {agents: [api-architect, practical-programmer, test-engineer], level: 3}
    P:R||D||A: {agents: [deep-researcher, api-architect, debug-detective], level: 4, pattern: "parallel"}
    H:R+D→O: {agents: [deep-researcher, api-architect, project-orchestrator], level: 5, pattern: "hierarchical"}
    I:D→P→T: {agents: [debug-detective, practical-programmer, test-engineer], level: 6, pattern: "iterative"}
```

**Deliverable**: `/hekat [R]` or `[Ctrl+H]` or `[R>D>I]` works and suggests correct agents

---

### 2.3 Implement Token Tracking Display

**What**: Show estimated vs actual tokens with variance tracking

**Where**: `/hekat --verbose` output

**Display format**:

```
/hekat --verbose "design auth endpoint"

SELECTION PHASE:
  Phase 1: Input parsing      [+487 tokens] ✅
  Phase 2: Complexity classify [+892 tokens] ✅
  Phase 3: Hotkey generation  [+507 tokens] ✅
  ─────────────────────────────
  Total overhead: 1886 tokens

EXECUTION PLAN:
  Selected: L5 Hierarchical
  Agents: [api-architect, deep-researcher] → project-orchestrator → [practical-programmer]
  Token budget: 7200 (range: 5500-9000)

TOKEN BUDGET ANALYSIS:
  Available: 50000
  Selection: 1886
  Execution: 7200
  Total: 9086
  Remaining: 40914
  Status: ✅ PROCEED (within budget, 82% remaining)
```

**Deliverable**: Users see token tracking on demand with `--verbose`

---

## Phase 3: Advanced Features (2-3 Weeks)

### Goal: Add consciousness patterns, DSL parsing, fallback mechanisms

---

### 3.1 Implement Consciousness Pattern Matching

**What**: Learn from query history, improve suggestions

**Where**: hekat-agent + consciousness storage

**Implementation**:

```python
def update_consciousness(query_record: dict) -> None:
    """
    Record query execution and update patterns
    """
    # Load consciousness file
    consciousness = load_yaml("~/.claude/hekat-consciousness.yaml")

    # Add invocation
    consciousness["invocations"].append(query_record)

    # Update or create pattern
    pattern_name = extract_pattern_name(query_record["input_query"])
    if pattern_name in consciousness["consciousness_patterns"]:
        pattern = consciousness["consciousness_patterns"][pattern_name]
        pattern["sample_count"] += 1
        # Update success rate (running average)
        old_rate = pattern["success_rate"]
        new_rate = (old_rate * (pattern["sample_count"] - 1) +
                   query_record["success_indicator"]) / pattern["sample_count"]
        pattern["success_rate"] = new_rate
        pattern["last_used"] = query_record["timestamp"]
    else:
        # Create new pattern
        consciousness["consciousness_patterns"][pattern_name] = {
            "pattern_text": extract_pattern_text(query_record["input_query"]),
            "default_level": query_record["detected_level"],
            "sample_count": 1,
            "success_rate": 1.0 if query_record["success_indicator"] else 0.0,
            "last_used": query_record["timestamp"],
            "recommended_agents": query_record["agents_executed"],
            "token_range": [query_record["tokens_actual"] * 0.8,
                          query_record["tokens_actual"] * 1.2]
        }

    # Save consciousness
    save_yaml(consciousness, "~/.claude/hekat-consciousness.yaml")
```

**Testing**:
- [ ] Run /hekat "explain JWT" 5 times → pattern emerges
- [ ] Second "auth design" query suggests L5 with 87% confidence
- [ ] Check consciousness file has updated success_rate

**Deliverable**: System learns from history, gets smarter with use

---

### 3.2 Implement DSL Parser

**What**: Parse DSL syntax and auto-infer complexity level

**Where**: `/hekat` command or hekat-agent

**Parser rules**:

```python
def parse_dsl(dsl_str: str) -> dict:
    """
    Parse DSL syntax and infer complexity level
    """

    # Count operators
    arrows = dsl_str.count("->")
    parallels = dsl_str.count("||")
    iterates = "iterate(" in dsl_str
    samples = "sample^" in dsl_str

    # Infer level from operators
    if samples or "mercurio" in dsl_str:
        level = 7
    elif iterates:
        level = 6
    elif "supervisor" in dsl_str or "[" in dsl_str:
        level = 5
    elif parallels > 0:
        level = 4
    elif arrows >= 2:
        level = 3
    elif arrows == 1:
        level = 2
    else:
        level = 1

    return {
        "level": level,
        "method": "dsl_parsing",
        "operators": {"arrows": arrows, "parallels": parallels, "iterates": iterates},
        "confidence": 0.98  # DSL is explicit
    }

# Examples:
parse_dsl("deep-researcher : 'explain JWT'")
# → {level: 1, operators: {arrows: 0, ...}}

parse_dsl("api-architect -> practical-programmer : 'design then build'")
# → {level: 2, operators: {arrows: 1, ...}}

parse_dsl("(deep-researcher || api-architect) : 'compare options'")
# → {level: 4, operators: {parallels: 1, ...}}

parse_dsl("iterate(debug-detective -> practical-programmer -> test-engineer) : 'fix bug'")
# → {level: 6, operators: {iterates: 1, ...}}
```

**Testing**:
- [ ] Parse L1 syntax: agent : "query"
- [ ] Parse L2 syntax: A -> B : "query"
- [ ] Parse L4 syntax: (A || B) : "query"
- [ ] Parse L7 syntax: sample^3(...) ; mercurio[...]
- [ ] Explicit override: @L5 agent -> agent : "query"

**Deliverable**: Users can use natural DSL syntax, system auto-detects level

---

### 3.3 Implement Fallback Mechanism

**What**: Handle token constraints with interactive UI

**Where**: `/hekat` command, interactive response

**Fallback logic**:

```python
def suggest_fallback(requested_level: int, available_tokens: int) -> dict:
    """
    If user requests level higher than budget allows, suggest fallback
    """

    min_tokens_required = TOKEN_BUDGETS[requested_level][0]

    if min_tokens_required > available_tokens:
        # Find best fallback level
        candidates = []
        for fallback_level in range(requested_level - 1, 0, -1):
            min_needed = TOKEN_BUDGETS[fallback_level][0]
            if min_needed <= available_tokens:
                candidates.append({
                    "level": fallback_level,
                    "tokens_needed": min_needed,
                    "quality_ratio": fallback_level / requested_level
                })

        best = max(candidates, key=lambda c: c["quality_ratio"])

        return {
            "original_level": requested_level,
            "original_tokens_needed": min_tokens_required,
            "fallback_level": best["level"],
            "fallback_tokens_needed": best["tokens_needed"],
            "message": f"L{requested_level} needs {min_tokens_required} tokens, "
                      f"you have {available_tokens}. "
                      f"Using L{best['level']} ({best['tokens_needed']} tokens) instead.",
            "options": candidates
        }
    else:
        return {"status": "ok", "level": requested_level}
```

**UI Display**:

```
You requested L7 (needs ~18K tokens)
Available: 10,000 tokens

FALLBACK OPTIONS:
[5] Use L5 Hierarchical (7-8K tokens) ⭐ RECOMMENDED
     Agents: 4-5 hierarchical
     Quality vs L7: 71% (missing parallel implementation)

[6] Use L6 Iterative (9-10K tokens) [TIGHT FIT]
     Agents: 4-6 iterative
     Quality vs L7: 86% (less synthesis depth)

[4] Use L4 Parallel (4-5K tokens) [CONSERVATIVE]
     Agents: 2-3 parallel
     Quality vs L7: 57% (missing implementation)

[C] Continue anyway (may truncate)
[X] Cancel

Your choice [5]:
```

**Testing**:
- [ ] Request L7 with 5K tokens → Fallback to L5
- [ ] Request L6 with 8K tokens → Tight fit warning
- [ ] Request L1 with 100 tokens → Error: minimum budget exceeded

**Deliverable**: Graceful degradation when token-constrained

---

## Phase 4: Integration & Refinement (1-2 Weeks)

### Goal: Full integration with Claude Code, testing, documentation

---

### 4.1 Create Query Library (Optional)

**What**: Pre-built examples for each level (LEVEL_1_GUIDE.md through LEVEL_7_GUIDE.md)

**Where**: `/Users/manu/Documents/LUXOR/PROJECTS/hekat/query-library/`

**Structure**:

```
query-library/
├── LEVEL_1_GUIDE.md    # L1 patterns: single-agent quick queries
├── LEVEL_2_GUIDE.md    # L2 patterns: 2-agent chains
├── LEVEL_3_GUIDE.md    # L3 patterns: 3-agent feature dev
├── LEVEL_4_GUIDE.md    # L4 patterns: parallel consensus
├── LEVEL_5_GUIDE.md    # L5 patterns: hierarchical architecture
├── LEVEL_6_GUIDE.md    # L6 patterns: iterative refinement
├── LEVEL_7_GUIDE.md    # L7 patterns: full ensemble
└── README.md           # Navigation guide
```

Each guide contains:
- Real DSL examples (with hotkey equivalents)
- Token budget breakdown
- Success rate from consciousness patterns
- When/how to use each pattern

**Optional Action**:
- [ ] Create LEVEL_1_GUIDE.md with 5-10 L1 examples
- [ ] Create LEVEL_7_GUIDE.md with 3-5 L7 examples
- [ ] Link from SKILL.md: "See query-library/ for detailed examples"

---

### 4.2 Add `/hekat --help` Reference Card

**What**: Printable hotkey reference and quick examples

**Implementation**: Extend hekat command with `--help` output

```bash
/hekat --help

╔═══════════════════════════════════════════════════════════╗
║           HEKAT Query Builder Quick Reference             ║
║                 Complexity L1-L7 Selection               ║
╚═══════════════════════════════════════════════════════════╝

TIER 1: SINGLE-KEY QUICK ACCESS (L1-L3)
  [R]esearch   [D]esign    [T]est     [B]uild    [F]rontend
  [I]mplement  [O]chestrate [S]ynthesize [C]ode-review

TIER 2: COMPLEXITY SELECTORS (Hold Ctrl)
  [Ctrl+P] → L4 Parallel      [Ctrl+H] → L5 Hierarchical
  [Ctrl+I] → L6 Iterative     [Ctrl+E] → L7 Ensemble

TIER 3: AGENT CHAINS
  [R>D>I]   Sequential (Research→Design→Implement)
  [P:R||D||A] Parallel (Research || Design || Analyze)
  [H:R+D→O]  Hierarchical (Research+Design → Orchestrate)

QUICK EXAMPLES:
  /hekat [R] "explain JWT"
    → L1: Single deep-researcher agent

  /hekat "design auth endpoint"
    → L3: auto-detect, suggests api-architect → practical-programmer → test-engineer

  /hekat [P] "compare databases"
    → L4: Parallel consensus from 2-3 agents

  /hekat @L5 "microservices architecture"
    → L5: Force hierarchical with approval gates

  /hekat --verbose "your query"
    → Show phase-by-phase token tracking

  /hekat --dry-run "your query"
    → Show execution plan without running

HOTKEY HEURISTICS:
  Quick answer?           Use [R] (L1, ~900 tokens)
  Two-step workflow?      Use [D], [I], [T] (L2, ~2000 tokens)
  Full feature?           Use [D>I>T] (L3, ~3500 tokens)
  Compare options?        Use [P] (L4, ~4500 tokens)
  Design system?          Use [H] (L5, ~7000 tokens)
  Fix & test?            Use [I] (L6, ~10K tokens)
  Build from scratch?    Use [E] (L7, ~18K tokens)

See: QUERY_BUILDER_SPECIFICATION.md for complete details
    hekat SKILL for examples and tutorials
    query-library/ for pattern library
```

**Deliverable**: Users never have to guess—help is clear and accessible

---

### 4.3 Write Integration Tests

**What**: Test suite to validate complexity classification, hotkey mapping, etc.

**Tests to create**:

```python
# test_hekat_classification.py

def test_l1_single_agent():
    result = hekat_classify("explain JWT")
    assert result["level"] == 1
    assert "deep-researcher" in result.get("recommended_agents", [])

def test_l3_feature_development():
    result = hekat_classify("build authentication endpoint")
    assert result["level"] == 3
    assert len(result.get("agents", [])) >= 2

def test_l4_parallel():
    result = hekat_classify("compare FastAPI vs Express")
    assert result["level"] == 4
    assert "parallel" in result.get("pattern", "").lower()

def test_l7_ensemble():
    result = hekat_classify("design and implement microservices platform")
    assert result["level"] == 7

def test_hotkey_r_maps_to_l1():
    result = hekat_hotkey("[R]")
    assert result["level"] == 1

def test_hotkey_ctrl_h_maps_to_l5():
    result = hekat_hotkey("[Ctrl+H]")
    assert result["level"] == 5

def test_token_constraint_fallback():
    result = hekat_classify("build platform", available_tokens=5000)
    assert result["level"] < 7  # Falls back from L7

def test_consciousness_learning():
    # Run query 5 times
    for _ in range(5):
        result = hekat_classify("auth design")

    # Verify pattern was created
    pattern = load_consciousness("auth_design")
    assert pattern["sample_count"] == 5
    assert pattern["success_rate"] > 0.0

def test_dsl_parser_inference():
    result = parse_dsl("deep-researcher : 'explain JWT'")
    assert result["level"] == 1

    result = parse_dsl("api-architect -> practical-programmer")
    assert result["level"] == 2

    result = parse_dsl("(agent_a || agent_b || agent_c)")
    assert result["level"] == 4
```

**Action Items**:
- [ ] Create `/Users/manu/Documents/LUXOR/PROJECTS/hekat/tests/test_hekat.py`
- [ ] Run tests, ensure all pass
- [ ] Add to CI/CD if applicable

---

### 4.4 Documentation & Tutorials

**What**: Write user-facing documentation

**Files to create**:

1. **HEKAT_QUICK_START.md** - Get started in 5 minutes
2. **HEKAT_TUTORIALS.md** - Step-by-step walkthroughs
3. **HEKAT_TROUBLESHOOTING.md** - FAQ and common issues
4. **Update CLAUDE.md** - Link to hekat documentation

**Example QUICK_START.md**:

```markdown
# HEKAT Quick Start (5 Minutes)

## What is HEKAT?

HEKAT automatically selects the right complexity level (L1-L7) for your task,
then orchestrates the optimal multi-agent workflow.

## Installation

HEKAT comes built-in. Just use it:

```bash
/hekat "your question or task"
```

## Examples

### Example 1: Quick Explanation (L1)
```bash
/hekat "explain OAuth 2.0"
→ deep-researcher explains the concept
```

### Example 2: Design & Build (L3)
```bash
/hekat "build authentication endpoint"
→ api-architect designs it
→ practical-programmer implements it
→ test-engineer verifies it
```

### Example 3: Compare Options (L4)
```bash
/hekat [P] "PostgreSQL vs MongoDB for our app"
→ Multiple perspectives analyze the tradeoffs
→ Consensus decision with confidence scores
```

### Example 4: Full Platform Design (L7)
```bash
/hekat @L7 "design production-ready microservices platform"
→ Parallel research from 4+ domain experts
→ Synthesis layer integrates findings
→ Implementation team builds architecture
→ Orchestrator coordinates everything
```

## Hotkey Cheat Sheet

```
[R] Research    [D] Design     [T] Test
[B] Build       [I] Implement  [P] Parallel
[Ctrl+H] L5 Hierarchical
[Ctrl+I] L6 Iterative
[Ctrl+E] L7 Ensemble
```

## Common Patterns

| Task | Command | Level |
|------|---------|-------|
| Explain concept | `/hekat [R] "..."` | L1 |
| Design then build | `/hekat [D>I>T] "..."` | L3 |
| Compare options | `/hekat [P] "..."` | L4 |
| Architecture | `/hekat [H] "..."` | L5 |
| Bug fix + tests | `/hekat [I] "..."` | L6 |
| Full project | `/hekat [E] "..."` | L7 |

## Token Budgets

System shows estimated tokens and keeps you under budget:

```bash
/hekat --verbose "design auth"
→ Est: 7200 tokens | Available: 40K | Status: ✅ Ready
```

## Next Steps

- Read: `hekat` SKILL for more details
- Browse: query-library/ for examples at each level
- Reference: QUERY_BUILDER_SPECIFICATION.md for complete spec
```

**Action Items**:
- [ ] Create HEKAT_QUICK_START.md
- [ ] Create HEKAT_TUTORIALS.md with 5-10 walkthroughs
- [ ] Create HEKAT_TROUBLESHOOTING.md
- [ ] Update ~/.claude/CLAUDE.md to mention hekat

---

## Phase 5: Ongoing Iteration (Continuous)

### Goal: Improve system based on real usage, refine level definitions, optimize token budgets

---

### 5.1 Monitor & Learn

**Monthly review**:
- [ ] Analyze consciousness patterns (which queries most common?)
- [ ] Review success rates (which levels performing best?)
- [ ] Identify misclassifications (queries assigned wrong level)
- [ ] Update token budgets (actual vs estimated)
- [ ] Refine trigger conditions based on real queries

**Example analysis**:

```yaml
monthly_analysis_2025_11:
  most_common_patterns:
    - pattern: "design * system"
      invocations: 45
      default_level: 5
      actual_success_rate: 0.92
      recommendation: "Keep at L5, very reliable"

    - pattern: "fix * bug"
      invocations: 12
      default_level: 6
      actual_success_rate: 0.75
      recommendation: "Consider L5 fallback, L6 sometimes overkill"

  token_budget_adjustments:
    L4: Actual avg 3200 vs est 4500 → Reduce to 3000-5000 ✓
    L6: Actual avg 10800 vs est 10000 → Increase to 9000-13000 ✓
    L7: Actual avg 16200 vs est 18000 → Reduce to 15000-20000 ✓

  misclassifications:
    - Query: "build microservice" → Classified L3, should L5
      Reason: "build" keyword, but "microservice" requires architecture
      Fix: Add "microservice" to L5 trigger keywords

    - Query: "fix memory leak" → Classified L6, success 100%
      Reason: Could use L5, wastes tokens
      Fix: Add "memory leak" to L5-triggering patterns with 95% confidence
```

---

### 5.2 Refine Level Definitions

**After 2-3 months of real usage**:
- [ ] Revisit L1-L7 definitions based on actual success rates
- [ ] Adjust agent counts per level (do we need 5 at L5, or can 4 work?)
- [ ] Refine token budgets based on real data
- [ ] Update query-library/ with best patterns from consciousness
- [ ] Document lessons learned

**Example refinement**:

```yaml
REFINEMENT_2025_12:
  L5_original:
    agents: 4-5
    token_budget: 5500-9000
    success_rate: 0.91

  L5_refined:
    agents: 4 (removed extra agent, was redundant)
    token_budget: 5000-8000 (reduced min, was conservative)
    success_rate: 0.92 (actually improved with better composition)
    rationale: "Leaner agent composition more efficient, consciousness patterns guide selection"
```

---

### 5.3 Add New Agents / Update Mappings

**As new agents become available**:
- [ ] Update hotkey matrix to include new agents
- [ ] Reassess L1-L7 compositions
- [ ] Test classifications with new agent combinations
- [ ] Update consciousness to track new agent performance

---

## Success Metrics

How to know Phase N is complete:

**Phase 1 Success**:
- [ ] `/hekat --help` shows hotkey reference
- [ ] `/hekat "simple query"` classifies to L1
- [ ] `/actualize` shows: Commands: 43, Skills: 76, Agents: 35

**Phase 2 Success**:
- [ ] `/hekat "design auth"` suggests L5 with reasoning
- [ ] `/hekat [D>I>T]` recognizes chain syntax
- [ ] `/hekat --verbose` shows token tracking
- [ ] User tests confirm ~90% accuracy of level classification

**Phase 3 Success**:
- [ ] `/hekat "auth"` (second time) suggests L5 based on history
- [ ] Consciousness file has 50+ invocations with patterns
- [ ] DSL parser handles all 7 complexity levels
- [ ] Fallback mechanism tested with token constraints

**Phase 4 Success**:
- [ ] All tests pass (100% test coverage for core logic)
- [ ] Documentation complete (QUICK_START, TUTORIALS, TROUBLESHOOTING)
- [ ] User feedback positive (system works intuitively)
- [ ] Integration with Claude Code smooth (no conflicts)

**Phase 5 Success** (Ongoing):
- [ ] Monthly consciousness analysis shows learning
- [ ] Token budgets converging to reality
- [ ] <5% misclassification rate
- [ ] Success rates consistently >85% per level

---

## Implementation Checklist

Use this to track progress:

```markdown
## Phase 1: Foundation ✅
- [ ] Create `/hekat` command
- [ ] Create `hekat` skill
- [ ] Create `hekat-agent` agent definition
- [ ] Create consciousness storage file
- [ ] Sync to project
- [ ] Run `/actualize`

## Phase 2: Core ⏳
- [ ] Implement complexity classification
- [ ] Implement hotkey matrix
- [ ] Implement token tracking display
- [ ] Test L1-L7 classification
- [ ] Test hotkey mapping
- [ ] Test token constraint handling

## Phase 3: Advanced ⏳
- [ ] Implement consciousness pattern matching
- [ ] Implement DSL parser
- [ ] Implement fallback mechanism
- [ ] Test learning (second query suggests L5)
- [ ] Test DSL syntax parsing
- [ ] Test token constraint fallback

## Phase 4: Integration ⏳
- [ ] Create query library (optional)
- [ ] Create `/hekat --help` reference
- [ ] Write integration tests
- [ ] Write QUICK_START.md
- [ ] Write TUTORIALS.md
- [ ] Write TROUBLESHOOTING.md
- [ ] Update CLAUDE.md

## Phase 5: Iteration 🔄
- [ ] Monthly consciousness review
- [ ] Update token budgets
- [ ] Refine level definitions
- [ ] Analyze success rates
- [ ] Document lessons learned
```

---

## How to Modify & Extend

### To Change Agent Composition at L5:

1. **Edit**: `~/.claude/skills/hekat/SKILL.md`
   - Change L5 example agents
   - Update description of what L5 does

2. **Edit**: `~/.claude/agents/hekat-agent/agent.yaml`
   - Update L5 agent recommendations

3. **Edit**: `/Users/manu/Documents/LUXOR/PROJECTS/hekat/QUERY_BUILDER_SPECIFICATION.md`
   - Update Part 1 "L5: Hierarchical Multi-Stage" section
   - Update token budget if composition changes

4. **Test**:
   - Run `/hekat @L5 "design system"` and verify agents
   - Run tests to ensure classification still works

5. **Document**:
   - Update query-library/LEVEL_5_GUIDE.md with new patterns
   - Update consciousness schema if tracking new data

---

### To Add New Hotkey:

1. **Edit**: Hotkey matrix in `~/.claude/commands/hekat.md`
2. **Edit**: Hotkey matrix in QUERY_BUILDER_SPECIFICATION.md Part 2
3. **Implement**: Update hekat command hotkey lookup logic
4. **Test**: Verify new hotkey maps to correct level/agents
5. **Document**: Update `/hekat --help` reference card

---

### To Introduce New Level (e.g., L8 for mega-ensemble):

1. **Edit**: QUERY_BUILDER_SPECIFICATION.md
   - Add L8 section (Part 1)
   - Update hotkey matrix (Part 2)

2. **Edit**: hekat skill
   - Document L8 use case

3. **Implement**:
   - Update TOKEN_BUDGETS dict
   - Update classify_complexity() keyword rules
   - Add L8 DSL patterns

4. **Test**: Ensure L8 classification works

5. **Document**: Create query-library/LEVEL_8_GUIDE.md

---

## Next Immediate Actions (What To Do Monday)

After reading this document:

1. **Phase 1 Quick Start** (1-2 hours):
   ```bash
   # Create basic structures
   mkdir -p ~/.claude/skills/hekat ~/.claude/agents/hekat-agent

   # Create command
   cat > ~/.claude/commands/hekat.md << EOF
   [paste hekat command content from Phase 1.1]
   EOF

   # Create skill
   cat > ~/.claude/skills/hekat/SKILL.md << EOF
   [paste skill content from Phase 1.2]
   EOF

   # Create agent config
   cat > ~/.claude/agents/hekat-agent/agent.yaml << EOF
   [paste agent config from Phase 1.3]
   EOF

   # Create consciousness storage
   cat > ~/.claude/hekat-consciousness.yaml << EOF
   [paste consciousness schema from Phase 1.4]
   EOF

   # Sync
   /actualize
   ```

2. **Test It Works** (30 min):
   ```bash
   /hekat --help                          # Should show usage
   /hekat "explain JWT"                   # Should output something
   /crew hekat-agent                      # Should find agent
   ```

3. **Start Phase 2** (complexity classification):
   - Use hekat-agent to design classification algorithm
   - Implement in hekat command
   - Test with L1-L7 examples

---

## Questions to Refine

As you work through this, you can refine:

1. **Hotkey Naming**: Are TIER 1-3 naming clear? Alternative suggestions?
2. **Token Budgets**: Do ranges seem realistic after first usage?
3. **Consciousness Schema**: Missing anything important to track?
4. **Level Definitions**: After 10-20 real invocations, do levels feel right?
5. **Fallback Mechanism**: Is interactive menu clear, or too much?
6. **DSL Syntax**: Need to add operators or simplify?
7. **Trigger Keywords**: Which keywords are most important?

Document your answers in IMPLEMENTATION_NOTES.md as you go.

---

## Summary

You now have:

✅ **Complete specification** (QUERY_BUILDER_SPECIFICATION.md) - what to build
✅ **Implementation roadmap** (this file) - how to build it step-by-step
✅ **Success metrics** - how to know you're done
✅ **Extension guide** - how to modify and improve

**Next step**: Read QUERY_BUILDER_SPECIFICATION.md to understand the design deeply, then start Phase 1 to get the basic command/skill/agent working.

The system will improve with use. Start simple, iterate fast, learn from consciousness patterns.

Good luck! 🚀
