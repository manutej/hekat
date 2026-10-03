# /hekat Command Specification

**Status**: Ready for Command Implementation
**Date**: 2025-10-27
**Version**: 1.0
**Type**: Interactive Multi-Option Command

## Overview

The `/hekat` command generates intelligent next-step suggestions using the Hekat DSL query system. After completing any task, users invoke `/hekat` to get 4 contextually-optimal suggestions with dynamic keyboard shortcuts.

## Syntax

```bash
/hekat [input] [flags] [options]

# Minimal (uses defaults)
/hekat

# With intent
/hekat "verbal description of what you want"

# With level override
/hekat -l 7
/hekat --level=5

# With display preference
/hekat --full
/hekat --minimal

# With document reference
/hekat::path/to/document

# Combined
/hekat "implement authentication" --level=5 --full
/hekat::LUXOR/PROJECTS/hekat/tmp/HEKAT_IMPLEMENTATION_SPEC.md -l 7 --minimal
```

## Input Types

### 1. No Input (Default)

```bash
/hekat
```

**Behavior:**
- Reads recent execution context
- Infers domain from previous task
- Generates 4 suggestions at default Level 3
- Displays with user's saved preference (--full or --minimal)

**Example Output:**
```
HEKAT-HELPER: Next Steps (Backend API - Level 3)

[R] RESEARCH - Explore error handling patterns
    Level 3 | Confidence: 0.92 | Est. Tokens: 950
    → deep-researcher : "error handling in async code"
    Why: 92% success for backend-api-error-handling

[T] TEST - Add error handling tests
    Level 4 | Confidence: 0.87 | Est. Tokens: 1200
    → test-engineer : "error handling test suite"
    Why: 87% success for test-first approach

[D] DEBUG - Analyze current error patterns
    Level 3 | Confidence: 0.79 | Est. Tokens: 800
    → debug-detective : "analyze error handling gaps"
    Why: 79% success for debug-focused approach

[I] IMPROVE - Refactor for robustness
    Level 4 | Confidence: 0.85 | Est. Tokens: 1100
    → practical-programmer : "refactor for error resilience"
    Why: 85% success when focusing on reliability
```

### 2. Verbal Command

```bash
/hekat "I need to optimize this query"
```

**Behavior:**
- Parses natural language intent
- Extracts action verb and context
- Matches against domain patterns
- Generates 4 tailored suggestions

**Example Output:**
```
HEKAT-HELPER: Next Steps (Database Optimization - Level 4)

[A] ANALYZE - Profile query performance
    Level 3 | Confidence: 0.94 | Est. Tokens: 900
    → debug-detective : "query performance profiling"

[O] OPTIMIZE - Index and rewrite strategy
    Level 4 | Confidence: 0.91 | Est. Tokens: 1350
    → api-architect : "database optimization strategy"

[T] TEST - Benchmark before/after
    Level 4 | Confidence: 0.88 | Est. Tokens: 1200
    → test-engineer : "performance benchmarking"

[D] DEPLOY - Apply optimizations carefully
    Level 4 | Confidence: 0.87 | Est. Tokens: 1100
    → deployment-orchestrator : "safe deployment of changes"
```

### 3. Specific Flag/Instruction

```bash
/hekat "add TypeScript types"
```

**Behavior:**
- Recognizes specific instruction format
- Matches against implementation patterns
- Generates targeted queries

### 4. Hekat DSL Snippet

```bash
/hekat "(deep-researcher || api-architect) -> practical-programmer"
```

**Behavior:**
- Parses Hekat DSL directly
- Generates confidence score for this pattern
- Suggests alternatives with hotkeys
- Allows user to refine or execute

### 5. Document Reference

```bash
/hekat::LUXOR/PROJECTS/hekat/tmp/HEKAT_IMPLEMENTATION_SPEC.md
```

**Behavior:**
- Reads document file
- Extracts context from document content
- Generates queries relevant to document topics
- Treats document as query seed

**Example Output:**
```
HEKAT-HELPER: Next Steps (Hekat Implementation - Level 5)

[B] BUILD - Create the specifications
    Level 5 | Confidence: 0.94 | Est. Tokens: 2100
    → practical-programmer : "implement HEKAT specs"

[V] VALIDATE - Validate architecture assumptions
    Level 5 | Confidence: 0.88 | Est. Tokens: 1800
    → deep-researcher : "validate HEKAT assumptions"

[T] TEST - Create test suite for system
    Level 4 | Confidence: 0.81 | Est. Tokens: 1400
    → test-engineer : "hekat system test coverage"

[D] DOCUMENT - Generate comprehensive documentation
    Level 4 | Confidence: 0.87 | Est. Tokens: 1300
    → docs-generator : "HEKAT API documentation"
```

## Flags

### Level Override

```bash
/hekat -l 3
/hekat --level=5
/hekat -l 7 --full
```

**Purpose:** Force queries at specific complexity level (no fallback)

**Levels:**
- **3**: Single agent, fast execution (<500 tokens)
- **4**: Two agents, moderate scope (1000-1500 tokens)
- **5**: Three agents, comprehensive (2000-3000 tokens)
- **6**: Four agents, deep analysis (3500-5000 tokens)
- **7**: Five+ agents, ensemble (5000+ tokens)

**Behavior:**
- Shows ONLY queries at specified level
- No fallback to other levels
- Helps when you know what complexity you need

### Display Preference

```bash
/hekat --full
/hekat --minimal
```

**Purpose:** Control output verbosity

**--full (default):**
- Expanded display with explanations
- Shows all metadata (confidence, tokens, pipeline)
- Includes "Why" field for each query
- Better for learning and understanding

**--minimal:**
- Single-line compact output
- Shows only hotkey, action, and level
- Faster to scan
- Better for rapid iteration

**Persistence:** Choice saved for session

### Task-Relay Flags

```bash
/hekat --track-tokens
/hekat --checkpoint
/hekat --variance=15%
```

**--track-tokens:** Explicit token accounting (default: on)
**--checkpoint:** Save intermediate results to memory
**--variance=N%:** Set acceptable variance tolerance (default: 20%)

## Hotkey System

### Default Hotkeys (DRET)

After suggestions display, user can press:

```
[D] - Execute 1st suggestion (DEVELOP/action verb)
[R] - Execute 2nd suggestion (RESEARCH/action verb)
[E] - Execute 3rd suggestion (EDIT/action verb)
[T] - Execute 4th suggestion (TEST/action verb)
```

**Dynamic Generation:** Hotkeys are generated from action verbs, NOT hardcoded to D/R/E/T

**Example:**
```
[A] ANALYZE - Analyze current system
[I] IMPLEMENT - Implement solution
[T] TEST - Test implementation
[F] FIX - Fix bugs

User presses: I → Executes "implement" suggestion
User presses: F → Executes "fix" suggestion
```

### Supporting Hotkeys

```
[?] - Show help/keyboard shortcuts
[TAB] - Show full query text (expanded)
[/] - Show explanation for rankings
[C] - Custom query (write your own Hekat DSL)
[ESC] - Dismiss suggestions
[q] - Alternative dismiss
```

### Alternative Keybinding Schemes

Users can configure alternative schemes:

```yaml
# Numbers
/hekat --scheme=numbers
→ Use: 1, 2, 3, 4

# Arrow keys
/hekat --scheme=arrows
→ Use: ↑ (1st), ↓ (2nd), ← (3rd), → (4th)

# Vim keys
/hekat --scheme=vim
→ Use: j (1st), k (2nd), l (3rd), h (4th), Enter to execute
```

## Examples

### Example 1: After Code Review

**Scenario:** Just completed code review, now need next steps

```bash
$ /hekat

HEKAT-HELPER: Next Steps (Backend Code Review - Level 3)

[R] RESEARCH - Explore refactoring patterns
[I] IMPLEMENT - Apply suggested improvements
[T] TEST - Add coverage for changes
[E] EVALUATE - Check performance impact

Your choice? (D/R/E/T or custom):
```

**User presses:** `I`
**Executes:** practical-programmer with refactoring focus

### Example 2: Deep Dive Research

**Scenario:** Need comprehensive understanding of new technology

```bash
$ /hekat -l 7

HEKAT-HELPER: Next Steps (Technology Research - Level 7)

[M] MERCURIO - Multi-perspective synthesis
    Level 7 | Confidence: 0.82 | Est. Tokens: 5200

[A] ARCHITECT - Complete system design
    Level 7 | Confidence: 0.88 | Est. Tokens: 4800

[S] SYNTHESIZE - Research + synthesis workflow
    Level 7 | Confidence: 0.84 | Est. Tokens: 5100

[O] ORCHESTRATE - Full project coordination
    Level 7 | Confidence: 0.79 | Est. Tokens: 5500

Your choice? (M/A/S/O or custom):
```

**User presses:** `A`
**Executes:** Multi-agent architecture design at level 7

### Example 3: Quick Iteration

**Scenario:** Rapid development, want compact view

```bash
$ /hekat "add authentication" --minimal

[A] Audit requirements | [I] Implement oauth | [T] Test auth | [D] Deploy
Your choice?
```

**User presses:** `I`
**Executes:** Implement OAuth query

### Example 4: Document-Based Query

**Scenario:** Load implementation spec as context

```bash
$ /hekat::LUXOR/PROJECTS/hekat/tmp/HEKAT_IMPLEMENTATION_SPEC.md

HEKAT-HELPER: Next Steps (Hekat Implementation - Level 5)

[B] BUILD - Implement specifications
[V] VALIDATE - Validate assumptions
[T] TEST - Create test suite
[D] DOCUMENT - Generate docs

Your choice?
```

### Example 5: Custom Query

**Scenario:** User wants to specify exact DSL query

```bash
$ /hekat "implement feature" --level=5

HEKAT-HELPER: Next Steps (Feature Development - Level 5)

[R] RESEARCH [I] IMPLEMENT [T] TEST [D] DOCUMENT

Your choice? (or press C for custom):
```

**User presses:** `C`
**Prompt:** "Enter custom Hekat DSL query:"

**User types:** `(deep-researcher || api-architect) -> practical-programmer`

**System:** Executes custom query, logs consciousness pattern

### Example 6: Error Debugging

**Scenario:** Just hit an error, need to debug

```bash
$ /hekat "test is failing"

HEKAT-HELPER: Next Steps (Testing & Debug - Level 4)

[D] DEBUG - Analyze test failure
    Level 3 | Confidence: 0.94 | Est. Tokens: 800

[F] FIX - Implement fix
    Level 4 | Confidence: 0.91 | Est. Tokens: 1200

[T] TEST - Re-run tests
    Level 4 | Confidence: 0.88 | Est. Tokens: 1100

[R] RESEARCH - Understand root cause
    Level 4 | Confidence: 0.85 | Est. Tokens: 1300

Your choice? (D/F/T/R or custom):
```

### Example 7: Frontend Component

**Scenario:** Building React component

```bash
$ /hekat "create reusable dropdown"

HEKAT-HELPER: Next Steps (Frontend Component - Level 4)

[D] DESIGN - Design component architecture
    → frontend-architect : "reusable dropdown design"

[I] IMPLEMENT - Build component code
    → practical-programmer : "React dropdown implementation"

[T] TEST - Create component tests
    → test-engineer : "dropdown unit tests"

[S] SHOWCASE - Create usage examples
    → docs-generator : "dropdown examples"

Your choice? (D/I/T/S or custom):
```

### Example 8: Performance Optimization

**Scenario:** Application running slowly

```bash
$ /hekat "application is slow" --full

HEKAT-HELPER: Next Steps (Performance Optimization - Level 5)

[P] PROFILE - Identify bottlenecks
    Level 3 | Confidence: 0.96 | Est. Tokens: 950
    → debug-detective : "performance profiling"
    Why: 96% success for identifying bottlenecks

[O] OPTIMIZE - Apply optimizations
    Level 5 | Confidence: 0.92 | Est. Tokens: 2100
    → (api-architect || frontend-architect) -> practical-programmer
    Why: 92% success for multi-domain optimization

[B] BENCHMARK - Measure improvements
    Level 4 | Confidence: 0.89 | Est. Tokens: 1300
    → test-engineer : "performance benchmarking"
    Why: 89% success when measuring improvements

[D] DEPLOY - Release optimizations
    Level 4 | Confidence: 0.87 | Est. Tokens: 1100
    → deployment-orchestrator : "safe deployment"
    Why: 87% success for careful deployment

Your choice? (P/O/B/D or custom):
```

### Example 9: Database Design

**Scenario:** Designing new database schema

```bash
$ /hekat "design user and post schema" --level=5 --full

HEKAT-HELPER: Next Steps (Database Design - Level 5)

[D] DESIGN - Create normalized schema
    Level 5 | Confidence: 0.95 | Est. Tokens: 2000
    → api-architect : "database schema design"
    Why: 95% success for schema design

[V] VALIDATE - Check schema quality
    Level 4 | Confidence: 0.88 | Est. Tokens: 1200
    → deep-researcher : "schema validation patterns"
    Why: 88% success for validation

[I] IMPLEMENT - Create migrations
    Level 4 | Confidence: 0.91 | Est. Tokens: 1400
    → practical-programmer : "SQLAlchemy migrations"
    Why: 91% success for migration implementation

[T] TEST - Create seed data & tests
    Level 4 | Confidence: 0.87 | Est. Tokens: 1300
    → test-engineer : "database tests and fixtures"
    Why: 87% success for test data

Your choice? (D/V/I/T or custom):
```

### Example 10: Microservices Architecture

**Scenario:** Designing microservices system

```bash
$ /hekat "multi-service architecture" -l 7 --full

HEKAT-HELPER: Next Steps (Microservices Architecture - Level 7)

[A] ARCHITECT - Design complete system
    Level 7 | Confidence: 0.88 | Est. Tokens: 4800
    → (api-architect || devops-github-expert || deployment-orchestrator)
    Why: 88% success for complete architecture

[E] EVALUATE - Multi-perspective analysis
    Level 7 | Confidence: 0.84 | Est. Tokens: 5200
    → mercurio-orchestrator : "multi-dimensional analysis"
    Why: 84% success for synthesis

[I] IMPLEMENT - Build services
    Level 6 | Confidence: 0.81 | Est. Tokens: 3800
    → practical-programmer : "microservice implementation"
    Why: 81% success for service implementation

[D] DEPLOY - Production deployment
    Level 6 | Confidence: 0.85 | Est. Tokens: 3500
    → deployment-orchestrator : "Kubernetes deployment"
    Why: 85% success for K8s deployment

Your choice? (A/E/I/D or custom):
```

### Example 11: Security Audit

**Scenario:** Need to audit application for security

```bash
$ /hekat "security audit" --level=6

HEKAT-HELPER: Next Steps (Security Audit - Level 6)

[A] AUDIT - Security vulnerability scan
[I] IDENTIFY - Root cause analysis
[F] FIX - Implement security patches
[V] VERIFY - Validate fixes

Your choice?
```

### Example 12: Documentation Project

**Scenario:** Building comprehensive documentation

```bash
$ /hekat "document REST API" --full

HEKAT-HELPER: Next Steps (API Documentation - Level 4)

[R] RESEARCH - Analyze API patterns
[D] DOCUMENT - Generate API docs
[E] EXAMPLES - Create code examples
[R] REVIEW - Review and refine

Your choice? (R/D/E/R or custom):
```

### Example 13: Integration Testing

**Scenario:** Setting up integration tests

```bash
$ /hekat "add integration tests"

HEKAT-HELPER: Next Steps (Integration Testing - Level 4)

[D] DESIGN - Test architecture
[I] IMPLEMENT - Create test suite
[R] RUN - Execute and validate
[C] COVERAGE - Measure coverage

Your choice? (D/I/R/C or custom):
```

### Example 14: CI/CD Pipeline

**Scenario:** Setting up deployment pipeline

```bash
$ /hekat "GitHub Actions pipeline" -l 5

HEKAT-HELPER: Next Steps (CI/CD Pipeline - Level 5)

[D] DESIGN - Pipeline architecture
[B] BUILD - Create workflow files
[T] TEST - Validate pipeline
[D] DEPLOY - Enable pipeline

Your choice? (D/B/T/D or custom):
```

### Example 15: Full-Stack Feature

**Scenario:** Building complete feature (backend + frontend)

```bash
$ /hekat "user authentication flow" --level=6 --full

HEKAT-HELPER: Next Steps (Full-Stack Feature - Level 6)

[D] DESIGN - Complete system design
    Level 6 | Confidence: 0.92 | Est. Tokens: 3200
    → (api-architect || frontend-architect) : "auth flow design"

[B] BACKEND - Implement auth service
    Level 5 | Confidence: 0.94 | Est. Tokens: 2100
    → practical-programmer : "OAuth implementation"

[F] FRONTEND - Build login UI
    Level 5 | Confidence: 0.91 | Est. Tokens: 1900
    → frontend-architect : "React login component"

[T] TEST - Integration testing
    Level 5 | Confidence: 0.88 | Est. Tokens: 1800
    → test-engineer : "auth flow e2e tests"

Your choice? (D/B/F/T or custom):
```

## Advanced Usage

### Combining Flags

```bash
# Deep analysis with minimal display
/hekat -l 7 --minimal

# Document reference at specific level
/hekat::path/to/doc -l 5 --full

# Custom query with token tracking
/hekat "(agent1 -> agent2)" --track-tokens --checkpoint
```

### Keyboard Shortcuts Within Hekat

```
[?]     Show help/keyboard documentation
[TAB]   Expand full query text (show agent pipeline)
[/]     Show ranking explanation ("Why did you rank them this way?")
[C]     Custom mode - write your own Hekat DSL query
[ESC]   Dismiss suggestions without executing
[q]     Alternative dismiss shortcut
```

### Learning from Execution

After executing a query:

```
Query executed: practical-programmer : "implement auth"
Result: ✅ Success (3 commits, all tests pass)
Tokens used: 1350 actual vs 1200 estimated (+12% variance) ⚠️

Consciousness pattern updated:
  - Context: backend-authentication-full-stack
  - Pattern success rate: 0.94 (was 0.89)
  - Sample size: 25 (was 24)
  - Variance trend: observed +12%, adjusted estimates down 5%

Next /hekat invocation will use updated patterns.
```

## Error Handling

### Invalid Input

```bash
$ /hekat "djdshjdsjkd"

⚠️  Could not parse intent clearly

Did you mean:
1. General advice/guidance
2. Research a topic
3. Implement a feature
4. Debug an error

Please refine your input or choose an option.
```

### Level Out of Range

```bash
$ /hekat -l 10

⚠️  Invalid level (10). Hekat supports levels 3-7.

Available levels:
  3 = Single agent (fast)
  4 = Two agents (moderate)
  5 = Three agents (comprehensive)
  6 = Four agents (deep)
  7 = Five+ agents (ensemble)

Using default level 3. Override with: /hekat -l 5
```

### Document Not Found

```bash
$ /hekat::path/not/found

⚠️  Document not found: path/not/found

Continuing with context-based suggestions...
```

## Configuration

### User Preferences

Saved to `~/.claude/hekat-profile.yaml`:

```yaml
hekat_preferences:
  display_mode: "full"              # or "minimal"
  hotkey_scheme: "dret"             # or "numbers", "arrows", "vim"
  default_level: 3                  # override default
  token_variance_tolerance: 0.20    # 20%
  show_confidence_explanation: true
  show_token_estimates: true
```

### Session State

Persisted during session, cleared at session end:

```yaml
hekat_session:
  domain: "backend-api"
  recent_tasks:
    - "code review"
    - "implementation"
  consciousness_patterns:
    backend-api-implementation: 0.92
    backend-api-testing: 0.87
    backend-api-debugging: 0.79
```

## Validation Checklist

- ✅ All input types parsed correctly
- ✅ Level flags respect 3-7 range
- ✅ Hotkeys deterministic from action verbs
- ✅ Display formatted per preference
- ✅ Task-relay protocol enforced
- ✅ Consciousness patterns updated
- ✅ Mode persists across invocations
- ✅ Custom query support via [C]
- ✅ Documentation accessible via [?]
- ✅ Alternative hotkey schemes supported

## Status

**Ready for Implementation**

The `/hekat` command is fully specified and ready for implementation using:
- hekat-agent (query selection logic)
- hekat skill (domain knowledge)
- hekat-workflow (orchestration)

Next step: Create command via `/create-command` or manual file creation.

---
