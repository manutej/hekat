# Hekat-Helper: Hotkeys Quick Reference

**Status**: ✅ Complete with full specification
**File**: `/tmp/hekat/HEKAT_HELPER_HOTKEYS_SPECIFICATION.md`

---

## Quick Hotkey Map

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║  [D] DEVELOP       [R] RESEARCH       [E] EDIT THINKING      [T] TEST/NEXT  ║
║                                                                               ║
║  [?] Help          [TAB] Full Query   [/] Explain            [ESC] Close     ║
║  [C] Custom        [Ctrl+H] History   [Ctrl+B] Ranking       [q] Alt-Close   ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## The 4 Main Options (Always Available)

| Key | Option | Purpose | Query Type |
|-----|--------|---------|-----------|
| **D** | DEVELOP | Implement the next step | Implementation-focused |
| **R** | RESEARCH | Investigate deeper | Research-focused |
| **E** | EDIT THINKING | Reconsider the approach | Reflection/refinement |
| **T** | TEST/DEPLOY/NEXT | Context-aware option | Varies by situation |

---

## Supporting Hotkeys

| Key | Action | Description |
|-----|--------|-------------|
| **?** | Help | Show keyboard shortcuts |
| **/** | Explain | Show why each option ranked where it did |
| **TAB** | Full Query | See complete query text |
| **C** | Custom | Write your own Hekat DSL query |
| **Esc** | Dismiss | Close suggestions |
| **q** | Alt-Dismiss | Alternative to Escape |

---

## Context-Dependent 4th Option (T)

The **T** key intelligently changes based on what you just completed:

```
After code implementation:  T = TEST       (test-engineer : 'add tests')
After research:            T = EVALUATE   (mercurio-orchestrator : 'evaluate')
After design:              T = IMPLEMENT  (practical-programmer : 'code')
After testing:             T = DEPLOY     (deployment-orchestrator : 'ship')
Default:                   T = NEXT       (practical-programmer : 'what next?')
```

---

## Accessibility Options

If you prefer different keys:

```yaml
# Numbers instead of D/R/E/T
active_scheme: "numbers"
→ Use: 1, 2, 3, 4

# Arrow keys only
active_scheme: "arrows"
→ Use: ↑ (develop), ↓ (research), ← (edit), → (test)

# Vim keys
active_scheme: "vim"
→ Use: j, k, l, h (Enter to execute)

# Configure in: ~/.claude/hekat/keybindings.yaml
```

---

## User Interface Example

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ HEKAT-HELPER: Next Steps (Backend Async Pattern - Level 5)                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║ [D] DEVELOP - Implement Next                                                ║
║     Level 5 | Confidence: 0.95 | Est. Tokens: 1850                          ║
║     → (deep-researcher || api-architect) -> practical-programmer            ║
║     Why: 95% success for backend-async-moderate                             ║
║                                                                               ║
║ [R] RESEARCH - Investigate Deeper                                           ║
║     Level 4 | Confidence: 0.78 | Est. Tokens: 1200                          ║
║     → deep-researcher -> api-architect                                       ║
║     Why: 78% success rate for research-first                                ║
║                                                                               ║
║ [E] EDIT THINKING - Reconsider Approach                                     ║
║     Level 5 | Confidence: 0.72 | Est. Tokens: 1400                          ║
║     → mercurio-orchestrator : 'multi-perspective analysis'                   ║
║     Why: 72% success for architectural review                               ║
║                                                                               ║
║ [T] TEST & VALIDATE - Quality Focus                                         ║
║     Level 5 | Confidence: 0.85 | Est. Tokens: 1600                          ║
║     → test-engineer -> frontend-architect                                    ║
║     Why: 85% success when focusing on quality                               ║
║                                                                               ║
║ [?] Help  [TAB] Full Query  [/] Explanation  [C] Custom  [ESC] Close        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Your choice? (D/R/E/T or custom):  _                                        ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## Example Usage Flow

```
User presses "?"
  → Shows help overlay

User presses "TAB"
  → Expands full query text

User presses "/"
  → Shows explanation: "Why: 95% success rate for backend-async pattern"

User presses "D"
  → Highlights DEVELOP option
  → Shows: "Executing: deep-researcher || api-architect..."
  → Overlay fades, execution begins

User now can type normally
  → D/R/E/T work as regular text input in editor
  → Hotkeys only active when Hekat overlay is showing
```

---

## Configuration File

Edit: `~/.claude/hekat/keybindings.yaml`

```yaml
hekat_keybindings:
  preferences:
    active_scheme: "dret"          # Options: dret, numbers, arrows, vim
    confirmation_required: false   # Press key twice to confirm
    case_sensitive: false          # "d" and "D" both work
    show_hint_text: true           # Show "(D)evelop" hints
    auto_dismiss_on_execution: true # Close overlay after executing
```

---

## Full Specification

For complete details, see:
**`/tmp/hekat/HEKAT_HELPER_HOTKEYS_SPECIFICATION.md`** (20 KB, 650+ lines)

Includes:
- Full hotkey lifecycle and state management
- Accessibility options (screen readers, high contrast, voice)
- Checkpoint format for hotkey testing
- Integration with Claude Code's hotkey system
- Configuration schema
- Fallback behavior
- User preference examples

---

**Status**: ✅ Ready for implementation
**Next**: Integrate hotkey spec into main HEKAT_HELPER_SPECIFICATION.md Part 4 (Integration)
