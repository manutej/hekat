# HEKAT Query Builder: Documentation Guide

**Status**: Unified Design → Implementation Ready
**Last Updated**: 2025-10-27
**Version**: 1.0

---

## What You Have

This folder contains **complete documentation** for the HEKAT Query Builder system—a complexity-aware, token-disciplined multi-agent orchestration system.

### Files in This Folder

```
hekat/
├── README_DOCUMENTATION.md                    ← You are here
├── QUERY_BUILDER_SPECIFICATION.md            ← Complete technical spec
├── IMPLEMENTATION_ROADMAP.md                 ← Step-by-step build plan
├── TIER_HOTKEY_REFERENCE.md                  ← Quick hotkey lookup
├── comonad/                                   ← Comonadic DSL patterns
├── query-library/                             ← (To be created) L1-L7 examples
├── tests/                                     ← (To be created) Test suite
└── IMPLEMENTATION_NOTES.md                    ← (To create) Your progress log
```

---

## How to Use This Documentation

### 1. First Time? Start Here 👇

**Read in this order**:

1. **This file** (README_DOCUMENTATION.md) - 5 min overview
2. **TIER_HOTKEY_REFERENCE.md** - Understand hotkey system (10 min)
3. **QUERY_BUILDER_SPECIFICATION.md Part 1** - L1-L7 levels (20 min)
4. **QUERY_BUILDER_SPECIFICATION.md Part 2** - Hotkey architecture (10 min)
5. **IMPLEMENTATION_ROADMAP.md Phase 1** - Ready to build (30 min)

**Total: ~75 minutes to understand the system fully**

### 2. Ready to Implement? Start Here 👇

1. Open **IMPLEMENTATION_ROADMAP.md**
2. Start with **Phase 1: Foundation**
3. Follow step-by-step instructions
4. Use checklist to track progress
5. Document decisions in **IMPLEMENTATION_NOTES.md**

**Expected timeline**: Phase 1 (1-2 hours), Phase 2 (1-2 weeks)

### 3. Need to Modify Something? Start Here 👇

**Changing L5 agent composition?**
1. Read: QUERY_BUILDER_SPECIFICATION.md Part 1 → L5
2. Edit: ~/.claude/skills/hekat/SKILL.md
3. Update: QUERY_BUILDER_SPECIFICATION.md (keep in sync)
4. Test: Run `/hekat @L5 "architecture"` verify agents
5. Document: Add note to IMPLEMENTATION_NOTES.md

**Adding new hotkey?**
1. Read: TIER_HOTKEY_REFERENCE.md
2. Choose: Tier 1, 2, or 3
3. Edit: TIER_HOTKEY_REFERENCE.md
4. Implement: Update hotkey lookup logic
5. Test: Verify hotkey maps correctly

**Learning from real usage (consciousness patterns)?**
1. Read: QUERY_BUILDER_SPECIFICATION.md Part 5
2. Monitor: ~/.claude/hekat-consciousness.yaml
3. Analyze: Monthly success rates, token budgets
4. Update: IMPLEMENTATION_ROADMAP.md Phase 5

---

## Document Overview

### QUERY_BUILDER_SPECIFICATION.md (Comprehensive Technical Spec)

**Purpose**: Complete design specification—what gets built

**Contains**:
- **Part 1**: L1-L7 complexity levels (detailed)
  - Comonad pattern mapping
  - Agent counts and coordination
  - Token budgets
  - Real DSL examples
  - Trigger conditions per level

- **Part 2**: Hotkey system architecture
  - TIER 1-3 hotkey paradigms
  - Semantic mapping (what [R] does)
  - Hotkey matrix by level
  - Discovery mechanism

- **Part 3**: Smart query selection & DSL parser
  - Input parsing algorithm
  - Complexity classification with code
  - DSL syntax and parser rules
  - Implicit vs explicit level detection

- **Part 4**: Token tracking & display
  - Task-relay checkpoint format
  - CLI display formats (default, verbose, error, streaming)
  - Token budget accounting

- **Part 5**: Consciousness integration
  - Pattern schema (what gets tracked)
  - Pattern matching algorithm
  - Learning loop
  - Improvement over time

- **Part 6**: Fallback mechanisms
  - Insufficient tokens
  - Agent unavailability
  - Context size explosion

- **Part 7**: Integration with Claude Code
  - `/hekat` command structure
  - `hekat` skill definition
  - `hekat-agent` agent definition
  - Consciousness storage file

**How to use it**:
- Reference for understanding design decisions
- Source of truth for agent compositions per level
- API specification for hotkey mapping
- Schema documentation for consciousness patterns
- Starting point for implementing any feature

---

### IMPLEMENTATION_ROADMAP.md (Step-by-Step Build Plan)

**Purpose**: How to build the system, phase by phase

**Contains**:

- **Phase 1: Foundation** (1-2 hours)
  - Create `/hekat` command
  - Create `hekat` skill
  - Create `hekat-agent` agent
  - Create consciousness storage
  - Run `/actualize`
  - Deliverable: System is registered and callable

- **Phase 2: Core Implementation** (1-2 weeks)
  - Implement complexity classification
  - Implement hotkey matrix
  - Implement token tracking display
  - Testing checklist
  - Deliverable: `/hekat "query"` works, classifies to L1-L7

- **Phase 3: Advanced Features** (2-3 weeks)
  - Implement consciousness pattern matching
  - Implement DSL parser
  - Implement fallback mechanisms
  - Testing and validation
  - Deliverable: Learning system, graceful degradation

- **Phase 4: Integration & Documentation** (1-2 weeks)
  - Query library (optional)
  - Help reference card
  - Integration tests
  - User documentation
  - Deliverable: Production-ready, well-documented

- **Phase 5: Ongoing Iteration** (Continuous)
  - Monitor usage
  - Learn from patterns
  - Refine definitions
  - Optimize token budgets

**How to use it**:
- Checklist for implementation tasks
- Code examples (Python pseudocode)
- Testing strategies per phase
- Success criteria per phase
- Extension guide (how to modify)

---

### TIER_HOTKEY_REFERENCE.md (Quick Lookup)

**Purpose**: Fast reference for hotkey system

**Contains**:
- TIER 1-3 hotkey tables
- Mnemonic meanings
- Common chains by level
- Decision tree (situation → hotkey)
- Mistake fixes
- Printable cheat sheet

**How to use it**:
- Quick lookup while implementing hotkey logic
- Teach users ("which hotkey for this task?")
- Test hotkey mapping
- Design help text (`/hekat --help`)

---

## Key Concepts (Tl;dr)

### Complexity Levels (L1-L7)

```
L1 (600-1200 tokens)     : Single agent, ultra-fast
L2 (1500-3000 tokens)    : Two agents in sequence
L3 (2500-4500 tokens)    : Three agents in sequence (feature dev)
L4 (3000-6000 tokens)    : 2-3 parallel agents (multi-perspective)
L5 (5500-9000 tokens)    : 4-5 hierarchical (architecture)
L6 (8000-12000 tokens)   : 4-6 iterative (refinement loops)
L7 (12000-22000 tokens)  : 7+ ensemble (full orchestration)
```

Each level maps to a **comonadic orchestration pattern**:
- Sequential (L1-L3)
- Parallel Consensus (L4)
- Hierarchical (L5)
- Iterative (L6)
- All Combined (L7)

### Hotkey TIER System

```
TIER 1: Single keys [R][D][T][B][I][P][O][S][C][A][V]
        → Progressive disclosure, muscle memory

TIER 2: Ctrl-modifiers [Ctrl+P][Ctrl+H][Ctrl+I][Ctrl+E]
        → Force specific complexity level

TIER 3: Agent chains [R>D>I][P:R||D||A][I:D→P→T]
        → Explicit composition for power users
```

### Core Algorithm

```
User Input
    ↓
Parse (hotkey? DSL? natural language?)
    ↓
Classify (keywords → base level)
    ↓
Match consciousness (historical patterns)
    ↓
Check tokens (available budget?)
    ↓
Suggest complexity level + hotkey
    ↓
Execute agents (with task-relay tracking)
    ↓
Log results (update consciousness)
    ↓
Return to user
```

### Token Discipline

**Every operation tracked**:
- Phase-by-phase checkpoints (selection, classification, execution)
- Token budget accounting
- Variance tracking (estimated vs actual)
- Fallback when budget insufficient

**Example**:
```
Query: "design auth"
Phase 1: Classify        +487 tokens
Phase 2: Select hotkey   +892 tokens
Phase 3: Execute L5      +7200 tokens
Total: 8579 tokens
Budget: 50000
Remaining: 41421
Status: ✅ OK
```

### Consciousness Patterns

**What gets tracked**:
- Query text
- Selected level
- Agents executed
- Tokens estimated vs actual
- Success/failure indicator
- Execution time

**How it learns**:
- Patterns emerge after 3-5 similar queries
- Success rates improve with history
- Future similar queries get better suggestions
- System becomes smarter with use

---

## Architecture at a Glance

```
┌─────────────────────────────────────────────────────┐
│                    /hekat Command                   │
│  (User entry point, routes to hekat-agent)         │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│                  hekat-agent                         │
│  (Analyzes query, classifies level, suggests       │
│   hotkey, estimates tokens)                         │
└─────────────────────────────────────────────────────┘
                           ↓
       ┌───────────────────┼───────────────────┐
       ↓                   ↓                   ↓
   Complexity      Token Tracking        Consciousness
   Classifier      Display                Patterns
       ↓                   ↓                   ↓
   [1-7]          [Checkpoint Log]      [History + Learning]
       ↓                   ↓                   ↓
       └───────────────────┼───────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│           hekat Skill (User Reference)              │
│  (Teaches L1-L7, hotkeys, examples)                │
└─────────────────────────────────────────────────────┘
```

---

## Quick Start (5 Minutes)

### Phase 1 Setup

```bash
# Create basic structure (10 min)
mkdir -p ~/.claude/skills/hekat ~/.claude/agents/hekat-agent
mkdir -p /Users/manu/Documents/LUXOR/.claude/skills/hekat

# Create minimal hekat command
cat > ~/.claude/commands/hekat.md << 'EOF'
---
name: hekat
description: HEKAT Query Builder - L1-L7 complexity selection
---

# /hekat Command

/hekat "your query"      # Auto-detect level
/hekat @L5 "query"      # Force level
/hekat [hotkey] "query" # Use hotkey (e.g., [R], [D], [P])
/hekat --help           # Show hotkeys
/hekat --verbose        # Show token tracking

See: QUERY_BUILDER_SPECIFICATION.md for details
EOF

# Create minimal skill
cat > ~/.claude/skills/hekat/SKILL.md << 'EOF'
---
name: hekat
description: HEKAT Query Builder - select complexity level L1-L7
---

# HEKAT Query Builder

## When to Use

- Need to know if task is L1 (quick) or L7 (complex)
- Want hotkey suggestions for fast execution
- Need token budget estimates
- Learning from past query patterns

## Complexity Levels

L1 (600 tokens): Quick explanation
L2 (2000 tokens): Two-step workflow
L3 (3500 tokens): Feature development
L4 (4500 tokens): Multi-perspective analysis
L5 (7000 tokens): Architecture design
L6 (10000 tokens): Iterative refinement
L7 (18000 tokens): Full platform project

## Quick Start

/hekat "explain JWT"              → L1
/hekat "design auth endpoint"    → L3
/hekat [P] "compare databases"   → L4
/hekat @L7 "build microservices" → L7

See QUERY_BUILDER_SPECIFICATION.md for complete reference
EOF

# Create agent config
cat > ~/.claude/agents/hekat-agent/agent.yaml << 'EOF'
name: hekat-agent
description: HEKAT expert - classifies complexity, suggests hotkeys
model: claude-sonnet

capabilities:
  - complexity_classification (L1-L7)
  - hotkey_suggestion
  - token_estimation
  - consciousness_pattern_matching
  - dsl_parsing
EOF

# Create consciousness storage
cat > ~/.claude/hekat-consciousness.yaml << 'EOF'
version: 1.0
created: 2025-10-27
invocations: []
consciousness_patterns: {}
EOF

# Sync
/actualize
```

### Test It

```bash
/hekat --help                    # Should show usage
/hekat "explain JWT"             # Should suggest L1
/crew hekat-agent                # Should find agent
```

### Next Step

Read **IMPLEMENTATION_ROADMAP.md Phase 2** to implement classification.

---

## Common Tasks

### "I want to understand why L5 was suggested"

1. Read: QUERY_BUILDER_SPECIFICATION.md → Part 1 → L5
2. Look: Trigger conditions section
3. Understand: Agent composition and token budget

---

### "How do I add support for a new hotkey?"

1. Read: TIER_HOTKEY_REFERENCE.md
2. Follow: IMPLEMENTATION_ROADMAP.md → "How to Modify & Extend"
3. Test: Verify new hotkey maps to correct level

---

### "Why did consciousness suggest L5 for this query?"

1. Check: ~/.claude/hekat-consciousness.yaml
2. Look: consciousness_patterns section
3. Review: Success rate and sample count
4. Understand: Historical learning influencing suggestion

---

### "My query was classified wrong (should be L4, got L3)"

1. Report: What query, what level suggested, what level expected
2. Document: Add to IMPLEMENTATION_NOTES.md
3. Fix: Update trigger keywords in Phase 2 implementation
4. Test: Verify similar queries now classify correctly

---

### "How do I extend this to L8 (hypothetical new level)?"

1. Read: IMPLEMENTATION_ROADMAP.md → "How to Introduce New Level"
2. Update: QUERY_BUILDER_SPECIFICATION.md (add L8 section)
3. Implement: Update token budgets, keywords, DSL parser
4. Test: Ensure L8 classification works
5. Document: Create query-library/LEVEL_8_GUIDE.md

---

## Files to Modify When Extending

```
To change:                          Edit:
──────────────────────────────────────────────────────────
L5 agent composition                QUERY_BUILDER_SPECIFICATION.md
                                    + ~/.claude/skills/hekat/SKILL.md

Hotkey mapping                       TIER_HOTKEY_REFERENCE.md
                                    + QUERY_BUILDER_SPECIFICATION.md

Token budgets                        QUERY_BUILDER_SPECIFICATION.md
                                    + IMPLEMENTATION_ROADMAP.md

Complexity classification            IMPLEMENTATION_ROADMAP.md Phase 2
                                    + hekat-agent implementation

Consciousness schema                 QUERY_BUILDER_SPECIFICATION.md Part 5
                                    + ~/.claude/hekat-consciousness.yaml

User-facing documentation            ~/.claude/skills/hekat/SKILL.md
                                    + query-library/ guides
```

---

## Metrics to Track

**System Health** (monthly review):
- Complexity classification accuracy (target: >90%)
- Token budget variance (target: ±5%)
- Consciousness pattern success rates (target: >85% per level)
- Query coverage (what % of queries match existing patterns)

**User Adoption** (quarterly review):
- Most popular complexity levels (which L1-L7?)
- Most-used hotkeys (which TIER 1 keys?)
- Fallback frequency (when do users downgrade?)
- Success rate by level (are all levels working well?)

**System Efficiency** (monthly review):
- Average tokens per level (matching budget?)
- Phase timing (is selection fast?)
- Consciousness growth (patterns improving?)

---

## Implementation Checklist

Copy this to a file and check off as you go:

```markdown
## HEKAT Implementation Checklist

### Phase 1: Foundation ⏳
- [ ] Created ~/.claude/commands/hekat.md
- [ ] Created ~/.claude/skills/hekat/SKILL.md
- [ ] Created ~/.claude/agents/hekat-agent/agent.yaml
- [ ] Created ~/.claude/hekat-consciousness.yaml
- [ ] Ran /actualize successfully
- [ ] Tested /hekat --help works
- [ ] Tested hekat-agent is discoverable

### Phase 2: Core ⏳
- [ ] Implemented classify_complexity() function
- [ ] Test L1 classification ("explain...") → L1 ✓
- [ ] Test L3 classification ("design...implement") → L3 ✓
- [ ] Test L7 classification ("build platform") → L7 ✓
- [ ] Implemented hotkey matrix lookup
- [ ] Test [R] → L1 research ✓
- [ ] Test [Ctrl+H] → L5 hierarchical ✓
- [ ] Implemented token tracking display
- [ ] Test /hekat --verbose shows phases ✓
- [ ] Test token budget constraint handling ✓

### Phase 3: Advanced ⏳
- [ ] Implemented consciousness pattern matching
- [ ] Test 2nd similar query suggests past level ✓
- [ ] Implemented DSL parser
- [ ] Test "A -> B -> C" parses to L3 ✓
- [ ] Test "(A || B)" parses to L4 ✓
- [ ] Implemented fallback mechanism
- [ ] Test L7 request with 5K tokens → fallback to L5 ✓

### Phase 4: Integration ⏳
- [ ] Created query-library/LEVEL_1_GUIDE.md (optional)
- [ ] Created /hekat --help reference card
- [ ] Wrote integration tests
- [ ] All tests pass ✓
- [ ] Created HEKAT_QUICK_START.md
- [ ] Created HEKAT_TUTORIALS.md
- [ ] Created HEKAT_TROUBLESHOOTING.md
- [ ] Updated ~/.claude/CLAUDE.md to mention hekat

### Phase 5: Iteration 🔄
- [ ] Reviewed consciousness patterns (monthly)
- [ ] Updated token budgets based on real data
- [ ] Refined trigger keywords
- [ ] Analyzed misclassifications
- [ ] Documented lessons learned
```

---

## Next Steps

1. **Right now**: Read TIER_HOTKEY_REFERENCE.md (10 min)
2. **This week**: Complete Phase 1 of IMPLEMENTATION_ROADMAP.md (2 hours)
3. **Next week**: Start Phase 2 (complexity classification)
4. **After 1 month**: Review consciousness patterns, refine L1-L7 definitions
5. **Ongoing**: Iterate based on real usage

---

## Questions?

- **Understanding the design?** → Read QUERY_BUILDER_SPECIFICATION.md
- **How to implement?** → Read IMPLEMENTATION_ROADMAP.md
- **What's the hotkey for X?** → Read TIER_HOTKEY_REFERENCE.md
- **How to modify something?** → See "How to Modify & Extend" in IMPLEMENTATION_ROADMAP.md

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-27 | Initial specification, roadmap, hotkey reference |

---

**Ready to build? → Start with IMPLEMENTATION_ROADMAP.md Phase 1** 🚀
