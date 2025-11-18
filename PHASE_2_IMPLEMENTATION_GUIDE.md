# HEKAT Phase 2: Core Implementation Guide

**Status**: Starting Phase 2
**Date**: 2025-10-27
**Duration**: 1-2 weeks
**Goal**: Make `/hekat` fully functional with complexity classification

---

## Overview

Phase 2 transforms HEKAT from a registered command into a **working system** that:
1. ✅ Classifies queries to L1-L7 complexity levels
2. ✅ Maps hotkeys to agent compositions
3. ✅ Displays token tracking information
4. ✅ Explains its decisions to users

---

## Task 2.1: Complexity Classification Algorithm

### What We're Building

A function that takes a query and returns:
```python
{
    "level": 5,                    # Complexity level 1-7
    "confidence": 0.92,            # How sure (0.0-1.0)
    "reasoning": "Keywords...",    # Explanation
    "method": "keyword + consciousness"
}
```

### Core Algorithm (4 Steps)

**Step 1: Check for Explicit Override**
```
/hekat @L5 "query"  → level=5, confidence=1.0, method="explicit"
```

**Step 2: Check for Hotkey Input**
```
/hekat [R] "query"  → hotkey=R → level=1, confidence=0.95, method="hotkey"
```

**Step 3: Keyword Classification**
```
Query: "design authentication system"
Keywords found: ["design", "system"]
Base level: L5 (design + system = architecture)
Confidence: 0.75 (keywords match)
```

**Step 4: Apply Consciousness Patterns & Token Budget**
```
If consciousness has learned pattern:
  - Similar "design" queries succeeded at L5 → use L5
  - Confidence: 0.92 (based on success rate)

If tokens available < budget for level:
  - Downgrade to lower level
  - E.g., L7 requested but only 6K tokens → suggest L5
```

### Keyword Mapping

```python
keywords = {
    "L1": {
        "explain", "understand", "what is", "how does",
        "tell me", "show me", "list", "summarize",
        "describe", "clarify", "define"
    },
    "L2": {
        "then", "and then", "next", "followed by",
        "fix and", "design and", "document",
        "build after", "then test"
    },
    "L3": {
        "design", "implement", "test", "build feature",
        "create endpoint", "develop", "develop and test"
    },
    "L4": {
        "compare", "evaluate", "versus", "pros and cons",
        "options", "alternatives", "perspectives",
        "analysis", "benchmark"
    },
    "L5": {
        "architect", "design system", "microservices",
        "infrastructure", "platform", "system design",
        "large scale"
    },
    "L6": {
        "refactor", "optimize", "improve", "debug",
        "iterate", "until", "refine", "enhance",
        "converge", "fix and verify"
    },
    "L7": {
        "build", "from scratch", "complete", "full platform",
        "production", "entire system", "startup"
    }
}
```

### Implementation

```python
def classify_query(user_input: str, available_tokens: int) -> dict:
    """
    Classify user query to complexity level L1-L7

    Args:
        user_input: The query string (may include @L5, [R], etc.)
        available_tokens: Tokens remaining in context

    Returns:
        {
            "level": 1-7,
            "confidence": 0.0-1.0,
            "reasoning": explanation string,
            "method": how we determined it
        }
    """

    # STEP 1: Check for explicit level override (@L5)
    if user_input.startswith("@L"):
        level = int(user_input[2])
        return {
            "level": level,
            "confidence": 1.0,
            "method": "explicit_override",
            "reasoning": f"User explicitly requested L{level}"
        }

    # STEP 2: Check for hotkey input ([R], [D], [Ctrl+H], etc.)
    if user_input.startswith("[") and "]" in user_input:
        hotkey = extract_hotkey(user_input)
        level = HOTKEY_TO_LEVEL.get(hotkey, None)
        if level:
            return {
                "level": level,
                "confidence": 0.95,
                "method": "hotkey",
                "reasoning": f"Hotkey [{hotkey}] maps to L{level}",
                "hotkey": hotkey
            }

    # STEP 3: Keyword-based classification
    query_lower = user_input.lower()
    keyword_level = classify_by_keywords(query_lower)
    keyword_confidence = 0.75

    # STEP 4: Check consciousness patterns (if available)
    pattern = find_consciousness_pattern(query_lower)
    if pattern and pattern["success_rate"] > 0.85:
        pattern_level = pattern["default_level"]
        pattern_confidence = pattern["success_rate"]
        reasoning = f"Similar query succeeded at L{pattern_level} (confidence: {pattern_confidence:.0%})"
    else:
        pattern_level = keyword_level
        pattern_confidence = 0.75
        reasoning = f"Keywords suggest L{keyword_level}"

    # STEP 5: Check token budget constraints
    final_level = pattern_level
    TOKEN_BUDGETS = {
        1: (600, 1200),
        2: (1500, 3000),
        3: (2500, 4500),
        4: (3000, 6000),
        5: (5500, 9000),
        6: (8000, 12000),
        7: (12000, 22000)
    }

    # Downgrade if insufficient tokens
    while final_level > 1 and TOKEN_BUDGETS[final_level][0] > available_tokens:
        final_level -= 1

    # If downgraded, adjust reasoning
    if final_level < pattern_level:
        reasoning += f"; downgraded to L{final_level} due to token budget ({available_tokens} available)"

    return {
        "level": final_level,
        "confidence": pattern_confidence,
        "method": "keyword + consciousness + budget",
        "reasoning": reasoning,
        "keyword_level": keyword_level,
        "pattern_level": pattern_level,
        "token_budget_min": TOKEN_BUDGETS[final_level][0]
    }


def classify_by_keywords(query_lower: str) -> int:
    """Classify query to level based on keyword matching"""

    KEYWORDS = {
        7: {"build", "from scratch", "complete", "full platform", "production"},
        6: {"refactor", "optimize", "improve", "debug", "iterate", "refine"},
        5: {"architect", "design system", "microservices", "infrastructure"},
        4: {"compare", "evaluate", "versus", "options", "alternatives"},
        3: {"design", "implement", "test", "build", "create"},
        2: {"then", "and then", "followed by", "document"},
        1: {"explain", "understand", "what", "how", "tell me", "show"}
    }

    # Check L7 → L1 (stop at first match)
    for level in range(7, 0, -1):
        for keyword in KEYWORDS[level]:
            if keyword in query_lower:
                return level

    # Default to L1 if no keywords match
    return 1


def extract_hotkey(user_input: str) -> str:
    """Extract hotkey from user input like '[R]' or '[Ctrl+H]'"""
    import re
    match = re.search(r'\[([^\]]+)\]', user_input)
    return match.group(1) if match else None


def find_consciousness_pattern(query: str) -> dict:
    """Find matching pattern in consciousness file (Phase 3)"""
    # For now, return None (Phase 2 doesn't implement consciousness yet)
    # Will be implemented in Phase 3
    return None
```

### Testing Phase 2.1

```python
# Test cases
test_cases = [
    ("explain JWT", 5000, 1, "L1 - Single agent research"),
    ("design and implement auth", 5000, 3, "L3 - Design → Implement → Test"),
    ("compare FastAPI vs Express", 5000, 4, "L4 - Parallel consensus"),
    ("design microservices", 5000, 5, "L5 - Architecture"),
    ("refactor database queries", 5000, 6, "L6 - Iterative"),
    ("build SaaS platform", 5000, 7, "L7 - Full ensemble"),
    ("@L5 anything", 5000, 5, "Explicit override"),
    ("[R] explain", 5000, 1, "Hotkey R → L1"),
    ("[Ctrl+H] query", 5000, 5, "Hotkey Ctrl+H → L5"),
    ("explain something", 1000, 1, "L1 with low tokens"),
    ("build platform", 8000, 7, "L7 with medium tokens"),
    ("build platform", 3000, 5, "L7 request downgraded to L5 (budget)"),
]

# Run tests
for query, tokens, expected_level, description in test_cases:
    result = classify_query(query, tokens)
    actual_level = result["level"]
    status = "✅" if actual_level == expected_level else "❌"
    print(f"{status} {description}")
    if actual_level != expected_level:
        print(f"   Expected L{expected_level}, got L{actual_level}")
```

---

## Task 2.2: Hotkey Matrix Implementation

### What We're Building

A lookup table mapping:
- Single keys [R], [D], [T], etc. → complexity levels
- Ctrl-modifiers [Ctrl+P], [Ctrl+H], etc. → levels
- Agent chains [R>D>I], [P:R||D||A] → agent compositions

### Hotkey Data Structure

```python
HOTKEY_MATRIX = {
    # TIER 1: Single keys
    "R": {"agents": ["deep-researcher"], "level": 1, "description": "Research/explain"},
    "D": {"agents": ["api-architect", "debug-detective"], "level": "1-5", "description": "Design/debug"},
    "T": {"agents": ["test-engineer"], "level": 1, "description": "Test/verify"},
    "B": {"agents": ["practical-programmer"], "level": 2, "description": "Build/implement"},
    "F": {"agents": ["frontend-architect"], "level": 2, "description": "Frontend"},
    "I": {"agents": ["practical-programmer"], "level": 2, "description": "Implement"},
    "O": {"agents": ["project-orchestrator"], "level": 5, "description": "Orchestrate"},
    "S": {"agents": ["mercurio-orchestrator"], "level": 6, "description": "Synthesize"},
    "C": {"agents": ["debug-detective", "test-engineer"], "level": 3, "description": "Code-review"},
    "P": {"pattern": "parallel", "level": 4, "description": "Parallel analysis"},
    "V": {"agents": ["test-engineer"], "level": 1, "description": "Verify"},
    "A": {"agents": ["deep-researcher", "debug-detective"], "level": 1, "description": "Analyze"},

    # TIER 2: Ctrl-modifiers for explicit level selection
    "Ctrl+P": {"level": 4, "description": "Force L4 Parallel"},
    "Ctrl+H": {"level": 5, "description": "Force L5 Hierarchical"},
    "Ctrl+I": {"level": 6, "description": "Force L6 Iterative"},
    "Ctrl+E": {"level": 7, "description": "Force L7 Ensemble"},

    # TIER 3: Agent chains (explicit DSL)
    "R>D>I": {
        "agents": ["deep-researcher", "api-architect", "practical-programmer"],
        "level": 3,
        "pattern": "sequential",
        "description": "Research → Design → Implement"
    },
    "D>I>T": {
        "agents": ["api-architect", "practical-programmer", "test-engineer"],
        "level": 3,
        "pattern": "sequential",
        "description": "Design → Implement → Test"
    },
    "P:R||D||A": {
        "agents": ["deep-researcher", "api-architect", "debug-detective"],
        "level": 4,
        "pattern": "parallel",
        "description": "Parallel: Research, Design, Analyze"
    },
}

def map_hotkey_to_level(hotkey: str) -> int:
    """Map hotkey to complexity level"""
    if hotkey in HOTKEY_MATRIX:
        return HOTKEY_MATRIX[hotkey].get("level", None)
    return None

def get_hotkey_agents(hotkey: str) -> list:
    """Get agents for a hotkey"""
    if hotkey in HOTKEY_MATRIX:
        return HOTKEY_MATRIX[hotkey].get("agents", [])
    return []

def suggest_hotkey_for_level(level: int) -> str:
    """Given a level, suggest a hotkey"""
    suggestions = {
        1: "[R] Research",
        2: "[B] Build",
        3: "[D>I>T] Design→Implement→Test",
        4: "[Ctrl+P] Parallel",
        5: "[Ctrl+H] Hierarchical",
        6: "[Ctrl+I] Iterative",
        7: "[Ctrl+E] Ensemble"
    }
    return suggestions.get(level, f"L{level}")
```

### Implementation

```python
def display_with_hotkey_suggestion(level: int, reasoning: str) -> str:
    """Display result with hotkey suggestion"""
    hotkey = suggest_hotkey_for_level(level)

    return f"""Selected: L{level} ({get_level_name(level)})
Hotkey: {hotkey}
Reasoning: {reasoning}
Status: ✅ Ready to execute"""

def get_level_name(level: int) -> str:
    names = {
        1: "Ultra-Fast",
        2: "Fast Chain",
        3: "Balanced",
        4: "Parallel Consensus",
        5: "Hierarchical",
        6: "Iterative",
        7: "Full Ensemble"
    }
    return names.get(level, f"L{level}")
```

### Testing Phase 2.2

```python
test_hotkeys = [
    ("R", 1, "Research → L1"),
    ("D", 1-5, "Design → Multiple levels"),
    ("Ctrl+P", 4, "Parallel → L4"),
    ("Ctrl+H", 5, "Hierarchical → L5"),
    ("R>D>I", 3, "Chain → L3"),
    ("P:R||D||A", 4, "Parallel chain → L4"),
]

for hotkey, expected, description in test_hotkeys:
    level = map_hotkey_to_level(hotkey)
    print(f"✅ {hotkey} → L{level}: {description}")
```

---

## Task 2.3: Token Tracking Display

### What We're Building

Display showing:
- Estimated vs actual tokens
- Phase-by-phase breakdown
- Variance (±% from budget)
- Budget status (safe/warning/over)

### Display Format (Default)

```
Selected: L5 Hierarchical (92% confidence)
Agents: api-architect → (practical-programmer || frontend-architect || test-engineer) → project-orchestrator
Tokens: Est 7200 | Budget 5500-9000 | Status: ✅ Within budget
```

### Display Format (Verbose with --verbose)

```
SELECTION PHASE:
  Phase 1: Input parsing       [+487 tokens] ✅
  Phase 2: Complexity classify [+892 tokens] ✅
  Phase 3: Hotkey generation   [+507 tokens] ✅
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

### Implementation

```python
def format_token_display(classification_result: dict, verbose: bool = False) -> str:
    """Format token tracking display"""

    level = classification_result["level"]
    confidence = classification_result["confidence"]

    TOKEN_BUDGETS = {
        1: (600, 1200),
        2: (1500, 3000),
        3: (2500, 4500),
        4: (3000, 6000),
        5: (5500, 9000),
        6: (8000, 12000),
        7: (12000, 22000)
    }

    min_tokens, max_tokens = TOKEN_BUDGETS[level]
    est_tokens = int((min_tokens + max_tokens) / 2)  # Midpoint estimate

    if not verbose:
        # Clean format
        return f"""
Selected: L{level} {get_level_name(level)} ({confidence:.0%} confidence)
Tokens: Est {est_tokens} | Budget {min_tokens}-{max_tokens} | Status: ✅ Ready"""

    else:
        # Verbose format with phases
        phase_tokens = [487, 892, 507]  # Estimated overhead
        total_overhead = sum(phase_tokens)

        phases = f"""
SELECTION PHASE:
  Phase 1: Input parsing       [+{phase_tokens[0]} tokens] ✅
  Phase 2: Complexity classify [+{phase_tokens[1]} tokens] ✅
  Phase 3: Hotkey generation   [+{phase_tokens[2]} tokens] ✅
  ─────────────────────────────
  Total overhead: {total_overhead} tokens
"""

        execution = f"""
EXECUTION PLAN:
  Selected: L{level} {get_level_name(level)}
  Token budget: {est_tokens} (range: {min_tokens}-{max_tokens})
  Confidence: {confidence:.0%}
"""

        return phases + execution


def display_variance(estimated: int, actual: int) -> str:
    """Display token variance status"""
    if estimated == 0:
        return "N/A"

    variance = (actual - estimated) / estimated

    if -0.5 <= variance <= 0.10:
        status = "✅"
        level = "Excellent"
    elif 0.10 < variance <= 0.20:
        status = "⚠️"
        level = "Warning"
    else:
        status = "❌"
        level = "Over budget"

    return f"{status} {variance:+.0%} ({level})"
```

---

## Summary: Phase 2 Tasks

### 2.1: Complexity Classification ✅ Ready to implement
- [ ] Implement `classify_query()` function
- [ ] Implement `classify_by_keywords()` function
- [ ] Test on 10 queries
- [ ] Verify accuracy ≥ 90%

### 2.2: Hotkey Matrix ✅ Ready to implement
- [ ] Create HOTKEY_MATRIX dict
- [ ] Implement `map_hotkey_to_level()` function
- [ ] Implement `suggest_hotkey_for_level()` function
- [ ] Test all hotkeys

### 2.3: Token Tracking ✅ Ready to implement
- [ ] Implement `format_token_display()` function
- [ ] Test default format
- [ ] Test verbose format
- [ ] Verify variance calculations

---

## Next Steps

1. **Choose implementation approach**:
   - Option A: Implement in Python script (easiest for testing)
   - Option B: Implement in hekat-agent YAML (integrates directly)
   - Option C: Implement as separate module imported by hekat command

2. **Create test suite**:
   - Test classification accuracy
   - Test hotkey mapping
   - Test token display formats

3. **Integrate with /hekat command**:
   - Wire up classification to command
   - Add hotkey parsing
   - Add token display on --verbose

---

## Files to Create/Modify

**New files**:
- `hekat/implementations/classifier.py` - Phase 2.1 implementation
- `hekat/implementations/hotkeys.py` - Phase 2.2 implementation
- `hekat/implementations/token_display.py` - Phase 2.3 implementation
- `hekat/tests/test_phase2.py` - Test suite

**Modified files**:
- `~/.claude/commands/hekat.md` - Update status to Phase 2
- `~/.claude/agents/hekat-agent/agent.yaml` - Integration logic
- `IMPLEMENTATION_ROADMAP.md` - Mark Phase 2 as in-progress

---

**Ready to implement? Let's start with Task 2.1!**
