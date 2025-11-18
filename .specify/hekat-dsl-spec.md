# HEKAT DSL Language Specification

**Version**: 1.0.0
**Date**: 2025-11-17
**Status**: Formal Language Specification

---

## 1. Introduction

### 1.1 Purpose

The HEKAT DSL (Domain-Specific Language) provides a declarative syntax for orchestrating Claude Code agents at varying complexity levels (L1-L7). The language emphasizes readability, type safety, and progressive complexity disclosure.

### 1.2 Design Philosophy

- **Human-readable**: Natural syntax that reads like intent
- **Type-safe**: Compile-time validation of agent compatibility
- **Composable**: Small operators combine into complex workflows
- **Level-aware**: Syntax implies complexity level
- **Backward-compatible**: Old syntax works in new versions

---

## 2. Lexical Structure

### 2.1 Character Set

```
Letters:     a-z, A-Z
Digits:      0-9
Symbols:     - _ / @ + | & > < [ ] ( ) { } , : ; . ! ?
Whitespace:  space, tab, newline
```

### 2.2 Tokens

```ebnf
token         ::= identifier
                | operator
                | keyword
                | literal
                | delimiter

identifier    ::= letter (letter | digit | '-' | '_')*
operator      ::= '->' | '||' | '+' | '//' | '|||' | '^'
keyword       ::= 'iterate' | 'sample' | 'until' | 'if' | 'else'
literal       ::= string | number | boolean
delimiter     ::= '(' | ')' | '[' | ']' | '{' | '}' | ',' | ':'
```

### 2.3 Comments

```
// Single-line comment
/* Multi-line
   comment */
```

---

## 3. Grammar Specification

### 3.1 EBNF Grammar

```ebnf
(* Program structure *)
program       ::= statement+

statement     ::= expression
                | assignment
                | workflow_def

(* Expressions - ordered by precedence *)
expression    ::= sequential

sequential    ::= parallel ('->' parallel)*

parallel      ::= fallback ('||' fallback)*

fallback      ::= ensemble ('//' ensemble)*

ensemble      ::= combination ('|||' combination)*

combination   ::= skill ('+' skill)*

skill         ::= command ('<' skill_list '>')?

command       ::= primary ('[' command_name ']')?

primary       ::= agent_ref
                | group
                | sample_expr
                | iterate_expr

group         ::= '(' expression ')'

(* Agent reference *)
agent_ref     ::= identifier
                | '@L' digit

(* Skills *)
skill_list    ::= identifier (',' identifier)*

(* Commands *)
command_name  ::= '/' identifier

(* Complex operators *)
sample_expr   ::= 'sample' '^' number '(' agent_list ')'

iterate_expr  ::= 'iterate' '(' expression ',' 'until' '=' condition ')'

agent_list    ::= agent_ref (',' agent_ref)*

(* Assignments *)
assignment    ::= identifier '=' expression
                | identifier ':' expression

(* Workflow definitions *)
workflow_def  ::= 'workflow' identifier '{' workflow_body '}'

workflow_body ::= metadata* statement+

metadata      ::= 'name' ':' string
                | 'version' ':' version
                | 'requires' ':' skill_list
```

### 3.2 Operator Precedence

From highest to lowest:

1. `()` - Grouping
2. `[]` - Commands
3. `<>` - Skills
4. `+` - Combination
5. `|||` - Ensemble
6. `//` - Fallback
7. `||` - Parallel
8. `->` - Sequential
9. `=` `:` - Assignment

---

## 4. Operators and Semantics

### 4.1 Sequential Operator (`->`)

**Syntax**: `A -> B`
**Semantics**: Execute A, then pass output to B
**Level**: L2-L3 typically

```
deep-researcher -> api-architect -> practical-programmer
```

**Type Rule**:
```
output_type(A) ⊆ input_type(B)
```

### 4.2 Parallel Operator (`||`)

**Syntax**: `A || B || C`
**Semantics**: Execute simultaneously, merge results
**Level**: L4 typically

```
api-architect || database-specialist || security-auditor
```

**Type Rule**:
```
merge_compatible(output_type(A), output_type(B), output_type(C))
```

### 4.3 Combination Operator (`+`)

**Syntax**: `A + skill1 + skill2`
**Semantics**: Augment agent with skills
**Level**: Enhances any level

```
api-architect + fastapi + postgresql
```

**Type Rule**:
```
compatible(agent, skill) ∧ no_conflicts(skill1, skill2)
```

### 4.4 Skills Operator (`<>`)

**Syntax**: `agent<skill1, skill2>`
**Semantics**: Load agent with specific skills
**Level**: Configuration, not coordination

```
practical-programmer<typescript, react-development>
```

### 4.5 Command Operator (`[]`)

**Syntax**: `agent[/command]`
**Semantics**: Apply command to agent
**Level**: Modifier, not coordination

```
deep-researcher[/ctx7("fastapi")]
```

### 4.6 Fallback Operator (`//`)

**Syntax**: `A // B`
**Semantics**: Try A, fallback to B on failure
**Level**: Error handling pattern

```
api-architect // practical-programmer
```

### 4.7 Ensemble Operator (`|||`)

**Syntax**: `A ||| B ||| C`
**Semantics**: Weighted consensus execution
**Level**: L7 typically

```
expert1 ||| expert2 ||| expert3
```

### 4.8 Sample Operator

**Syntax**: `sample^n(agents)`
**Semantics**: Sample n executions for variance
**Level**: L7 statistical patterns

```
sample^3(deep-researcher, api-architect, claude-sdk-expert)
```

### 4.9 Iterate Operator

**Syntax**: `iterate(workflow, until=condition)`
**Semantics**: Repeat until condition met
**Level**: L6 typically

```
iterate(debug -> fix -> test, until=tests_pass)
```

---

## 5. Level-Specific Patterns

### 5.1 L1: Single Agent

```
deep-researcher
```

### 5.2 L2: Two-Step Chain

```
api-architect -> docs-generator
```

### 5.3 L3: Three-Step Chain

```
deep-researcher -> api-architect -> practical-programmer
```

### 5.4 L4: Parallel Consensus

```
(deep-researcher || api-architect || claude-sdk-expert)
```

### 5.5 L5: Hierarchical

```
[research_team] -> project-orchestrator -> [implementation_team]

where:
  research_team = api-architect + deep-researcher
  implementation_team = practical-programmer || deployment-orchestrator
```

### 5.6 L6: Iterative

```
iterate(
  debug-detective -> practical-programmer -> test-engineer,
  until=all_tests_pass
)
```

### 5.7 L7: Full Ensemble

```
sample^3(deep-researcher, api-architect, frontend-architect) ;
mercurio-orchestrator[consensus] ;
(practical-programmer || deployment-orchestrator || docs-generator) ;
project-orchestrator[final-synthesis]
```

---

## 6. Type System

### 6.1 Agent Types

```typescript
type Agent = {
  name: string
  capabilities: Capability[]
  compatible_skills: Skill[]
  input_types: Type[]
  output_types: Type[]
}
```

### 6.2 Skill Types

```typescript
type Skill = {
  name: string
  domain: Domain
  requires: Skill[]
  conflicts: Skill[]
}
```

### 6.3 Type Checking Rules

```typescript
// Sequential compatibility
canSequence(a: Agent, b: Agent): boolean {
  return a.output_types.some(t =>
    b.input_types.includes(t)
  )
}

// Parallel compatibility
canParallelize(agents: Agent[]): boolean {
  return agents.every(a =>
    !hasResourceConflict(a, agents)
  )
}

// Skill compatibility
canAugment(agent: Agent, skill: Skill): boolean {
  return agent.compatible_skills.includes(skill) &&
         !hasConflicts(agent.current_skills, skill)
}
```

---

## 7. Syntax Sugar and Shortcuts

### 7.1 Level Forcing

```
@L5 "design system"      // Force L5 regardless of classification
@L7 complex_workflow     // Force L7 execution
```

### 7.2 Quick Chains

```
[R>D>I]                  // Research -> Design -> Implement
[D>I>T]                  // Design -> Implement -> Test
```

### 7.3 Quick Parallel

```
[P:R||D||A]             // Parallel: Research || Design || Analyze
```

### 7.4 Named Groups

```
research_phase = deep-researcher || api-architect
build_phase = practical-programmer<fastapi> || database-specialist

research_phase -> build_phase
```

---

## 8. Workflow Definitions

### 8.1 Basic Workflow

```
workflow api_development {
  deep-researcher -> api-architect -> practical-programmer
}
```

### 8.2 Parameterized Workflow

```
workflow feature_development(skill: Skill) {
  requires: [skill]

  research = deep-researcher + skill
  design = api-architect + skill
  implement = practical-programmer + skill

  research -> design -> implement
}
```

### 8.3 Conditional Workflow

```
workflow smart_fix {
  analysis = debug-detective

  if (analysis.complexity > HIGH) {
    team = practical-programmer || senior-developer
    team -> test-engineer
  } else {
    practical-programmer -> test-engineer
  }
}
```

---

## 9. Semantic Rules

### 9.1 Execution Order

1. Commands execute before agent
2. Skills load before execution
3. Parallel branches execute simultaneously
4. Sequential steps wait for completion
5. Fallbacks trigger on failure only

### 9.2 Result Aggregation

```typescript
// Parallel merge strategy
mergeParallel(results: Result[]): Result {
  return {
    combined: results.flatMap(r => r.outputs),
    consensus: findConsensus(results),
    confidence: averageConfidence(results)
  }
}

// Sequential passing
passSequential(from: Result, to: Agent): Input {
  return {
    context: from.context,
    data: from.output,
    metadata: from.metadata
  }
}
```

### 9.3 Error Propagation

```typescript
// Fallback handling
executeFallback(primary: Agent, fallback: Agent): Result {
  try {
    return execute(primary)
  } catch (error) {
    log.warn(`Primary failed: ${error}`)
    return execute(fallback)
  }
}

// Iteration termination
executeIteration(workflow: Workflow, condition: Condition): Result {
  let iteration = 0
  let result = null

  while (!condition.met(result) && iteration < MAX_ITERATIONS) {
    result = execute(workflow)
    iteration++
  }

  return result
}
```

---

## 10. Examples

### 10.1 Simple Research

```
// L1: Single agent
deep-researcher : "explain quantum computing"
```

### 10.2 API Development

```
// L3: Sequential chain
/ctx7("fastapi") -> api-architect + fastapi -> practical-programmer
```

### 10.3 Architecture Review

```
// L4: Parallel consensus
(api-architect || security-expert || database-specialist) : "review architecture"
```

### 10.4 Bug Fix Iteration

```
// L6: Iterative refinement
iterate(
  debug-detective -> practical-programmer -> test-engineer,
  until=tests_pass
) : "fix memory leak"
```

### 10.5 Platform Development

```
// L7: Full ensemble
workflow saas_platform {
  // Research phase (parallel)
  research = sample^3(
    deep-researcher,
    api-architect,
    frontend-architect,
    claude-sdk-expert
  )

  // Synthesis
  synthesis = research -> mercurio-orchestrator[consensus]

  // Implementation (parallel)
  implement = (
    practical-programmer<fastapi> ||
    frontend-developer<react> ||
    deployment-orchestrator<kubernetes>
  )

  // Final orchestration
  synthesis -> implement -> project-orchestrator[final]
}
```

---

## 11. Parser Implementation

### 11.1 Tokenization

```typescript
class Lexer {
  tokenize(input: string): Token[] {
    const tokens: Token[] = []
    let position = 0

    while (position < input.length) {
      // Skip whitespace
      if (isWhitespace(input[position])) {
        position++
        continue
      }

      // Multi-character operators
      if (input.slice(position, position + 2) === '->') {
        tokens.push({ type: 'ARROW', value: '->' })
        position += 2
        continue
      }

      // ... other token types
    }

    return tokens
  }
}
```

### 11.2 Parsing

```typescript
class Parser {
  parse(tokens: Token[]): AST {
    return this.parseExpression(tokens)
  }

  parseExpression(tokens: Token[]): AST {
    return this.parseSequential(tokens)
  }

  parseSequential(tokens: Token[]): AST {
    let left = this.parseParallel(tokens)

    while (this.current?.type === 'ARROW') {
      this.consume('ARROW')
      const right = this.parseParallel(tokens)
      left = new SequentialNode(left, right)
    }

    return left
  }

  // ... other parse methods
}
```

---

## 12. Validation Rules

### 12.1 Static Validation

- All referenced agents must exist
- All referenced skills must exist
- Type compatibility for sequences
- No circular dependencies
- Token budget compliance

### 12.2 Runtime Validation

- Agent availability
- Skill loading success
- Resource limits
- Timeout compliance
- Result type matching

---

## 13. Evolution Strategy

### 13.1 Version Compatibility

```yaml
v1.0.0:
  operators: ['->', '||', '+']

v1.1.0:
  operators: ['->', '||', '+', '//', '<>', '[]']
  backward_compatible: true

v2.0.0:
  operators: [all_previous, '|||', 'sample^', 'iterate']
  migration_tool: provided
```

### 13.2 Deprecation Policy

1. Announce deprecation in version N
2. Provide migration guide
3. Support both syntaxes in N+1, N+2
4. Remove in version N+3
5. Maintain transpiler for legacy

---

## Appendix A: Quick Reference Card

```
OPERATORS
---------
->        Sequential execution
||        Parallel execution
+         Skill combination
<>        Skill loading
[]        Command application
//        Fallback on error
|||       Ensemble voting
sample^n  Statistical sampling
iterate   Loop until condition

PATTERNS BY LEVEL
-----------------
L1: agent
L2: agent1 -> agent2
L3: agent1 -> agent2 -> agent3
L4: (agent1 || agent2 || agent3)
L5: [team1] -> supervisor -> [team2]
L6: iterate(workflow, until=condition)
L7: sample^n(agents) -> synthesize -> implement

SHORTCUTS
---------
@L5       Force complexity level
[R>D>I]   Quick sequential chain
[P:A||B]  Quick parallel group
```

---

**Document Status**: Complete Language Specification
**Parser Implementation**: TypeScript (hekat-ts)
**Next Steps**: Extend parser for advanced operators