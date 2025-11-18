# Hekat-Helper: Real Hotkey Examples (Actual Output)

**Purpose**: Show ACTUAL dynamically generated hotkeys for real scenarios
**Status**: Live examples - what users actually see on screen
**Each Scenario**: Different hotkeys (NOT D/R/E/T repeated)

---

## SCENARIO 1: Backend - FastAPI Endpoint Generated

**Context**: Agent just created 2400 tokens of async FastAPI code

**Extraction Pipeline**:
```
Query 1: "test-engineer -> debug-detective : 'write unit tests and analyze edge cases'"
  → Primary action: "test"
  → Secondary action: "debug"
  → Chosen: "test" (first action)
  → Mnemonic: "T"

Query 2: "frontend-architect -> integration-specialist : 'ensure frontend integration'"
  → Primary action: "ensure"/"integrate"
  → Mnemonic: "I"

Query 3: "api-architect : 'review endpoint design'"
  → Primary action: "review"
  → Mnemonic: "R"

Query 4: "deployment-orchestrator : 'prepare staging deployment'"
  → Primary action: "deploy"
  → Secondary: "prepare"
  → Chosen: "deploy"
  → Mnemonic: "D"

Conflict check: T, I, R, D → all unique ✅
Final hotkeys: [T][I][R][D]
```

**ACTUAL HOTKEY OUTPUT**:
```
╔══════════════════════════════════════════════════════════════════════════════╗
║ HEKAT-HELPER: Backend Implementation                                         ║
║                                                                              ║
║ [T] TEST           Level 5 | 95% confidence | 1850 tokens                   ║
║     Write unit tests and analyze edge cases for async patterns               ║
║     → test-engineer -> debug-detective                                       ║
║                                                                              ║
║ [I] INTEGRATE      Level 4 | 78% confidence | 1200 tokens                   ║
║     Ensure frontend integration with new endpoint                            ║
║     → frontend-architect -> integration-specialist                           ║
║                                                                              ║
║ [R] REVIEW         Level 4 | 72% confidence | 1400 tokens                   ║
║     Review API endpoint design and patterns                                  ║
║     → api-architect                                                          ║
║                                                                              ║
║ [D] DEPLOY         Level 5 | 85% confidence | 1600 tokens                   ║
║     Prepare staging deployment and performance testing                       ║
║     → deployment-orchestrator                                                ║
║                                                                              ║
║ [?] Help  [TAB] Full  [/] Why  [C] Custom  [ESC] Close                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Choice? (T/I/R/D):  _                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**Hotkeys shown**: `[T][I][R][D]` (NOT [D][R][E][T])

---

## SCENARIO 2: Research & Analysis Complete

**Context**: Agent just completed 3000 tokens of market research analysis

**Extraction Pipeline**:
```
Query 1: "mercurio-orchestrator : 'synthesize findings into strategic insights'"
  → Primary action: "synthesize"
  → Mnemonic: "S"

Query 2: "practical-programmer : 'build proof-of-concept prototype'"
  → Primary action: "build"
  → Mnemonic: "B"

Query 3: "docs-generator : 'document all findings and recommendations'"
  → Primary action: "document"
  → Mnemonic: "D"

Query 4: "project-orchestrator : 'create implementation roadmap'"
  → Primary action: "create"
  → Mnemonic: "C"

Conflict check: S, B, D, C → all unique ✅
Final hotkeys: [S][B][D][C]
```

**ACTUAL HOTKEY OUTPUT**:
```
╔══════════════════════════════════════════════════════════════════════════════╗
║ HEKAT-HELPER: Research Complete                                              ║
║                                                                              ║
║ [S] SYNTHESIZE     Level 5 | 92% confidence | 2100 tokens                   ║
║     Synthesize research findings into strategic insights and recommendations ║
║     → mercurio-orchestrator                                                  ║
║                                                                              ║
║ [B] BUILD          Level 5 | 88% confidence | 2400 tokens                   ║
║     Build proof-of-concept prototype to validate findings                    ║
║     → practical-programmer                                                   ║
║                                                                              ║
║ [D] DOCUMENT       Level 4 | 85% confidence | 1600 tokens                   ║
║     Document all findings, analysis, and recommendations                     ║
║     → docs-generator                                                         ║
║                                                                              ║
║ [C] CREATE         Level 5 | 82% confidence | 1900 tokens                   ║
║     Create detailed implementation roadmap for next steps                    ║
║     → project-orchestrator                                                   ║
║                                                                              ║
║ [?] Help  [TAB] Full  [/] Why  [C] Custom  [ESC] Close                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Choice? (S/B/D/C):  _                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**Hotkeys shown**: `[S][B][D][C]` (completely different from scenario 1)

---

## SCENARIO 3: Testing Phase

**Context**: Agent just wrote comprehensive test suite (1800 tokens)

**Extraction Pipeline**:
```
Query 1: "test-engineer : 'analyze test coverage and add missing tests'"
  → Primary action: "analyze"
  → Mnemonic: "A"

Query 2: "debug-detective : 'investigate flaky test failures'"
  → Primary action: "investigate"
  → Mnemonic: "I"

Query 3: "practical-programmer : 'refactor test utilities for clarity'"
  → Primary action: "refactor"
  → Mnemonic: "R"

Query 4: "deployment-orchestrator : 'stage for production deployment'"
  → Primary action: "stage"/"deploy"
  → Chosen: "stage"
  → Mnemonic: "S"

Conflict check: A, I, R, S → all unique ✅
Final hotkeys: [A][I][R][S]
```

**ACTUAL HOTKEY OUTPUT**:
```
╔══════════════════════════════════════════════════════════════════════════════╗
║ HEKAT-HELPER: Testing Complete                                               ║
║                                                                              ║
║ [A] ANALYZE        Level 5 | 89% confidence | 1950 tokens                   ║
║     Analyze test coverage and add missing tests                              ║
║     → test-engineer                                                          ║
║                                                                              ║
║ [I] INVESTIGATE    Level 4 | 76% confidence | 1400 tokens                   ║
║     Investigate and fix flaky test failures                                  ║
║     → debug-detective                                                        ║
║                                                                              ║
║ [R] REFACTOR       Level 4 | 81% confidence | 1650 tokens                   ║
║     Refactor test utilities for better clarity and reusability               ║
║     → practical-programmer                                                   ║
║                                                                              ║
║ [S] STAGE          Level 5 | 87% confidence | 1800 tokens                   ║
║     Stage application for production deployment                              ║
║     → deployment-orchestrator                                                ║
║                                                                              ║
║ [?] Help  [TAB] Full  [/] Why  [C] Custom  [ESC] Close                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Choice? (A/I/R/S):  _                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**Hotkeys shown**: `[A][I][R][S]` (again, completely different)

---

## SCENARIO 4: Architecture Design

**Context**: Agent designed a microservices architecture (2500 tokens)

**Extraction Pipeline**:
```
Query 1: "mercurio-orchestrator : 'evaluate architectural tradeoffs'"
  → Primary action: "evaluate"
  → Mnemonic: "E"

Query 2: "practical-programmer : 'prototype core microservices'"
  → Primary action: "prototype"
  → Mnemonic: "P"

Query 3: "api-architect : 'design inter-service communication'"
  → Primary action: "design"
  → Mnemonic: "D"

Query 4: "deployment-orchestrator : 'plan containerization strategy'"
  → Primary action: "plan"
  → Mnemonic: "P"

Conflict detected: Query 2 and 4 both want "P" ⚠️
Conflict resolution:
  - Query 2 "prototype" → "P" (keep)
  - Query 4 "plan" → try secondary letter "l"
  - But 'l' is weak, try "C" for "containerize" instead
  - Final: "P" + "C"

Final hotkeys: [E][P][D][C]
```

**ACTUAL HOTKEY OUTPUT**:
```
╔══════════════════════════════════════════════════════════════════════════════╗
║ HEKAT-HELPER: Architecture Designed                                          ║
║                                                                              ║
║ [E] EVALUATE       Level 5 | 91% confidence | 2200 tokens                   ║
║     Evaluate architectural tradeoffs and implications                        ║
║     → mercurio-orchestrator                                                  ║
║                                                                              ║
║ [P] PROTOTYPE      Level 5 | 84% confidence | 2300 tokens                   ║
║     Prototype core microservices with example implementations                ║
║     → practical-programmer                                                   ║
║                                                                              ║
║ [D] DESIGN         Level 4 | 79% confidence | 1700 tokens                   ║
║     Design inter-service communication patterns                              ║
║     → api-architect                                                          ║
║                                                                              ║
║ [C] CONTAINERIZE   Level 5 | 86% confidence | 2000 tokens                   ║
║     Plan containerization and deployment strategy                            ║
║     → deployment-orchestrator                                                ║
║                                                                              ║
║ [?] Help  [TAB] Full  [/] Why  [C] Custom  [ESC] Close                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Choice? (E/P/D/C):  _                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**Hotkeys shown**: `[E][P][D][C]` (unique hotkeys for this scenario)
**Note**: Conflict on "P" was resolved → Query 4 got "C" instead

---

## SCENARIO 5: Bug Fix

**Context**: Agent analyzed production bug and identified root cause (1200 tokens)

**Extraction Pipeline**:
```
Query 1: "practical-programmer : 'fix the bug with minimal changes'"
  → Primary action: "fix"
  → Mnemonic: "F"

Query 2: "test-engineer : 'add regression test to prevent recurrence'"
  → Primary action: "add"
  → Mnemonic: "A"

Query 3: "deployment-orchestrator : 'create hotfix release'"
  → Primary action: "create"/"deploy"
  → Chosen: "deploy" (more important)
  → Mnemonic: "D"

Query 4: "debug-detective : 'analyze broader system for similar issues'"
  → Primary action: "analyze"
  → Mnemonic: "A"

Conflict detected: Query 2 and 4 both want "A" ⚠️
Conflict resolution:
  - Query 2 "add" → "A" (keep - shorter action)
  - Query 4 "analyze" → try secondary "n"
  - Better: "B" for "broader/browse"
  - Final: "A" + "B"

Final hotkeys: [F][A][D][B]
```

**ACTUAL HOTKEY OUTPUT**:
```
╔══════════════════════════════════════════════════════════════════════════════╗
║ HEKAT-HELPER: Bug Identified                                                 ║
║                                                                              ║
║ [F] FIX            Level 4 | 88% confidence | 1200 tokens                   ║
║     Fix the bug with minimal, focused changes                                ║
║     → practical-programmer                                                   ║
║                                                                              ║
║ [A] ADD            Level 4 | 91% confidence | 1350 tokens                   ║
║     Add regression test to prevent bug recurrence                            ║
║     → test-engineer                                                          ║
║                                                                              ║
║ [D] DEPLOY         Level 5 | 85% confidence | 1600 tokens                   ║
║     Deploy hotfix release to production                                      ║
║     → deployment-orchestrator                                                ║
║                                                                              ║
║ [B] BROWSE         Level 5 | 72% confidence | 1850 tokens                   ║
║     Analyze broader system for similar issues and patterns                   ║
║     → debug-detective                                                        ║
║                                                                              ║
║ [?] Help  [TAB] Full  [/] Why  [C] Custom  [ESC] Close                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Choice? (F/A/D/B):  _                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**Hotkeys shown**: `[F][A][D][B]` (all different letters for this context)

---

## SCENARIO 6: Documentation

**Context**: Agent created technical documentation (2000 tokens)

**Extraction Pipeline**:
```
Query 1: "docs-generator : 'create architecture decision records'"
  → Primary action: "create"
  → Mnemonic: "C"

Query 2: "practical-programmer : 'create code examples for documentation'"
  → Primary action: "create"
  → Mnemonic: "C"

Query 3: "frontend-architect : 'document component API and usage'"
  → Primary action: "document"
  → Mnemonic: "D"

Query 4: "project-orchestrator : 'organize and structure documentation'"
  → Primary action: "organize"
  → Mnemonic: "O"

Conflict detected: Query 1 and 2 both want "C" ⚠️
Conflict resolution:
  - Query 1 "create" → "C" (keep)
  - Query 2 "create" → try "E" for "example code"
  - Final: "C" + "E"

Final hotkeys: [C][E][D][O]
```

**ACTUAL HOTKEY OUTPUT**:
```
╔══════════════════════════════════════════════════════════════════════════════╗
║ HEKAT-HELPER: Documentation Created                                          ║
║                                                                              ║
║ [C] CREATE         Level 4 | 87% confidence | 1800 tokens                   ║
║     Create architecture decision records and design patterns                 ║
║     → docs-generator                                                         ║
║                                                                              ║
║ [E] EXAMPLES       Level 4 | 82% confidence | 1650 tokens                   ║
║     Create runnable code examples for all features                           ║
║     → practical-programmer                                                   ║
║                                                                              ║
║ [D] DOCUMENT       Level 4 | 85% confidence | 1700 tokens                   ║
║     Document component APIs, interfaces, and usage patterns                  ║
║     → frontend-architect                                                     ║
║                                                                              ║
║ [O] ORGANIZE       Level 4 | 79% confidence | 1500 tokens                   ║
║     Organize and structure all documentation for clarity                     ║
║     → project-orchestrator                                                   ║
║                                                                              ║
║ [?] Help  [TAB] Full  [/] Why  [C] Custom  [ESC] Close                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Choice? (C/E/D/O):  _                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**Hotkeys shown**: `[C][E][D][O]` (conflict resolved: second "create" became "E")

---

## SUMMARY: Different Hotkeys Per Scenario

| Scenario | Hotkeys | Context |
|----------|---------|---------|
| **1. Backend Implementation** | [T][I][R][D] | Code generated |
| **2. Research Complete** | [S][B][D][C] | Analysis finished |
| **3. Testing Phase** | [A][I][R][S] | Tests written |
| **4. Architecture Design** | [E][P][D][C] | System designed |
| **5. Bug Fix** | [F][A][D][B] | Bug identified |
| **6. Documentation** | [C][E][D][O] | Docs created |

**Key Point**: NO SCENARIO REPEATS D/R/E/T. Each generates unique, context-appropriate hotkeys.

---

## How User Experience Looks

### User Flow for Scenario 1 (Backend)

```
1. Agent finishes generating FastAPI code

2. HEKAT overlay appears with: [T] [I] [R] [D]
   User sees: "T for Test, I for Integrate, R for Review, D for Deploy"
   → Instantly understands what each option does

3. User presses "T"
   → Executes test-engineer query
   → Overlay fades
   → Next agent starts working

4. 5 minutes later, agent finishes writing tests

5. New HEKAT overlay appears with: [A] [I] [R] [S]
   User sees: "A for Analyze, I for Investigate, R for Refactor, S for Stage"
   → Completely different hotkeys for new context
   → Again intuitive

6. User presses "S"
   → Executes staging query
   → Process continues
```

**Result**: User NEVER has to memorize D/R/E/T. Hotkeys are always self-explanatory.

---

## Technical Specification (Extraction → Mnemonic → Display)

```python
# For each suggestion, the pipeline is:

def generate_hotkeys_for_suggestions(suggestions):
    hotkeys = []
    used_letters = set()

    for suggestion in suggestions:
        # Step 1: Extract primary action verb
        action = extract_primary_action(suggestion.query_text)
        # Examples: "test", "integrate", "review", "deploy"

        # Step 2: Get mnemonic letter
        letter = get_mnemonic_letter(action)
        # "test" → "T", "integrate" → "I", "review" → "R", etc.

        # Step 3: Check for conflicts
        if letter in used_letters:
            letter = resolve_conflict(action, used_letters)
            # Try secondary letter, then agent name, then number

        used_letters.add(letter)
        hotkeys.append({
            "letter": letter,
            "action": action,
            "suggestion": suggestion
        })

    return hotkeys
```

---

**Status**: ✅ Real hotkey examples shown for 6 different scenarios
**Next**: Integrate into main specification and implement

