# HEKAT Query Builder: System Synthesis & Improvement Guide

**Status**: ✅ Complete Design Unified → Ready for Iterative Improvement
**Date**: 2025-10-27
**Purpose**: Detailed summary of what was built + pathways to modify/improve skills, agents, commands

---

## 🎯 Executive Summary

The HEKAT Query Builder convergence session unified three research streams into a **production-ready complexity-aware orchestration system**:

1. **Comonadic Memory Models** → Token-disciplined context distribution
2. **Hekat DSL Research** → L1-L7 complexity spectrum with agent compositions
3. **Mercurio Synthesis** → TIER hotkey system + consciousness pattern learning

**Result**: A system where users can request multi-agent workflows at 7 complexity levels, with automatic classification, token tracking, and learning capabilities.

---

## Part 1: What Was Built

### 1.1 Complete Architecture (Converged)

The convergence session produced a **unified specification** combining:

#### A. Comonadic Foundation
From `hekat/comonad/ORCHESTRATION_PATTERNS.md`:
- **Pattern 1**: Sequential (L1-L3)
  - Simple: A→B→C with extract/compress at each step
  - Token cost: Extract (20%), Compress (15%), Agent work (65%)
  - Example: Research→Design→Implement

- **Pattern 2**: Parallel Consensus (L4)
  - Multiple agents duplicate context, parallel execution, smart merge
  - Token cost: Duplicate (30%), Agents (50%), Consensus (20%)
  - Example: Design decision with 3-agent consensus

- **Pattern 3**: Hierarchical with Gates (L5)
  - Lead agent → parallel approval stage → synthesis
  - Token cost: Lead (20%), Parallel (40%), Synthesis (40%)
  - Example: Architecture with senior + junior team review

- **Pattern 4**: Iterative Refinement (L6)
  - Loop: A→B→Evaluate→Feedback→Refine→Synthesize
  - Token cost: Per loop (25-30%), growing with iterations
  - Example: Code design→implement→test→review→refactor

- **Pattern 5**: Full Ensemble (L7)
  - Combination: Sequential + Parallel + Hierarchical + Iterative
  - Token cost: Streaming setup (20%), Core work (60%), Synthesis (20%)
  - Example: Major architectural redesign across 7+ agents

#### B. Hekat DSL Specification
From agent analysis:
- **L1-L7 Complexity Spectrum** with:
  - Agent compositions per level
  - Token budgets (validated against comonad examples)
  - Hotkey assignments (TIER 1-3)
  - Trigger conditions (what inputs activate each level)
  - Real DSL examples for each level

#### C. Mercurio Integration
From orchestrator synthesis:
- **TIER Hotkey System** (progressive disclosure)
- **Smart query classification algorithm**
- **Consciousness pattern matching** (learning system)
- **Token tracking display formats**
- **Fallback mechanisms** (graceful degradation)

### 1.2 Documentation Generated

**Total**: 15,000+ lines across 5 core documents

#### QUERY_BUILDER_SPECIFICATION.md (7000+ lines)
**What it contains**:
- Part 1: L1-L7 definitions with complete details
  - Agent count, composition, hotkeys
  - Token budgets with breakdown
  - Context distribution model
  - Trigger conditions
  - Real DSL examples
- Part 2: TIER Hotkey System architecture
  - Tier 1 (11 single keys): [R][D][T][B][F][I][O][S][C][P][V][A]
  - Tier 2 (5 Ctrl-modifiers): [Ctrl+P][Ctrl+H][Ctrl+I][Ctrl+E][Ctrl+F]
  - Tier 3 (agent chains): [R>D>I][P:R||D||A]
- Part 3: Smart query selection algorithm
  - Keyword detection (30 keywords per level)
  - Consciousness pattern matching
  - Token budget constraints
  - DSL syntax parsing
- Part 4: Token tracking displays
  - Clean default format
  - Verbose phase-by-phase breakdown
  - Budget vs actual comparison
  - Variance monitoring
- Part 5: Consciousness schema
  - Query storage format
  - Pattern extraction algorithm
  - Success rate calculation
  - Learning feedback mechanism
- Part 6: Fallback mechanisms
  - Interactive UI when insufficient tokens
  - Graceful degradation (suggest lower level)
  - User choice preservation

**How to use it**: Technical reference for implementation. Parts 1 & 3 are most essential.

#### IMPLEMENTATION_ROADMAP.md (4000+ lines)
**What it contains**:
- **Phase 1: Foundation** (2 hours)
  - Create ~/.claude/commands/hekat.md
  - Create ~/.claude/skills/hekat/SKILL.md
  - Create ~/.claude/agents/hekat-agent/agent.yaml
  - Create ~/.claude/hekat-consciousness.yaml
  - Run /actualize
  - Result: `/hekat` is callable

- **Phase 2: Core Implementation** (1-2 weeks)
  - Implement complexity classification
  - Implement hotkey lookup
  - Implement token tracking display
  - Write unit tests
  - Result: `/hekat "query"` → L1-L7 with confidence

- **Phase 3: Advanced Features** (2-3 weeks)
  - Implement consciousness pattern matching
  - Implement DSL parser
  - Implement fallback mechanism
  - Test learning cycle
  - Result: System learns from use

- **Phase 4: Integration & Testing** (1-2 weeks)
  - Query library (optional)
  - User documentation
  - Comprehensive testing
  - Production deployment

- **Phase 5: Continuous Iteration** (ongoing)
  - Monthly consciousness analysis
  - Token budget optimization
  - Trigger refinement

**How to use it**: Step-by-step build guide. Includes code examples and checklists.

#### TIER_HOTKEY_REFERENCE.md (2000+ lines)
**What it contains**:
- Hotkey matrices (all 16 keys + combos)
- Mnemonic meanings (why R=Research, etc.)
- Decision trees (how to pick hotkey)
- Printable reference cards
- Test cases and examples

**How to use it**: Quick lookup while implementing hotkey system. Use for Phase 2.

#### README_DOCUMENTATION.md (1500+ lines)
**What it contains**:
- Architecture overview diagram
- Quick start guide (5 minutes)
- Common tasks and how-tos
- Modification guide
- Troubleshooting

**How to use it**: Entry point for new users. Links to detailed documentation.

#### INDEX.md (you just read this)
**What it contains**:
- File navigation map
- What was built section
- Next steps
- FAQ
- Learning paths

**How to use it**: Jump to other files as needed.

### 1.3 Key Design Artifacts

#### Token Budget Matrices
```
L1: 600-1200       L2: 1500-3000    L3: 2500-4500
L4: 3000-6000      L5: 5500-9000    L6: 8000-12000
L7: 12000-22000
```
✅ Validated against comonad examples
✅ Proportional to orchestration complexity
✅ No overlaps or gaps

#### Agent Compositions
```
L1: single-agent only
L2: agent-A → agent-B
L3: agent-A → agent-B → agent-C
L4: 2-3 agents in parallel with consensus
L5: lead-agent → (agent-B || agent-C || agent-D) → synthesis
L6: feedback loop with 4-6 agents
L7: streaming + parallel + hierarchical + iterative (7+)
```
✅ Maps to comonadic patterns
✅ Cognitive load increases with level
✅ Each improves on previous

#### Consciousness Schema
```yaml
query_record:
  id: unique_id
  input: user's natural language query
  detected_level: L1-L7 (auto-detected)
  user_override: optional @Ln override
  agents_used: [list of agents]
  tokens_estimated: budgeted
  tokens_actual: observed
  success_rate: 0.0-1.0 (user feedback)
  timestamp: when executed

pattern:
  cluster_key: hash(keywords + level)
  frequency: count of similar queries
  success_rate: mean of success_rates
  recommended_level: most successful level
  alternative_levels: [second choice, third choice]
  learned_confidence: increases with samples
```
✅ Enables machine learning over time
✅ Tracks what works in practice
✅ Improves suggestions with use

#### Hotkey Tier System
```
TIER 1 (Simple)
  [R]esearch [D]esign [T]est [B]uild [F]rontend [I]mplement
  [O]rchestrate [S]ynthesize [C]ode-review [P]arallel [V]erify [A]nalyze
  → L1-L3 triggered by single key

TIER 2 (Power User)
  [Ctrl+P] L4 Parallel     [Ctrl+H] L5 Hierarchical
  [Ctrl+I] L6 Iterative     [Ctrl+E] L7 Ensemble
  [Ctrl+F] L5 Frontend-specific
  → Force specific level

TIER 3 (Advanced)
  [R>D>I] Research → Design → Implement chain
  [P:R||D||A] Parallel: Research, Design, Analyze
  [I:D→P→T] Iterative: Design → (Parallel run) → Test
  → Explicit DSL chains
```
✅ Scales from novice (TIER 1) to expert (TIER 3)
✅ No cognitive overload at any level
✅ Natural progression

---

## Part 2: Architecture Analysis

### 2.1 System Flow

```
User Input
    ↓
/hekat Command Entry Point
    ├─ Parse input
    │   ├─ Detect hotkey? (TIER 1 single key)
    │   ├─ Detect override? (@L5 prefix)
    │   ├─ Detect DSL? (A->B->C syntax)
    │   └─ Natural language query?
    ├─ Classify complexity (Algorithm)
    │   ├─ Keyword detection (30 keywords per level)
    │   ├─ Consciousness pattern match (historical)
    │   ├─ Token budget check (available < required?)
    │   └─ Return suggested level L1-L7
    ├─ Display suggestion
    │   ├─ "Selected: L5 Hierarchical (est 7200 tokens) ✅"
    │   └─ Optional: --verbose shows phase breakdown
    └─ Get user confirmation
        ├─ User accepts → Execute
        ├─ User overrides → Downgrade/upgrade
        └─ User cancels → Abort

    ↓
hekat-Agent (CLASSIFICATION)
    ├─ Parse decision input
    ├─ Determine exact level (1-7)
    ├─ Select appropriate agent composition
    └─ Return execution plan

    ↓
Task-Relay Orchestration (EXECUTION)
    ├─ Sequential (L1-L3)
    │   └─ A → B → C with extracts
    ├─ Parallel Consensus (L4)
    │   └─ (A || B || C) → Consensus
    ├─ Hierarchical (L5)
    │   └─ Lead → (B || C || D) → Synthesis
    ├─ Iterative (L6)
    │   └─ Loop: A → B → Eval → Feedback → Refine
    └─ Full Ensemble (L7)
        └─ Streaming + Parallel + Hierarchical + Iterative

    ↓
Token Tracking (MONITORING)
    ├─ Record phase-by-phase tokens
    ├─ Compare to budget
    ├─ Calculate variance
    └─ Warn if approaching limit

    ↓
Consciousness Learning (IMPROVEMENT)
    ├─ Record: query → level → agents → tokens → success
    ├─ Cluster: group similar queries
    ├─ Learn: success rates per pattern
    └─ Improve: future suggestions get smarter

    ↓
Display Results
    └─ Clean output (or verbose breakdown if requested)
```

### 2.2 Component Dependencies

```
/hekat Command
    ↓
hekat-Agent (intelligence)
    ├─ Uses: TIER Hotkey System
    ├─ Uses: Classification Algorithm
    ├─ Uses: Consciousness Schema
    └─ Uses: Token Budget Matrix

Task-Relay Orchestration
    ├─ Uses: 34 existing Claude Code agents
    ├─ Uses: Comonadic patterns (context distribution)
    └─ Uses: Task-relay checkpoint discipline

Token Tracking Module
    ├─ Uses: Task-Relay token accounting
    └─ Uses: Display formats

Consciousness Learning
    ├─ Reads: hekat-consciousness.yaml (persistent store)
    ├─ Writes: Updated patterns and success rates
    └─ Uses: Query classification

hekat Skill
    ├─ Documents: When to use hekat
    ├─ Documents: How TIER hotkeys work
    ├─ Documents: L1-L7 complexity spectrum
    └─ References: QUERY_BUILDER_SPECIFICATION.md
```

### 2.3 Data Flow

```
Input: User types /hekat "design auth system"
   ↓
Parse: Extract keywords: ["design", "auth", "system"]
   ↓
Classify:
   ├─ Keyword match: "design" → typically L5
   ├─ Query complexity: Multi-step architectural → L5
   ├─ Consciousness check: Similar past queries → L5 success rate 85%
   ├─ Token check: Available 10K, L5 needs 7-9K → OK ✓
   └─ Decision: L5 Hierarchical (confidence 92%)
   ↓
Plan: Select agents
   ├─ Lead: api-architect
   ├─ Parallel: [practical-programmer, frontend-architect, test-engineer]
   ├─ Synthesis: project-orchestrator
   └─ Est tokens: 7800 / 10000 budget
   ↓
Display: "Selected: L5 Hierarchical (est 7800 tokens, 92% confidence) ✅"
   ↓
Execute: Task-Relay with hierarchical pattern
   ├─ Phase 1: api-architect leads design
   ├─ Phase 2: Parallel implement/test/frontend review
   ├─ Phase 3: Synthesize results
   └─ Track tokens: [+2100, +2400, +2100, +1200] = 7800 actual
   ↓
Learn:
   ├─ Record: query, L5, agents, 7800 tokens, success=100%
   ├─ Cluster: Similar to 5 past "design" queries
   ├─ Update: Pattern success_rate = (85%*5 + 100%*1) / 6 = 92%
   └─ Next time: Suggest L5 with 92% confidence
   ↓
Return: Results + confidence metrics
```

---

## Part 3: Improvement Pathways

### 3.1 Skills Modification

**Location**: `~/.claude/skills/hekat/SKILL.md`

#### Pathway A: Add New Complexity Level (L0 or L8)

**Step 1**: Understand existing structure
```
Read: QUERY_BUILDER_SPECIFICATION.md Part 1 → Choose level to add
Read: IMPLEMENTATION_ROADMAP.md → How to extend
```

**Step 2**: Define new level
```yaml
# Example: L0 (ultra-minimal, single keyword)
L0:
  name: "Instant Answer"
  agents: 1 (specialized expert only)
  token_budget: 300-600
  pattern: "Direct lookup"
  hotkey: "[?]" or maybe just auto-detect
  trigger: Single noun (e.g., "JWT", "Docker")
  example: /hekat "PostgreSQL" → Lists top 3 facts
```

**Step 3**: Update documentation
```
Files to modify:
1. ~/.claude/skills/hekat/SKILL.md → Add L0 to "Complexity Levels"
2. QUERY_BUILDER_SPECIFICATION.md Part 1 → Add L0 definition
3. TIER_HOTKEY_REFERENCE.md → Update hotkey matrices
4. IMPLEMENTATION_ROADMAP.md → Add L0 to classification algorithm
```

**Step 4**: Implement classification logic
```python
# In Phase 2 implementation
if len(query.split()) == 1 and len(query) < 15:
    return Level.L0  # Instant answer
```

**Step 5**: Test and document
```
Test cases:
  /hekat "JWT" → L0
  /hekat "Docker" → L0
  /hekat "authentication" → L0
  /hekat "design authentication" → L3 (not L0)
```

#### Pathway B: Modify Agent Composition at Specific Level

**Step 1**: Understand current level
```
Read: QUERY_BUILDER_SPECIFICATION.md → Find L5 definition
Read: IMPLEMENTATION_ROADMAP.md Phase 2.2 → Agent selection code
```

**Example**: Change L5 from:
```
Lead: api-architect
Parallel: [practical-programmer, frontend-architect, test-engineer]
Synthesis: project-orchestrator
```

To:
```
Lead: deep-researcher (research first)
Parallel: [api-architect, practical-programmer, frontend-architect]
Synthesis: mercurio-orchestrator (better synthesis)
```

**Step 2**: Update documentation
```
Files to modify:
1. QUERY_BUILDER_SPECIFICATION.md Part 1 → L5 agent composition
2. ~/.claude/skills/hekat/SKILL.md → L5 description
3. TIER_HOTKEY_REFERENCE.md → L5 example
```

**Step 3**: Implement code change
```python
if level == Level.L5:
    return AgentComposition(
        lead_agent='deep-researcher',
        parallel_agents=['api-architect', 'practical-programmer', 'frontend-architect'],
        synthesis_agent='mercurio-orchestrator'
    )
```

**Step 4**: Test with real queries
```
Test case: /hekat @L5 "design authentication system"
Expected: deep-researcher leads, then 3 parallel agents, merges
```

#### Pathway C: Add New Keywords/Triggers

**Step 1**: Understand trigger structure
```
Read: QUERY_BUILDER_SPECIFICATION.md Part 3 → Trigger conditions
```

Current structure:
```yaml
L3:
  keywords:
    - "design ...", "build ...", "implement ..."
    - "create ...", "develop ...", "write ..."
  patterns:
    - "[noun] [design/build]" → L3
```

**Step 2**: Add new trigger
```yaml
# Example: Add "refactor" as L6 trigger
L6:
  keywords:
    - "refactor ...", "optimize ...", "improve ..."
    - "clean up ...", "restructure ..."
```

**Step 3**: Update files
```
Files to modify:
1. QUERY_BUILDER_SPECIFICATION.md Part 3 → Add "refactor" to L6 keywords
2. hekat/SKILL.md → Update trigger examples
3. IMPLEMENTATION_ROADMAP.md Phase 2.1 → Update keyword detection code
```

**Step 4**: Implement
```python
if any(word in query for word in ['refactor', 'optimize', 'improve']):
    return Level.L6
```

**Step 5**: Test
```
/hekat "refactor the authentication module" → Should suggest L6
```

#### Pathway D: Change Token Budgets

**Step 1**: Analyze current budgets
```
Current: L5 = 5500-9000 tokens
Question: Why this range? Is it realistic?
```

**Step 2**: Validate against comonad patterns
```
Read: hekat/comonad/ORCHESTRATION_PATTERNS.md
Pattern 3 (Hierarchical) token costs:
  - Lead agent: 20% of budget
  - Parallel execution: 40% of budget
  - Synthesis: 40% of budget

If L5 = 8000 tokens:
  - Lead (api-architect): ~1600 tokens
  - Parallel 3 agents: ~3200 tokens
  - Synthesis (project-orchestrator): ~3200 tokens
  ✅ Realistic
```

**Step 3**: Update budget
```yaml
Old: L5: 5500-9000
New: L5: 6000-10000  # More generous for synthesis
```

**Step 4**: Update documentation
```
Files to modify:
1. QUERY_BUILDER_SPECIFICATION.md Part 1 → L5 token budget
2. TIER_HOTKEY_REFERENCE.md → Token matrices
3. IMPLEMENTATION_ROADMAP.md → Classification algorithm (constraints)
```

**Step 5**: Test
```
Query with 10,000 token limit:
  /hekat "design auth" → L5 (6-10K used, still in budget)
  /hekat "refactor everywhere" → L6 or lower (larger query)
```

### 3.2 Agent Modifications

**Location**: `~/.claude/agents/hekat-agent/agent.yaml`

#### Pathway A: Enhance Classification Algorithm

**Current algorithm** (simplified):
```python
def classify_complexity(query):
    keywords = extract_keywords(query)
    base_level = keyword_detection(keywords)
    consciousness_level = pattern_matching(query)

    # Use consciousness if available and recent
    if consciousness_level and recency > 7_days:
        return consciousness_level
    return base_level
```

**Enhancement 1**: Add semantic similarity
```python
def classify_complexity(query):
    embeddings = get_query_embedding(query)  # Use Claude embeddings

    for level in [L7, L6, L5, L4, L3, L2, L1]:
        for pattern in level.patterns:
            similarity = cosine_similarity(embeddings, pattern.embedding)
            if similarity > 0.85:
                return level

    # Fallback to keyword detection
    return keyword_detection(extract_keywords(query))
```

**Step to implement**:
1. Read: QUERY_BUILDER_SPECIFICATION.md Part 3 (algorithm)
2. Modify: hekat-agent to use embeddings
3. Test: `/hekat "create a todo app"` should classify as L3-L4
4. Document: Update IMPLEMENTATION_ROADMAP.md Phase 2.1

#### Pathway B: Add Fallback Refinement

**Current fallback**:
```
User requests L7 (20K tokens)
Available: 5K tokens
System: Suggests L4 instead
```

**Enhanced fallback**:
```
User requests L7 (20K tokens)
Available: 5K tokens
System:
  - Suggest L4 (parallel consensus, 4-5K) ← best match
  - BUT also suggest: "Split into 2 sequential L3s?"
    ✓ Option A: First L3 for design, then L3 for implementation
    ✓ Option B: Use L4 now, continue with remaining tokens
```

**To implement**:
1. Read: QUERY_BUILDER_SPECIFICATION.md Part 6 (fallback)
2. Enhance: hekat-agent to suggest split approaches
3. Test: Request L7 with 6K budget
4. Document: Update IMPLEMENTATION_ROADMAP.md Phase 3

#### Pathway C: Improve Consciousness Learning

**Current learning**:
```
Record successful query → Calculate pattern match
Update success_rate
```

**Enhanced learning**:
```
Record successful query → Analyze what worked
├─ Which agents actually provided value?
├─ Did we use all agents or only some?
├─ What was the actual vs estimated token cost?
├─ Did synthesis actually improve result?
└─ Could we have used lower level?

Update pattern with insights:
├─ success_rate (global)
├─ agent_effectiveness (per-agent)
├─ optimal_level (empirically best)
└─ alternative_paths (secondary options)
```

**To implement**:
1. Read: QUERY_BUILDER_SPECIFICATION.md Part 5 (consciousness schema)
2. Enhance: Agent feedback collection mechanism
3. Add: Agent-level effectiveness metrics
4. Test: Second similar query gets better recommendations
5. Document: IMPLEMENTATION_ROADMAP.md Phase 3

### 3.3 Command Enhancements

**Location**: `~/.claude/commands/hekat.md`

#### Pathway A: Add Subcommands

**Current**:
```
/hekat <query>
/hekat @L5 <query>
/hekat --verbose <query>
/hekat --help
```

**Enhanced**:
```
/hekat <query>                    # Auto-detect
/hekat @L5 <query>               # Force level
/hekat --verbose <query>          # Show breakdown
/hekat --help                     # Show hotkeys

# New subcommands:
/hekat --history                  # Show past queries
/hekat --pattern <keyword>        # Show patterns for keyword
/hekat --learn <query> <feedback> # Provide feedback
/hekat --stats                    # Show consciousness stats
/hekat --reset-consciousness      # Clear learning (for testing)
```

**To implement**:
1. Update: ~/.claude/commands/hekat.md
2. Update: hekat-agent to handle subcommands
3. Test: `/hekat --history` shows last 10 queries
4. Test: `/hekat --pattern "design"` shows learned patterns
5. Document: Update hekat/SKILL.md with examples

#### Pathway B: Add Interactive Mode

**Current**:
```
/hekat "query" → Suggests level → Execute
```

**Interactive mode**:
```
/hekat --interactive
→ Prompt: "What do you want to do?"
→ User: "Design authentication"
→ System: "L5 Hierarchical suggested (89% confidence)"
→ Prompt: "Which agents? (Y/N for defaults, or [R]esearch/[D]esign/etc)"
→ User: Picks agents
→ System: Shows final plan
→ Prompt: "Execute? (Y/N)"
```

**To implement**:
1. Design: Interactive UI flow
2. Update: hekat-agent to support interactive mode
3. Test: `/hekat --interactive`
4. Document: New command in hekat/SKILL.md

#### Pathway C: Add Query Library

**Current**:
```
No pre-built queries
```

**Enhanced**:
```
/hekat --library
→ Shows categories:
   ├─ [1] API Design (5 templates)
   ├─ [2] Testing Strategies (8 templates)
   ├─ [3] Debugging (6 templates)
   ├─ [4] Refactoring (7 templates)
   └─ [5] Documentation (4 templates)

/hekat --library api
→ Shows 5 pre-built API design queries
→ User selects one
→ System customizes and runs
```

**To implement**:
1. Create: hekat/query-library/LEVEL_*.md files
2. Update: hekat-agent to match user input to library
3. Test: `/hekat --library api`
4. Document: LEVEL_GUIDES in query-library/

---

## Part 4: Step-by-Step Improvement Plan

### Phase A: Foundation Improvements (Week 1)

**Goal**: Core system callable and working

1. **Create Phase 1 files** (2 hours)
   - ~/.claude/commands/hekat.md
   - ~/.claude/skills/hekat/SKILL.md
   - ~/.claude/agents/hekat-agent/agent.yaml
   - ~/.claude/hekat-consciousness.yaml
   - Run `/actualize`

2. **Implement Phase 2** (1 week)
   - Classification algorithm (keyword detection)
   - Hotkey lookup
   - Token tracking display
   - Basic tests

3. **Success metrics**:
   - [ ] `/hekat --help` works
   - [ ] `/hekat "explain JWT"` classifies to L1
   - [ ] `/hekat "design auth"` classifies to L5
   - [ ] `/hekat @L3 "explain"` forces L3
   - [ ] `/hekat --verbose "query"` shows tokens

### Phase B: Learning Improvements (Week 2-3)

**Goal**: System learns from use

1. **Implement consciousness pattern matching**
   - Store query → level → success mapping
   - Calculate pattern clusters
   - Improve recommendations

2. **Implement DSL parser**
   - Parse `A -> B -> C` syntax
   - Parse `(A || B || C)` parallel syntax
   - Parse `I:A -> (B || C)` iterative syntax

3. **Success metrics**:
   - [ ] System remembers successful queries
   - [ ] `/hekat "design X"` suggests L5 based on history
   - [ ] `/hekat "A -> B -> C"` parses and executes chain
   - [ ] Learning improves over 10 queries

### Phase C: Advanced Improvements (Week 4+)

**Goal**: Production ready with bells & whistles

1. **Add new levels or modify existing ones**
   - Evaluate if L0 or L8 needed
   - Optimize agent compositions
   - Refine token budgets based on actual usage

2. **Add command enhancements**
   - Subcommands (--history, --stats, etc.)
   - Interactive mode
   - Query library

3. **Add fallback refinement**
   - Split complex queries
   - Suggest alternative approaches
   - Learn which fallbacks work best

4. **Success metrics**:
   - [ ] All subcommands work
   - [ ] Interactive mode available
   - [ ] Query library has 20+ templates
   - [ ] Consciousness stats show learning
   - [ ] No user needs >L7

---

## Part 5: Quick Reference for Modifications

### Where to Make Changes

| What You Want to Do | Primary File | Supporting Files |
|---|---|---|
| Add new level (L0 or L8) | QUERY_BUILDER_SPECIFICATION.md | hekat.md, TIER_HOTKEY_REFERENCE.md |
| Change L5 agents | QUERY_BUILDER_SPECIFICATION.md Part 1 | hekat-agent/agent.yaml, hekat/SKILL.md |
| Add new keyword trigger | QUERY_BUILDER_SPECIFICATION.md Part 3 | hekat-agent/agent.yaml, IMPLEMENTATION_ROADMAP.md |
| Modify token budgets | QUERY_BUILDER_SPECIFICATION.md Part 1 | TIER_HOTKEY_REFERENCE.md, hekat-agent/agent.yaml |
| Enhance classification algorithm | IMPLEMENTATION_ROADMAP.md Phase 2.1 | hekat-agent/agent.yaml |
| Add consciousness learning | QUERY_BUILDER_SPECIFICATION.md Part 5 | hekat-agent/agent.yaml, IMPLEMENTATION_ROADMAP.md Phase 3 |
| Add new hotkey | TIER_HOTKEY_REFERENCE.md | hekat/SKILL.md, QUERY_BUILDER_SPECIFICATION.md Part 2 |
| Add subcommand | ~/.claude/commands/hekat.md | hekat-agent/agent.yaml, hekat/SKILL.md |
| Improve fallback | QUERY_BUILDER_SPECIFICATION.md Part 6 | hekat-agent/agent.yaml, IMPLEMENTATION_ROADMAP.md Phase 3 |
| Create query library | hekat/query-library/*.md | hekat-agent/agent.yaml, hekat/SKILL.md |

### Pattern: Making a Modification

1. **Identify**: What do you want to change?
2. **Read**: Find the relevant section in documentation
3. **Understand**: Why was it designed this way?
4. **Modify**: Change the documentation first
5. **Implement**: Update code/config files
6. **Test**: Create test cases
7. **Verify**: Check all references are updated
8. **Document**: Update IMPLEMENTATION_NOTES.md

### Example: Add "optimize" keyword → L6 trigger

**Step 1-2**: Identify & Read
```
Want: Add "optimize" as L6 keyword
Read: QUERY_BUILDER_SPECIFICATION.md Part 3 → L6 triggers
```

**Step 3**: Understand
```
L6 is iterative (loop with refinement)
"Optimize" implies iteration: measure → improve → remeasure
Good fit for L6 ✓
```

**Step 4-5**: Modify & Implement
```
Files to change:
1. QUERY_BUILDER_SPECIFICATION.md
   L6 triggers:
   keywords:
     - "refactor ...", "optimize ..."  ← ADD HERE
     - "improve ...", "enhance ..."

2. IMPLEMENTATION_ROADMAP.md Phase 2.1
   if any(word in query for word in ['refactor', 'optimize']):
       return Level.L6

3. hekat/SKILL.md
   "optimize ..." → typically L6 (iterative refinement)
```

**Step 6**: Test
```
Test cases:
  /hekat "optimize database queries" → L6 ✓
  /hekat "optimize everything" → L6 ✓
  /hekat "is this optimized?" → L1 (not a request)
```

**Step 7**: Verify
```
Check all files updated:
  ✓ QUERY_BUILDER_SPECIFICATION.md
  ✓ IMPLEMENTATION_ROADMAP.md
  ✓ hekat/SKILL.md
  ✓ Test cases added
```

**Step 8**: Document
```
In IMPLEMENTATION_NOTES.md:
Date: 2025-10-28
Change: Added "optimize" as L6 keyword trigger
Reason: "Optimize" implies iterative improvement
Impact: Queries with "optimize" now suggest L6
Tests: 3 test cases passing
```

---

## Part 6: Success Metrics

### How to Know Your Improvements Are Working

#### Classification Accuracy
```
Goal: 90%+ accuracy on L1-L7 classification
Measure:
  - Create 20 diverse test queries
  - Run through classifier
  - Compare to human judgment
  - Calculate accuracy percentage
```

#### Learning System Effectiveness
```
Goal: System improves recommendations with each query
Measure:
  - Query 1: System suggests L5, confidence 70%
  - Query 2 (similar): System suggests L5, confidence 75%
  - Query 3 (similar): System suggests L5, confidence 80%
  - Trend: Confidence increasing ✓
```

#### Token Budget Accuracy
```
Goal: Actual tokens within 10% of budget
Measure:
  - Track 50 queries
  - For each: estimated vs actual tokens
  - Calculate variance
  - Adjust budgets if consistently off
```

#### User Satisfaction
```
Goal: Users find suggestions helpful
Measure:
  - Add /hekat --feedback "good|neutral|bad"
  - Track feedback over time
  - Adjust triggers that get bad feedback
```

---

## Part 7: Common Improvement Patterns

### Pattern 1: "L5 is too complex for my use case"

**Diagnosis**:
```
Review: Your typical L5 queries
Examples: "design X", "architect Y", "build Z"
Check: Do they actually need 4-5 parallel agents?
```

**Possible solutions**:
1. **Change agent composition** (smaller team)
   - Remove one parallel agent
   - Simplify synthesis
   - Save ~2K tokens

2. **Create L4.5 level** (between L4-L5)
   - 3 agents parallel + light synthesis
   - Token budget: 4500-6000

3. **Improve trigger detection**
   - If classification is guessing L5 incorrectly
   - Add more specific keywords
   - Use consciousness patterns instead

### Pattern 2: "L6 never gets selected"

**Diagnosis**:
```
Review: When would L6 actually be needed?
Current: L6 = iterative refinement (4-6 loops)
Problem: Users might not know to request it
```

**Solutions**:
1. **Add refactor/optimize keywords** (that trigger L6)
   - Makes L6 discoverable

2. **Add subcommand** `/hekat --refactor "code"`
   - Directly selects L6

3. **Improve fallback logic**
   - If user says "refactor and optimize", suggest L6
   - Instead of staying in L3-L4

4. **Document L6 better**
   - Add examples to hekat/SKILL.md
   - Explain when iterative is better than sequential

### Pattern 3: "Token budget keeps growing"

**Diagnosis**:
```
Monitor: Actual tokens per level over time
Trend: L5 was 7000, now averaging 8500
Cause: Agents are more thorough? More complex queries?
```

**Solutions**:
1. **Increase budget** (if justified)
   ```yaml
   Old: L5: 5500-9000
   New: L5: 6500-10000
   ```

2. **Optimize agent work** (reduce verbosity)
   - Train agents to be more concise
   - Use query-specific parameters

3. **Add parallelism** (reduce sequential work)
   - L5 → split some sequential work into L4 parallel

4. **Split into two queries**
   - If L5 consistently exceeds budget
   - Recommend two sequential L3s instead

---

## Part 8: Documentation Update Checklist

Every improvement should update these files:

### Documentation Files
- [ ] QUERY_BUILDER_SPECIFICATION.md (primary reference)
- [ ] IMPLEMENTATION_ROADMAP.md (if implementation changes)
- [ ] hekat/SKILL.md (user-facing examples)
- [ ] TIER_HOTKEY_REFERENCE.md (if hotkeys change)
- [ ] IMPLEMENTATION_NOTES.md (your improvement log)

### Code/Config Files
- [ ] ~/.claude/commands/hekat.md (if command changes)
- [ ] ~/.claude/agents/hekat-agent/agent.yaml (if algorithm changes)
- [ ] ~/.claude/skills/hekat/SKILL.md (if behavior changes)
- [ ] ~/.claude/hekat-consciousness.yaml (if schema changes)

### Test Files
- [ ] tests/test_hekat.py (add test cases)
- [ ] examples/ (add examples if new features)

---

## 🎯 Next Immediate Steps

**This week**:
1. Read IMPLEMENTATION_ROADMAP.md Phase 1 (30 min)
2. Create 4 Phase 1 files (2 hours)
3. Run `/actualize` (5 min)
4. Test `/hekat --help` (5 min)

**Next week**:
1. Implement Phase 2 classification (1 week)
2. Test on 20 diverse queries (2 hours)
3. Document accuracy in IMPLEMENTATION_NOTES.md

**Month 1+**:
1. Add consciousness learning (Phase 3)
2. Choose your first improvement
3. Follow the modification pattern above
4. Test, document, iterate

---

## 📚 Complete File Navigation

All improvement pathways reference these core files:

```
QUERY_BUILDER_SPECIFICATION.md
  ├─ Part 1: L1-L7 definitions (modify here to change levels)
  ├─ Part 2: Hotkey system (modify to change hotkeys)
  ├─ Part 3: Classification algorithm (modify to change triggers)
  ├─ Part 4: Token tracking (modify to change display)
  ├─ Part 5: Consciousness schema (modify to change learning)
  └─ Part 6: Fallback mechanisms (modify to change constraints)

IMPLEMENTATION_ROADMAP.md
  ├─ Phase 1: Foundation files to create
  ├─ Phase 2: Classification algorithm pseudocode
  ├─ Phase 3: Advanced features
  ├─ Phase 4: Polish & production
  └─ "How to Modify & Extend" section

TIER_HOTKEY_REFERENCE.md
  ├─ Hotkey matrices
  ├─ Mnemonic meanings
  ├─ Decision trees
  └─ All hotkey examples

hekat/SKILL.md
  ├─ When to use
  ├─ Core concepts
  ├─ Quick start
  ├─ Advanced patterns
  └─ Real examples

~/.claude/commands/hekat.md
  ├─ Command usage
  ├─ Examples
  └─ Subcommands (to add)

~/.claude/agents/hekat-agent/agent.yaml
  ├─ Classification logic
  ├─ Token estimation
  └─ Consciousness integration

IMPLEMENTATION_NOTES.md
  └─ Your improvement log (create as you go)
```

---

## Summary

**What was built**: A complete, unified, production-ready specification for a complexity-aware query orchestration system (HEKAT Query Builder) combining comonadic patterns, DSL research, and learning systems.

**How to improve it**: Follow the three pathways (Skills → Agents → Commands) with documented modification patterns. Every improvement has a checklist and success criteria.

**Your next action**: Start Phase 1 in IMPLEMENTATION_ROADMAP.md and begin building the system. The documentation will guide you every step of the way.

---

**Questions?** All answers are in the documentation. Use this file as a navigation guide to find the right section.

**Last Updated**: 2025-10-27
**Status**: ✅ Ready for Implementation & Iteration
