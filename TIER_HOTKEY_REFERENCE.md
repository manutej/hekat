# HEKAT TIER Hotkey Reference

**Quick lookup for hotkey mapping by complexity level**

---

## TIER 1: Single-Key Quick Access (L1-L3)

Always available. No modifiers needed.

```
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: Single Keys for Quick Access                         │
├─────────────────────────────────────────────────────────────┤
│ KEY │ MNEMONIC      │ AGENTS             │ LEVEL  │ USE      │
├─────┼───────────────┼────────────────────┼────────┼──────────┤
│ [R] │ Research      │ deep-researcher    │ L1-L2  │ Explore  │
│ [D] │ Design/Debug  │ api-architect,     │ L1-L5  │ Plan     │
│     │               │ debug-detective    │        │          │
│ [T] │ Test/Verify   │ test-engineer      │ L1-L2  │ Validate │
│ [B] │ Build         │ practical-pgmer    │ L2     │ Implement│
│ [F] │ Frontend      │ frontend-architect │ L2-L3  │ UI/UX    │
│ [I] │ Implement     │ practical-pgmer    │ L2-L3  │ Code     │
│ [O] │ Orchestrate   │ project-orch       │ L5-L7  │ Coord    │
│ [S] │ Synthesize    │ mercurio-orch      │ L6-L7  │ Integrate│
│ [C] │ Code-review   │ debug-detective,   │ L2-L3  │ Review   │
│     │               │ test-engineer      │        │          │
│ [P] │ Parallel      │ Parallel agents    │ L4     │ Multi-   │
│     │               │                    │        │ perspective
│ [V] │ Verify        │ test-engineer      │ L1-L2  │ Check    │
│ [A] │ Analyze       │ deep-researcher,   │ L1-L3  │ Investigate
│     │               │ debug-detective    │        │          │
└─────┴───────────────┴────────────────────┴────────┴──────────┘
```

**Usage**:
```bash
/hekat [R] "explain JWT"              → L1
/hekat [D] "design API"               → L3
/hekat [T] "test this function"       → L1
/hekat [B] "build endpoint"           → L2
/hekat [I] "implement auth"           → L3
/hekat [P] "parallel analysis"        → L4
```

---

## TIER 2: Complexity Selectors (L4-L7)

Hold **Ctrl** while pressing key.

```
┌───────────────────────────────────────────────────────────┐
│ TIER 2: Ctrl-Modifiers for Complexity Selection           │
├───────────────────────────────────────────────────────────┤
│ KEY        │ COMPLEXITY    │ AGENTS    │ USE              │
├────────────┼───────────────┼───────────┼──────────────────┤
│ [Ctrl+P]   │ L4 Parallel   │ 2-3       │ Multiple views   │
│ [Ctrl+H]   │ L5 Hierarchical│ 4-5      │ Architecture     │
│ [Ctrl+I]   │ L6 Iterative  │ 4-6      │ Refinement loops │
│ [Ctrl+E]   │ L7 Ensemble   │ 7+       │ Full orchestration
└────────────┴───────────────┴───────────┴──────────────────┘
```

**Usage**:
```bash
/hekat [Ctrl+P] "compare frameworks"  → L4 (2-3 agents in parallel)
/hekat [Ctrl+H] "design system"       → L5 (4-5 agents hierarchical)
/hekat [Ctrl+I] "fix with tests"      → L6 (4-6 agents iterative)
/hekat [Ctrl+E] "build platform"      → L7 (7+ agents ensemble)
```

**When to use TIER 2 over TIER 1**:
- Tier 1 auto-detects level (guesses from keywords)
- Tier 2 forces specific level (guarantees that level)
- Use Tier 2 when you want to override auto-detection

---

## TIER 3: Agent Chains (Advanced)

Specify exact agent sequence or parallel group.

```
┌─────────────────────────────────────────────────────────────┐
│ TIER 3: Agent Chain Patterns                                │
├─────────────────────────────────────────────────────────────┤
│ PATTERN      │ SYNTAX          │ MEANING         │ LEVEL    │
├──────────────┼─────────────────┼─────────────────┼──────────┤
│ Sequential   │ A -> B -> C     │ One after next  │ L2-L3    │
│              │                 │                 │          │
│ Parallel     │ (A || B || C)   │ Simultaneous    │ L4       │
│              │                 │ then consensus  │          │
│              │                 │                 │          │
│ Hierarchical │ lead[A->(B||C)] │ Stages with     │ L5       │
│              │                 │ supervisor      │          │
│              │                 │                 │          │
│ Iterative    │ iterate(A→B→C)  │ Feedback loops  │ L6       │
│              │                 │ until condition │          │
│              │                 │                 │          │
│ Ensemble     │ sample^3(...);  │ Parallel phase, │ L7       │
│              │ synthesize;     │ synthesis,      │          │
│              │ parallel impl   │ implementation  │          │
└──────────────┴─────────────────┴─────────────────┴──────────┘
```

**Common Chains**:

### L2 Chains
```
[R>D]      Research → Design
[D>I]      Design → Implement
[B>T]      Build → Test
[A>R]      Analyze → Report
```

### L3 Chains
```
[R>D>I]    Research → Design → Implement (classic TDD prep)
[D>I>T]    Design → Implement → Test (standard feature dev)
[A>D>I]    Analyze → Design → Implement (requirements-driven)
[B>R>T]    Build → Refactor → Test (legacy refactoring)
```

### L4 Parallel
```
[P:R||D||A]        Research || Design || Analyze
[C:Sec||Perf||Read] Security || Performance || Readability reviews
```

### L5 Hierarchical
```
[H:R+D→O]    Research + Design → Orchestrate
[H:R+D+F→O]  Research + Design + Frontend → Orchestrate
```

### L6 Iterative
```
[I:D→P→T]       Debug → Program → Test (repeat)
[I:A→F→V]       Analyze → Fix → Verify (repeat)
```

### L7 Ensemble
```
[E:P→S→I→O]     Parallel → Synthesize → Implement → Orchestrate
```

**Usage**:
```bash
/hekat [R>D>I] "build auth endpoint"
→ deep-researcher → api-architect → practical-programmer

/hekat [P:R||D||A] "audit this code"
→ (deep-researcher || api-architect || debug-detective) consensus

/hekat [I:D→P→T] "fix production bug"
→ iterate(debug-detective → practical-programmer → test-engineer)
```

---

## Level-by-Level Hotkey Options

### L1: Ultra-Fast Single-Hop

**Recommended hotkey**: Single key
```
[R] - Quick research/explanation (default)
[D] - Quick debugging
[T] - Quick test check
[A] - Quick analysis
```

**Example**:
```bash
/hekat [R] "What is OAuth?"
/hekat [D] "Why is this function slow?"
```

---

### L2: Fast Simple-Chain

**Recommended hotkey**: Single key (context infers chain)
```
[D] - Design first (triggers → [D>I] chain)
[B] - Build first (triggers → [B>T] chain)
[A] - Analyze first (triggers → [A>R] chain)
```

**Or explicit chain**:
```bash
/hekat [R>D] "research then design API"
/hekat [D>I] "design then implement"
/hekat [B>T] "build then test"
```

---

### L3: Balanced Sequential

**Recommended hotkey**: Chain pattern
```bash
/hekat [D>I>T] "full feature development"
/hekat [R>D>I] "research then implement"
/hekat [A>D>I] "analyze requirements then implement"
```

**Or let it auto-detect**:
```bash
/hekat "design and implement authentication"
→ System infers L3 from keywords
```

---

### L4: Parallel Consensus

**Recommended hotkey**: [P] or [Ctrl+P]
```bash
/hekat [P] "compare databases"
→ 2-3 agents analyze in parallel

/hekat [P:R||D||A] "evaluate SDKs"
→ Research || Design || Analyze (explicit agents)

/hekat [Ctrl+P] "architecture options"
→ Force L4 Parallel regardless of input
```

---

### L5: Hierarchical Multi-Stage

**Recommended hotkey**: [H] or [Ctrl+H]
```bash
/hekat [H] "design microservices"
→ Hierarchical architecture with approval gates

/hekat [H:R+D→O] "design system"
→ Research + Design → Orchestrate (explicit)

/hekat [Ctrl+H] "architecture decision"
→ Force L5 Hierarchical
```

---

### L6: Deep Iterative Refinement

**Recommended hotkey**: [I] or [Ctrl+I]
```bash
/hekat [I] "fix production bug with tests"
→ Iterative refinement until passing

/hekat [I:D→P→T] "debug, fix, verify"
→ Explicit iterative chain

/hekat [Ctrl+I] "refine implementation"
→ Force L6 Iterative
```

---

### L7: Full Ensemble Synthesis

**Recommended hotkey**: [E] or [Ctrl+E]
```bash
/hekat [E] "build production platform"
→ Full ensemble: parallel research → synthesis → implementation

/hekat [E:P→S→I→O] "complete architecture"
→ Parallel → Synthesize → Implement → Orchestrate (explicit)

/hekat [Ctrl+E] "greenfield project"
→ Force L7 Ensemble
```

---

## Hotkey Decision Tree

**I want to...** → **Use this hotkey**

```
Explain/understand something?              → [R]
Debug/troubleshoot?                        → [D] or [Ctrl+I] (if iterative)
Test something?                            → [T]
Design (no implementation)?                → [D]
Build/implement?                           → [I]
Compare options?                           → [P] or [Ctrl+P]
Architecture/system design?                → [H] or [Ctrl+H]
Fix bug with testing?                      → [I] or [Ctrl+I]
Code review?                               → [C]
Full project from scratch?                 → [E] or [Ctrl+E]
Not sure?                                  → /hekat "your query" (auto-detect)
Need specific level (e.g., L5)?            → /hekat @L5 "your query"
```

---

## Hotkey Mnemonics (Memory Aids)

```
[R] = Research      (yellow light 🟡: explore/learn)
[D] = Design/Debug  (orange light 🟠: plan or troubleshoot)
[T] = Test/Verify   (green light 🟢: validate)
[B] = Build         (blueprint 📐: construct)
[I] = Implement     (hammer 🔨: execute)
[P] = Parallel      (arrows ↔️: multiple paths)
[H] = Hierarchical  (pyramid 🔺: levels/stages)
[I] = Iterative     (loop ⤴️: refinement cycles)
[E] = Ensemble      (orchestra 🎼: orchestration)
[O] = Orchestrate   (conductor 🎩: coordination)
[S] = Synthesize    (integration ⚙️: merge)
[C] = Code-review   (magnifying 🔍: examine)
[A] = Analyze       (microscope 🔬: investigate)
[V] = Verify        (checkmark ✓: confirm)
```

---

## Common Mistakes & Fixes

### Mistake 1: Using [D] for "detail-oriented" query

**Wrong**:
```bash
/hekat [D] "explain JWT in detail"
```

**Why**: [D] = Design/Debug (domain-specific), not "detail"
- [R] Research is for explanations
- [A] Analyze is for detailed investigation

**Correct**:
```bash
/hekat [R] "explain JWT"
/hekat [A] "analyze JWT security"
```

---

### Mistake 2: Using [Ctrl+E] when you mean [E]

**Context matters**:
```bash
/hekat [E] "ensemble query"        → Maybe L7, maybe auto-detect
/hekat [Ctrl+E] "simple question"  → FORCE L7 (wastes tokens!)
```

**Fix**: Use [E] for most queries, [Ctrl+E] only to force level override

---

### Mistake 3: Forgetting that [I] can mean two things

**Context-dependent**:
```bash
/hekat [I] "implement feature"     → L3: Implement as chain
/hekat [I] "fix bug"               → L6: Iterative refinement
```

**System infers from context**:
- "implement" keyword → uses [I] as L3
- "fix" + "test" keywords → uses [I] as L6 iterative
- Ambiguous? → Ask user to clarify

---

## Hotkey Cheat Sheet (Printable)

```
╔════════════════════════════════════════════════════════════╗
║              HEKAT HOTKEY CHEAT SHEET                      ║
╠════════════════════════════════════════════════════════════╣
║ TIER 1: Single Keys (Always Available)                    ║
║  [R]esearch [D]esign [T]est [B]uild [I]mplement          ║
║  [P]arallel [A]nalyze [C]ode-review [V]erify [O]rchestrate║
║                                                            ║
║ TIER 2: Ctrl-Modifiers (Complexity Select)                ║
║  [Ctrl+P] L4  [Ctrl+H] L5  [Ctrl+I] L6  [Ctrl+E] L7       ║
║                                                            ║
║ TIER 3: Chains (Advanced)                                 ║
║  [R>D>I] Sequential  [P:R||D||A] Parallel  [I:D→P→T] Loop ║
║                                                            ║
║ QUICK DECISION:                                           ║
║  Explain?      [R]          Compare?       [P]            ║
║  Design?       [D]          Architecture?  [H]            ║
║  Test?         [T]          Full project?  [E]            ║
║  Build?        [I]          Fix bug?       [I]            ║
║  Unsure?       /hekat "query" (auto-detect)              ║
╚════════════════════════════════════════════════════════════╝
```

---

## Testing Hotkeys

After implementation, verify:

```bash
# TIER 1: Single keys
/hekat [R] "explain"        # Should → L1
/hekat [D] "design"         # Should → L1 or L3
/hekat [P] "parallel"       # Should → L4

# TIER 2: Ctrl modifiers
/hekat [Ctrl+P] "test"      # Should FORCE L4
/hekat [Ctrl+H] "simple"    # Should FORCE L5
/hekat [Ctrl+E] "hello"     # Should FORCE L7

# TIER 3: Chains
/hekat [R>D>I] "feature"    # Should → L3
/hekat [P:R||D||A] "review" # Should → L4
/hekat [I:D→P→T] "debug"    # Should → L6
```

All should execute without errors and select correct level.
