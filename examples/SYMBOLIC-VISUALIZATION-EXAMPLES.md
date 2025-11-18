# Hekat DSL: Symbolic Architecture Visualization Examples

Testing guide for using the `symbolic-architecture-visualization` skill with Hekat DSL project.

## Overview

This document demonstrates how to invoke and test the symbolic-architecture-visualization skill to create visual representations of Hekat DSL concepts, workflows, and architecture.

---

## How to Invoke the Skill

### Method 1: Natural Request (Automatic Invocation)

Claude Code automatically uses the skill when you request diagrams:

```bash
# Simply ask naturally
"Create a diagram showing the Hekat DSL execution pipeline"
"Visualize the Level 3 parallel streams example using box-drawing characters"
"Show me the DAG for this workflow using symbolic notation"
```

### Method 2: Explicit Reference

Reference the skill directly for specific patterns:

```bash
"Using symbolic-architecture-visualization, create a diagram of Hekat's 6 complexity levels"
"Apply the symbolic-architecture-visualization skill to show the voice interface flow"
```

### Method 3: With Context

Combine with file reading for context-aware diagrams:

```bash
"Read hekat/README.md and create symbolic architecture diagrams for the core operators"
"Analyze hekat/design/dsl-specification.md and visualize the type system"
```

---

## Test Examples for Hekat

### Example 1: DSL Execution Pipeline

**Request**:
```
"Visualize the Hekat DSL execution pipeline from natural language to execution"
```

**Expected Output**:
```
Natural Language
      │
      ▼
┌─────────────┐
│   Parser    │
│  (Verbal)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Compiler  │
│  (Formal)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│     AST     │
│   Builder   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Type Checker│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ DAG Builder │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Stratify   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Execute    │
└─────────────┘
```

---

### Example 2: Level 3 Parallel Streams

**Request**:
```
"Show the Level 3 parallel streams example from Hekat using symbolic notation"
```

**DSL Code**:
```dsl
(/deep + /ctx7 + /research || /orch /wflw /coord || /meta-skill-builder || /meta-agent)
: "DSL for Claude code"
```

**Expected Visualization**:
```
                    Task: "DSL for Claude code"
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Stream 1     │   │  Stream 2     │   │  Stream 3     │
│               │   │               │   │               │
│ /deep         │   │ /orch         │   │ /meta-skill-  │
│   +           │   │ /wflw         │   │  builder      │
│ /ctx7         │   │ /coord        │   │               │
│   +           │   │               │   │               │
│ /research     │   │               │   │               │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │   Synthesize │
                    │    Results   │
                    └──────────────┘

Parallel Execution:
  ∀ stream ∈ {Stream1, Stream2, Stream3}: execute(stream) ∥ concurrent
  ∃ results: combine(results₁, results₂, results₃) → output
```

---

### Example 3: Category Theory Foundations

**Request**:
```
"Visualize Hekat's category theory foundations: agents as morphisms, composition, and functors"
```

**Expected Output**:
```
┌────────────────────────────────────────────────────────────┐
│            CATEGORY THEORY IN HEKAT DSL                    │
└────────────────────────────────────────────────────────────┘

Agents as Morphisms:
────────────────────

Agent: A → B (transforms input A to output B)

    A ───[agent]───▶ B


Sequential Composition (∘):
──────────────────────────

(g ∘ f): A → C  where  f: A → B, g: B → C

    A ───[f]───▶ B ───[g]───▶ C

    Equivalent to:  A ───[g∘f]───▶ C


Laws:
────

Associativity:
  (h ∘ g) ∘ f = h ∘ (g ∘ f)

Identity:
  id_A ∘ f = f = f ∘ id_B

    A ───[id_A]───▶ A

    A ───[f]───▶ B ───[id_B]───▶ B


Functor (Workflow):
──────────────────

fmap: (A → B) → Workflow<A> → Workflow<B>

    Workflow<A>
        │
        │ fmap(f)
        ▼
    Workflow<B>

where f: A → B


Monad Operations:
────────────────

return: A → Workflow<A>

    A ───[return]───▶ Workflow<A>

bind (>>=): Workflow<A> → (A → Workflow<B>) → Workflow<B>

    Workflow<A> ───[>>=]───▶ Workflow<B>
            ╲              ╱
             ╲            ╱
              (A → Workflow<B>)
```

---

### Example 4: DAG Construction Algorithm

**Request**:
```
"Create a symbolic diagram showing how Hekat builds and stratifies a DAG for execution"
```

**Expected Output**:
```
DAG Construction & Stratification
═════════════════════════════════

Input: DSL Expression
    │
    ▼
┌──────────────────┐
│  Parse           │
│  Expression      │
└────────┬─────────┘
         │
         ▼
    ┌────────┐
    │  AST   │
    └────┬───┘
         │
         ▼
┌──────────────────┐
│  Extract Nodes   │
│  & Edges         │
└────────┬─────────┘
         │
         ▼
    ┌────────┐
    │  DAG   │
    └────┬───┘
         │
         ▼
┌──────────────────┐
│  Calculate       │
│  In-Degrees      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Topological     │
│  Sort (Kahn's)   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Stratify into   │
│  Execution       │
│  Levels          │
└────────┬─────────┘
         │
         ▼

Execution Levels:
─────────────────

Level 0: {nodes with in-degree = 0}
    │
    ▼
Level 1: {nodes whose deps in Level 0}
    │
    ▼
Level 2: {nodes whose deps in Levels 0-1}
    │
    ⋮
    │
    ▼
Level n: {final nodes}


Algorithm:
─────────

∀ level ∈ Levels:
  Execute(level) in parallel
  Wait for completion
  Update in-degrees
  Continue to next level
```

---

### Example 5: Six Complexity Levels

**Request**:
```
"Visualize all 6 Hekat complexity levels with token counts and execution times"
```

**Expected Output**:
```
┌─────────────────────────────────────────────────────────────────┐
│              HEKAT DSL COMPLEXITY HIERARCHY                     │
└─────────────────────────────────────────────────────────────────┘

Level 1: Basic Invocation
──────────────────────────
Tokens: 5-15K  │  Time: 2-5 min

    agent : "task"

    ┌──────────┐
    │  Agent   │───▶ Result
    └──────────┘


Level 2: Binary Operations
───────────────────────────
Tokens: 10-30K  │  Time: 5-15 min

    A -> B              (Sequential)
    A || B              (Parallel)
    agent + skill       (Combination)

    ┌───┐    ┌───┐
    │ A │───▶│ B │       Sequential
    └───┘    └───┘

    ┌───┐
    │ A │─┐
    └───┘ │
          ├───▶ Result   Parallel
    ┌───┐ │
    │ B │─┘
    └───┘


Level 3: Parallel Streams ⭐
───────────────────────────
Tokens: 40-100K  │  Time: 20-45 min

    (A || B || C) : "task"

    ┌───┐  ┌───┐  ┌───┐
    │ A │  │ B │  │ C │
    └─┬─┘  └─┬─┘  └─┬─┘
      │      │      │
      └──────┼──────┘
             │
             ▼
        ┌────────┐
        │Synthesize
        └────────┘


Level 4: Complex Orchestration
───────────────────────────────
Tokens: 80-150K  │  Time: 45-90 min

    A -> if(condition) B : C

    ┌───┐    ┌──────────┐
    │ A │───▶│Condition?│
    └───┘    └─────┬────┘
               ┌───┴───┐
             true    false
               │       │
               ▼       ▼
             ┌───┐   ┌───┐
             │ B │   │ C │
             └───┘   └───┘


Level 5: Workflow Composition
──────────────────────────────
Tokens: 120-250K  │  Time: 90-180 min

    workflow name(params) { ... }

    ┌─────────────────────┐
    │  Workflow Template  │
    │                     │
    │  research -> design │
    │     ↓          ↓    │
    │  implement -> test  │
    │     ↓               │
    │   deploy            │
    └─────────────────────┘


Level 6: Meta-Programming
──────────────────────────
Tokens: 200K+  │  Time: 3+ hours

    workflow_generator<T> -> Workflow<T>

    ┌──────────────────────┐
    │ Workflow Generator   │
    │   (Higher-Order)     │
    └──────────┬───────────┘
               │
    ┌──────────┴───────────┐
    │                      │
    ▼                      ▼
┌─────────┐          ┌─────────┐
│Workflow │          │Workflow │
│   <A>   │          │   <B>   │
└─────────┘          └─────────┘

Type System:
───────────

∀ T, U:
  fmap: (T → U) → Workflow<T> → Workflow<U>
  bind: Workflow<T> → (T → Workflow<U>) → Workflow<U>
```

---

### Example 6: Voice Interface Translation

**Request**:
```
"Show the voice-to-DSL translation pipeline for Hekat"
```

**Expected Output**:
```
VOICE INTERFACE TRANSLATION PIPELINE
═════════════════════════════════════

Step 1: Natural Language Input
───────────────────────────────

🗣️  "Run deep research and context lookup in parallel,
     then synthesize findings on DSL design"

    │
    ▼

Step 2: Intent Recognition
───────────────────────────

Extract:
  - Operators: ["parallel", "then"]
  - Agents: ["deep research", "context lookup", "synthesize"]
  - Task: "DSL design"

    │
    ▼

Step 3: Verbal DSL
──────────────────

parallel: deep research, context lookup
then: synthesize
task: DSL design

    │
    ▼

Step 4: Formal DSL Compilation
───────────────────────────────

(/deep || /ctx7) -> synthesize : "DSL design"

    │
    ▼

Step 5: Execution DAG
─────────────────────

        ┌──────┐  ┌──────┐
        │/deep │  │/ctx7 │
        └───┬──┘  └───┬──┘
            │         │
            └────┬────┘
                 │
                 ▼
           ┌───────────┐
           │synthesize │
           └───────────┘

Translation Table:
─────────────────

Natural → Verbal → Formal
"then"  → "then"  → "->"
"and"   → "and"   → "||"
"with"  → "with"  → "+"
"on"    → "task"  → ":"
```

---

### Example 7: Type System Visualization

**Request**:
```
"Create a diagram showing Hekat's type system and type checking rules"
```

**Expected Output**:
```
HEKAT TYPE SYSTEM
═════════════════

Type Definitions:
────────────────

Agent<A, B>     : A → B  (transforms A to B)
Skill<T>        : T → T  (enhances T)
Workflow<T>     : Context → T


Type Rules:
──────────

Sequential Composition:
  Agent<A, B> -> Agent<B, C> : Agent<A, C>  ✓

  ┌─────────┐    ┌─────────┐    ┌─────────┐
  │Agent<A,B│───▶│Agent<B,C│───▶│Agent<A,C│
  └─────────┘    └─────────┘    └─────────┘
       f              g           g ∘ f


Type Error Example:
  Agent<A, B> -> Agent<X, Y> : TYPE ERROR  ✗

  ┌─────────┐    ┌─────────┐
  │Agent<A,B│ ✗─▶│Agent<X,Y│
  └─────────┘    └─────────┘
       B ≠ X (mismatch)


Parallel Composition:
  Agent<A, B> || Agent<A, C> : Agent<A, (B, C)>  ✓

  ┌─────────┐    ┌─────────┐
  │Agent<A,B│─┐  │         │
  └─────────┘ │  │Agent<A, │
              ├─▶│ (B,C)   │
  ┌─────────┐ │  │         │
  │Agent<A,C│─┘  └─────────┘
  └─────────┘


Skill Combination:
  Agent<A, B> + Skill<B> : Agent<A, B'>  ✓

  where B' is enhanced version of B

  ┌─────────┐    ┌────────┐    ┌─────────┐
  │Agent<A,B│───▶│Skill<B>│───▶│Agent<A,B'│
  └─────────┘    └────────┘    └─────────┘


Type Constraints:
────────────────

∀ agents f: A → B, g: B → C:
  f -> g : A → C  (composition type-checks)

∀ agents f: A → B, g: X → Y where B ≠ X:
  f -> g : TYPE_ERROR  (composition fails)

∀ parallel agents f: A → B, g: A → C:
  f || g : A → (B, C)  (fan-out)
```

---

### Example 8: Error Handling Flow

**Request**:
```
"Show Hekat's error handling and retry mechanism using symbolic notation"
```

**Expected Output**:
```
ERROR HANDLING & RETRY MECHANISM
═════════════════════════════════

Retry Operator (⟲):
──────────────────

DSL: A ⟲³ -> fallback

    ┌─────┐
    │  A  │
    └──┬──┘
       │
    attempt 1
       │
     ┌─┴─┐
   ✓ │   │ ✗
     │   │
     │   ▼
     │ ┌─────┐
     │ │retry│
     │ └──┬──┘
     │    │
     │ attempt 2
     │    │
     │  ┌─┴─┐
     │✓ │   │ ✗
     │  │   │
     │  │   ▼
     │  │ ┌─────┐
     │  │ │retry│
     │  │ └──┬──┘
     │  │    │
     │  │ attempt 3
     │  │    │
     │  │  ┌─┴─┐
     │  │✓ │   │ ✗
     │  │  │   │
     │  │  │   ▼
     ▼  ▼  ▼  ┌─────────┐
    ┌──────────┤fallback │
    │          └─────────┘
    ▼
  Success


Conditional Recovery:
────────────────────

DSL: test -> if(pass) deploy : (fix -> retest)

       ┌──────┐
       │ test │
       └───┬──┘
           │
       ┌───┴────┐
    pass│        │fail
       │        │
       ▼        ▼
    ┌──────┐ ┌─────┐
    │deploy│ │ fix │
    └──────┘ └──┬──┘
                │
                ▼
             ┌──────┐
             │retest│
             └───┬──┘
                 │
              ┌──┴───┐
           pass│      │fail
               ▼      ▼
            ┌──────┐ ┌──────┐
            │deploy│ │ abort│
            └──────┘ └──────┘


Error Propagation:
─────────────────

∀ workflow W:
  ∃ error e ∈ W → propagate(e) ∨ handle(e)

Error Types:
  - Timeout: agent exceeds time limit
  - Type Error: composition type mismatch
  - Runtime Error: agent execution failure
  - Resource Error: insufficient tokens/memory

Handling Strategy:
  try {
    execute(workflow)
  } catch(error) {
    if (retryable(error) && attempts < max_retries)
      retry()
    else if (fallback_defined)
      execute(fallback)
    else
      propagate(error)
  }
```

---

## Testing Workflow

### Step 1: Navigate to Hekat Project

```bash
cd /Users/manu/Documents/LUXOR/PROJECTS/hekat
```

### Step 2: Request Visualizations

Use any of the examples above or create your own:

```bash
# Example request
"Read the Hekat README and create a symbolic diagram showing
the progression from Level 1 to Level 6 complexity"
```

### Step 3: Verify Output

Check that the output:
- ✅ Uses box-drawing characters correctly
- ✅ Includes mathematical notation where appropriate
- ✅ Shows clear flow and structure
- ✅ Maintains 80-column width for code comments
- ✅ Uses legends for custom symbols
- ✅ Is monospace-font compatible

### Step 4: Save to Documentation

```bash
# Save useful diagrams to docs
"Save this diagram to hekat/docs/visual-pipeline.md"
```

---

## Integration with Hekat Documentation

### Adding Diagrams to Existing Docs

**Request**:
```
"Read hekat/docs/DSL-COMPLEXITY-LEVELS.md and enhance it with
symbolic architecture diagrams for each level"
```

**Result**: Enhanced documentation with visual representations

### Creating Architecture Documentation

**Request**:
```
"Create a comprehensive architecture document for Hekat showing:
1. System overview diagram
2. Component relationships
3. Data flow
4. Execution pipeline
Save to hekat/docs/ARCHITECTURE-VISUAL.md"
```

---

## Advanced Testing Scenarios

### Scenario 1: Full Workflow Visualization

**Request**:
```
"Visualize the complete workflow for 'microservice_dev' from Hekat,
showing all phases from research to deployment with token estimates"
```

### Scenario 2: Compare Verbal vs Formal

**Request**:
```
"Show side-by-side comparison of verbal DSL and formal DSL
for the Level 3 parallel streams example"
```

### Scenario 3: Mathematical Proofs

**Request**:
```
"Create symbolic proofs showing that Hekat's sequential composition
satisfies the category theory laws (associativity and identity)"
```

### Scenario 4: Performance Visualization

**Request**:
```
"Diagram the performance characteristics of each complexity level
showing token count, execution time, and parallelization potential"
```

---

## Tips for Best Results

### ✅ Do

1. **Be Specific**: Reference exact sections from Hekat docs
2. **Provide Context**: Mention the DSL level or feature
3. **Request Legends**: Ask for symbol explanations
4. **Iterate**: Start simple, add complexity

### ❌ Don't

1. **Over-complicate**: Don't request diagrams >100 lines at once
2. **Mix Styles**: Stick to one box-drawing style per diagram
3. **Forget Width**: Remind about 80-column width if needed
4. **Skip Labels**: Always label nodes and transitions

---

## Example Session

```bash
# Session 1: Basic Operators
"Show me symbolic diagrams for all Hekat core operators:
sequential, parallel, combination, and specification"

# Session 2: Complexity Ladder
"Create a progression diagram showing how each complexity
level builds on the previous one"

# Session 3: Type System
"Visualize the type checking rules with examples of
valid and invalid compositions"

# Session 4: Execution Engine
"Diagram the DAG construction and stratification algorithm
with a concrete example workflow"

# Session 5: Voice Interface
"Show the complete voice-to-execution pipeline with
natural language, verbal DSL, formal DSL, and DAG stages"
```

---

## Resources

- **Skill Location**: `~/.claude/skills/symbolic-architecture-visualization/`
- **Quick Help**: `cat ~/.claude/skills/symbolic-architecture-visualization/HELP.md`
- **Examples**: `cat ~/.claude/skills/symbolic-architecture-visualization/EXAMPLES.md`
- **Hekat Docs**: `/Users/manu/Documents/LUXOR/PROJECTS/hekat/docs/`

---

## Next Steps

1. **Test Examples**: Try each example above
2. **Create Custom**: Design Hekat-specific visualizations
3. **Enhance Docs**: Add diagrams to existing documentation
4. **Share Patterns**: Document reusable visualization patterns

---

**Created**: 2025-10-19
**Skill**: symbolic-architecture-visualization v1.0.0
**Project**: Hekat DSL
**Status**: Ready for testing ✅
