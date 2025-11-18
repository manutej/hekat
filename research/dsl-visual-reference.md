# CCAO-DSL: Visual Reference Guide

**Version**: 1.0.0
**Date**: 2025-10-19
**Purpose**: Visual diagrams and flowcharts for DSL architecture

---

## Table of Contents

1. [System Architecture Diagrams](#1-system-architecture-diagrams)
2. [Execution Flow Charts](#2-execution-flow-charts)
3. [Type System Diagrams](#3-type-system-diagrams)
4. [Operator Precedence Trees](#4-operator-precedence-trees)
5. [DAG Visualizations](#5-dag-visualizations)
6. [State Machine Diagrams](#6-state-machine-diagrams)

---

## 1. System Architecture Diagrams

### 1.1 Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER LAYER                               │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Workflow Files (.dsl)                                    │ │
│  │  - api-design.dsl                                         │ │
│  │  - fullstack-app.dsl                                      │ │
│  │  - code-review.dsl                                        │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COMPILER FRONTEND                            │
│  ┌──────────┐      ┌──────────┐      ┌──────────────┐         │
│  │  Lexer   │  →   │  Parser  │  →   │ Type Checker │         │
│  │          │      │          │      │              │         │
│  │ .dsl →   │      │ Tokens → │      │ AST →        │         │
│  │ Tokens   │      │ AST      │      │ TypedAST     │         │
│  └──────────┘      └──────────┘      └──────────────┘         │
│                                                                  │
│  Error Reporting: Syntax errors, type mismatches               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COMPILER BACKEND                             │
│  ┌──────────┐      ┌──────────┐      ┌──────────────┐         │
│  │   DAG    │  →   │ Parallel │  →   │  Resource    │         │
│  │ Builder  │      │ Detector │      │  Allocator   │         │
│  │          │      │          │      │              │         │
│  │ TypedAST │      │ DAG →    │      │ Plan →       │         │
│  │ → DAG    │      │ Groups   │      │ Optimized    │         │
│  └──────────┘      └──────────┘      └──────────────┘         │
│                                                                  │
│  Optimization: Parallelization, resource allocation             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RUNTIME LAYER                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Execution Coordinator                       │  │
│  │  ┌────────────┐  ┌────────────┐  ┌─────────────┐       │  │
│  │  │ Sequential │  │  Parallel  │  │   Merge     │       │  │
│  │  │  Executor  │  │  Executor  │  │ Aggregator  │       │  │
│  │  └────────────┘  └────────────┘  └─────────────┘       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Agent Registry & Loader                     │  │
│  │  - 33 Agents (api-architect, practical-programmer, ...)  │  │
│  │  - 68 Skills (fastapi, postgresql, react, ...)          │  │
│  │  - 36 Commands (/ctx7, /crew, /workflows, ...)          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Execution Context                           │  │
│  │  - Working directory                                     │  │
│  │  - Environment variables                                 │  │
│  │  - Skill cache                                           │  │
│  │  - MCP server connections                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL INTEGRATIONS                        │
│  ┌──────────┐      ┌──────────┐      ┌──────────────┐         │
│  │ Context7 │      │  Linear  │      │  Playwright  │         │
│  │  (MCP)   │      │  (MCP)   │      │    (MCP)     │         │
│  └──────────┘      └──────────┘      └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Interaction Diagram

```
    ┌─────────┐
    │   DSL   │
    │  Source │
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │  Lexer  │ ───────→ [Token Stream]
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │ Parser  │ ───────→ [AST]
    └────┬────┘
         │
         ▼
    ┌─────────┐         ┌──────────────┐
    │  Type   │ ←──────→│    Agent     │
    │ Checker │         │   Registry   │
    └────┬────┘         └──────────────┘
         │
         │ [TypedAST]
         ▼
    ┌─────────┐
    │   DAG   │
    │ Builder │ ───────→ [Dependency Graph]
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │Optimizer│ ───────→ [Execution Plan]
    └────┬────┘
         │
         ▼
    ┌─────────┐         ┌──────────────┐
    │Executor │ ←──────→│   Context    │
    │         │         │   Manager    │
    └────┬────┘         └──────────────┘
         │
         │ [Result]
         ▼
    ┌─────────┐
    │  Output │
    └─────────┘
```

---

## 2. Execution Flow Charts

### 2.1 End-to-End Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│ START                                                       │
└────┬────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ Read DSL Source File                                        │
└────┬────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ Tokenize (Lexer)                                            │
│ - Recognize keywords, identifiers, operators                │
│ - Generate token stream                                     │
└────┬────────────────────────────────────────────────────────┘
     │
     │ Success?
     ▼ No
┌─────────────────────────────────────────────────────────────┐
│ Report Lexical Error ──────────────────────────────→ EXIT  │
└─────────────────────────────────────────────────────────────┘
     │ Yes
     ▼
┌─────────────────────────────────────────────────────────────┐
│ Parse (Parser)                                              │
│ - Build Abstract Syntax Tree                                │
│ - Check grammar rules                                       │
└────┬────────────────────────────────────────────────────────┘
     │
     │ Success?
     ▼ No
┌─────────────────────────────────────────────────────────────┐
│ Report Parse Error ─────────────────────────────────→ EXIT │
└─────────────────────────────────────────────────────────────┘
     │ Yes
     ▼
┌─────────────────────────────────────────────────────────────┐
│ Type Check (Type Checker)                                   │
│ - Verify agent-skill compatibility                          │
│ - Check pipeline type compatibility                         │
│ - Infer workflow types                                      │
└────┬────────────────────────────────────────────────────────┘
     │
     │ Success?
     ▼ No
┌─────────────────────────────────────────────────────────────┐
│ Report Type Error ──────────────────────────────────→ EXIT │
└─────────────────────────────────────────────────────────────┘
     │ Yes
     ▼
┌─────────────────────────────────────────────────────────────┐
│ Build DAG (DAG Builder)                                     │
│ - Create dependency graph                                   │
│ - Detect cycles                                             │
└────┬────────────────────────────────────────────────────────┘
     │
     │ Acyclic?
     ▼ No
┌─────────────────────────────────────────────────────────────┐
│ Report Cycle Error ─────────────────────────────────→ EXIT │
└─────────────────────────────────────────────────────────────┘
     │ Yes
     ▼
┌─────────────────────────────────────────────────────────────┐
│ Optimize (Optimizer)                                        │
│ - Detect parallel groups                                    │
│ - Allocate resources                                        │
│ - Create execution plan                                     │
└────┬────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ Execute (Executor)                                          │
│ - Initialize context                                        │
│ - Load agents and skills                                    │
│ - Run tasks (sequential/parallel)                           │
└────┬────────────────────────────────────────────────────────┘
     │
     │ Success?
     ▼ No
┌─────────────────────────────────────────────────────────────┐
│ Handle Runtime Error                                        │
│ - Retry if configured                                       │
│ - Rollback if needed                                        │
│ - Report error                                              │
└────┬────────────────────────────────────────────────────────┘
     │
     │ Retry?
     ▼ No
┌─────────────────────────────────────────────────────────────┐
│ Report Runtime Error ───────────────────────────────→ EXIT │
└─────────────────────────────────────────────────────────────┘
     │ Yes
     │ (loop back to Execute)
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ Aggregate Results                                           │
│ - Merge parallel results                                    │
│ - Combine outputs                                           │
└────┬────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ Return Final Result                                         │
└────┬────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ END                                                         │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Parallel Execution Flow

```
Sequential Executor                Parallel Executor
       │                                  │
       │ Receives Plan                    │ Receives Plan
       ▼                                  ▼
┌──────────────┐                   ┌──────────────┐
│ Topological  │                   │   Identify   │
│     Sort     │                   │   Parallel   │
│              │                   │    Groups    │
└──────┬───────┘                   └──────┬───────┘
       │                                  │
       │ For each task                    │ For each group
       ▼                                  ▼
┌──────────────┐                   ┌──────────────┐
│   Execute    │                   │     Fork     │
│     Task     │                   │   Workers    │
└──────┬───────┘                   └──────┬───────┘
       │                                  │
       │ Wait for completion              │ Distribute tasks
       ▼                                  ▼
┌──────────────┐                   ┌──────────────┐    ┌──────────────┐
│ Pass result  │                   │   Worker 1   │    │   Worker 2   │
│  to next     │                   │   Execute    │    │   Execute    │
│     task     │                   │    Task A    │    │    Task B    │
└──────┬───────┘                   └──────┬───────┘    └──────┬───────┘
       │                                  │                    │
       │ Repeat                           │ Wait for all       │
       ▼                                  ▼                    ▼
┌──────────────┐                   ┌──────────────────────────┐
│     Done     │                   │        Join Results      │
└──────────────┘                   └───────────┬──────────────┘
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │     Done     │
                                        └──────────────┘
```

---

## 3. Type System Diagrams

### 3.1 Type Hierarchy

```
                        Type
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
      Agent             Skill           Primitive
        │                 │                 │
        │                 │          ┌──────┼──────┐
        │                 │          │      │      │
   ┌────┴────┐       ┌────┴────┐  String Number Boolean
   │         │       │         │
AgentType  Workflow  │      Command
           ⟨In,Out⟩  │
                   SkillType
```

### 3.2 Type Inference Tree

```
Example: api-architect + rest-api-design-patterns

                  CombinationNode
                        │
          ┌─────────────┴─────────────┐
          │                           │
     AgentNode                   SkillNode
    "api-architect"        "rest-api-design-patterns"
          │                           │
    [Type Inference]            [Type Lookup]
          │                           │
          ▼                           ▼
    AgentType(                  SkillType(
      name="api-architect"        name="rest-api-design-patterns"
      capabilities=[...]          domain="api-design"
    )                             requires=[]
                                )
          │                           │
          └─────────────┬─────────────┘
                        │
              [Compatibility Check]
                        │
                        ▼
                 compatible: true
                        │
                        ▼
                 Agent⟨SkillType⟩
```

### 3.3 Type Checking Workflow

```
                    Input: AST
                         │
                         ▼
            ┌─────────────────────────┐
            │   Initialize Type       │
            │     Environment         │
            │  (load agent registry)  │
            └────────────┬────────────┘
                         │
                         ▼
            ┌─────────────────────────┐
            │   Visit AST Nodes       │
            │   (depth-first)         │
            └────────────┬────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
  AgentNode        SequenceNode     ParallelNode
        │                │                │
        ▼                ▼                ▼
  [Lookup Type]   [Check I/O        [Unify Types]
                   Compatible]
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
            ┌─────────────────────────┐
            │   Annotate AST with     │
            │   Type Information      │
            └────────────┬────────────┘
                         │
                         ▼
              Success?   │   Failure
                    ┌────┴────┐
                    │         │
                    ▼         ▼
              TypedAST   TypeError
```

---

## 4. Operator Precedence Trees

### 4.1 Precedence Levels (High to Low)

```
Level 1: ( )              [Grouping]
Level 2: /command         [Command invocation]
Level 3: agent[skills]    [Skill loading]
Level 4: +                [Combination]
Level 5: ||               [Parallel]
Level 6: ->               [Sequence]
Level 7: =, :             [Assignment]
```

### 4.2 Parse Tree Example

**Input**: `a + b -> c || d`

**Parse Tree**:
```
                    SequenceNode (->)
                         │
            ┌────────────┴────────────┐
            │                         │
    CombinationNode (+)         ParallelNode (||)
            │                         │
       ┌────┴────┐              ┌────┴────┐
       │         │              │         │
    AgentNode AgentNode     AgentNode AgentNode
      "a"       "b"           "c"       "d"

Execution order:
1. Combine a + b
2. Execute in parallel: (a+b) and d
3. Wait for c and d to complete
4. Merge results
```

**Alternative Grouping**: `a + (b -> c) || d`

**Parse Tree**:
```
                    ParallelNode (||)
                         │
            ┌────────────┴────────────┐
            │                         │
    CombinationNode (+)           AgentNode
            │                         "d"
       ┌────┴────┐
       │         │
    AgentNode SequenceNode (->)
      "a"         │
            ┌─────┴─────┐
            │           │
        AgentNode   AgentNode
          "b"         "c"

Execution order:
1. Execute b -> c (sequential)
2. Combine a + (result of b->c)
3. Execute (a + result) || d in parallel
4. Merge results
```

---

## 5. DAG Visualizations

### 5.1 Simple Sequential DAG

**DSL**: `a -> b -> c`

**DAG**:
```
┌───┐     ┌───┐     ┌───┐
│ a │ ──→ │ b │ ──→ │ c │
└───┘     └───┘     └───┘

Critical Path: a → b → c
Total Time: time(a) + time(b) + time(c)
```

### 5.2 Simple Parallel DAG

**DSL**: `a || b || c`

**DAG**:
```
        ┌───┐
    ┌──→│ a │──┐
    │   └───┘  │
    │          │
START│   ┌───┐  │ MERGE
    ├──→│ b │──┤
    │   └───┘  │
    │          │
    └──→│ c │──┘
        └───┘

Critical Path: max(a, b, c)
Total Time: max(time(a), time(b), time(c))
```

### 5.3 Mixed Sequential/Parallel DAG

**DSL**: `a -> (b || c) -> d`

**DAG**:
```
┌───┐     ┌───┐     ┌───┐
│ a │ ──┬→│ b │──┬→ │ d │
└───┘   │ └───┘  │  └───┘
        │        │
        └→│ c │──┘
          └───┘

Critical Path: a → max(b, c) → d
Total Time: time(a) + max(time(b), time(c)) + time(d)
```

### 5.4 Complex Workflow DAG

**DSL**:
```
workflow complex {
  research -> (design || prototype) -> (impl1 || impl2 || impl3) -> test -> deploy
}
```

**DAG**:
```
┌──────────┐
│ research │
└────┬─────┘
     │
     ├────┬────────┐
     │    │        │
     ▼    ▼        │
  ┌──────┬──────┐  │
  │design│proto-│  │
  │      │type  │  │
  └──┬───┴───┬──┘  │
     │       │     │
     └───┬───┴─────┘
         │
    ┌────┼────┐
    │    │    │
    ▼    ▼    ▼
  ┌────┬────┬────┐
  │impl│impl│impl│
  │ 1  │ 2  │ 3  │
  └─┬──┴─┬──┴─┬──┘
    │    │    │
    └────┼────┘
         │
         ▼
    ┌────────┐
    │  test  │
    └────┬───┘
         │
         ▼
    ┌────────┐
    │ deploy │
    └────────┘

Parallel Groups:
1. [design, prototype]
2. [impl1, impl2, impl3]

Critical Path:
research → max(design, prototype) → max(impl1, impl2, impl3) → test → deploy
```

---

## 6. State Machine Diagrams

### 6.1 Execution State Machine

```
                    ┌─────────┐
                    │  INIT   │
                    └────┬────┘
                         │
                         ▼
                    ┌─────────┐
                    │ PARSING │
                    └────┬────┘
                         │
                    Success│ Failure
                         │
          ┌──────────────┼──────────────┐
          │                             │
          ▼                             ▼
    ┌──────────┐                  ┌──────────┐
    │  TYPING  │                  │  ERROR   │
    └────┬─────┘                  └──────────┘
         │
    Success│ Failure
         │
    ┌────┼────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────┐
│BUILDING │ │  ERROR   │
│   DAG   │ └──────────┘
└────┬────┘
     │
Success│ Failure
     │
┌────┼────┐
│         │
▼         ▼
┌─────────┐ ┌──────────┐
│OPTIMIZ- │ │  ERROR   │
│  ING    │ └──────────┘
└────┬────┘
     │
     ▼
┌─────────┐
│EXECUTING│←──┐ Retry
└────┬────┘   │
     │        │
Success│ Failure─┘
     │
     ▼
┌─────────┐
│COMPLETE │
└─────────┘
```

### 6.2 Task State Machine

```
┌─────────┐
│ PENDING │
└────┬────┘
     │
     │ Schedule
     ▼
┌─────────┐
│  READY  │
└────┬────┘
     │
     │ Start
     ▼
┌─────────┐     Timeout
│ RUNNING │────────────┐
└────┬────┘            │
     │                 │
Success│ Error         │
     │    │            │
     ▼    ▼            ▼
┌─────────┬──────┬─────────┐
│COMPLETE │FAILED│ TIMEOUT │
└─────────┴──────┴─────────┘
               │
               │ Retry?
               ▼
          ┌─────────┐
          │ PENDING │ (loop back)
          └─────────┘
```

### 6.3 Parallel Execution State Machine

```
                ┌─────────┐
                │  START  │
                └────┬────┘
                     │
                     │ Fork
                     ▼
            ┌────────────────┐
            │  FORK_WORKERS  │
            └────────┬───────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │WORKER 1 │ │WORKER 2 │ │WORKER 3 │
   │ RUNNING │ │ RUNNING │ │ RUNNING │
   └────┬────┘ └────┬────┘ └────┬────┘
        │            │            │
        │ Complete   │ Complete   │ Complete
        ▼            ▼            ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │WORKER 1 │ │WORKER 2 │ │WORKER 3 │
   │  DONE   │ │  DONE   │ │  DONE   │
   └────┬────┘ └────┬────┘ └────┬────┘
        │            │            │
        └────────────┼────────────┘
                     │
                     │ All Done
                     ▼
              ┌─────────────┐
              │ JOIN_RESULTS│
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │   MERGED    │
              └─────────────┘
```

---

## 7. Memory Model Diagrams

### 7.1 Execution Context Structure

```
┌─────────────────────────────────────────────────────────┐
│              Execution Context                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌────────────────────┐  ┌────────────────────┐       │
│  │  Working Directory │  │   Environment Vars │       │
│  │  /path/to/project  │  │   PYTHONPATH=...   │       │
│  └────────────────────┘  └────────────────────┘       │
│                                                         │
│  ┌────────────────────────────────────────────┐       │
│  │           State Dictionary                 │       │
│  │  ┌──────────────┐  ┌─────────────────┐    │       │
│  │  │   Variable   │  │   Intermediate  │    │       │
│  │  │   Bindings   │  │     Results     │    │       │
│  │  └──────────────┘  └─────────────────┘    │       │
│  └────────────────────────────────────────────┘       │
│                                                         │
│  ┌────────────────────────────────────────────┐       │
│  │           Agent Instances                  │       │
│  │  ┌─────────────────┐  ┌──────────────┐    │       │
│  │  │  api-architect  │  │  database-   │    │       │
│  │  │  (loaded)       │  │  specialist  │    │       │
│  │  └─────────────────┘  └──────────────┘    │       │
│  └────────────────────────────────────────────┘       │
│                                                         │
│  ┌────────────────────────────────────────────┐       │
│  │            Skill Cache                     │       │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────┐  │       │
│  │  │ fastapi  │  │postgre-  │  │  react  │  │       │
│  │  │ (cached) │  │sql       │  │ (cached)│  │       │
│  │  └──────────┘  └──────────┘  └─────────┘  │       │
│  └────────────────────────────────────────────┘       │
│                                                         │
│  ┌────────────────────────────────────────────┐       │
│  │          MCP Connections                   │       │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────┐  │       │
│  │  │Context7  │  │  Linear  │  │Playwright│ │       │
│  │  │ (active) │  │ (active) │  │ (active)│  │       │
│  │  └──────────┘  └──────────┘  └─────────┘  │       │
│  └────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
```

### 7.2 Skill Loading Memory Model

```
Agent Memory Space
┌─────────────────────────────────────────┐
│  Agent: api-architect                   │
├─────────────────────────────────────────┤
│  Base Capabilities:                     │
│  - API design knowledge                 │
│  - REST principles                      │
│  - Database concepts                    │
│                                         │
│  ┌────────────────────────────────┐    │
│  │  Loaded Skills (+ operator)    │    │
│  ├────────────────────────────────┤    │
│  │                                │    │
│  │  ┌──────────────────────────┐ │    │
│  │  │ rest-api-design-patterns │ │    │
│  │  │  - Endpoint conventions  │ │    │
│  │  │  - HTTP methods         │ │    │
│  │  │  - Status codes         │ │    │
│  │  └──────────────────────────┘ │    │
│  │                                │    │
│  │  ┌──────────────────────────┐ │    │
│  │  │ postgresql-database-eng  │ │    │
│  │  │  - Schema design        │ │    │
│  │  │  - Index optimization   │ │    │
│  │  │  - Query patterns       │ │    │
│  │  └──────────────────────────┘ │    │
│  │                                │    │
│  │  ┌──────────────────────────┐ │    │
│  │  │ oauth2-authentication    │ │    │
│  │  │  - OAuth flows          │ │    │
│  │  │  - Token management     │ │    │
│  │  │  - Security patterns    │ │    │
│  │  └──────────────────────────┘ │    │
│  └────────────────────────────────┘    │
└─────────────────────────────────────────┘

Memory Growth:
Base: 100 MB
+ rest-api-design-patterns: +50 MB
+ postgresql-database-eng: +80 MB
+ oauth2-authentication: +40 MB
Total: 270 MB
```

---

## 8. Workflow Execution Timeline

### 8.1 Sequential Execution Timeline

**DSL**: `research -> design -> implement`

```
Time →
0s        10s       25s       50s
│─────────┼─────────┼─────────┼
│         │         │         │
├─────────┤         │         │
│research │         │         │
└─────────┘         │         │
          ├─────────────────┤ │
          │     design      │ │
          └─────────────────┘ │
                    ├─────────────────────┤
                    │     implement       │
                    └─────────────────────┘

Total time: 50s
Parallelism: None
Resource usage: 1 agent at a time
```

### 8.2 Parallel Execution Timeline

**DSL**: `frontend || backend || database`

```
Time →
0s        10s       20s
│─────────┼─────────┼
│         │         │
├─────────────────┤ │
│   frontend      │ │
└─────────────────┘ │
├─────────┤         │
│ backend │         │
└─────────┘         │
├─────────────────────┤
│     database        │
└─────────────────────┘

Total time: 20s (max of 15s, 10s, 20s)
Parallelism: 3 concurrent agents
Resource usage: Peak 3 agents
```

### 8.3 Mixed Execution Timeline

**DSL**: `research -> (frontend || backend) -> deploy`

```
Time →
0s    5s      15s       25s       35s
│─────┼───────┼─────────┼─────────┼
│     │       │         │         │
├─────┤       │         │         │
│res- │       │         │         │
│earch│       │         │         │
└─────┘       │         │         │
      ├───────────────┤ │         │
      │   frontend    │ │         │
      └───────────────┘ │         │
      ├─────────┤       │         │
      │ backend │       │         │
      └─────────┘       │         │
                ├───────────────┤ │
                │    deploy     │ │
                └───────────────┘ │

Total time: 30s
Phases:
1. research (5s) - sequential
2. frontend || backend (10s) - parallel
3. deploy (10s) - sequential
```

---

## Summary

This visual reference provides diagrams for:

1. **System Architecture**: Overall structure and component interaction
2. **Execution Flow**: Step-by-step workflow execution
3. **Type System**: Type hierarchy and inference
4. **Operator Precedence**: Parse tree construction
5. **DAG Visualization**: Dependency graphs
6. **State Machines**: Execution and task states
7. **Memory Model**: Context and skill loading
8. **Execution Timelines**: Sequential vs parallel execution

Use these diagrams to:
- Understand system architecture
- Debug execution flows
- Visualize type checking
- Optimize workflow performance
- Explain DSL concepts

---

**Version**: 1.0.0
**Companion Documents**: dsl-specification.md, dsl-examples.md, dsl-api-blueprint.md
