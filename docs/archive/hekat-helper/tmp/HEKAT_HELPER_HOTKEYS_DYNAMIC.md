# Hekat-Helper: Dynamic Hotkeys Specification

**Status**: Architecture redesign (replacing static D/R/E/T)
**Created**: 2025-10-27
**Concept**: Dynamically generate single-letter hotkeys from suggested queries

---

## 1. Core Principle: Dynamic Mnemonic Generation

Instead of hardcoding **D/R/E/T**, generate hotkeys dynamically:

```yaml
# STATIC (old approach) ❌
suggestion_1: "deep-researcher : 'investigate pattern'"
hotkey: "D"  # Hardcoded, doesn't match action

# DYNAMIC (new approach) ✅
suggestion_1: "deep-researcher : 'investigate pattern'"
primary_action: "investigate"
hotkey: "I"  # Generated from actual action, self-documenting
```

**Advantages**:
- ✅ Hotkeys match actual actions
- ✅ Self-documenting (user sees "I" knows it's Investigate)
- ✅ Context-aware (changes per execution)
- ✅ Prevents key conflicts automatically
- ✅ Helps learning (letter ≈ action)

---

## 2. Mnemonic Extraction Algorithm

### Step 1: Extract Primary Action Verb

```python
def extract_primary_action(hekat_query_text):
    """
    Extract the primary action/concept from a Hekat query.

    Examples:
    - "deep-researcher : 'investigate pattern'" → "investigate"
    - "(api-architect || practical-programmer) -> test-engineer : 'design and implement'" → "design"
    - "test-engineer : 'write comprehensive tests'" → "test"
    - "deployment-orchestrator : 'deploy to production'" → "deploy"
    - "mercurio-orchestrator : 'analyze and synthesize findings'" → "analyze"
    """

    # Parse Hekat DSL to extract prompt/goal
    prompt = extract_prompt_from_query(hekat_query_text)

    # Extract primary verb (first action mentioned)
    verbs = [
        "investigate", "research", "analyze", "explore",  # Research
        "implement", "code", "build", "write",            # Implementation
        "design", "architect", "plan", "draft",           # Design
        "test", "validate", "check", "verify",            # Testing
        "deploy", "ship", "release", "launch",            # Deployment
        "refactor", "improve", "optimize", "enhance",     # Refactoring
        "document", "explain", "describe", "summarize",   # Documentation
        "review", "evaluate", "assess", "audit",          # Review
        "debug", "fix", "patch", "resolve",               # Debugging
        "integrate", "connect", "link", "combine",        # Integration
    ]

    for verb in verbs:
        if verb in prompt.lower():
            return verb

    # Fallback: Extract first meaningful word
    return extract_first_meaningful_word(prompt)


def get_mnemonic_letter(action_verb):
    """
    Get single letter mnemonic from action verb.

    Examples:
    - "investigate" → "I"
    - "implement" → "I"
    - "design" → "D"
    - "test" → "T"
    - "deploy" → "D"
    - "refactor" → "R"
    """

    # Primary letter mapping
    primary_letters = {
        "investigate": "I",
        "research": "R",
        "analyze": "A",
        "explore": "E",
        "implement": "I",
        "code": "C",
        "build": "B",
        "write": "W",
        "design": "D",
        "architect": "A",
        "plan": "P",
        "draft": "D",
        "test": "T",
        "validate": "V",
        "check": "C",
        "verify": "V",
        "deploy": "D",
        "ship": "S",
        "release": "R",
        "launch": "L",
        "refactor": "R",
        "improve": "I",
        "optimize": "O",
        "enhance": "E",
        "document": "D",
        "explain": "E",
        "describe": "D",
        "summarize": "S",
        "review": "R",
        "evaluate": "E",
        "assess": "A",
        "audit": "A",
        "debug": "B",
        "fix": "F",
        "patch": "P",
        "resolve": "R",
        "integrate": "I",
        "connect": "C",
        "link": "L",
        "combine": "C",
    }

    return primary_letters.get(action_verb, action_verb[0].upper())
```

### Step 2: Handle Key Conflicts

```python
def resolve_hotkey_conflicts(suggestions):
    """
    Handle cases where multiple suggestions map to same letter.

    Strategy: Use uniqueness resolution
    1. Primary letter (first letter of verb)
    2. Secondary letter (second letter of verb)
    3. Third letter
    4. Combine with agent abbreviation
    """

    suggested_keys = []
    used_keys = set()

    for i, suggestion in enumerate(suggestions):
        action = extract_primary_action(suggestion.query_text)

        # Try primary letter
        letter = get_mnemonic_letter(action)

        if letter not in used_keys:
            used_keys.add(letter)
            suggested_keys.append({
                "option": i + 1,
                "letter": letter,
                "action": action,
                "collision": False
            })
        else:
            # Try secondary letter (second char of verb)
            secondary = action[1].upper() if len(action) > 1 else "?"

            if secondary not in used_keys:
                used_keys.add(secondary)
                suggested_keys.append({
                    "option": i + 1,
                    "letter": secondary,
                    "action": action,
                    "collision": True,
                    "collision_resolution": "secondary_letter"
                })
            else:
                # Try combining with agent abbreviation
                agent = extract_primary_agent(suggestion.query_text)
                agent_letter = agent[0].upper()

                if agent_letter not in used_keys:
                    used_keys.add(agent_letter)
                    suggested_keys.append({
                        "option": i + 1,
                        "letter": agent_letter,
                        "action": action,
                        "agent": agent,
                        "collision": True,
                        "collision_resolution": "agent_abbreviation"
                    })
                else:
                    # Fallback: numeric
                    suggested_keys.append({
                        "option": i + 1,
                        "letter": str(i + 1),
                        "action": action,
                        "collision": True,
                        "collision_resolution": "numeric"
                    })

    return suggested_keys
```

---

## 3. Real-World Examples

### Example 1: Backend Implementation Scenario

```
HEKAT-HELPER SUGGESTIONS (Backend async pattern):
═══════════════════════════════════════════════════════════════════

[I] INVESTIGATE  (Level 5 | Confidence: 0.95)
    (deep-researcher || api-architect) -> practical-programmer
    "Research async patterns, design error handling, then implement"

[D] DESIGN (Level 4 | Confidence: 0.78)
    api-architect -> practical-programmer
    "Design the API, implement the solution"

[T] TEST (Level 5 | Confidence: 0.72)
    test-engineer -> frontend-architect
    "Write tests, ensure frontend integration"

[M] MULTI-PERSPECTIVE (Level 5 | Confidence: 0.85)
    mercurio-orchestrator : "analyze from multiple angles"
    "Review approach technically, architecturally, and organizationally"

═══════════════════════════════════════════════════════════════════
Your choice? (I/D/T/M or custom):  _
```

**Hotkey Generation**:
```yaml
suggestion_1:
  query: "deep-researcher || api-architect -> practical-programmer : 'research...'"
  primary_action: "research"
  mnemonic: "R"
  conflict: true  # 'R' might conflict with 'research' elsewhere
  resolution: "investigate"  # Second action in query
  final_hotkey: "I"

suggestion_2:
  query: "api-architect -> practical-programmer : 'design...'"
  primary_action: "design"
  mnemonic: "D"
  conflict: false
  final_hotkey: "D"

suggestion_3:
  query: "test-engineer -> frontend-architect : 'write tests...'"
  primary_action: "test"
  mnemonic: "T"
  conflict: false
  final_hotkey: "T"

suggestion_4:
  query: "mercurio-orchestrator : 'analyze...'"
  primary_action: "analyze"
  mnemonic: "A"
  conflict: false
  alternatives: ["M" for "Multi-perspective", "O" for "Orchestrator"]
  final_hotkey: "M"  # More meaningful than "A"
```

### Example 2: Testing Scenario

```
HEKAT-HELPER SUGGESTIONS (After code implementation):
═══════════════════════════════════════════════════════════════════

[W] WRITE (Level 5 | Confidence: 0.85)
    test-engineer : "write comprehensive unit tests"

[D] DEBUG (Level 4 | Confidence: 0.72)
    debug-detective : "analyze code for edge cases"

[I] INTEGRATE (Level 4 | Confidence: 0.68)
    frontend-architect : "ensure frontend integration"

[V] VALIDATE (Level 6 | Confidence: 0.75)
    test-engineer -> deployment-orchestrator : "test and stage"

═══════════════════════════════════════════════════════════════════
Your choice? (W/D/I/V or custom):  _
```

### Example 3: Research Scenario

```
HEKAT-HELPER SUGGESTIONS (After architecture decision):
═══════════════════════════════════════════════════════════════════

[E] EVALUATE (Level 5 | Confidence: 0.90)
    mercurio-orchestrator : "evaluate tradeoffs"

[D] DOCUMENT (Level 4 | Confidence: 0.78)
    docs-generator : "create architecture docs"

[P] PROTOTYPE (Level 5 | Confidence: 0.82)
    practical-programmer : "build proof-of-concept"

[V] VALIDATE (Level 5 | Confidence: 0.68)
    debug-detective : "validate assumptions"

═══════════════════════════════════════════════════════════════════
Your choice? (E/D/P/V or custom):  _
```

---

## 4. Display Format (Dynamic)

### Compact Single-Line

```
HEKAT: [I] Investigate  [D] Design  [T] Test  [M] Multi-perspective  (?=help)
```

### Full Format

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ HEKAT-HELPER: Smart Next Steps                                                ║
║                                                                               ║
║ [I] INVESTIGATE   Level 5 | Confidence: 0.95 | Est. 1850 tokens              ║
║     Action: research async patterns, design, implement                        ║
║     Query: (deep-researcher || api-architect) -> practical-programmer         ║
║                                                                               ║
║ [D] DESIGN        Level 4 | Confidence: 0.78 | Est. 1200 tokens              ║
║     Action: design API, implement solution                                   ║
║     Query: api-architect -> practical-programmer                              ║
║                                                                               ║
║ [T] TEST          Level 5 | Confidence: 0.72 | Est. 1400 tokens              ║
║     Action: write tests, ensure integration                                  ║
║     Query: test-engineer -> frontend-architect                                ║
║                                                                               ║
║ [M] MULTI-PERSPECTIVE Level 5 | Confidence: 0.85 | Est. 1600 tokens         ║
║     Action: analyze from multiple perspectives                               ║
║     Query: mercurio-orchestrator : "comprehensive review"                     ║
║                                                                               ║
║ [?] Help  [TAB] Full Query  [/] Explanation  [C] Custom  [ESC] Close        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Your choice? (I/D/T/M or custom):  _                                        ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## 5. Configuration File (Dynamic)

Location: `~/.claude/hekat/hotkey_config.yaml`

```yaml
hekat_dynamic_hotkeys:
  version: 2.0
  strategy: "dynamic_mnemonic"

  # Letter generation strategy
  mnemonic_generation:
    enabled: true
    algorithm: "action_verb_first_letter"
    conflict_resolution: "secondary_letter_then_agent"

    # Custom verb-to-letter mappings (overrides defaults)
    custom_mappings:
      "investigate": "I"
      "multi-perspective": "M"
      "comprehensive-review": "R"
      "fast-implementation": "F"

  # Fallback behavior
  fallback:
    if_no_mnemonic: "use_number"  # Use 1,2,3,4
    if_user_prefers: "numbers"

  # Display options
  display:
    show_action_label: true        # Show "INVESTIGATE" under hotkey
    show_explanation: true         # Show "research async patterns..."
    show_confidence: true          # Show "0.95"
    show_tokens: true              # Show "1850 tokens"
    show_collision_warning: false  # Warn if letter collision resolved

  # Accessibility
  accessibility:
    screen_reader_description: "[I] Investigate: Research async patterns, design, implement"
    high_contrast: false
    large_font: false

  # User preferences
  preferences:
    always_show_fallback_numbers: false  # Also show [1] [2] [3] [4]
    prefer_numeric: false                # Use numbers instead of letters
    prefer_traditional_dret: false       # Use D/R/E/T instead of generated
    mnemonic_case_sensitive: false       # "i" and "I" both work
```

---

## 6. Integration Point: Hotkey Generation

```python
# File: ~/.claude/hekat/hotkey_generator.py

from hekat_helper import extract_queries, extract_action, resolve_conflicts

def generate_dynamic_hotkeys(suggestions):
    """
    Called by Hekat-Helper after selecting 4 query candidates.
    Generates hotkeys dynamically based on actual queries.
    """

    # Step 1: Extract action from each query
    actions = [
        extract_action(suggestion.query_text)
        for suggestion in suggestions
    ]

    # Step 2: Get mnemonic letters
    mnemonics = [
        get_mnemonic_letter(action)
        for action in actions
    ]

    # Step 3: Resolve conflicts
    hotkeys = resolve_hotkey_conflicts(
        suggestions, actions, mnemonics
    )

    # Step 4: Return structured hotkey map
    return {
        "hotkeys": [h["letter"] for h in hotkeys],
        "actions": [h["action"] for h in hotkeys],
        "mappings": hotkeys,
        "display_format": generate_display(hotkeys, suggestions)
    }


def display_hekat_overlay(suggestions, hotkeys):
    """
    Display Hekat-Helper overlay with dynamically generated hotkeys.
    """

    overlay = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ HEKAT-HELPER: Smart Next Steps
║
"""

    for hotkey_map, suggestion in zip(hotkeys, suggestions):
        letter = hotkey_map["letter"]
        action = hotkey_map["action"].upper()
        level = suggestion.level
        confidence = suggestion.confidence
        tokens = suggestion.estimated_tokens

        overlay += f"""║ [{letter}] {action:<20} Level {level} | {confidence:.0%} | {tokens} tokens
║     {suggestion.query_summary}
║
"""

    overlay += """║ [?] Help  [TAB] Full Query  [/] Explanation  [C] Custom  [ESC] Close
╠══════════════════════════════════════════════════════════════════════════════╣
║ Your choice? ({hotkeys}) or custom:  _
╚══════════════════════════════════════════════════════════════════════════════╝
"""

    print(overlay)
```

---

## 7. Checkpoint Format (Dynamic Hotkeys)

```yaml
HEKAT_DYNAMIC_HOTKEY_CHECKPOINT:
  timestamp: "2025-10-27T17:15:00Z"
  operation: "dynamic-hotkey-generation"

  input:
    suggestions: 4
    queries: [
      "(deep-researcher || api-architect) -> practical-programmer : 'research...'",
      "api-architect -> practical-programmer : 'design...'",
      "test-engineer -> frontend-architect : 'write tests...'",
      "mercurio-orchestrator : 'analyze from angles...'"
    ]

  processing:
    step_1_action_extraction:
      query_1: "research"
      query_2: "design"
      query_3: "test"
      query_4: "analyze"
      time_ms: 45

    step_2_mnemonic_generation:
      query_1: "R" (from "research")
      query_2: "D" (from "design")
      query_3: "T" (from "test")
      query_4: "A" (from "analyze")
      time_ms: 20

    step_3_conflict_resolution:
      conflicts_detected: 0
      resolution_time_ms: 5
      final_hotkeys: ["R", "D", "T", "A"]

  output:
    hotkey_map: {
      "R": "Research async patterns, design error handling",
      "D": "Design the API",
      "T": "Write tests, ensure integration",
      "A": "Analyze from multiple perspectives"
    }
    display_ready: true
    tokens_used: 120

  total_time_ms: 70
  status: ✅ COMPLETE
```

---

## 8. Advantages of Dynamic Hotkeys

✅ **Self-Documenting**: Letter matches action
✅ **Adaptive**: Changes per execution context
✅ **Conflict-Free**: Automatically resolves duplicates
✅ **Learnable**: Patterns emerge (I=Investigate, D=Design, T=Test)
✅ **Memorable**: More meaningful than arbitrary D/R/E/T
✅ **Accessible**: Numeric fallback (1/2/3/4) always available
✅ **Flexible**: User can override in config
✅ **Transparent**: Show letter → action mapping clearly

---

## 9. Fallback Strategies

```yaml
# If dynamic generation fails or conflicts are unresolvable
fallback_strategies:

  # Strategy 1: Numeric (always works)
  numeric:
    hotkeys: ["1", "2", "3", "4"]
    display: "[1] First suggestion  [2] Second..."
    reliability: 100%
    downside: "Less intuitive than mnemonics"

  # Strategy 2: Traditional (if user prefers)
  traditional_dret:
    hotkeys: ["D", "R", "E", "T"]
    display: "[D] First suggestion  [R] Second..."
    reliability: 100%
    downside: "Doesn't match action"

  # Strategy 3: Agent abbreviation (backup for collision)
    if conflict_unresolvable: use_agent_name_letter
    example: "test-engineer" → "T", "deployment-orchestrator" → "D"

  # Strategy 4: Uppercase/lowercase distinction
    if_two_actions_same_first_letter:
      option_1: "I" (Investigate)
      option_2: "i" (Implement)
    note: "Requires case-sensitive hotkey handling"
```

---

## 10. Configuration Examples

### Config 1: Full Dynamic (Default)

```yaml
hekat_dynamic_hotkeys:
  mnemonic_generation:
    enabled: true
    algorithm: "action_verb_first_letter"
  display:
    show_action_label: true
    show_collision_warning: false
```

**Result**: I/D/T/M or R/P/E/V (changes per execution)

### Config 2: Numeric Fallback Only

```yaml
hekat_dynamic_hotkeys:
  mnemonic_generation:
    enabled: false
  fallback:
    if_no_mnemonic: "use_number"
```

**Result**: Always 1/2/3/4

### Config 3: Hybrid (Dynamic + Numeric)

```yaml
hekat_dynamic_hotkeys:
  mnemonic_generation:
    enabled: true
  display:
    always_show_fallback_numbers: true
```

**Result**: [I]1  [D]2  [T]3  [M]4 (user can use either)

---

## Summary: Dynamic > Static

| Aspect | Static (D/R/E/T) | Dynamic (Generated) |
|--------|------------------|-------------------|
| **Matches action?** | No | ✅ Yes |
| **Context-aware?** | No | ✅ Yes |
| **Conflict possible?** | Never (hardcoded) | ✅ Handled automatically |
| **Self-documenting?** | No (arbitrary) | ✅ Yes (letter ≈ action) |
| **Memorable?** | Medium | ✅ High |
| **Learning curve?** | Medium | ✅ Low (patterns emerge) |

**Winner**: Dynamic hotkeys 🎯

---

**Status**: Ready to replace static D/R/E/T spec
**Next**: Integrate into main HEKAT_HELPER_SPECIFICATION.md
