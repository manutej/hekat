# Domain-Specific Language (DSL) Design Patterns
## Comprehensive Research for Agent Orchestration Systems

**Version:** 1.0
**Date:** October 19, 2025
**Author:** Deep Research Analysis
**Status:** Comprehensive Reference Document

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Introduction to DSL Theory](#introduction-to-dsl-theory)
3. [Formal Grammar Specifications](#formal-grammar-specifications)
4. [Abstract Syntax Trees and Semantic Analysis](#abstract-syntax-trees-and-semantic-analysis)
5. [Lambda Calculus and Functional Composition](#lambda-calculus-and-functional-composition)
6. [Agent Orchestration Patterns](#agent-orchestration-patterns)
7. [Real-World DSL Examples](#real-world-dsl-examples)
8. [Parser and Interpreter Design](#parser-and-interpreter-design)
9. [Claude Code CLI Architecture Analysis](#claude-code-cli-architecture-analysis)
10. [Mathematical Foundations](#mathematical-foundations)
11. [Implementation Patterns](#implementation-patterns)
12. [DSL Design for Agent Orchestration](#dsl-design-for-agent-orchestration)
13. [Bibliography and References](#bibliography-and-references)

---

## Executive Summary

This document presents comprehensive research on Domain-Specific Language (DSL) design patterns with specific focus on agent orchestration systems. The research synthesizes formal language theory, practical implementation patterns, and real-world examples to inform the design of DSLs optimized for Claude Code's multi-agent orchestration architecture.

### Key Findings

1. **DSL Patterns**: Eight recurring design patterns have been identified for DSL implementation, including language extension, restriction, partial usage, and lexical processing.

2. **Agent Orchestration**: Sequential and parallel execution patterns can be mathematically modeled using Directed Acyclic Graphs (DAGs) with topological sorting algorithms achieving O(V + E) complexity.

3. **Parser Architecture**: Recursive descent parsing provides the simplest and most maintainable approach for DSL implementation, with parser combinators offering functional composition benefits.

4. **YAML-based DSLs**: Modern orchestration systems (GitHub Actions, Airflow, Kubernetes) converge on YAML as a declarative DSL format, validated through JSON Schema.

5. **Functional Foundations**: Combinator libraries and monadic composition provide powerful abstractions for building composable DSL semantics.

### Strategic Recommendations

For Claude Code agent orchestration DSL:

- **Use YAML** as the surface syntax for declarative workflow definitions
- **Implement DAG-based** execution with topological sorting for dependency resolution
- **Support hybrid** sequential and parallel execution strategies
- **Leverage JSON Schema** for validation and tooling support
- **Design for composability** using functional combinator patterns
- **Provide progressive disclosure** with metadata enrichment (token estimates, timing)

---

## Introduction to DSL Theory

### What is a Domain-Specific Language?

A Domain-Specific Language (DSL) is a computer language specialized to a particular application domain. Unlike general-purpose languages (GPLs) like Python or Java, DSLs are optimized for expressing solutions in a specific problem space.

#### Characteristics of DSLs

1. **Limited Expressiveness**: Focused on specific domain concepts
2. **High Abstraction**: Domain concepts as first-class language constructs
3. **Declarative Nature**: Focus on "what" rather than "how"
4. **Domain Proximity**: Language maps naturally to domain vocabulary
5. **Productivity Boost**: Reduced code volume for domain-specific tasks

#### Types of DSLs

**External DSLs** (eDSL):
- Custom syntax and grammar
- Require dedicated parser and interpreter
- Examples: SQL, GraphQL, Terraform HCL, YAML workflows

**Internal DSLs** (iDSL):
- Embedded in host language
- Leverage host language parser
- Examples: jQuery, RSpec, ScalaTest

**Hybrid Approaches**:
- Custom syntax with host language embedding
- Examples: Template languages, configuration DSLs

### DSL Design Space

```
┌────────────────────────────────────────────────────────────┐
│                    DSL Design Spectrum                     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Low Abstraction                      High Abstraction    │
│  ──────────────────────────────────────────────────────   │
│                                                            │
│  [General Purpose]  →  [DSL]  →  [Pure Declarative]      │
│                                                            │
│  Examples:                                                 │
│  Python/Java  →  YAML Workflows  →  SQL/Datalog          │
│                                                            │
│  Characteristics:                                          │
│  Full Turing     →  Limited Logic  →  No Computation     │
│  Complete        →  Domain-Focused →  Pure Declaration    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Notable DSL Design Patterns

Based on research by Spinellis (2000), eight recurring patterns exist for DSL design:

#### 1. **Language Extension**
Extend existing language with domain constructs.
- **Example**: Ruby on Rails extending Ruby with ActiveRecord DSL
- **Advantages**: Leverage existing tooling, familiar syntax
- **Disadvantages**: Constrained by host language limitations

#### 2. **Language Restriction**
Subset of existing language, removing dangerous features.
- **Example**: JavaScript strict mode, SQL subset
- **Advantages**: Security, predictability, formal verification
- **Disadvantages**: Limited expressiveness

#### 3. **Language Specialization**
General language with domain-specific libraries.
- **Example**: NumPy for scientific computing
- **Advantages**: Full language power when needed
- **Disadvantages**: Can be verbose for simple domain tasks

#### 4. **Standalone Language**
Completely custom language and toolchain.
- **Example**: SQL, GraphQL, Terraform
- **Advantages**: Perfect domain fit, optimal syntax
- **Disadvantages**: High implementation cost, tooling burden

#### 5. **Preprocessing**
Transform domain syntax to general-purpose code.
- **Example**: JSX → JavaScript, SASS → CSS
- **Advantages**: Clean domain syntax, compile-time processing
- **Disadvantages**: Debugging complexity, multi-stage compilation

#### 6. **Embedding**
Host language with fluent API mimicking DSL.
- **Example**: jQuery, Mockito, Builder patterns
- **Advantages**: No parser needed, IDE support
- **Disadvantages**: Syntax constraints, verbosity

#### 7. **Metaprogramming**
Use language's metaprogramming facilities to create DSL.
- **Example**: Lisp macros, Ruby metaprogramming
- **Advantages**: Powerful transformations, compile-time evaluation
- **Disadvantages**: Complexity, debugging difficulty

#### 8. **Lexical Processing**
Simple text transformation without full parsing.
- **Example**: Template engines, simple configuration formats
- **Advantages**: Simplicity, low overhead
- **Disadvantages**: Limited sophistication, fragile

---

## Formal Grammar Specifications

### Context-Free Grammars (CFG)

A context-free grammar G is a 4-tuple: **G = (V, Σ, R, S)** where:

- **V**: Finite set of non-terminal symbols
- **Σ**: Finite set of terminal symbols (vocabulary)
- **R**: Finite set of production rules (V → (V ∪ Σ)*)
- **S**: Start symbol (S ∈ V)

#### Example: Simple Expression Grammar

```
G = ({E, T, F}, {+, *, (, ), number}, R, E)

Where R consists of:
  E → E + T | T
  T → T * F | F
  F → ( E ) | number
```

### Backus-Naur Form (BNF)

BNF is a notation technique for context-free grammars, widely used for describing programming language syntax.

#### BNF Notation Elements

```
<symbol>    ::= definition
|               alternative
<symbol>        non-terminal
"text"          terminal (literal)
[ optional ]    optional element
{ repeated }    zero or more repetitions
```

#### Example: Agent Workflow Grammar (BNF)

```bnf
<workflow>      ::= <header> <steps> <metadata>

<header>        ::= "name:" <identifier>
                    "description:" <string>
                    "version:" <version>

<steps>         ::= "steps:" <step-list>

<step-list>     ::= <step> | <step> <step-list>

<step>          ::= <step-id>
                    <description>
                    <agent>
                    [<dependencies>]
                    [<inputs>]
                    [<outputs>]
                    [<estimates>]

<step-id>       ::= "- id:" <identifier>

<description>   ::= "description:" <string>

<agent>         ::= "suggested_agent:" <agent-name>

<dependencies>  ::= "depends_on:" "[" <id-list> "]"

<inputs>        ::= "inputs:" "[" <id-list> "]"

<outputs>       ::= "outputs:" "[" <id-list> "]"

<estimates>     ::= <token-estimate> <time-estimate>

<metadata>      ::= "metadata:"
                    <step-count>
                    <token-total>
                    <time-total>
                    <tags>

<execution>     ::= "execution:"
                    "strategy:" <strategy-type>
                    ["parallel_groups:" <group-list>]
```

### Extended Backus-Naur Form (EBNF)

EBNF extends BNF with additional operators for more concise grammars.

#### EBNF Operators

```
=       definition
|       alternation
( )     grouping
[ ]     option (0 or 1 time)
{ }     repetition (0 to n times)
-       exception
```

#### Example: Workflow DSL in EBNF

```ebnf
Workflow     = Header, StepList, Metadata, [Execution] ;

Header       = "name:", Identifier,
               "description:", String,
               "version:", Version ;

StepList     = "steps:", { Step } ;

Step         = "-", "id:", Identifier,
               "description:", String,
               "suggested_agent:", AgentName,
               ["depends_on:", "[", IdentifierList, "]"],
               ["inputs:", "[", IdentifierList, "]"],
               ["outputs:", "[", IdentifierList, "]"],
               "estimated_tokens:", Integer,
               ["estimated_time_minutes:", Integer] ;

Metadata     = "metadata:",
               "total_steps:", Integer,
               "total_estimated_tokens:", Integer,
               ["total_estimated_time_minutes:", Integer],
               ["tags:", "[", StringList, "]"] ;

Execution    = "execution:",
               "strategy:", Strategy,
               ["optimization:", Optimization],
               ["parallel_groups:", GroupList] ;

Strategy     = "sequential" | "parallel" | "parallel_where_possible" ;

Optimization = "speed" | "quality" | "balanced" ;
```

### Grammar Ambiguity

A grammar is **ambiguous** if there exists a string that has two or more distinct parse trees.

#### Example: Ambiguous Expression Grammar

```bnf
E ::= E + E | E * E | number
```

String "2 + 3 * 4" has two parse trees:
```
   +                *
  / \              / \
 2   *            +   4
    / \          / \
   3   4        2   3
```

#### Disambiguation Strategies

1. **Precedence Rules**: Define operator precedence (* before +)
2. **Associativity**: Define left/right associativity
3. **Grammar Refactoring**: Restructure grammar to encode precedence

#### Unambiguous Expression Grammar

```bnf
E → E + T | T          (addition, left-associative)
T → T * F | F          (multiplication, left-associative)
F → ( E ) | number     (primary expressions)
```

---

## Abstract Syntax Trees and Semantic Analysis

### Abstract Syntax Tree (AST)

An Abstract Syntax Tree is a tree representation of the abstract syntactic structure of source code. It abstracts away syntactic details (like parentheses, semicolons) while preserving semantic structure.

#### AST vs Parse Tree

**Parse Tree (Concrete Syntax Tree)**:
- Includes all grammatical details
- One-to-one mapping with derivation
- Contains terminals and non-terminals

**Abstract Syntax Tree**:
- Omits syntactic noise
- Focuses on semantic structure
- Only meaningful constructs

#### Example: Expression "2 + 3 * 4"

**Parse Tree**:
```
       E
       |
    E  +  T
    |     |
    T   T * F
    |   |   |
    F   F   4
    |   |
    2   3
```

**AST**:
```
     +
    / \
   2   *
      / \
     3   4
```

### AST Processing Pipeline

```
Source Code
    ↓
[Lexical Analysis] → Tokens
    ↓
[Parsing] → Parse Tree
    ↓
[AST Construction] → AST
    ↓
[Semantic Analysis] → Annotated AST
    ↓
[Type Checking] → Type-Safe AST
    ↓
[Optimization] → Optimized AST
    ↓
[Code Generation] → Target Code
```

### AST for Agent Workflow

#### Workflow YAML:
```yaml
name: api-development
steps:
  - id: design
    suggested_agent: api-architect
    depends_on: []
  - id: implement
    suggested_agent: code-craftsman
    depends_on: [design]
```

#### Corresponding AST:
```python
Workflow(
    name="api-development",
    steps=[
        Step(
            id="design",
            agent=AgentRef("api-architect"),
            depends_on=[]
        ),
        Step(
            id="implement",
            agent=AgentRef("code-craftsman"),
            depends_on=[StepRef("design")]
        )
    ]
)
```

### Semantic Analysis

Semantic analysis validates the meaning of syntactically correct programs.

#### Semantic Checks for Workflow DSL

1. **Name Resolution**
   - All agent references resolve to actual agents
   - All dependency references resolve to actual steps

2. **Type Checking**
   - Step IDs are unique identifiers
   - Token estimates are positive integers
   - Dependencies form valid DAG

3. **Dependency Validation**
   - No circular dependencies
   - All dependencies reference existing steps
   - Dependencies maintain topological order

4. **Data Flow Analysis**
   - Step outputs match consumer inputs
   - All required inputs are provided
   - No undefined variables

#### Example Semantic Errors

```yaml
# ERROR: Circular dependency
steps:
  - id: step-a
    depends_on: [step-b]
  - id: step-b
    depends_on: [step-a]

# ERROR: Undefined agent reference
steps:
  - id: step-1
    suggested_agent: nonexistent-agent

# ERROR: Undefined dependency
steps:
  - id: step-1
    depends_on: [missing-step]
```

### Type Systems

A **type system** is a tractable syntactic method for proving the absence of certain program behaviors by classifying phrases according to the kinds of values they compute.

#### Simple Type System for Workflows

```
Types:
  WorkflowType = Workflow
  StepType = Step
  AgentType = Agent
  IdType = Identifier
  TokenType = Integer
  DependencyType = List[IdType]

Type Rules:
  workflow: WorkflowType
  workflow.name: IdType
  workflow.steps: List[StepType]

  step: StepType
  step.id: IdType
  step.agent: AgentType
  step.depends_on: DependencyType
  step.estimated_tokens: TokenType
```

#### Type Inference

Type inference automatically deduces types without explicit annotations.

```yaml
# Explicit types (verbose)
name: string = "api-development"
estimated_tokens: int = 16000

# Inferred types (concise)
name: "api-development"  # inferred: string
estimated_tokens: 16000   # inferred: int
```

---

## Lambda Calculus and Functional Composition

### Lambda Calculus Foundations

Lambda calculus (λ-calculus) is a formal system for expressing computation based on function abstraction and application.

#### Syntax

```
<term> ::= <variable>              (variable)
         | λ<variable>.<term>      (abstraction)
         | <term> <term>           (application)
```

#### Example Terms

```
Identity:     λx.x
Constant:     λx.λy.x
Application:  (λx.x) y  →  y
Composition:  λf.λg.λx.f (g x)
```

### Church Encodings

Lambda calculus can encode data structures and control flow.

#### Booleans

```
TRUE  = λx.λy.x
FALSE = λx.λy.y
IF    = λp.λt.λf.p t f
AND   = λp.λq.p q FALSE
OR    = λp.λq.p TRUE q
NOT   = λp.p FALSE TRUE
```

#### Numbers (Church Numerals)

```
0 = λf.λx.x
1 = λf.λx.f x
2 = λf.λx.f (f x)
3 = λf.λx.f (f (f x))

SUCC = λn.λf.λx.f (n f x)
ADD  = λm.λn.λf.λx.m f (n f x)
MULT = λm.λn.λf.m (n f)
```

### Functional Composition

Function composition is the application of one function to the result of another.

#### Mathematical Definition

```
(f ∘ g)(x) = f(g(x))
```

#### Composition Operator

```haskell
-- Haskell
(.) :: (b -> c) -> (a -> b) -> (a -> c)
(f . g) x = f (g x)

-- Example
addOne :: Int -> Int
addOne x = x + 1

double :: Int -> Int
double x = x * 2

addOneThenDouble :: Int -> Int
addOneThenDouble = double . addOne

-- addOneThenDouble 3 == 8
```

### Combinators

Combinators are functions with no free variables - they combine their arguments in various ways.

#### SKI Combinator Calculus

```
S = λx.λy.λz.x z (y z)    (substitution)
K = λx.λy.x               (constant)
I = λx.x                  (identity)
```

Any lambda expression can be converted to SKI combinators.

#### Common Combinators

```haskell
-- Identity
id :: a -> a
id x = x

-- Constant (K combinator)
const :: a -> b -> a
const x y = x

-- Apply ($ operator)
apply :: (a -> b) -> a -> b
apply f x = f x

-- Flip
flip :: (a -> b -> c) -> b -> a -> c
flip f y x = f x y

-- Compose
compose :: (b -> c) -> (a -> b) -> (a -> c)
compose f g x = f (g x)
```

### Monads

A **monad** is a design pattern for composing computations with side effects.

#### Monad Laws

```haskell
-- Left Identity
return a >>= f  ≡  f a

-- Right Identity
m >>= return  ≡  m

-- Associativity
(m >>= f) >>= g  ≡  m >>= (\x -> f x >>= g)
```

#### Common Monads

**Maybe Monad** (optional values):
```haskell
data Maybe a = Nothing | Just a

instance Monad Maybe where
    return x = Just x
    Nothing >>= f = Nothing
    (Just x) >>= f = f x
```

**List Monad** (non-determinism):
```haskell
instance Monad [] where
    return x = [x]
    xs >>= f = concat (map f xs)
```

**IO Monad** (effects):
```haskell
getLine >>= \line ->
putStrLn ("You said: " ++ line)
```

### Applicative Functors

Applicative functors allow function application lifted to computational contexts.

```haskell
class Functor f => Applicative f where
    pure :: a -> f a
    (<*>) :: f (a -> b) -> f a -> f b

-- Example
Just (+1) <*> Just 2  -- Result: Just 3
```

### Combinator Libraries for DSLs

Combinator libraries enable building complex behaviors from simple, composable functions.

#### Parser Combinators

```haskell
-- Parser type
newtype Parser a = Parser (String -> [(a, String)])

-- Basic combinators
item :: Parser Char
item = Parser (\s -> case s of
    []     -> []
    (x:xs) -> [(x, xs)])

-- Choice
(<|>) :: Parser a -> Parser a -> Parser a
p <|> q = Parser (\s -> case parse p s of
    []  -> parse q s
    res -> res)

-- Sequencing
(>>=) :: Parser a -> (a -> Parser b) -> Parser b
p >>= f = Parser (\s -> concat [parse (f a) s'
                                | (a, s') <- parse p s])

-- Example: Parse digit
digit :: Parser Char
digit = sat isDigit
  where sat p = item >>= \x -> if p x then return x else empty
```

### Application to Agent Orchestration

#### Sequential Composition

```haskell
-- Sequential workflow execution
(>>=) :: Workflow a -> (a -> Workflow b) -> Workflow b

research >>= \results ->
design results >>= \spec ->
implement spec >>= \code ->
test code >>= \report ->
return report
```

#### Parallel Composition

```haskell
-- Applicative parallel execution
(<*>) :: Workflow (a -> b) -> Workflow a -> Workflow b

liftA2 :: (a -> b -> c) -> Workflow a -> Workflow b -> Workflow c

-- Execute in parallel, combine results
results = liftA2 merge scanFrontend scanBackend
```

---

## Agent Orchestration Patterns

### Mathematical Models for Agent Coordination

Agent orchestration can be modeled as a **Directed Acyclic Graph (DAG)** where:
- **Vertices (V)** represent agent tasks
- **Edges (E)** represent dependencies between tasks
- **No cycles** ensure deterministic execution order

#### Formal Definition

```
Workflow W = (A, D, I, O, M)

Where:
  A = {a₁, a₂, ..., aₙ}    (set of agent tasks)
  D ⊆ A × A                 (dependency relation)
  I: A → 2^V               (input mapping)
  O: A → 2^V               (output mapping)
  M: A → Metadata          (task metadata)

Constraints:
  (D, A) forms a DAG (acyclic)
  ∀(aᵢ, aⱼ) ∈ D: O(aᵢ) ∩ I(aⱼ) ≠ ∅  (data flow)
```

### Execution Models

#### 1. Sequential Execution

Tasks execute in strict linear order with no parallelism.

**Model**:
```
Execution: a₁ → a₂ → a₃ → ... → aₙ

Time complexity: T = Σ t(aᵢ)
Token complexity: K = Σ k(aᵢ)
```

**Example**:
```yaml
steps:
  - id: step-1
  - id: step-2
    depends_on: [step-1]
  - id: step-3
    depends_on: [step-2]
```

**Execution Timeline**:
```
Time:  0────────5────────12───────18
Tasks: [step-1]→[step-2]→[step-3]
```

#### 2. Parallel Execution

Independent tasks execute concurrently.

**Model**:
```
Execution: {a₁, a₂, a₃} ∥ {a₄, a₅} ∥ a₆

Time complexity: T = max(Tᵢ) for each parallel group
Space complexity: S = max(Sᵢ) for concurrent tasks
```

**Example**:
```yaml
steps:
  - id: scan-frontend
    can_parallelize: true
  - id: scan-backend
    can_parallelize: true
  - id: scan-database
    can_parallelize: true
```

**Execution Timeline**:
```
Time:  0──────────────5
       [scan-frontend]
       [scan-backend ]
       [scan-database]
Tasks execute simultaneously
```

#### 3. Hybrid (DAG-based) Execution

Combination of sequential and parallel execution based on dependencies.

**Model**:
```
Topological levels L₀, L₁, ..., Lₖ where:
  L₀ = {a ∈ A | in-degree(a) = 0}
  Lᵢ₊₁ = {a ∈ A | all dependencies ∈ L₀∪...∪Lᵢ}

Execute levels sequentially, tasks within level in parallel.

Time complexity: T = Σ max(t(a) for a ∈ Lᵢ)
```

**Example**:
```yaml
execution:
  strategy: parallel_where_possible
  parallel_groups:
    - [scan-frontend, scan-backend]  # Level 0 (parallel)
    - [analyze-results]              # Level 1 (sequential)
    - [generate-report]              # Level 2 (sequential)
```

**Execution Timeline**:
```
Time:  0────5────────10─────────15
Level: L₀   | L₁      | L₂
       [scan-frontend]
       [scan-backend ] [analyze] [report]
```

### Dependency Graph Algorithms

#### Topological Sort (Kahn's Algorithm)

**Purpose**: Order tasks such that dependencies execute before dependents.

**Algorithm**:
```python
def topological_sort(graph):
    # Calculate in-degrees
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] += 1

    # Queue nodes with no dependencies
    queue = [node for node in graph if in_degree[node] == 0]
    result = []

    while queue:
        # Process node with no remaining dependencies
        node = queue.pop(0)
        result.append(node)

        # Reduce in-degree of neighbors
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Check for cycles
    if len(result) != len(graph):
        raise Exception("Cycle detected in dependency graph")

    return result
```

**Complexity**: O(V + E) where V = vertices, E = edges

**Application to Workflows**:
```python
# Example workflow
graph = {
    'design': ['implement'],
    'implement': ['test', 'document'],
    'test': [],
    'document': []
}

# Topological sort
order = topological_sort(graph)
# Result: ['design', 'implement', 'test', 'document']
# or:     ['design', 'implement', 'document', 'test']
```

#### Parallel Level Detection

**Algorithm**:
```python
def parallel_levels(graph):
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] += 1

    levels = []
    current_level = [n for n in graph if in_degree[n] == 0]

    while current_level:
        levels.append(current_level)
        next_level = []

        for node in current_level:
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    next_level.append(neighbor)

        current_level = next_level

    return levels
```

**Example**:
```python
graph = {
    'research': ['design', 'prototype'],
    'design': ['implement'],
    'prototype': ['implement'],
    'implement': ['test'],
    'test': ['deploy']
}

levels = parallel_levels(graph)
# Result: [
#   ['research'],                    # Level 0
#   ['design', 'prototype'],         # Level 1 (parallel)
#   ['implement'],                   # Level 2
#   ['test'],                        # Level 3
#   ['deploy']                       # Level 4
# ]
```

### Resource Allocation and Scheduling

#### Token Budget Allocation

**Problem**: Distribute token budget across N tasks with estimates eᵢ and actual usage aᵢ.

**Strategy 1: Equal Distribution**
```
Budget per task: B/N
Risk: Some tasks may exceed budget
```

**Strategy 2: Proportional to Estimates**
```
Budget for task i: B × (eᵢ / Σeⱼ)
Advantage: Fair distribution based on expected usage
```

**Strategy 3: Reserve Buffer**
```
Task budget: 0.8 × B × (eᵢ / Σeⱼ)
Reserve: 0.2 × B (for overruns)
Advantage: Handles estimation errors
```

#### Scheduling Algorithms

**Earliest Deadline First (EDF)**:
```python
def schedule_edf(tasks):
    # Sort by deadline
    sorted_tasks = sorted(tasks, key=lambda t: t.deadline)
    return sorted_tasks
```

**Critical Path Method (CPM)**:
```python
def critical_path(graph, durations):
    # Forward pass: earliest start times
    es = {node: 0 for node in graph}
    for node in topological_sort(graph):
        for successor in graph[node]:
            es[successor] = max(es[successor],
                                es[node] + durations[node])

    # Backward pass: latest start times
    ls = {node: es[max(es, key=es.get)] for node in graph}
    for node in reversed(topological_sort(graph)):
        for successor in graph[node]:
            ls[node] = min(ls[node],
                           ls[successor] - durations[node])

    # Critical path: nodes where es == ls
    critical = [node for node in graph if es[node] == ls[node]]
    return critical
```

### Parallel vs Sequential Trade-offs

```
┌─────────────────────────────────────────────────────────────┐
│         Sequential vs Parallel Execution Trade-offs         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Sequential Execution:                                      │
│  ✓ Simple to implement and debug                           │
│  ✓ Predictable resource usage                              │
│  ✓ Clear causality and state management                    │
│  ✗ Longer total execution time                             │
│  ✗ Underutilizes available parallelism                     │
│                                                             │
│  Parallel Execution:                                        │
│  ✓ Reduced total execution time                            │
│  ✓ Better resource utilization                             │
│  ✓ Scalability to multiple workers                         │
│  ✗ Complexity in coordination                              │
│  ✗ Harder to debug and reason about                        │
│  ✗ Requires careful state management                       │
│                                                             │
│  Hybrid (DAG-based):                                        │
│  ✓ Balances parallelism and simplicity                     │
│  ✓ Automatic parallelism where safe                        │
│  ✓ Sequential where dependencies require                   │
│  ✓ Optimal for most real-world workflows                   │
│  ~ Moderate implementation complexity                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Real-World DSL Examples

### 1. GitHub Actions (YAML)

GitHub Actions uses YAML for CI/CD workflow definitions.

#### Example Workflow:
```yaml
name: CI Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh
```

#### Key Patterns:
- **Declarative**: What to run, not how
- **Dependency expression**: `needs` keyword
- **Reusable actions**: `uses` keyword
- **Matrix builds**: Parallel execution across configurations
- **Conditional execution**: `if` expressions

#### Grammar Structure:
```
Workflow := name + triggers + jobs
Job := runs-on + [needs] + steps
Step := action | run + [with] + [if]
```

### 2. Apache Airflow (Python DAG)

Airflow uses Python to define DAGs but with DSL-like patterns.

#### Example DAG:
```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

dag = DAG(
    'data_pipeline',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily'
)

extract = BashOperator(
    task_id='extract',
    bash_command='extract_data.sh',
    dag=dag
)

transform = BashOperator(
    task_id='transform',
    bash_command='transform_data.sh',
    dag=dag
)

load = BashOperator(
    task_id='load',
    bash_command='load_data.sh',
    dag=dag
)

# Define dependencies
extract >> transform >> load

# Or parallel
[extract_users, extract_orders] >> merge >> load
```

#### Key Patterns:
- **Operator abstraction**: BashOperator, PythonOperator
- **Dependency operators**: >> (downstream), << (upstream)
- **Programmatic DAG construction**: Python loops, conditionals
- **Task groups**: Logical grouping of related tasks

### 3. Terraform HCL

Terraform uses HashiCorp Configuration Language for infrastructure as code.

#### Example Configuration:
```hcl
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = {
    Name = "WebServer"
  }
}

resource "aws_db_instance" "database" {
  engine         = "postgres"
  instance_class = "db.t2.micro"

  depends_on = [aws_vpc.main]
}

output "instance_ip" {
  value = aws_instance.web.public_ip
}
```

#### Key Patterns:
- **Resource blocks**: Core abstraction
- **Dependency tracking**: Implicit via references, explicit via `depends_on`
- **Variables and outputs**: Parameterization
- **Modules**: Reusable configurations
- **State management**: Track real-world resources

### 4. Kubernetes Manifests (YAML)

Kubernetes uses YAML for declarative resource definitions.

#### Example Deployment:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
```

#### Key Patterns:
- **Resource types**: Deployment, Service, ConfigMap, etc.
- **Label selectors**: Loose coupling between resources
- **Desired state**: Declare what you want, K8s makes it happen
- **Controllers**: Reconciliation loops

### 5. Make/Makefile

Traditional build system DSL.

#### Example Makefile:
```makefile
.PHONY: all clean test

CC = gcc
CFLAGS = -Wall -O2

SOURCES = main.c utils.c
OBJECTS = $(SOURCES:.c=.o)
TARGET = myapp

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c $<

test: $(TARGET)
	./run_tests.sh

clean:
	rm -f $(OBJECTS) $(TARGET)
```

#### Key Patterns:
- **Targets and dependencies**: Make syntax
- **Pattern rules**: Generic build rules
- **Variables**: Configuration
- **Automatic variables**: $@, $<, $^
- **Lazy evaluation**: Only rebuild changed dependencies

### Common Patterns Across DSLs

```
┌────────────────────────────────────────────────────────────┐
│           Cross-DSL Common Patterns                        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1. Declarative Syntax                                     │
│     • State what, not how                                  │
│     • YAML, HCL, SQL-like syntax                          │
│                                                            │
│  2. Dependency Declaration                                 │
│     • Explicit: depends_on, needs                         │
│     • Implicit: variable references                        │
│     • Graph-based: >> operators                           │
│                                                            │
│  3. Resource Abstraction                                   │
│     • Named entities (jobs, tasks, resources)             │
│     • Type system (kind, type, operator)                  │
│     • Metadata (labels, tags, annotations)                │
│                                                            │
│  4. Parameterization                                       │
│     • Variables and interpolation                         │
│     • Environment-specific configs                        │
│     • Template expansion                                   │
│                                                            │
│  5. Composition                                            │
│     • Modules/includes                                     │
│     • Inheritance/extension                               │
│     • Mixins/traits                                        │
│                                                            │
│  6. Validation                                             │
│     • Schema validation (JSON Schema)                     │
│     • Type checking                                        │
│     • Linting rules                                        │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Parser and Interpreter Design

### Lexical Analysis

Lexical analysis (lexing/tokenization) converts character stream to token stream.

#### Token Types

```python
from enum import Enum

class TokenType(Enum):
    # Literals
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"

    # Keywords
    NAME = "name"
    STEPS = "steps"
    METADATA = "metadata"

    # Symbols
    COLON = ":"
    DASH = "-"
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"

    # Special
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    EOF = "EOF"
```

#### Lexer Implementation

```python
class Lexer:
    def __init__(self, source):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1

    def peek(self):
        if self.position >= len(self.source):
            return None
        return self.source[self.position]

    def advance(self):
        char = self.peek()
        self.position += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def skip_whitespace(self):
        while self.peek() in ' \t':
            self.advance()

    def read_identifier(self):
        start = self.position
        while self.peek() and (self.peek().isalnum() or self.peek() in '_-'):
            self.advance()
        return self.source[start:self.position]

    def read_string(self):
        quote = self.advance()  # " or '
        start = self.position
        while self.peek() != quote:
            if self.peek() is None:
                raise SyntaxError("Unterminated string")
            self.advance()
        value = self.source[start:self.position]
        self.advance()  # closing quote
        return value

    def next_token(self):
        self.skip_whitespace()

        if self.peek() is None:
            return Token(TokenType.EOF, None, self.line, self.column)

        if self.peek() in '"\'':
            return Token(TokenType.STRING, self.read_string(),
                        self.line, self.column)

        if self.peek().isdigit():
            return self.read_number()

        if self.peek().isalpha():
            ident = self.read_identifier()
            token_type = KEYWORDS.get(ident, TokenType.IDENTIFIER)
            return Token(token_type, ident, self.line, self.column)

        # Single-character tokens
        char_tokens = {
            ':': TokenType.COLON,
            '-': TokenType.DASH,
            '[': TokenType.LEFT_BRACKET,
            ']': TokenType.RIGHT_BRACKET,
        }

        char = self.advance()
        if char in char_tokens:
            return Token(char_tokens[char], char, self.line, self.column)

        raise SyntaxError(f"Unexpected character: {char}")
```

### Parsing Techniques

#### 1. Recursive Descent Parsing

Top-down parsing where each non-terminal becomes a function.

**Advantages**:
- Simple to implement
- Easy to debug
- Good error messages
- No external tools needed

**Example**:
```python
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def peek(self):
        if self.position >= len(self.tokens):
            return None
        return self.tokens[self.position]

    def consume(self, expected_type):
        token = self.peek()
        if token.type != expected_type:
            raise SyntaxError(
                f"Expected {expected_type}, got {token.type}")
        self.position += 1
        return token

    # Grammar: workflow = "name:" identifier "steps:" step_list
    def parse_workflow(self):
        self.consume(TokenType.NAME)
        self.consume(TokenType.COLON)
        name = self.consume(TokenType.IDENTIFIER)

        self.consume(TokenType.STEPS)
        self.consume(TokenType.COLON)
        steps = self.parse_step_list()

        return Workflow(name.value, steps)

    # Grammar: step_list = step+
    def parse_step_list(self):
        steps = []
        while self.peek() and self.peek().type == TokenType.DASH:
            steps.append(self.parse_step())
        return steps

    # Grammar: step = "-" "id:" identifier ...
    def parse_step(self):
        self.consume(TokenType.DASH)
        self.consume(TokenType.IDENTIFIER)  # "id"
        self.consume(TokenType.COLON)
        step_id = self.consume(TokenType.IDENTIFIER)

        # Parse other step fields...
        return Step(step_id.value)
```

#### 2. Parser Combinators

Functional approach using higher-order functions.

**Example (Haskell-style)**:
```haskell
-- Basic combinators
satisfy :: (Char -> Bool) -> Parser Char
satisfy predicate = Parser $ \input -> case input of
    (x:xs) | predicate x -> [(x, xs)]
    _                    -> []

char :: Char -> Parser Char
char c = satisfy (== c)

string :: String -> Parser String
string [] = return []
string (x:xs) = do
    char x
    string xs
    return (x:xs)

-- Choice combinator
(<|>) :: Parser a -> Parser a -> Parser a
p <|> q = Parser $ \input -> case parse p input of
    []  -> parse q input
    res -> res

-- Sequence combinator
(>>=) :: Parser a -> (a -> Parser b) -> Parser b
p >>= f = Parser $ \input -> concat
    [parse (f x) rest | (x, rest) <- parse p input]

-- Example: parse identifier
identifier :: Parser String
identifier = many1 (satisfy isAlpha)

-- Example: parse key-value pair
keyValue :: Parser (String, String)
keyValue = do
    key <- identifier
    char ':'
    spaces
    value <- identifier
    return (key, value)
```

**Advantages**:
- Highly composable
- Concise and expressive
- Easy to extend
- Type-safe (in typed languages)

#### 3. Parser Generators (Yacc/Bison style)

Specification-driven parser generation.

**Example (BNF input)**:
```yacc
%token NAME COLON STEPS DASH IDENTIFIER

%%

workflow: NAME COLON IDENTIFIER STEPS COLON step_list
        { $$ = make_workflow($3, $6); }
        ;

step_list: step
         { $$ = list_create($1); }
         | step_list step
         { $$ = list_append($1, $2); }
         ;

step: DASH IDENTIFIER COLON IDENTIFIER
    { $$ = make_step($4); }
    ;
```

**Advantages**:
- Handles complex grammars
- Automatic conflict resolution
- Optimized performance

**Disadvantages**:
- Requires external tools
- Less flexible error handling
- Debugging difficulty

### Execution Engines

#### Interpreter Pattern

Direct AST interpretation.

```python
class Interpreter:
    def __init__(self):
        self.context = {}

    def interpret(self, node):
        method_name = f'interpret_{node.__class__.__name__}'
        method = getattr(self, method_name, self.generic_interpret)
        return method(node)

    def interpret_Workflow(self, node):
        print(f"Executing workflow: {node.name}")
        results = []
        for step in node.steps:
            result = self.interpret(step)
            results.append(result)
        return results

    def interpret_Step(self, node):
        print(f"Executing step: {node.id}")

        # Check dependencies
        for dep_id in node.depends_on:
            if dep_id not in self.context:
                raise RuntimeError(f"Dependency {dep_id} not satisfied")

        # Execute agent
        agent = self.load_agent(node.agent)
        inputs = [self.context[inp] for inp in node.inputs]
        result = agent.execute(node.description, inputs)

        # Store outputs
        for output_name in node.outputs:
            self.context[output_name] = result

        return result

    def load_agent(self, agent_name):
        # Load agent implementation
        return Agent(agent_name)
```

#### Compilation Pattern

Translate to intermediate or target code.

```python
class Compiler:
    def compile(self, workflow):
        # Generate Python code
        code = []
        code.append("def execute_workflow():")
        code.append("    results = {}")

        for step in workflow.steps:
            code.append(f"    # Step: {step.id}")

            # Wait for dependencies
            if step.depends_on:
                deps = ", ".join(f"'{d}'" for d in step.depends_on)
                code.append(f"    wait_for([{deps}], results)")

            # Execute step
            inputs = ", ".join(f"results['{i}']" for i in step.inputs)
            code.append(
                f"    results['{step.id}'] = "
                f"execute_agent('{step.agent}', '{step.description}', [{inputs}])"
            )

        code.append("    return results")

        return "\n".join(code)
```

### Error Handling and Validation

#### Syntax Errors

Detected during parsing.

```python
class ParseError(Exception):
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        return f"Syntax error at line {self.line}, column {self.column}: {self.message}"
```

#### Semantic Errors

Detected during semantic analysis.

```python
class SemanticValidator:
    def validate(self, workflow):
        self.check_unique_step_ids(workflow)
        self.check_dependencies(workflow)
        self.check_agents_exist(workflow)
        self.check_data_flow(workflow)

    def check_unique_step_ids(self, workflow):
        ids = [step.id for step in workflow.steps]
        duplicates = [id for id in ids if ids.count(id) > 1]
        if duplicates:
            raise SemanticError(f"Duplicate step IDs: {duplicates}")

    def check_dependencies(self, workflow):
        step_ids = {step.id for step in workflow.steps}
        for step in workflow.steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    raise SemanticError(
                        f"Step '{step.id}' depends on undefined step '{dep}'")

        # Check for cycles
        if has_cycle(workflow.dependency_graph()):
            raise SemanticError("Circular dependency detected")

    def check_agents_exist(self, workflow):
        available_agents = load_available_agents()
        for step in workflow.steps:
            if step.agent not in available_agents:
                raise SemanticError(
                    f"Agent '{step.agent}' not found in step '{step.id}'")
```

#### Runtime Errors

Detected during execution.

```python
class RuntimeError(Exception):
    def __init__(self, step_id, message):
        self.step_id = step_id
        self.message = message

    def __str__(self):
        return f"Runtime error in step '{self.step_id}': {self.message}"
```

---

## Claude Code CLI Architecture Analysis

### Current Workflow System

Based on analysis of the LUXOR codebase, Claude Code implements a sophisticated multi-agent orchestration system.

#### Workflow YAML Structure

```yaml
name: api-development
description: End-to-end REST API development from design to deployment
created: 2025-10-12T15:00:00Z
version: 1.0

steps:
  - id: design-api
    description: Design REST API with OpenAPI specification
    suggested_agent: api-architect
    estimated_tokens: 16000
    estimated_time_minutes: 12
    inputs: []
    outputs:
      - openapi_spec
      - api_design_doc

  - id: implement-endpoints
    description: Implement API endpoints with proper error handling
    suggested_agent: code-craftsman
    estimated_tokens: 18000
    estimated_time_minutes: 14
    depends_on:
      - design-api
    inputs:
      - openapi_spec
    outputs:
      - source_code
      - implementation_files

metadata:
  total_steps: 4
  total_estimated_tokens: 60000
  total_estimated_time_minutes: 46
  tags:
    - api
    - backend
    - development
  author: system

execution:
  strategy: sequential
  optimization: balanced
```

#### Key Architectural Components

**1. Agent Registry**:
```
.claude/agents/
├── api-architect.md
├── code-craftsman.md
├── test-engineer.md
├── docs-generator.md
└── ... (33 total)
```

**2. Workflow Library**:
```
.claude/workflows/
├── api-development.yaml
├── frontend-feature-complete.yaml
├── claude-sdk-integration.yaml
└── ... (10+ workflows)
```

**3. Command System**:
```
/wflw --generate <name> <steps>    # Generate workflow
/wflw --list                       # List workflows
/wflw --validate <name>            # Validate workflow
/orch <workflow>                   # Execute workflow
/orch <workflow> --dry-run         # Preview execution
```

#### Execution Flow

```
User Command: /orch api-development
         ↓
[1] Parse command and load workflow YAML
         ↓
[2] Validate workflow structure
    - Check YAML syntax
    - Validate agent references
    - Check dependency graph (DAG)
    - Verify data flow
         ↓
[3] Build execution plan
    - Topological sort of steps
    - Calculate token budget
    - Identify parallel opportunities
         ↓
[4] Execute steps sequentially/parallel
    For each step:
      - Build agent context
      - Execute agent with Task tool
      - Capture outputs
      - Update workflow state
         ↓
[5] Aggregate results
    - Collect all step outputs
    - Generate execution summary
    - Calculate actual vs estimated metrics
         ↓
[6] Return results to user
```

#### Agent Invocation Pattern

```python
# Pseudo-code for agent execution
def execute_step(step, workflow_state):
    # 1. Resolve dependencies
    dependency_outputs = []
    for dep_id in step.depends_on:
        if dep_id not in workflow_state:
            raise DependencyError(f"Dependency {dep_id} not satisfied")
        dependency_outputs.append(workflow_state[dep_id])

    # 2. Build context
    context = {
        'task_description': step.description,
        'inputs': [workflow_state[inp] for inp in step.inputs],
        'dependency_outputs': dependency_outputs,
        'metadata': {
            'step_id': step.id,
            'workflow_name': workflow.name
        }
    }

    # 3. Invoke agent via Task tool
    result = invoke_task(
        subagent_type=step.suggested_agent,
        task=step.description,
        context=context
    )

    # 4. Store outputs
    for output_name in step.outputs:
        workflow_state[output_name] = result[output_name]

    return result
```

### Skill System Integration

Skills provide domain knowledge to agents automatically.

```python
# Skills are automatically invoked based on context
# No explicit loading required

# Example: Agent task invokes relevant skills
task = "Build FastAPI endpoint with PostgreSQL"

# System automatically uses:
# - fastapi skill
# - postgresql skill
# - rest-api-design-patterns skill
# - pydantic skill
```

### MCP Integration Patterns

Model Context Protocol (MCP) provides dynamic data access.

```python
# MCP servers augment agent capabilities
# Example: Linear MCP integration

def execute_with_mcp(step):
    # Agent can use MCP tools directly
    # e.g., create Linear issue during workflow

    if step.requires_linear:
        issue = mcp_linear_create_issue(
            title=f"Task: {step.description}",
            team="engineering"
        )

        # Store issue reference in workflow state
        return {'linear_issue': issue.id}
```

### Token Budget Management

```python
class TokenBudgetManager:
    def __init__(self, total_budget):
        self.total_budget = total_budget
        self.used = 0
        self.reserved = {}

    def reserve(self, step_id, estimated_tokens):
        # Reserve tokens for step
        if self.used + estimated_tokens > self.total_budget:
            raise BudgetExceededError()
        self.reserved[step_id] = estimated_tokens
        self.used += estimated_tokens

    def release(self, step_id, actual_tokens):
        # Release reserved, charge actual
        reserved = self.reserved.pop(step_id)
        self.used = self.used - reserved + actual_tokens

    def available(self):
        return self.total_budget - self.used
```

---

## Mathematical Foundations

### Graph Theory Formalization

#### Directed Acyclic Graph (DAG) Properties

**Definition**: A DAG G = (V, E) is a directed graph with no directed cycles.

**Properties**:
1. **Topological Ordering**: Vertices can be ordered such that for every edge (u, v), u comes before v
2. **Transitive Reduction**: Minimum set of edges preserving reachability
3. **Longest Path**: Can be computed in O(V + E) time
4. **Critical Path**: Longest path from source to sink

**Workflow Mapping**:
```
Workflow W = (A, D) where:
  A = {a₁, a₂, ..., aₙ}     (agent tasks)
  D ⊆ A × A                  (dependencies)

  (A, D) forms a DAG
```

#### Graph Algorithms Complexity

| Algorithm | Complexity | Use Case |
|-----------|-----------|----------|
| Topological Sort (Kahn) | O(V + E) | Dependency ordering |
| Topological Sort (DFS) | O(V + E) | Alternative ordering |
| Cycle Detection | O(V + E) | Validation |
| Longest Path | O(V + E) | Critical path analysis |
| Transitive Closure | O(V³) | Reachability analysis |

### Formal Language Theory

#### Chomsky Hierarchy

```
Type 0: Recursively Enumerable (Turing Machine)
   ↑
Type 1: Context-Sensitive
   ↑
Type 2: Context-Free (Pushdown Automaton)
   ↑
Type 3: Regular (Finite Automaton)
```

**Workflow DSL Classification**: Type 2 (Context-Free)

#### Automata Theory

**Finite State Machine for Workflow Execution**:

```
States: {PENDING, RUNNING, COMPLETED, FAILED}

Transitions:
  PENDING → RUNNING      (when dependencies satisfied)
  RUNNING → COMPLETED    (on successful execution)
  RUNNING → FAILED       (on error)
  FAILED → RUNNING       (on retry)
```

**State Machine Definition**:
```
M = (Q, Σ, δ, q₀, F)

Where:
  Q = {PENDING, RUNNING, COMPLETED, FAILED}
  Σ = {start, success, error, retry}
  δ: Q × Σ → Q (transition function)
  q₀ = PENDING (initial state)
  F = {COMPLETED} (accepting states)
```

### Category Theory Foundations

#### Functors

A functor F maps between categories, preserving structure.

```haskell
class Functor f where
    fmap :: (a -> b) -> f a -> f b

-- Laws:
-- fmap id = id
-- fmap (g . h) = fmap g . fmap h
```

**Application to Workflows**:
```haskell
-- Workflow is a functor
instance Functor Workflow where
    fmap f workflow = workflow {
        steps = map (fmap f) (steps workflow)
    }

-- Transform all step outputs
transformOutputs :: (Output -> Output) -> Workflow -> Workflow
transformOutputs = fmap
```

#### Monads for Sequential Composition

```haskell
class Monad m where
    return :: a -> m a
    (>>=) :: m a -> (a -> m b) -> m b

-- Workflow as monad
instance Monad Workflow where
    return x = Workflow [Step "return" x]

    workflow >>= f = Workflow $
        concat [steps (f output) | Step _ output <- steps workflow]
```

#### Applicative for Parallel Composition

```haskell
class Applicative f where
    pure :: a -> f a
    (<*>) :: f (a -> b) -> f a -> f b

-- Parallel workflow execution
instance Applicative Workflow where
    pure x = Workflow [Step "pure" x]

    wf <*> wx = Workflow $
        [Step "apply" (f x) |
         Step _ f <- steps wf,
         Step _ x <- steps wx]
```

### Operational Semantics

Small-step operational semantics for workflow execution.

#### Execution Rules

```
Notation: ⟨step, σ⟩ → ⟨step', σ'⟩
  where σ is workflow state

Rule 1 (Dependency Check):
  step.depends_on ⊆ dom(σ)
  ────────────────────────────────
  ⟨PENDING(step), σ⟩ → ⟨RUNNING(step), σ⟩

Rule 2 (Execution):
  result = execute(step.agent, step.description, inputs)
  ────────────────────────────────────────────────────────
  ⟨RUNNING(step), σ⟩ → ⟨COMPLETED(step), σ ∪ {step.id → result}⟩

Rule 3 (Error):
  execute(step.agent, step.description, inputs) throws error
  ──────────────────────────────────────────────────────────
  ⟨RUNNING(step), σ⟩ → ⟨FAILED(step), σ⟩

Rule 4 (Skip):
  step.depends_on ⊈ dom(σ)
  ────────────────────────────────
  ⟨PENDING(step), σ⟩ → ⟨PENDING(step), σ⟩
```

---

## Implementation Patterns

### Pattern 1: External DSL with Parser

**When to Use**: Custom syntax, complex grammar, strong tooling requirements

**Implementation**:
```python
# 1. Define grammar (EBNF)
grammar = """
    workflow = header steps metadata
    header = "workflow" identifier "{"
    steps = "steps" "{" step+ "}"
    step = identifier "->" agent
"""

# 2. Generate or write parser
class WorkflowParser:
    def parse(self, source):
        tokens = self.lexer.tokenize(source)
        ast = self.parse_tokens(tokens)
        return ast

# 3. Semantic analysis
validator = SemanticValidator()
validator.validate(ast)

# 4. Execution
interpreter = WorkflowInterpreter()
result = interpreter.execute(ast)
```

**Pros**:
- Perfect syntax for domain
- Strong validation
- IDE support possible

**Cons**:
- High implementation cost
- Tooling burden
- Learning curve

### Pattern 2: YAML + JSON Schema

**When to Use**: Declarative configuration, existing YAML tooling, rapid development

**Implementation**:
```python
import yaml
import jsonschema

# 1. Define schema
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "agent": {"type": "string"},
                    "depends_on": {"type": "array"}
                },
                "required": ["id", "agent"]
            }
        }
    },
    "required": ["name", "steps"]
}

# 2. Parse and validate
with open("workflow.yaml") as f:
    data = yaml.safe_load(f)

jsonschema.validate(data, schema)

# 3. Convert to AST
workflow = Workflow.from_dict(data)

# 4. Execute
executor = WorkflowExecutor()
result = executor.run(workflow)
```

**Pros**:
- Familiar syntax
- Rich ecosystem
- Easy to learn
- IDE support

**Cons**:
- Less expressive than custom syntax
- YAML quirks (Norway problem)
- Limited type safety

### Pattern 3: Internal DSL (Fluent API)

**When to Use**: Embedding in host language, leverage existing tools, dynamic construction

**Implementation**:
```python
class WorkflowBuilder:
    def __init__(self, name):
        self.name = name
        self.steps = []

    def step(self, step_id, agent):
        self.steps.append(Step(step_id, agent))
        return self

    def depends_on(self, *deps):
        self.steps[-1].depends_on = list(deps)
        return self

    def build(self):
        return Workflow(self.name, self.steps)

# Usage
workflow = (WorkflowBuilder("api-development")
    .step("design", "api-architect")
    .step("implement", "code-craftsman")
    .depends_on("design")
    .step("test", "test-engineer")
    .depends_on("implement")
    .build())
```

**Pros**:
- No parser needed
- Full language power
- IDE autocomplete
- Type safety (in typed languages)

**Cons**:
- Verbose syntax
- Host language constraints
- Less declarative

### Pattern 4: Hybrid (YAML + Python)

**When to Use**: Declarative base with programmatic extensions

**Implementation**:
```python
# workflow.yaml (declarative)
name: dynamic-workflow
steps:
  - id: setup
    agent: code-craftsman
    script: setup.py

# setup.py (programmatic)
def generate_steps(workflow):
    services = ["users", "orders", "payments"]

    for service in services:
        workflow.add_step(
            id=f"test-{service}",
            agent="test-engineer",
            depends_on=["setup"]
        )

# Executor
workflow = load_yaml("workflow.yaml")
workflow.execute_scripts()  # Runs setup.py
executor.run(workflow)
```

**Pros**:
- Best of both worlds
- Flexibility where needed
- Simple for simple cases

**Cons**:
- Complexity in interaction
- Security concerns (code execution)

### Pattern 5: Parser Combinators

**When to Use**: Functional programming style, composable parsing, Haskell/Scala projects

**Implementation**:
```haskell
import Text.Parsec

-- Basic parsers
identifier :: Parser String
identifier = many1 letter

step :: Parser Step
step = do
    string "step"
    spaces
    stepId <- identifier
    spaces
    string "uses"
    spaces
    agent <- identifier
    return $ Step stepId agent

workflow :: Parser Workflow
workflow = do
    string "workflow"
    spaces
    name <- identifier
    spaces
    steps <- many1 step
    return $ Workflow name steps

-- Parse
parseWorkflow :: String -> Either ParseError Workflow
parseWorkflow = parse workflow ""
```

**Pros**:
- Highly composable
- Type-safe
- Concise
- Easy to extend

**Cons**:
- Requires functional language
- Learning curve
- Performance considerations

---

## DSL Design for Agent Orchestration

### Design Principles

#### 1. Declarative over Imperative

**Declarative** (What):
```yaml
steps:
  - id: test-api
    agent: test-engineer
    depends_on: [implement-api]
```

**Imperative** (How):
```python
if implement_api.complete:
    test_api = execute_agent("test-engineer")
```

**Rationale**: Declarative DSLs are easier to reason about, optimize, and parallelize.

#### 2. Domain-Centric Vocabulary

Use terminology from agent orchestration domain:
- `workflow`, `step`, `agent` (not `program`, `function`, `module`)
- `depends_on`, `outputs` (not `requires`, `returns`)
- `estimated_tokens` (domain-specific metric)

#### 3. Progressive Disclosure

Simple cases should be simple, complex cases should be possible.

**Simple**:
```yaml
name: quick-test
steps:
  - id: test
    agent: test-engineer
```

**Complex**:
```yaml
name: full-pipeline
steps:
  - id: research
    agent: deep-researcher
    estimated_tokens: 25000
    inputs: [requirements]
    outputs: [research_doc]

execution:
  strategy: parallel_where_possible
  parallel_groups:
    - [scan-frontend, scan-backend]
```

#### 4. Fail Fast with Clear Errors

```yaml
# Error: Circular dependency
steps:
  - id: a
    depends_on: [b]
  - id: b
    depends_on: [a]

# Error message:
# ❌ Circular dependency detected: a → b → a
#    Step 'a' at line 2
#    Step 'b' at line 4
```

#### 5. Composition and Reuse

```yaml
# Base workflow
name: api-base
steps:
  - id: design
    agent: api-architect

---
# Extended workflow
name: api-complete
extends: api-base
steps:
  - id: implement
    agent: code-craftsman
    depends_on: [design]
```

### Recommended DSL Design for Claude Code

Based on research and analysis of existing systems:

#### Surface Syntax: YAML

**Rationale**:
- Familiar to developers
- Rich tooling ecosystem
- Human-readable and writable
- JSON Schema validation
- Used by GitHub Actions, K8s, Airflow

#### Core Grammar (EBNF)

```ebnf
Workflow     = Metadata, StepList, [ExecutionConfig] ;

Metadata     = Name, Description, [Version], [Created], [Author] ;

Name         = "name:", String ;
Description  = "description:", String ;
Version      = "version:", SemanticVersion ;

StepList     = "steps:", { Step } ;

Step         = StepId, StepDesc, Agent, [Dependencies],
               [Inputs], [Outputs], [Estimates], [Conditions] ;

StepId       = "-", "id:", Identifier ;
StepDesc     = "description:", String ;
Agent        = "suggested_agent:", AgentName ;

Dependencies = "depends_on:", "[", IdentifierList, "]" ;
Inputs       = "inputs:", "[", IdentifierList, "]" ;
Outputs      = "outputs:", "[", IdentifierList, "]" ;

Estimates    = TokenEstimate, [TimeEstimate] ;
TokenEstimate = "estimated_tokens:", Integer ;
TimeEstimate  = "estimated_time_minutes:", Integer ;

Conditions   = "condition:", Expression ;

ExecutionConfig = "execution:",
                  Strategy, [Optimization],
                  [ParallelGroups], [ErrorHandling] ;

Strategy     = "strategy:", ("sequential" | "parallel" |
                            "parallel_where_possible") ;
```

#### Example Workflow (Proposed)

```yaml
name: fullstack-feature
description: Complete full-stack feature implementation
version: 1.0
created: 2025-10-19T10:00:00Z
author: engineering-team

# Workflow-level configuration
config:
  max_retries: 2
  timeout_minutes: 120
  token_budget: 100000

# Sequential steps with dependencies
steps:
  # Research phase
  - id: research-patterns
    description: Research authentication patterns and best practices
    suggested_agent: deep-researcher
    estimated_tokens: 20000
    estimated_time_minutes: 15
    outputs:
      - research_doc
      - best_practices
    tags: [research, authentication]

  # Parallel design phase
  - id: design-api
    description: Design REST API with OpenAPI specification
    suggested_agent: api-architect
    estimated_tokens: 16000
    estimated_time_minutes: 12
    depends_on: [research-patterns]
    inputs: [research_doc, best_practices]
    outputs:
      - openapi_spec
      - api_design_doc
    can_parallelize: true

  - id: design-ui
    description: Design React component architecture
    suggested_agent: frontend-architect
    estimated_tokens: 14000
    estimated_time_minutes: 10
    depends_on: [research-patterns]
    inputs: [research_doc]
    outputs:
      - component_design
      - ui_mockups
    can_parallelize: true

  # Implementation phase
  - id: implement-backend
    description: Implement API endpoints with authentication
    suggested_agent: code-craftsman
    estimated_tokens: 22000
    estimated_time_minutes: 18
    depends_on: [design-api]
    inputs: [openapi_spec, api_design_doc]
    outputs:
      - backend_code
      - api_implementation

  - id: implement-frontend
    description: Implement React components
    suggested_agent: code-craftsman
    estimated_tokens: 20000
    estimated_time_minutes: 16
    depends_on: [design-ui, design-api]
    inputs: [component_design, openapi_spec]
    outputs:
      - frontend_code
      - components

  # Testing phase (parallel)
  - id: test-backend
    description: Create backend integration tests
    suggested_agent: test-engineer
    estimated_tokens: 12000
    estimated_time_minutes: 10
    depends_on: [implement-backend]
    inputs: [backend_code, openapi_spec]
    outputs:
      - backend_tests
    can_parallelize: true

  - id: test-frontend
    description: Create React component tests
    suggested_agent: test-engineer
    estimated_tokens: 12000
    estimated_time_minutes: 10
    depends_on: [implement-frontend]
    inputs: [frontend_code]
    outputs:
      - frontend_tests
    can_parallelize: true

  # Integration
  - id: e2e-tests
    description: Create end-to-end integration tests
    suggested_agent: test-engineer
    estimated_tokens: 16000
    estimated_time_minutes: 14
    depends_on: [implement-backend, implement-frontend]
    inputs: [backend_code, frontend_code, openapi_spec]
    outputs:
      - e2e_test_suite

  # Documentation
  - id: generate-docs
    description: Generate comprehensive documentation
    suggested_agent: docs-generator
    estimated_tokens: 14000
    estimated_time_minutes: 11
    depends_on:
      - implement-backend
      - implement-frontend
      - e2e-tests
    inputs:
      - openapi_spec
      - backend_code
      - frontend_code
      - e2e_test_suite
    outputs:
      - documentation

# Execution metadata
metadata:
  total_steps: 9
  total_estimated_tokens: 146000
  total_estimated_time_minutes: 116
  tags:
    - fullstack
    - authentication
    - api
    - react
  complexity: high

# Execution configuration
execution:
  strategy: parallel_where_possible
  optimization: balanced

  # Define parallel execution groups
  parallel_groups:
    - [research-patterns]                    # Level 0
    - [design-api, design-ui]               # Level 1 (parallel)
    - [implement-backend, implement-frontend] # Level 2 (sequential after design)
    - [test-backend, test-frontend]         # Level 3 (parallel)
    - [e2e-tests]                           # Level 4 (sequential)
    - [generate-docs]                       # Level 5 (sequential)

  # Error handling
  on_failure:
    strategy: stop  # stop, continue, retry
    notify: true

  # Resource limits
  limits:
    max_parallel_tasks: 3
    token_budget_per_step: 25000
    timeout_per_step_minutes: 30
```

### Advanced Features

#### Conditional Execution

```yaml
steps:
  - id: check-coverage
    agent: coverage-analyzer
    outputs: [coverage_percent]

  - id: improve-coverage
    agent: test-engineer
    condition: coverage_percent < 80
    depends_on: [check-coverage]
```

#### Loops and Iteration

```yaml
steps:
  - id: scan-services
    agent: code-analyzer
    for_each:
      service: [users, orders, payments, inventory]
    description: "Scan ${service} service for vulnerabilities"
    outputs: [scan_results_${service}]
```

#### Workflow Composition

```yaml
workflows:
  - import: base-api-workflow.yaml
    as: api

  - import: frontend-workflow.yaml
    as: frontend

steps:
  - id: integrate
    depends_on: [api.deploy, frontend.deploy]
```

#### Dynamic Steps

```yaml
steps:
  - id: discover-services
    agent: code-analyzer
    outputs: [service_list]

  - id: test-services
    agent: test-engineer
    dynamic: true
    generate_from: service_list
    template:
      id: test-${service}
      description: Test ${service} service
```

---

## Bibliography and References

### Academic Papers

1. **Spinellis, D. (2000)**. "Notable Design Patterns for Domain-Specific Languages." Journal of Systems and Software, 56(1), 91-99.
   - Eight recurring DSL design patterns
   - Comparison of implementation approaches

2. **Fowler, M. (2010)**. Domain-Specific Languages. Addison-Wesley.
   - Comprehensive DSL catalog
   - Internal vs external DSL patterns
   - Real-world examples

3. **Mernik, M., Heering, J., & Sloane, A. M. (2005)**. "When and how to develop domain-specific languages." ACM Computing Surveys, 37(4), 316-344.
   - Decision framework for DSL development
   - Analysis, design, implementation phases

### Technical Documentation

4. **GitHub Actions Documentation**
   - https://docs.github.com/en/actions
   - YAML workflow syntax reference

5. **Apache Airflow Documentation**
   - https://airflow.apache.org/docs/
   - DAG construction patterns

6. **Terraform HCL Documentation**
   - https://www.terraform.io/docs/language/
   - HashiCorp Configuration Language specification

7. **Kubernetes API Reference**
   - https://kubernetes.io/docs/reference/
   - YAML manifest specifications

### Parser Theory

8. **Aho, A. V., Sethi, R., & Ullman, J. D. (2006)**. Compilers: Principles, Techniques, and Tools (2nd ed.). Addison-Wesley.
   - Parsing techniques
   - Lexical analysis
   - Semantic analysis

9. **Parr, T. (2013)**. The Definitive ANTLR 4 Reference. Pragmatic Bookshelf.
   - Parser generator tools
   - Grammar design

### Functional Programming

10. **Lipovača, M. (2011)**. Learn You a Haskell for Great Good!
    - Functors, Applicatives, Monads
    - Parser combinators

11. **Chiusano, P., & Bjarnason, R. (2014)**. Functional Programming in Scala. Manning.
    - Combinator libraries
    - Type-driven design

### Graph Theory

12. **Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009)**. Introduction to Algorithms (3rd ed.). MIT Press.
    - Topological sorting algorithms
    - DAG properties and algorithms

13. **Coffman Jr, E. G., & Graham, R. L. (1972)**. "Optimal scheduling for two-processor systems." Acta Informatica, 1(3), 200-213.
    - Task scheduling with dependencies

### Lambda Calculus

14. **Church, A. (1936)**. "An unsolvable problem of elementary number theory." American Journal of Mathematics, 58(2), 345-363.
    - Original lambda calculus paper

15. **Barendregt, H. P. (1984)**. The Lambda Calculus: Its Syntax and Semantics. North-Holland.
    - Comprehensive lambda calculus reference

### Online Resources

16. **Martin Fowler's DSL Catalog**
    - https://martinfowler.com/dslCatalog/
    - Practical DSL patterns

17. **Matt Might's Grammar Articles**
    - https://matt.might.net/articles/grammars-bnf-ebnf/
    - BNF/EBNF tutorial

18. **JSON Schema Documentation**
    - https://json-schema.org/
    - YAML validation with JSON Schema

19. **YAML Specification**
    - https://yaml.org/spec/
    - Official YAML 1.2 specification

### Claude Code Specific

20. **Claude Code Documentation**
    - https://docs.claude.com/en/docs/claude-code
    - Official Claude Code CLI documentation

21. **Agent Skills Blog Post**
    - https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
    - Model-invoked skills architecture

### Research Applications

22. **Grammar Prompting (2023)**. "Grammar Prompting for Domain-Specific Language Generation with Large Language Models." arXiv:2305.19234
    - BNF-based LLM prompting
    - DSL generation techniques

23. **Building Multi-Agent Architectures (2024)**. Medium article on orchestrating intelligent agent systems
    - Sequential vs parallel patterns
    - Agent coordination strategies

---

## Appendix A: YAML Schema for Workflow DSL

```yaml
$schema: "http://json-schema.org/draft-07/schema#"
title: "Claude Code Workflow Schema"
description: "JSON Schema for agent orchestration workflow YAML files"
type: object

required:
  - name
  - steps

properties:
  name:
    type: string
    pattern: "^[a-z][a-z0-9-]*$"
    description: "Workflow identifier (lowercase, hyphens allowed)"

  description:
    type: string
    description: "Human-readable workflow description"

  version:
    type: string
    pattern: "^\\d+\\.\\d+(\\.\\d+)?$"
    description: "Semantic version (e.g., 1.0 or 1.0.0)"

  created:
    type: string
    format: date-time
    description: "ISO 8601 creation timestamp"

  author:
    type: string
    description: "Workflow author or team"

  steps:
    type: array
    minItems: 1
    items:
      type: object
      required:
        - id
        - description
        - suggested_agent
      properties:
        id:
          type: string
          pattern: "^[a-z][a-z0-9-]*$"
          description: "Unique step identifier"

        description:
          type: string
          minLength: 10
          description: "Clear description of what this step does"

        suggested_agent:
          type: string
          enum:
            - api-architect
            - code-craftsman
            - test-engineer
            - docs-generator
            - deep-researcher
            - frontend-architect
            - debug-detective
            - deployment-orchestrator
          description: "Agent to execute this step"

        depends_on:
          type: array
          items:
            type: string
          description: "List of step IDs this step depends on"

        inputs:
          type: array
          items:
            type: string
          description: "Input data from previous steps"

        outputs:
          type: array
          items:
            type: string
          description: "Output data produced by this step"

        estimated_tokens:
          type: integer
          minimum: 1000
          maximum: 100000
          description: "Estimated token usage"

        estimated_time_minutes:
          type: integer
          minimum: 1
          maximum: 180
          description: "Estimated execution time"

        can_parallelize:
          type: boolean
          description: "Whether this step can run in parallel with others"

        condition:
          type: string
          description: "Conditional execution expression"

  metadata:
    type: object
    properties:
      total_steps:
        type: integer
      total_estimated_tokens:
        type: integer
      total_estimated_time_minutes:
        type: integer
      tags:
        type: array
        items:
          type: string
      complexity:
        type: string
        enum: [low, medium, high]

  execution:
    type: object
    properties:
      strategy:
        type: string
        enum:
          - sequential
          - parallel
          - parallel_where_possible
        description: "Execution strategy"

      optimization:
        type: string
        enum: [speed, quality, balanced]
        description: "Optimization preference"

      parallel_groups:
        type: array
        items:
          type: array
          items:
            type: string
        description: "Groups of steps that can execute in parallel"
```

---

## Appendix B: Reference Implementation

### Minimal Workflow Executor (Python)

```python
from typing import List, Dict, Set, Any
from dataclasses import dataclass
from collections import defaultdict
import yaml

@dataclass
class Step:
    id: str
    description: str
    agent: str
    depends_on: List[str]
    inputs: List[str]
    outputs: List[str]
    estimated_tokens: int

@dataclass
class Workflow:
    name: str
    description: str
    steps: List[Step]

class WorkflowExecutor:
    def __init__(self):
        self.state: Dict[str, Any] = {}

    def load_yaml(self, path: str) -> Workflow:
        """Load workflow from YAML file"""
        with open(path) as f:
            data = yaml.safe_load(f)

        steps = [
            Step(
                id=s['id'],
                description=s['description'],
                agent=s['suggested_agent'],
                depends_on=s.get('depends_on', []),
                inputs=s.get('inputs', []),
                outputs=s.get('outputs', []),
                estimated_tokens=s.get('estimated_tokens', 10000)
            )
            for s in data['steps']
        ]

        return Workflow(
            name=data['name'],
            description=data['description'],
            steps=steps
        )

    def validate(self, workflow: Workflow) -> None:
        """Validate workflow structure"""
        step_ids = {s.id for s in workflow.steps}

        # Check unique IDs
        if len(step_ids) != len(workflow.steps):
            raise ValueError("Duplicate step IDs")

        # Check dependencies exist
        for step in workflow.steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    raise ValueError(
                        f"Step '{step.id}' depends on undefined step '{dep}'"
                    )

        # Check for cycles
        if self._has_cycle(workflow):
            raise ValueError("Circular dependency detected")

    def _has_cycle(self, workflow: Workflow) -> bool:
        """Detect cycles using DFS"""
        graph = defaultdict(list)
        for step in workflow.steps:
            for dep in step.depends_on:
                graph[dep].append(step.id)

        visited = set()
        rec_stack = set()

        def visit(node):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph[node]:
                if neighbor not in visited:
                    if visit(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for step in workflow.steps:
            if step.id not in visited:
                if visit(step.id):
                    return True

        return False

    def topological_sort(self, workflow: Workflow) -> List[Step]:
        """Sort steps by dependencies using Kahn's algorithm"""
        # Build graph
        in_degree = {s.id: len(s.depends_on) for s in workflow.steps}
        graph = defaultdict(list)
        steps_by_id = {s.id: s for s in workflow.steps}

        for step in workflow.steps:
            for dep in step.depends_on:
                graph[dep].append(step.id)

        # Find steps with no dependencies
        queue = [s.id for s in workflow.steps if in_degree[s.id] == 0]
        result = []

        while queue:
            step_id = queue.pop(0)
            result.append(steps_by_id[step_id])

            # Reduce in-degree of neighbors
            for neighbor in graph[step_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(workflow.steps):
            raise ValueError("Cycle detected (topological sort failed)")

        return result

    def execute_step(self, step: Step) -> Dict[str, Any]:
        """Execute a single step"""
        print(f"Executing step: {step.id}")
        print(f"  Agent: {step.agent}")
        print(f"  Description: {step.description}")

        # Check dependencies satisfied
        for dep in step.depends_on:
            if dep not in self.state:
                raise RuntimeError(
                    f"Dependency {dep} not satisfied for step {step.id}"
                )

        # Collect inputs
        inputs = {inp: self.state[inp] for inp in step.inputs if inp in self.state}

        # Execute agent (placeholder)
        result = self._invoke_agent(step.agent, step.description, inputs)

        # Store outputs
        for output in step.outputs:
            self.state[output] = result

        return result

    def _invoke_agent(self, agent: str, description: str, inputs: Dict) -> Any:
        """Placeholder for agent invocation"""
        # In real implementation, this would invoke the actual agent
        # via Claude Code's Task tool or similar mechanism
        return {
            'agent': agent,
            'description': description,
            'inputs': inputs,
            'status': 'completed'
        }

    def execute(self, workflow: Workflow) -> Dict[str, Any]:
        """Execute complete workflow"""
        self.validate(workflow)
        sorted_steps = self.topological_sort(workflow)

        results = {}
        for step in sorted_steps:
            result = self.execute_step(step)
            results[step.id] = result

        return results

# Usage
if __name__ == '__main__':
    executor = WorkflowExecutor()
    workflow = executor.load_yaml('api-development.yaml')
    results = executor.execute(workflow)
    print("Workflow completed:", results)
```

---

## Summary

This comprehensive research document provides:

1. **Theoretical Foundations**: Formal grammar theory, lambda calculus, category theory
2. **Practical Patterns**: Real-world DSL examples from GitHub Actions, Airflow, Terraform, Kubernetes
3. **Implementation Guidance**: Parser design, execution engines, validation strategies
4. **Mathematical Models**: Graph algorithms, operational semantics, complexity analysis
5. **Concrete Recommendations**: YAML-based DSL design optimized for Claude Code agent orchestration

### Key Takeaways for Claude Code DSL

**Recommended Approach**:
- **Surface Syntax**: YAML (familiar, tooling-rich, declarative)
- **Validation**: JSON Schema (standard, IDE support)
- **Execution Model**: Hybrid DAG-based (sequential + parallel where possible)
- **Dependency Resolution**: Topological sort (O(V + E) efficiency)
- **Composition**: Combinator patterns for step composition
- **Error Handling**: Fail-fast validation, clear error messages
- **Extensibility**: Support for conditional execution, loops, workflow composition

**Success Criteria**:
- Simple workflows are simple to write
- Complex workflows are possible
- Clear error messages
- Predictable execution
- Efficient resource utilization
- Maintainable and debuggable

---

**Document Status**: Complete
**Total Research Sources**: 23 academic and industry references
**Implementation Examples**: 15+ code samples across multiple languages
**Mathematical Formulations**: 8 formal models
**Real-World Case Studies**: 5 production DSL systems analyzed

This research provides a comprehensive foundation for designing and implementing DSLs optimized for agent orchestration in Claude Code and similar multi-agent systems.
