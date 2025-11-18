# CCAO-DSL: Six Levels of Complexity

**Visual Reference for Claude Code Agent Orchestration DSL**
**Date**: 2025-10-19

---

## ASCII Complexity Pyramid

```
                           ╔════════════════════════════════════════════════╗
                           ║         LEVEL 6: MATHEMATICAL META             ║
                           ║    Category Theory & Parameterized Workflows   ║
                           ║  W⟨τ⟩(f) = λx. (f₁ ∘ f₂ ∘ ... ∘ fₙ)(x)        ║
                           ║  Functors, Monads, Abstract Composition        ║
                           ╚════════════════════════════════════════════════╝
                                            ▲
                                            │
                        ╔═══════════════════════════════════════════════════════╗
                        ║       LEVEL 5: WORKFLOW COMPOSITION & LOOPS           ║
                        ║   Named workflows calling workflows with parameters   ║
                        ║   workflow(params) -> sub_workflow -> map(fn)         ║
                        ║   Context sharing, dynamic selection, iteration       ║
                        ╚═══════════════════════════════════════════════════════╝
                                            ▲
                                            │
                ╔═══════════════════════════════════════════════════════════════════╗
                ║        LEVEL 4: COMPLEX ORCHESTRATION & CONDITIONALS              ║
                ║   Nested parallel/sequential, if/else, error handling             ║
                ║   research -> (design || implement) -> if(success) test : rollback║
                ║   Resource constraints, retry logic, conditional branches         ║
                ╚═══════════════════════════════════════════════════════════════════╝
                                            ▲
                                            │
        ╔═══════════════════════════════════════════════════════════════════════════════╗
        ║           LEVEL 3: PARALLEL STREAMS + SEQUENTIAL (YOUR EXAMPLE)               ║
        ║   Multiple parallel execution streams with task specification                 ║
        ║   (/deep + /ctx7 + /research || /orch /wflw /coord || /meta-skill) : task    ║
        ║   3 parallel streams, skill combination, complex coordination                 ║
        ╚═══════════════════════════════════════════════════════════════════════════════╝
                                            ▲
                                            │
╔═══════════════════════════════════════════════════════════════════════════════════════════╗
║                    LEVEL 2: SIMPLE COMBINATION & BASIC OPERATORS                          ║
║   Single operator usage: combination (+), sequence (->), parallel (||)                    ║
║   agent1 + skill1          (combination)                                                  ║
║   agent1 -> agent2         (sequence)                                                     ║
║   agent1 || agent2         (parallel)                                                     ║
╚═══════════════════════════════════════════════════════════════════════════════════════════╝
                                            ▲
                                            │
╔═══════════════════════════════════════════════════════════════════════════════════════════════╗
║                            LEVEL 1: BASIC SINGLE INVOCATION                                   ║
║   Single agent, skill, or command with optional parameters                                    ║
║   api-architect : "design REST API"                                                           ║
║   /ctx7 = express                                                                             ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════╝
```

---

## Detailed Level Breakdown

### 📊 Level 1: Basic Single Invocation

**Complexity**: Minimal
**Execution Model**: Single function call
**Token Budget**: 5,000-15,000
**Time Estimate**: 2-5 minutes

#### Syntax Pattern
```dsl
<agent> : <task>
<command> = <parameter>
<skill>
```

#### Examples
```dsl
// Single agent invocation
api-architect : "design REST API for user management"

// Single command execution
/ctx7 = fastapi

// Single skill activation
postgresql-database-engineering
```

#### Execution Flow
```
┌──────────────┐
│  User Input  │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌────────────┐
│   Parser     │────▶│  Registry  │
└──────┬───────┘     └────────────┘
       │
       ▼
┌──────────────┐
│   Execute    │
│  Single Unit │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Result     │
└──────────────┘
```

#### Mathematical Model
```
f: Input → Output
Simple function application with no composition
```

---

### 📊 Level 2: Simple Combination & Basic Operators

**Complexity**: Low
**Execution Model**: Binary operations
**Token Budget**: 10,000-30,000
**Time Estimate**: 5-15 minutes

#### Syntax Pattern
```dsl
<agent> + <skill>           // Combination
<agent> -> <agent>          // Sequence
<agent> || <agent>          // Parallel
```

#### Examples
```dsl
// Combination: Agent with skill augmentation
api-architect + rest-api-design-patterns + postgresql

// Sequence: Pipeline of two agents
deep-researcher -> api-architect

// Parallel: Two agents running concurrently
frontend-architect || backend-architect
```

#### Execution Flow
```
COMBINATION (+):
┌────────┐   ┌───────┐   ┌────────┐
│ Agent  │ + │ Skill │ = │ Agent' │
└────────┘   └───────┘   └────────┘
              (augmented)

SEQUENCE (->):
┌────────┐      ┌────────┐      ┌────────┐
│ Agent1 │─────▶│ Agent2 │─────▶│ Result │
└────────┘      └────────┘      └────────┘
   t₁              t₂           (t₁ + t₂)

PARALLEL (||):
┌────────┐ ────┐
│ Agent1 │     │
└────────┘     ├────▶ ┌────────┐
               │      │ Merge  │────▶ Result
┌────────┐     │      └────────┘
│ Agent2 │ ────┘
└────────┘
  max(t₁, t₂)
```

#### Mathematical Model
```
Combination:  S₁ ⊕ S₂ → S₃
Sequence:     f ∘ g = λx. f(g(x))
Parallel:     f ⊗ g = λx. (f(x), g(x))
```

#### Operator Properties
```
COMBINATION (+):
• Associative:  (A + B) + C = A + (B + C)
• Commutative:  A + B = B + A
• Identity:     A + ∅ = A

SEQUENCE (->):
• Associative:  (A -> B) -> C = A -> (B -> C)
• NOT Commutative: A -> B ≠ B -> A
• Identity:     id -> A = A

PARALLEL (||):
• Associative:  (A || B) || C = A || (B || C)
• Commutative:  A || B = B || A
```

---

### 📊 Level 3: Parallel Streams + Sequential ⭐ YOUR EXAMPLE

**Complexity**: Medium
**Execution Model**: Multi-stream DAG execution
**Token Budget**: 40,000-100,000
**Time Estimate**: 20-45 minutes

#### Syntax Pattern
```dsl
(<stream1> || <stream2> || <stream3>) : <task>

Where each stream can be:
  - Single agent: agent
  - Combination: agent + skill
  - Sequence: cmd -> cmd -> cmd
```

#### Your Example Deconstructed
```dsl
(/deep + /ctx7 + /research || /orch /wflw /coord || /meta-skill-builder || /meta-agent)
: DSL for Claude code
```

#### Parallel Stream Analysis
```
STREAM 1: Deep Research Foundation
┌──────┐   ┌──────┐   ┌──────────┐
│/deep │ + │/ctx7 │ + │/research │
└──────┘   └──────┘   └──────────┘
    │          │            │
    └──────────┴────────────┘
              │
    Combined Research Context

STREAM 2: Orchestration Tools
┌──────┐   ┌──────┐   ┌──────┐
│/orch │   │/wflw │   │/coord│
└──────┘   └──────┘   └──────┘
    │          │          │
    └──────────┴──────────┘
              │
   Workflow Management Tools

STREAM 3: Meta-builders
┌───────────────────┐   ┌─────────────┐
│/meta-skill-builder│   │/meta-agent  │
└───────────────────┘   └─────────────┘
         │                      │
         └──────────┬───────────┘
                    │
         Meta-construction Capabilities

TASK SPECIFICATION:
: DSL for Claude code (mathematical mapping of agentic workers)
```

#### Execution Flow
```
                        START
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   STREAM 1    │ │   STREAM 2    │ │   STREAM 3    │
│               │ │               │ │               │
│ /deep + /ctx7 │ │ /orch /wflw   │ │ /meta-skill   │
│ + /research   │ │    /coord     │ │ /meta-agent   │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        │                 │                 │
        │  (runs in parallel - fork/join)   │
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                    SYNCHRONIZE
                          │
                          ▼
                ┌─────────────────┐
                │  MERGE RESULTS  │
                │                 │
                │ Research +      │
                │ Orchestration + │
                │ Meta-building   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  EXECUTE TASK:  │
                │  "DSL for       │
                │   Claude code"  │
                └────────┬────────┘
                         │
                         ▼
                    FINAL RESULT
```

#### DAG Representation
```
     ┌──────────┐
     │  START   │
     └────┬─────┘
          │
          ├──────────────┬──────────────┬──────────────┐
          │              │              │              │
          ▼              ▼              ▼              ▼
      ┌──────┐      ┌──────┐      ┌──────────┐   ┌───────────┐
      │/deep │      │/orch │      │  /meta-  │   │  /meta-   │
      └──┬───┘      └──┬───┘      │  skill   │   │  agent    │
         │             │           └────┬─────┘   └─────┬─────┘
         ▼             ▼                │               │
      ┌──────┐      ┌──────┐           │               │
      │/ctx7 │      │/wflw │           │               │
      └──┬───┘      └──┬───┘           │               │
         │             │                │               │
         ▼             ▼                │               │
    ┌─────────┐    ┌──────┐            │               │
    │/research│    │/coord│            │               │
    └────┬────┘    └──┬───┘            │               │
         │            │                 │               │
         └────────────┴─────────────────┴───────────────┘
                              │
                              ▼
                        ┌──────────┐
                        │  MERGE   │
                        └────┬─────┘
                             │
                             ▼
                        ┌──────────┐
                        │  TASK:   │
                        │  "DSL"   │
                        └────┬─────┘
                             │
                             ▼
                        ┌──────────┐
                        │  RESULT  │
                        └──────────┘
```

#### Mathematical Model
```
Let:
  S₁ = /deep + /ctx7 + /research
  S₂ = /orch /wflw /coord
  S₃ = /meta-skill-builder
  S₄ = /meta-agent

Execution:
  W = (S₁ || S₂ || S₃ || S₄) ∘ task

Where:
  (S₁ || S₂ || S₃ || S₄) = fork([S₁, S₂, S₃, S₄]) → join → merge

Time complexity:
  T(W) = max(T(S₁), T(S₂), T(S₃), T(S₄)) + T(merge) + T(task)
```

#### Resource Allocation
```yaml
stream_1:
  agents: [deep-researcher, context7-doc-reviewer]
  commands: [/deep, /ctx7, /research]
  estimated_tokens: 25,000
  estimated_time: 15-20 min

stream_2:
  commands: [/orch, /wflw, /coord]
  estimated_tokens: 15,000
  estimated_time: 10-15 min

stream_3:
  commands: [/meta-skill-builder, /agent]
  estimated_tokens: 20,000
  estimated_time: 12-18 min

total_parallel:
  max_tokens: 60,000 (not summed, concurrent)
  max_time: ~20 minutes (longest stream)

task_execution:
  tokens: 30,000
  time: 15-25 min

grand_total:
  tokens: ~90,000
  time: ~45 minutes
```

---

### 📊 Level 4: Complex Orchestration & Conditionals

**Complexity**: High
**Execution Model**: DAG with branching logic
**Token Budget**: 80,000-150,000
**Time Estimate**: 45-90 minutes

#### Syntax Pattern
```dsl
<agent> -> (<parallel_group>) -> if(<condition>) <then_branch> : <else_branch>
```

#### Examples
```dsl
// Nested parallel within sequence
research -> (design || implement || test) -> integrate

// Conditional execution
deploy -> if(tests_pass) production : rollback

// Error handling with retry
api_call -> catch(error) retry(3) : fail_gracefully

// Resource-constrained execution
(heavy_task1 || heavy_task2)[budget=50000]
```

#### Execution Flow
```
NESTED PARALLEL IN SEQUENCE:

research
   │
   ├──────────────┬──────────────┬──────────────┐
   │              │              │              │
   ▼              ▼              ▼              │
design      implement        test             │
   │              │              │              │
   └──────────────┴──────────────┴──────────────┘
                  │
                  ▼
              integrate


CONDITIONAL BRANCHING:

         deploy
           │
           ▼
    ┌──────────────┐
    │ tests_pass?  │
    └──────┬───────┘
           │
      ┌────┴────┐
      │         │
    YES        NO
      │         │
      ▼         ▼
 production  rollback


ERROR HANDLING:

    api_call
       │
   ┌───┴────┐
   │ Error? │
   └───┬────┘
       │
    ┌──┴──┐
    │ YES │ ────▶ retry (attempt 1)
    └─────┘           │
                  ┌───┴────┐
                  │ Error? │
                  └───┬────┘
                   retry 2...
```

#### Advanced Features

**1. Conditional Execution**
```dsl
workflow test_and_deploy {
  test_result = run_tests

  if (test_result.success) {
    deploy -> monitor
  } else {
    notify_team -> fix_bugs -> retry
  }
}
```

**2. Loop Constructs**
```dsl
workflow process_all_files {
  files = glob("*.py")

  for file in files {
    analyze(file) || test(file)
  }

  aggregate_results
}
```

**3. Resource Constraints**
```dsl
// Limit token budget for parallel execution
(agent1 || agent2 || agent3)[
  budget = 50000,
  timeout = 30min,
  retry = 2
]
```

#### Mathematical Model
```
Conditional:
  if(p) a else b = p ? a : b

  where p: Context → Boolean
        a, b: Workflow

Loop:
  for x in xs: f(x) = map(f, xs)

  where xs: List⟨τ⟩
        f: τ → Result

Resource Constraint:
  constrained(w, r) = w with resource_limit(r)

  where w: Workflow
        r: {budget, timeout, ...}
```

---

### 📊 Level 5: Workflow Composition & Iteration

**Complexity**: Very High
**Execution Model**: Higher-order workflows
**Token Budget**: 120,000-250,000
**Time Estimate**: 90-180 minutes

#### Syntax Pattern
```dsl
workflow <name>(<params>) {
  <sub_workflow1>(<args>) ->
  <sub_workflow2>(<args>) ->
  map(<collection>, <workflow_fn>)
}
```

#### Examples
```dsl
// Named workflow with parameters
workflow full_stack_app(spec, tech_stack) {
  research(spec) ->
  design_api(tech_stack.backend) ->
  design_ui(tech_stack.frontend) ->
  (implement_backend || implement_frontend) ->
  integrate ->
  test ->
  deploy
}

// Workflow calling workflow
workflow ci_cd_pipeline {
  build_workflow() ->
  test_workflow() ->
  if(tests_pass) {
    deploy_workflow(environment="staging") ->
    smoke_test_workflow() ->
    if(smoke_pass) {
      deploy_workflow(environment="production")
    }
  }
}

// Map-reduce pattern
workflow analyze_repository {
  files = glob("src/**/*.py")

  // Map: analyze each file in parallel
  analyses = map(files, file => {
    code_quality(file) ||
    security_scan(file) ||
    test_coverage(file)
  })

  // Reduce: aggregate results
  report = reduce(analyses, merge_reports)
}
```

#### Execution Flow
```
WORKFLOW COMPOSITION:

┌─────────────────────────────────────────────┐
│  full_stack_app(spec, tech_stack)           │
├─────────────────────────────────────────────┤
│                                             │
│  research(spec)                             │
│     │                                       │
│     ▼                                       │
│  design_api(tech_stack.backend)            │
│     │                                       │
│     ▼                                       │
│  design_ui(tech_stack.frontend)            │
│     │                                       │
│     ├──────────┬──────────┐                │
│     ▼          ▼          │                │
│  impl_backend impl_frontend                │
│     │          │          │                │
│     └──────────┴──────────┘                │
│     │                                       │
│     ▼                                       │
│  integrate                                  │
│     │                                       │
│     ▼                                       │
│  test                                       │
│     │                                       │
│     ▼                                       │
│  deploy                                     │
│                                             │
└─────────────────────────────────────────────┘


MAP-REDUCE:

       glob("src/**/*.py")
              │
              ▼
      [file1, file2, ..., fileN]
              │
        ┌─────┴─────┐
        │    map    │
        └─────┬─────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
 analyze1  analyze2  analyzeN
 (parallel)(parallel)(parallel)
    │         │         │
    └─────────┼─────────┘
              │
        ┌─────┴─────┐
        │  reduce   │
        └─────┬─────┘
              │
              ▼
         final_report
```

#### Context Sharing Pattern
```dsl
workflow api_with_context {
  // Build shared context
  ctx = {}
  ctx = ctx + /ctx7("fastapi")
  ctx = ctx + /ctx7("postgresql")
  ctx = ctx + /ctx7("redis")

  // All agents share context
  researcher[ctx] ->
  architect[ctx] ->
  implementer[ctx] ->
  tester[ctx]

  // Context contains all library docs
}
```

#### Mathematical Model
```
Named Workflow:
  W⟨τ₁, ..., τₙ⟩ : (τ₁ × ... × τₙ) → Result

Workflow Composition:
  W₁ ∘ W₂ = λx. W₁(W₂(x))

Map:
  map: List⟨τ⟩ × (τ → σ) → List⟨σ⟩
  map(xs, f) = [f(x₁), f(x₂), ..., f(xₙ)]

Reduce:
  reduce: List⟨τ⟩ × (τ × τ → τ) → τ
  reduce([x₁, ..., xₙ], f) = f(...f(f(x₁, x₂), x₃)..., xₙ)

Context Sharing:
  W[ctx]: (Context × Input) → (Context' × Output)
```

---

### 📊 Level 6: Mathematical Meta-Programming

**Complexity**: Extreme
**Execution Model**: Abstract workflow generators
**Token Budget**: 200,000+
**Time Estimate**: 3+ hours

#### Syntax Pattern
```dsl
meta_workflow <name>⟨τ⟩ = λ(params) -> workflow_ast

functor map_workflow: Workflow⟨τ⟩ → Workflow⟨σ⟩

monad compose_workflows: List⟨Workflow⟩ → Workflow
```

#### Examples
```dsl
// Parameterized workflow generator
meta_workflow microservice⟨Domain⟩ {
  // Abstract over domain type
  type_check Domain

  // Generate workflow based on domain
  λ(domain: Domain) -> {
    design_schema(domain) ->
    generate_api(domain) ->
    implement_crud(domain) ->
    generate_tests(domain) ->
    deploy_service(domain)
  }
}

// Instantiate concrete workflows
user_service = microservice⟨User⟩("user management")
product_service = microservice⟨Product⟩("product catalog")

// Functor: map over workflow results
workflow_functor = map_workflow(
  base_workflow,
  transform_fn: (result) -> enhanced_result
)

// Monad: compose workflows with context threading
composed = do {
  r1 <- research_workflow
  r2 <- design_workflow(r1)
  r3 <- implement_workflow(r2)
  return r3
}
```

#### Category Theory Foundations
```dsl
// Workflows form a category
Category Workflow where
  objects = {Agent, Skill, Result}
  morphisms = {Workflow⟨τ₁, τ₂⟩}

  // Identity morphism
  id: τ → τ
  id(x) = x

  // Composition
  (∘): (β → γ) → (α → β) → (α → γ)
  (f ∘ g)(x) = f(g(x))

  // Laws:
  // 1. Left identity:  id ∘ f = f
  // 2. Right identity: f ∘ id = f
  // 3. Associativity:  (f ∘ g) ∘ h = f ∘ (g ∘ h)

// Functors between categories
Functor F: Workflow → EnhancedWorkflow where
  fmap: (α → β) → (F α → F β)

// Applicative Functor
Applicative F where
  pure: α → F α
  (<*>): F (α → β) → F α → F β

// Monad
Monad M where
  return: α → M α
  (>>=): M α → (α → M β) → M β

  // Laws:
  // 1. Left identity:  return a >>= f  = f a
  // 2. Right identity: m >>= return    = m
  // 3. Associativity:  (m >>= f) >>= g = m >>= (λx -> f x >>= g)
```

#### Advanced Meta-Programming
```dsl
// Dynamic workflow construction
meta build_workflow(capabilities: List⟨Capability⟩) -> Workflow {
  // Select agents based on capabilities
  agents = select_agents(capabilities)

  // Optimize execution order
  dag = build_dependency_graph(agents)
  schedule = optimize_schedule(dag)

  // Generate workflow AST
  return workflow_from_schedule(schedule)
}

// Type-level computation
type family OptimalAgent⟨τ⟩ where
  OptimalAgent⟨API⟩ = api-architect
  OptimalAgent⟨Frontend⟩ = frontend-specialist
  OptimalAgent⟨Backend⟩ = backend-specialist

// Dependent types
workflow type_safe_pipeline⟨τ₁, τ₂, τ₃⟩(
  input: τ₁,
  f: τ₁ → τ₂,
  g: τ₂ → τ₃
) -> τ₃ {
  result = g(f(input))
  return result : τ₃  // Type guaranteed at compile time
}
```

#### Execution Model
```
META-WORKFLOW COMPILATION:

┌──────────────────────────────────┐
│  Meta-Workflow Definition        │
│  meta_workflow⟨τ⟩ = λ...         │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  Type Inference & Checking       │
│  - Infer type parameters         │
│  - Check type constraints        │
│  - Verify category laws          │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  Workflow AST Generation         │
│  - Build abstract syntax tree    │
│  - Apply transformations         │
│  - Optimize execution plan       │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  Concrete Workflow Instantiation │
│  - Specialize generic workflows  │
│  - Resolve type variables        │
│  - Generate executable DAG       │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  Execution                       │
│  - Standard DAG execution        │
│  - Type-safe at runtime          │
└──────────────────────────────────┘
```

#### Mathematical Formalization
```
Abstract Workflow Type:
  W⟨τ₁, ..., τₙ⟩ : (Context × τ₁ × ... × τₙ) → Result⟨σ⟩

Higher-Kinded Types:
  F⟨_⟩ : Type → Type
  Example: Workflow⟨_⟩, Result⟨_⟩, List⟨_⟩

Type Constructor Composition:
  (F ∘ G)⟨τ⟩ = F⟨G⟨τ⟩⟩
  Example: Result⟨List⟨Workflow⟨Agent⟩⟩⟩

Polymorphic Workflows:
  ∀τ. W⟨τ⟩ : τ → Result⟨τ⟩
  Example: identity workflow works for any type

Dependent Types:
  W : Π(x : τ₁). τ₂(x)
  Example: pipeline length determines result type
```

---

## Complexity Comparison Table

| Level | Name | Operators | Control Flow | Composition | Token Budget | Time Est. | Example |
|-------|------|-----------|--------------|-------------|--------------|-----------|---------|
| **1** | Basic | None | Linear | None | 5-15K | 2-5 min | `agent : task` |
| **2** | Simple | `+`, `->`, `\|\|` | Sequential/Parallel | Binary | 10-30K | 5-15 min | `a -> b` |
| **3** | Parallel Streams | `+`, `->`, `\|\|`, `()` | Multi-stream | N-ary | 40-100K | 20-45 min | `(a \|\| b \|\| c) : task` |
| **4** | Complex Orch. | All + `if`, `catch` | Conditional | Nested | 80-150K | 45-90 min | `a -> (b \|\| c) -> if(x) d : e` |
| **5** | Workflows | All + `workflow`, `map` | Loops, Named | Higher-order | 120-250K | 90-180 min | `workflow w { map(xs, f) }` |
| **6** | Meta | All + `⟨τ⟩`, `λ` | Abstract | Category Theory | 200K+ | 3+ hours | `meta⟨τ⟩ = λx. ...` |

---

## Progression Path

```
LEARNING PROGRESSION:

Level 1: Basic
  └─▶ Master single invocations
       └─▶ Level 2: Simple Operators
            └─▶ Combine agents with skills
                 └─▶ Level 3: Parallel Streams ⭐
                      └─▶ Orchestrate multiple streams
                           └─▶ Level 4: Complex Orchestration
                                └─▶ Add conditionals and error handling
                                     └─▶ Level 5: Workflow Composition
                                          └─▶ Build reusable workflows
                                               └─▶ Level 6: Meta-Programming
                                                    └─▶ Generate workflows programmatically

TYPICAL USER JOURNEY:

Week 1:   Levels 1-2 (basics)
Week 2-3: Level 3 (parallel coordination) ⭐
Week 4-6: Level 4 (complex orchestration)
Month 2+: Level 5 (workflow library)
Month 3+: Level 6 (meta-workflows, if needed)
```

---

## Visual Summary

```
╔══════════════════════════════════════════════════════════════╗
║                    COMPLEXITY SPECTRUM                       ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Simple                                            Complex   ║
║  ───────────────────────────────────────────────────────────║
║                                                              ║
║  L1    L2        L3 ⭐      L4          L5          L6      ║
║  │     │         │          │           │           │       ║
║  │     │         │          │           │           │       ║
║  ▼     ▼         ▼          ▼           ▼           ▼       ║
║                                                              ║
║  Single  Binary   Multi-     Nested     Named       Meta    ║
║  call    ops      stream     control    workflows   λ⟨τ⟩    ║
║                                                              ║
║  5K      15K      50K        100K       200K        500K+   ║
║  tokens  tokens   tokens     tokens     tokens      tokens  ║
║                                                              ║
║  5 min   10 min   30 min     60 min     2 hrs       4+ hrs  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

YOUR STARTING POINT: Level 3 ⭐
  (/deep + /ctx7 + /research || /orch /wflw /coord || /meta-skill) : task
```

---

## Recommendations by Use Case

### Quick Task (Use Level 1-2)
```dsl
/ctx7 = express
api-architect : "design auth API"
```

### Research & Planning (Use Level 3) ⭐
```dsl
(deep-researcher || context7-doc-reviewer || api-architect) : "research payment systems"
```

### Full Feature Development (Use Level 4-5)
```dsl
workflow feature {
  research -> (design || test-plan) -> implement -> test -> deploy
}
```

### Reusable Workflow Library (Use Level 5)
```dsl
workflow microservice(domain) {
  design_api(domain) ->
  implement(domain) ->
  test(domain) ->
  deploy(domain)
}
```

### Advanced Automation (Use Level 6)
```dsl
meta_workflow⟨Domain⟩ = λd. optimize(generate_workflow(d))
```

---

**Your complexity level (Level 3) is optimal for most real-world orchestration tasks!**
