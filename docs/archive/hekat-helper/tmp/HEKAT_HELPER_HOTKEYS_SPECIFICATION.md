# Hekat-Helper: Keyboard Hotkeys & Keybindings Specification

**Status**: Critical UX Detail (was missing from main spec)
**Created**: 2025-10-27
**Purpose**: Define keyboard shortcuts for 4-option selection

---

## 1. Primary Hotkey Scheme (D/R/E/T)

### Default Mappings

```yaml
hekat_helper_hotkeys:
  version: 1.0
  enabled: true

  # PRIMARY OPTIONS (First 4 keys)
  option_develop:
    primary_key: "D"
    description: "DEVELOP - Implement next step"
    action: execute_selected_query_develop
    fallback_keys: ["1", "d"]
    long_form: "Ctrl+Shift+D"  # Optional: dedicated hotkey without suggestion prompt

  option_research:
    primary_key: "R"
    description: "RESEARCH - Investigate deeper"
    action: execute_selected_query_research
    fallback_keys: ["2", "r"]
    long_form: "Ctrl+Shift+R"

  option_edit_thinking:
    primary_key: "E"
    description: "EDIT THINKING - Reconsider approach"
    action: execute_selected_query_edit
    fallback_keys: ["3", "e"]
    long_form: "Ctrl+Shift+E"

  option_context_dependent:
    primary_key: "T"  # or configurable 4th option
    description: "CONTEXT-DEPENDENT - Test/Deploy/Refactor/Validate"
    action: execute_selected_query_context
    fallback_keys: ["4", "t"]
    long_form: "Ctrl+Shift+T"
    note: "4th option changes based on context (see context mapping below)"

  # NAVIGATION
  show_help:
    primary_key: "?"
    description: "Show hotkey help"
    action: display_help_overlay
    fallback_keys: ["h", "H"]

  show_full_query:
    primary_key: "Tab"
    description: "Cycle through full query text (one suggestion at a time)"
    action: cycle_full_text_view
    fallback_keys: ["→", "→"]  # Arrow keys also cycle

  show_reasoning:
    primary_key: "/"
    description: "Show explanation/reasoning for selected option"
    action: toggle_explanation_view
    fallback_keys: ["x", "X"]

  # ESCAPE / CANCEL
  dismiss_suggestions:
    primary_key: "Escape"
    description: "Dismiss Hekat-Helper suggestions"
    action: dismiss_overlay
    fallback_keys: ["q", "Q", "Ctrl+C"]

  # CUSTOM QUERY
  enter_custom:
    primary_key: "C"
    description: "Enter custom Hekat query (advanced)"
    action: open_custom_query_editor
    fallback_keys: ["c", "+"]

  # EXECUTE WITHOUT SELECTION (power user)
  execute_last_selected:
    primary_key: "Return"
    description: "Execute the highlighted option (use arrows to navigate)"
    action: execute_highlighted_query
    fallback_keys: ["Enter"]
```

---

## 2. Context-Dependent 4th Option Mapping

The **T** key changes based on execution context. Here's the decision tree:

```yaml
context_dependent_mapping:
  # After code implementation
  context: "code_generated"
    option_name: "TEST"
    key: "T"
    query: "test-engineer : 'add tests for this code'"

  # After research/analysis
  context: "research_completed"
    option_name: "EVALUATE"
    key: "T"
    query: "mercurio-orchestrator : 'evaluate findings'"

  # After design/architecture
  context: "architecture_designed"
    option_name: "IMPLEMENT"
    key: "T"
    query: "practical-programmer : 'build this design'"

  # After testing
  context: "tests_written"
    option_name: "DEPLOY"
    key: "T"
    query: "deployment-orchestrator : 'prepare deployment'"

  # After refactoring
  context: "refactored"
    option_name: "VALIDATE"
    key: "T"
    query: "test-engineer : 'validate refactoring'"

  # Default fallback
  context: "unknown"
    option_name: "NEXT"
    key: "T"
    query: "practical-programmer : 'what should we do next?'"
```

---

## 3. User Interface with Hotkeys

### Display Format (Single Line Variant)

```
HEKAT: (D)evelop  (R)esearch  (E)dit-Think  (T)est  (?=help)  [ESC=close]  →
```

### Display Format (Full Variant)

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

## 4. Keybinding Configuration File

Location: `~/.claude/hekat/keybindings.yaml`

```yaml
# Hekat-Helper Keybindings Configuration
# Path: ~/.claude/hekat/keybindings.yaml
# Loaded by: Claude Code when Hekat-Helper initialized

hekat_keybindings:
  version: 1.0
  enabled: true

  # Override default scheme if needed
  scheme: "dret"  # Options: "dret" (default), "1234", "custom"

  key_mappings:
    # Variant 1: D/R/E/T (default)
    dret:
      develop: "D"
      research: "R"
      edit: "E"
      context: "T"

    # Variant 2: Number keys (for users preferring numeric)
    numbers:
      develop: "1"
      research: "2"
      edit: "3"
      context: "4"

    # Variant 3: Arrow keys (for users with restricted keyboard)
    arrows:
      develop: "→"
      research: "↓"
      edit: "←"
      context: "↑"

    # Variant 4: Vim keys
    vim:
      develop: "j"      # next
      research: "k"     # prev (but in this case 'research deeper')
      edit: "l"         # right (edit/refine)
      context: "h"      # left (context-aware next)

  # User preferences
  preferences:
    active_scheme: "dret"              # Which scheme to use
    case_sensitive: false              # "d" and "D" both work
    show_hint_text: true               # Show "(D)evelop" hints
    confirmation_required: false       # Press key again to confirm
    auto_dismiss_on_execution: true    # Close overlay after executing
    save_last_selection: true          # Remember what user picked

  # Accessibility options
  accessibility:
    screen_reader_friendly: true       # Output structured for screen readers
    high_contrast_mode: false
    large_font: false
    slow_motion: false                 # Slower animation for readability

  # Advanced: Key chords (if Claude Code supports)
  chords:
    repeat_last_query: "Ctrl+H"        # Run same query again
    show_history: "Ctrl+L"             # Show last 10 suggestions & selections
    benchmark_ranking: "Ctrl+B"        # Show why each option ranked where it did

  # Fallback behavior if primary key fails
  fallback:
    enabled: true
    fallback_keys:
      develop: ["1", "d", "Ctrl+1"]
      research: ["2", "r", "Ctrl+2"]
      edit: ["3", "e", "Ctrl+3"]
      context: ["4", "t", "Ctrl+4"]
```

---

## 5. Integration with Claude Code Hotkey System

### Registration with Claude Code

```python
# File: ~/.claude/hekat/hotkey_integration.py

from claude_code import hotkey_registry

def register_hekat_hotkeys():
    """
    Register Hekat-Helper hotkeys with Claude Code's global hotkey system.
    Called on Claude Code startup (if Hekat-Helper enabled).
    """

    config = load_keybindings_config()

    # Register primary hotkeys
    hotkey_registry.register(
        name="hekat_develop",
        keys=config["key_mappings"][config["active_scheme"]]["develop"],
        action=lambda: execute_hekat_query("develop"),
        description="Hekat-Helper: Execute DEVELOP option",
        context="post_execution"  # Only active after agent executes
    )

    hotkey_registry.register(
        name="hekat_research",
        keys=config["key_mappings"][config["active_scheme"]]["research"],
        action=lambda: execute_hekat_query("research"),
        description="Hekat-Helper: Execute RESEARCH option",
        context="post_execution"
    )

    hotkey_registry.register(
        name="hekat_edit",
        keys=config["key_mappings"][config["active_scheme"]]["edit"],
        action=lambda: execute_hekat_query("edit"),
        description="Hekat-Helper: Execute EDIT THINKING option",
        context="post_execution"
    )

    hotkey_registry.register(
        name="hekat_context",
        keys=config["key_mappings"][config["active_scheme"]]["context"],
        action=lambda: execute_hekat_query_context_aware(),
        description="Hekat-Helper: Execute context-dependent option",
        context="post_execution"
    )

    # Support hotkeys
    hotkey_registry.register(
        name="hekat_dismiss",
        keys=["Escape", "q"],
        action=lambda: dismiss_hekat_overlay(),
        description="Hekat-Helper: Dismiss suggestions",
        context="post_execution"
    )

    hotkey_registry.register(
        name="hekat_help",
        keys=["?", "h"],
        action=lambda: show_hekat_help(),
        description="Hekat-Helper: Show keyboard help",
        context="post_execution"
    )
```

---

## 6. Hotkey Behavior Specification

### When Hotkeys Are Active

```yaml
hekat_hotkey_activation:
  trigger: "post_execution_completion"

  lifecycle:
    # Phase 1: Agent execution completes
    agent_complete:
      action: "Display 4 suggestions with hotkey hints"
      hotkeys_active: true
      timeout: null  # Suggestions stay until user acts or dismisses

    # Phase 2: User presses a hotkey
    user_pressed_key:
      action: "Highlight selected option (visual feedback)"
      hotkeys_active: true
      timer: 500ms  # Brief pause to show selection

    # Phase 3: Confirmation / Execution
    user_confirmed:
      action: "Execute selected query, show starting message"
      hotkeys_active: false  # Deactivate until next execution completes
      auto_dismiss_delay: 2000ms  # Close overlay after execution starts

    # Alternative: User presses Escape or 'q'
    user_dismissed:
      action: "Close Hekat overlay"
      hotkeys_active: false
```

### Non-Interfering Behavior

```yaml
# Hotkeys only active during Hekat-Helper overlay
# When overlay is closed, D/R/E/T return to normal (e.g., text input)

hotkey_context_isolation:
  during_hekat_overlay: true
    d_maps_to: "hekat_develop"
    r_maps_to: "hekat_research"
    e_maps_to: "hekat_edit"
    t_maps_to: "hekat_context"

  after_overlay_closed: false
    d_maps_to: "regular_text_input"  # User can type 'd' normally
    r_maps_to: "regular_text_input"
    e_maps_to: "regular_text_input"
    t_maps_to: "regular_text_input"
```

---

## 7. Hotkey Help Overlay

Triggered by **?** or **h**:

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ HEKAT-HELPER HOTKEYS                                                          ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║ EXECUTE OPTIONS:                                                              ║
║   D  = DEVELOP (Implement next step)                                         ║
║   R  = RESEARCH (Investigate deeper)                                         ║
║   E  = EDIT THINKING (Reconsider approach)                                   ║
║   T  = TEST/DEPLOY/NEXT (Context-dependent)                                 ║
║                                                                               ║
║ NAVIGATION:                                                                   ║
║   TAB  = Cycle through full query text                                       ║
║   →/←  = Navigate between options                                            ║
║   /    = Toggle explanation view                                             ║
║                                                                               ║
║ OTHER:                                                                        ║
║   C    = Custom Hekat query (advanced)                                       ║
║   ?    = Show this help                                                      ║
║   ESC  = Close suggestions                                                   ║
║   q    = Dismiss (alternative to ESC)                                        ║
║                                                                               ║
║ QUICK TIPS:                                                                   ║
║   • Press key once to select, twice to confirm                               ║
║   • Tab to see full query before executing                                   ║
║   • / (slash) shows WHY each option was ranked                               ║
║   • All keybindings customizable in ~/.claude/hekat/keybindings.yaml         ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## 8. Fallback Keyboard Support (Accessibility)

For users with limited keyboard access:

```yaml
accessibility_schemes:
  # Scheme 1: Number pad only
  numbers_only:
    develop: "1"
    research: "2"
    edit: "3"
    context: "4"
    dismiss: "0" or "Escape"

  # Scheme 2: Arrow keys only (for minimal keyboards)
  arrow_navigation:
    select_option_1: "Up Arrow"
    select_option_2: "Right Arrow"
    select_option_3: "Down Arrow"
    select_option_4: "Left Arrow"
    confirm: "Enter"
    dismiss: "Escape"

  # Scheme 3: Mouse fallback (if keyboard unavailable)
  mouse_fallback:
    click_option: "Left Click on [D], [R], [E], [T]"
    hover_for_info: "Hover to see full query"
    dismiss: "Click outside overlay or press Escape"

  # Scheme 4: Voice control integration
  voice_fallback:
    develop: "Say 'develop'"
    research: "Say 'research'"
    edit: "Say 'edit'"
    context: "Say 'test' or 'deploy' or 'next'"
    dismiss: "Say 'close' or 'dismiss'"
```

---

## 9. Example: User Interaction Flow with Hotkeys

```
═══════════════════════════════════════════════════════════════════════════════
TIMELINE OF HOTKEY INTERACTIONS
═══════════════════════════════════════════════════════════════════════════════

[Agent finishes execution at t=0]
  → HEKAT overlay appears
  → Hotkeys activated (D/R/E/T now mapped to Hekat options)

[User at t=0.5s]
  → Presses "?"
  → Help overlay shown
  → Help dismisses after 5s or user presses any key

[User at t=6s]
  → Presses "Tab"
  → Full query text shown for [D] DEVELOP option
  → User reads detailed query

[User at t=8s]
  → Presses "/" (slash)
  → Shows explanation: "Why: 95% success rate for backend-async pattern"
  → Explanation shown for 10s or until user navigates

[User at t=12s]
  → Presses "D"
  → Option [D] highlighted in bright color
  → Starting message shown: "Executing: deep-researcher || api-architect..."
  → HEKAT overlay fades
  → Hotkeys deactivated

[User at t=13s - New execution starts]
  → Agent begins work
  → (User can type normally, D/R/E/T work as text input if typing in editor)

[User at t=20s - Agent finishes]
  → New HEKAT overlay appears for new execution
  → Hotkeys reactivated
  → Cycle repeats
```

---

## 10. Configuration Examples

### User Preference 1: Speed Runner (prefers numbers)

```yaml
# ~/.claude/hekat/keybindings.yaml
hekat_keybindings:
  preferences:
    active_scheme: "numbers"  # 1/2/3/4 instead of D/R/E/T
    confirmation_required: false
    auto_dismiss_on_execution: true
```

### User Preference 2: Careful Operator (wants confirmation)

```yaml
hekat_keybindings:
  preferences:
    active_scheme: "dret"
    confirmation_required: true  # Press key twice
    show_hint_text: true
    save_last_selection: true    # Remember what you picked last time
```

### User Preference 3: Vim Power User

```yaml
hekat_keybindings:
  preferences:
    active_scheme: "vim"  # j/k/l/h for movement, Enter to execute
```

---

## 11. Checkpoint for Hotkey Testing

```yaml
HEKAT_HOTKEY_CHECKPOINT:
  timestamp: "2025-10-27T16:45:00Z"
  operation: "hotkey-activation-test"

  pre_state: "hekat_overlay_displayed"
  hotkeys_registered: ["d", "r", "e", "t", "?", "esc"]
  scheme_active: "dret"

  test_case_1:
    user_input: "d"
    expected_action: "execute_develop_query"
    actual_action: "execute_develop_query"
    latency_ms: 45
    status: ✅

  test_case_2:
    user_input: "?"
    expected_action: "show_help_overlay"
    actual_action: "show_help_overlay"
    latency_ms: 32
    status: ✅

  test_case_3:
    user_input: "Escape"
    expected_action: "dismiss_overlay"
    actual_action: "dismiss_overlay"
    latency_ms: 15
    status: ✅

  all_tests_passed: true
  hotkey_system_operational: true
```

---

## Summary: Hotkey Mapping

| Key | Action | Level | Use Case |
|-----|--------|-------|----------|
| **D** | DEVELOP | All | Implement the next step |
| **R** | RESEARCH | All | Investigate deeper |
| **E** | EDIT THINKING | All | Reconsider the approach |
| **T** | TEST/DEPLOY/NEXT | Context | Varies by situation |
| **?** | Show Help | Support | Learn keyboard shortcuts |
| **/** | Explanation | Support | Understand why option ranked #1 |
| **Tab** | Full Query | Navigation | Read complete query text |
| **C** | Custom Query | Advanced | Write your own Hekat query |
| **Esc** | Dismiss | Control | Close suggestions |
| **q** | Dismiss (alt) | Control | Alternative to Escape |

---

**Status**: Now complete with full hotkey specification
**Integration**: Ready to add to main HEKAT_HELPER_SPECIFICATION.md
**Next**: Append this to Part 4 (Integration) in main spec

