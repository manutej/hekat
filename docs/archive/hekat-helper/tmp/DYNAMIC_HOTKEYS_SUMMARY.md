# Hekat-Helper Hotkeys: Static → Dynamic Evolution

**Status**: Architecture evolved based on user insight ✨
**Created**: 2025-10-27 (after review)
**Impact**: Better UX, self-documenting, context-aware

---

## The Insight 💡

**User**: "Hotkeys should be DYNAMIC, generated from the actual suggestion concepts"

**Why This Is Better**:
- ❌ **Static D/R/E/T**: Arbitrary, doesn't match context
- ✅ **Dynamic I/D/T/M**: Generated from actions, self-documenting

---

## Evolution: Before → After

### BEFORE (Static)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ HEKAT-HELPER: Next Steps
║
║ [D] DEVELOP       [R] RESEARCH      [E] EDIT THINKING     [T] TEST
║
║ [?] Help  [TAB] Full Query  [/] Explain  [C] Custom  [ESC] Close
╚══════════════════════════════════════════════════════════════════════════════╝

User experience: "D = Develop? But I don't see anything about developing..."
```

**Problem**: D/R/E/T are arbitrary. User must memorize them.

---

### AFTER (Dynamic)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ HEKAT-HELPER: Smart Next Steps
║
║ [I] INVESTIGATE   Level 5 | 0.95 confidence | 1850 tokens
║     Research async patterns, design, implement
║
║ [D] DESIGN        Level 4 | 0.78 confidence | 1200 tokens
║     Design the API, implement solution
║
║ [T] TEST          Level 5 | 0.72 confidence | 1400 tokens
║     Write tests, ensure integration
║
║ [M] MULTI-PERSPECTIVE  Level 5 | 0.85 confidence | 1600 tokens
║     Analyze from multiple perspectives
║
║ [?] Help  [TAB] Full Query  [/] Explain  [C] Custom  [ESC] Close
╚══════════════════════════════════════════════════════════════════════════════╝

User experience: "I = Investigate, D = Design, T = Test, M = Multi-perspective"
```

**Benefit**: Hotkeys match the actual actions. Self-documenting.

---

## How It Works: Dynamic Generation

```
EXECUTION COMPLETE
    ↓
SELECT 4 QUERIES FROM LATTICE
    ├─ Query 1: "(deep-researcher || api-architect) -> practical-programmer : 'research...'"
    ├─ Query 2: "api-architect -> practical-programmer : 'design...'"
    ├─ Query 3: "test-engineer -> frontend-architect : 'write tests...'"
    └─ Query 4: "mercurio-orchestrator : 'analyze from angles...'"
    ↓
EXTRACT PRIMARY ACTION FROM EACH QUERY
    ├─ Query 1 → "research" / "investigate"
    ├─ Query 2 → "design"
    ├─ Query 3 → "test"
    └─ Query 4 → "analyze"
    ↓
GENERATE MNEMONIC LETTER
    ├─ "research" → "R" (but could conflict)
    ├─ "design" → "D"
    ├─ "test" → "T"
    └─ "analyze" → "A"
    ↓
RESOLVE CONFLICTS (if any)
    ├─ If two queries want "R", use "R" for primary, "R" → "I" for secondary
    └─ If still conflicting, use second letter or agent abbreviation
    ↓
DISPLAY WITH GENERATED HOTKEYS
    ├─ [I] INVESTIGATE
    ├─ [D] DESIGN
    ├─ [T] TEST
    └─ [A] ANALYZE
    ↓
USER PRESSES A KEY
    └─ "I" → Execute suggestion 1 (Investigate)
```

---

## Real Examples Across Different Contexts

### Context 1: After Code Implementation

```
✅ Agent just generated 2400 tokens of FastAPI code

HEKAT-HELPER (AUTOMATICALLY GENERATED HOTKEYS):

[W] WRITE       (write comprehensive tests)
[D] DEBUG       (debug and analyze edge cases)
[I] INTEGRATE   (integrate with frontend)
[V] VALIDATE    (validate and stage for deployment)

User presses "W" → Executes test-engineer query
```

---

### Context 2: After Architecture Design

```
✅ Agent just documented a system architecture

HEKAT-HELPER (AUTOMATICALLY GENERATED HOTKEYS):

[E] EVALUATE    (evaluate tradeoffs)
[D] DOCUMENT    (create detailed docs)
[P] PROTOTYPE   (build proof-of-concept)
[V] VALIDATE    (validate assumptions)

User presses "P" → Executes practical-programmer query
```

---

### Context 3: After Research/Analysis

```
✅ Agent just completed technology research

HEKAT-HELPER (AUTOMATICALLY GENERATED HOTKEYS):

[S] SYNTHESIZE  (synthesize findings)
[B] BUILD       (build prototype)
[I] INTEGRATE   (integrate with current system)
[A] ARCHIVE     (document for future reference)

User presses "S" → Executes mercurio-orchestrator query
```

---

### Context 4: Bug Investigation

```
✅ Agent just analyzed a production bug

HEKAT-HELPER (AUTOMATICALLY GENERATED HOTKEYS):

[F] FIX         (fix the bug)
[T] TEST        (add regression tests)
[D] DEPLOY      (deploy hotfix)
[M] MONITOR     (monitor in production)

User presses "F" → Executes practical-programmer query
```

---

## Algorithm Overview

### Mnemonic Letter Extraction

```python
def extract_mnemonic(hekat_query):
    """
    Extract primary action from Hekat query and generate hotkey.

    Examples:
    - "deep-researcher : 'investigate patterns'"  → "I" (Investigate)
    - "api-architect : 'design the API'"           → "D" (Design)
    - "test-engineer : 'write tests'"              → "W" (Write)
    - "deployment-orchestrator : 'ship it'"        → "S" (Ship)
    - "mercurio-orchestrator : 'evaluate'"         → "E" (Evaluate)
    - "docs-generator : 'document'"                → "D" (Document)
    - "practical-programmer : 'build'"             → "B" (Build)
    - "debug-detective : 'fix'"                    → "F" (Fix)
    """

    action = extract_primary_action_verb(hekat_query)
    letter = get_mnemonic_letter(action)
    return letter
```

### Conflict Resolution

```
If two suggestions want same letter:

Attempt 1: Use second letter
  "Design" + "Deploy" → "D" + "D"
  → Try "e" (dEsign) and "e" (dEploy)
  → Still conflict!

Attempt 2: Use more distinctive letter
  "Design" → "D"
  "Deploy" → "S" (deploy → "S" for Ship/Send)
  → Solved!

If still conflict: Use numeric [1][2][3][4]
  (But this is rare in practice)
```

---

## Configuration (User Can Override)

**File**: `~/.claude/hekat/hotkey_config.yaml`

```yaml
hekat_dynamic_hotkeys:
  # Enable/disable dynamic generation
  enabled: true

  # What to do if conflicts arise
  conflict_resolution: "secondary_letter"  # or "agent_abbrev", "numeric"

  # Custom letter overrides (if you want specific mapping)
  custom_mappings:
    "implement": "I"
    "multi-perspective": "M"
    "fast-implementation": "F"

  # Fallback if user prefers traditional
  prefer_traditional_dret: false
  prefer_numeric: false

  # Display options
  show_action_label: true
  show_explanation: true
```

**Result**: Works out of box, fully customizable.

---

## Benefits Summary

| Aspect | Static D/R/E/T | Dynamic Generated |
|--------|---|---|
| **Self-documenting?** | ❌ No (arbitrary) | ✅ Yes (matches action) |
| **Context-aware?** | ❌ No (always same) | ✅ Yes (changes per execution) |
| **Memorable?** | ⚠️ Medium (must memorize) | ✅ High (letter ≈ action) |
| **Conflicts?** | ❌ Never | ✅ Handled automatically |
| **Learning curve?** | ⚠️ Medium | ✅ Low (patterns emerge) |
| **Flexibility?** | ❌ Fixed | ✅ Adaptive |
| **User control?** | ❌ None | ✅ Full (can customize) |

**Winner**: Dynamic generation is objectively better 🎯

---

## Files Delivered

### Static Version (Original - Now Superseded)
```
❌ /tmp/hekat/HEKAT_HELPER_HOTKEYS_SPECIFICATION.md (20 KB)
   └─ Hardcoded D/R/E/T approach
```

### Dynamic Version (New - Recommended) ✅
```
✅ /tmp/hekat/HEKAT_HELPER_HOTKEYS_DYNAMIC.md (20 KB)
   ├─ Dynamic mnemonic generation algorithm
   ├─ Conflict resolution strategies
   ├─ Real-world examples
   ├─ Configuration options
   └─ Integration points
```

---

## Next Steps

### 1. Update Main Specification ⏭️
Replace Part 4 (Integration) in `HEKAT_HELPER_SPECIFICATION.md`:
- Remove static hotkey section
- Add reference to dynamic hotkeys spec
- Update UI examples to show dynamic keys

### 2. Implementation Order
```
Step 1: Implement mnemonic extraction algorithm
Step 2: Add conflict resolution logic
Step 3: Integrate with hotkey generator
Step 4: Add configuration file support
Step 5: Test with 100+ real execution scenarios
```

### 3. Success Metrics
```
✅ 95%+ of executions generate unique, meaningful hotkeys
✅ User doesn't have to memorize D/R/E/T
✅ Hotkey letter matches visible action label
✅ Fallback to numbers works seamlessly
```

---

## Example: Full Integration

```python
# Hekat-Helper execution flow with dynamic hotkeys

def hekat_helper_post_execution(output_context):
    # 1. Get 4 query candidates from lattice
    candidates = select_query_candidates(output_context)

    # 2. Extract actions from each
    actions = [extract_action(c.query) for c in candidates]

    # 3. Generate hotkeys dynamically
    hotkeys = generate_dynamic_hotkeys(actions)
    # Returns: ['I', 'D', 'T', 'M'] (or however they resolve)

    # 4. Display with generated hotkeys
    display_hekat_overlay(candidates, actions, hotkeys)
    #    Shows: [I] Investigate, [D] Design, [T] Test, [M] Multi-perspective

    # 5. Wait for user input
    user_key = wait_for_keypress()  # User presses 'I'

    # 6. Execute selected query
    execute_hekat_query(candidates[hotkeys.index('I')])
```

---

## Comparison: Before vs After

### Before User Feedback
```
User sees: [D] DEVELOP [R] RESEARCH [E] EDIT [T] TEST
User thinks: "What key does what again?"
User must memorize arbitrary mapping
```

### After User Feedback (Now)
```
User sees: [I] INVESTIGATE [D] DESIGN [T] TEST [M] MULTI-PERSPECTIVE
User thinks: "Oh, easy. I for Investigate, D for Design..."
User learns naturally from context
No memorization needed
```

**This is exactly what good UI design looks like** 🎯

---

## Status

**Dynamic Hotkeys Specification**: ✅ Complete
**Location**: `/tmp/hekat/HEKAT_HELPER_HOTKEYS_DYNAMIC.md`
**Ready for**: Implementation planning

---

**Thank you for the insight!** This evolution from static → dynamic makes the system significantly more intuitive and user-friendly.
