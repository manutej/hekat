# Hekat Implementation Specification

**Status**: Ready for Tool Invocation
**Date**: 2025-10-27
**Next**: `/meta-agent` → `/meta-skill-builder` → `/wflw` → `/create-command`

---

## Clarifications (From User Feedback)

### Entry Points

```bash
/hekat "verbal command"           # Natural language query
/hekat "flag"                     # Specific instruction
/hekat ```dsl query```            # Direct DSL
/hekat::path/to/doc              # Load document as query
/hekat -l 7                       # Level 7 only
/hekat -l 3 --minimal            # Level 3, compact display
```

### Display Preferences

- **Default**: `/hekat --full` (expanded, with explanations)
- **Alternative**: `/hekat --minimal` (single-line compact)
- **Persistent**: User preference saved across session

### Level System

- **Default**: Level 3 (execution speed + token efficiency)
- **User override**: `-l 3` through `-l 7`
- **Behavior**: Shows ONLY queries at specified level (no fallbacks)

### Mode Persistence

- ✅ Persists across entire session
- ✅ Carries context from previous `/hekat` invocations
- ✅ Can eventually become automatic profile preference

### Hotkey Conflict Resolution

- Strategy: **Fastest without conflict**
- Display: Show final hotkeys only (no "resolution showed" messages)
- Algorithm: Primary letter → secondary letter → context word → numeric

### Task-Relay Integration

**Task-Relay is a sub-mode within `/hekat`**

Tracks:
- Agent execution timing
- Token consumption per phase
- Time spent per operation
- Checkpoint logging (before display + after execution)

Follows: `~/.claude/task-relay.md` (ABSOLUTE MUST)

### Document References

```
/hekat::LUXOR/PROJECTS/hekat/tmp/HEKAT_HELPER_SPECIFICATION.md
/hekat::LUXOR/PROJECTS/hekat/tmp/HEKAT_HOTKEYS_REAL_EXAMPLES.md
/hekat::path/to/any/document
```

Loads document, treats it as context + query for `/hekat` mode.

---

## Architecture (What to Build)

### 1. `/hekat` Command (Slash Command)
- Entry point for all Hekat queries
- Parses input type (verbal, flag, DSL, document reference)
- Displays 4 dynamic hotkey options
- Enforces task-relay protocol
- Persists mode across session

### 2. `hekat` Skill (Domain-Specific Language Expertise)
- Knowledge about Hekat DSL (8 query types, levels 3-7)
- Dynamic hotkey generation rules
- Query selection patterns
- Domain-agnostic verb-to-letter mapping
- Level characteristics and constraints
- Task-relay best practices

### 3. `hekat-agent` Agent
- Reads LUXOR/PROJECTS/hekat/ files
- Constructs queries based on context
- Understands flags (`-l 7`, `-c`, etc.)
- Generates confidence scores
- Integrates consciousness patterns
- Provides explanations for rankings

### 4. `/wflw` Hekat Workflow
- Orchestrates `/hekat` mode across multi-step tasks
- Task-relay checkpointing at each step
- Consciousness pattern accumulation
- Fallback strategies for low-confidence scenarios

---

## Sub-Documentation (Knowledge Spreading)

The **hekat skill** should reference modular docs:

```
LUXOR/PROJECTS/hekat/tmp/
├── HEKAT_HELPER_SPECIFICATION.md          [Core architecture]
├── HEKAT_HOTKEYS_REAL_EXAMPLES.md         [UI patterns, 6 scenarios]
├── HEKAT_HOTKEYS_GENERAL_PURPOSE.md       [Generality proof, 10 domains]
├── HEKAT_HELPER_HOTKEYS_DYNAMIC.md        [Algorithm, conflict resolution]
├── DYNAMIC_HOTKEYS_SUMMARY.md             [Evolution, before/after]
├── NEXT_STEPS_FROM_DOCS.md                [Decision points]
└── skill-reference/ (NEW)
    ├── query-types.md                     [8 Hekat query types explained]
    ├── levels-3-7.md                      [Level characteristics & when to use]
    ├── verb-to-letter-map.md              [Complete mnemonic mapping]
    ├── task-relay-protocol.md             [How to track tokens/time/phases]
    ├── conflict-resolution-rules.md       [Hotkey collision algorithm]
    └── consciousness-patterns.md          [Pattern storage & matching]
```

---

## Tools to Invoke (In Order)

### 1. Create Hekat Agent Spec
```bash
/meta-agent "Hekat DSL dynamic query builder..."
→ Outputs: Agent specification YAML
```

### 2. Create Hekat Skill Spec
```bash
/meta-skill-builder "hekat" --references="LUXOR/PROJECTS/hekat/tmp/"
→ Outputs: Skill structure with sub-doc references
```

### 3. Create Hekat Workflow
```bash
/wflw hekat-workflow --type="multi-step" --hekat-aware
→ Outputs: Workflow YAML with task-relay integration
```

### 4. Create /hekat Command
```bash
/create-command hekat-command --dry-run --examples-heavy
→ Outputs: Command file with 15+ examples
```

---

## Key Requirements (Non-Negotiable)

✅ **Task-Relay Compliance**: EVERY operation follows `~/.claude/task-relay.md`
✅ **Dynamic Hotkeys**: Generated fresh per execution, not hardcoded
✅ **Level System**: Respects `-l` flag, defaults to 3
✅ **Persistence**: Mode stays active across session
✅ **Document References**: Support `/hekat::path/to/doc`
✅ **Preference Storage**: `--full` vs `--minimal` remembers user choice
✅ **Conflict-Free**: Hotkey algorithm guarantees no collisions
✅ **Sub-Documentation**: Skill references modular knowledge base

---

## Ready for Tool Invocation

All questions answered. All architecture clear.

**Next Action**: Invoke tools in order:
1. `/meta-agent` (agent spec)
2. `/meta-skill-builder` (skill structure)
3. `/wflw` (workflow)
4. `/create-command` (command)

Should I proceed?

