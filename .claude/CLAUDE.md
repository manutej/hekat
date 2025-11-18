# HEKAT - L1-L7 Orchestration System

**Autonomous Repository Configuration** for remote agent development

---

## Project Overview

**HEKAT** is a complexity-aware agent composition system providing L1-L7 orchestration levels from novice (600 tokens) to genius (22,000 tokens) with DSL-based query building and <100ms performance guarantees.

### Core Capabilities
- **L1-L7 Complexity Levels**: Automatic level selection based on task complexity
- **HEKAT DSL**: Formal EBNF grammar with 9 operators (→, ||, +, <>, [], //, |||, sample^, iterate)
- **TypeScript Implementation**: fp-ts based functional implementation with ReaderTaskEither monad stack
- **Performance Guarantees**: <100ms query parsing, <200ms agent selection
- **Multiple Variants**: DSL, TypeScript, TUI, Business OS, HKT implementations

---

## Autonomous Configuration

This repository contains everything needed for remote agent development:

### Skills Available (3 core)
- `functional-programming` - Pure functions, immutability, composition patterns
- `fp-ts` - Type-safe functional programming with monadic error handling
- `typescript-fp` - Advanced TypeScript patterns and generic pipelines

### Agents Available (5 specialized)
- `hekat-agent` - Primary L1-L7 orchestration
- `mercurio-orchestrator` - Multi-dimensional synthesis
- `api-architect` - System design and architecture
- `practical-programmer` - Pragmatic implementation
- `spec-driven-development-expert` - Constitutional framework enforcement

---

## Constitutional Principles

This project follows 9 immutable principles (see `.specify/constitution.md`):

1. **L1-L7 Level Selection** - Automatic complexity detection, never force wrong level
2. **DSL Syntax Stability** - EBNF grammar immutable, extensions only via new operators
3. **Performance Guarantees** - <100ms parsing, <200ms selection, <5s total execution
4. **Type Safety** - Full fp-ts type checking, no runtime type errors
5. **Composition Over Configuration** - DSL operators compose, no complex config files
6. **Token Budget Discipline** - L1: 600, L2: 1.5K, L3: 3K, L4: 7K, L5: 12K, L6: 18K, L7: 22K
7. **Agent Independence** - Agents stateless, idempotent, independently testable
8. **Operator Semantics Preservation** - Each operator maintains consistent meaning across all levels
9. **Progressive Disclosure** - Lower levels hide complexity, higher levels expose full power

---

## Quick Start

### Development Workflow
```bash
# Parse and execute HEKAT DSL query
npm run hekat -- "spec-driven-development-expert → practical-programmer + test-engineer"

# Run at specific L-level
npm run hekat -- --level L5 "complex task requiring multiple agents"

# Test DSL parser
npm test -- dslParser

# Generate TypeScript agents from DSL
npm run codegen -- --input queries.hekat --output src/agents/
```

---

## Specification Framework

All specifications in `.specify/`:

- `constitution.md` - 9 immutable architectural principles
- `l1-l7-architecture.md` - Detailed specs for each complexity level
- `hekat-dsl-spec.md` - Formal EBNF grammar with operator semantics
- `typescript-implementation.md` - fp-ts based functional implementation

---

## Architecture

### L1-L7 Complexity Levels

```
L1 Novice      → 600 tokens   → Single skill, basic task
L2 Competent   → 1,500 tokens → 2-3 skills, simple workflow
L3 Proficient  → 3,000 tokens → Multiple agents, coordination
L4 Expert      → 7,000 tokens → Complex multi-agent orchestration
L5 Master      → 12,000 tokens → Advanced synthesis, multiple domains
L6 Visionary   → 18,000 tokens → Breakthrough design, novel solutions
L7 Genius      → 22,000 tokens → Systems-level transformation
```

### HEKAT DSL Operators

```ebnf
Query     ::= Agent (Op Agent)*
Op        ::= "→"      # Sequential composition
            | "||"     # Parallel execution
            | "+"      # Skill augmentation
            | "<>"     # Conditional branching
            | "[]"     # Optional agent
            | "//"     # Fallback/retry
            | "|||"    # Fan-out/broadcast
            | "sample^N" # Sample N agents
            | "iterate@N" # Iterate N times

Agent     ::= Identifier ("+" Skill)*
Skill     ::= Identifier
```

### Example Queries

```hekat
# Sequential pipeline (L3)
spec-driven-development-expert → practical-programmer → test-engineer

# Parallel execution (L4)
frontend-architect || backend-expert || database-specialist

# Skill augmentation (L2)
api-architect + fastapi + postgresql

# Conditional branching (L5)
<bug-fix ? debug-detective : feature-architect> → practical-programmer

# Complex orchestration (L7)
mars-innovator → (mars-architect || mars-executor) → mercurio-synthesizer
```

---

## Development Guidelines

### TypeScript Implementation Pattern
```typescript
import { pipe } from 'fp-ts/function';
import { ReaderTaskEither } from 'fp-ts/ReaderTaskEither';

// HEKAT query executor
type HEKATContext = {
  level: L1_L7;
  agents: AgentRegistry;
  skills: SkillRegistry;
};

const executeQuery = (query: string): ReaderTaskEither<HEKATContext, Error, Result> =>
  pipe(
    parseQuery(query),
    chain(validateComplexity),
    chain(selectLevel),
    chain(orchestrateAgents),
    chain(synthesizeResults)
  );
```

### Testing Strategy
```typescript
describe('HEKAT L1-L7', () => {
  test('L1 single agent execution', async () => {
    const result = await hekat.execute("practical-programmer", L1);
    expect(result.tokenUsage).toBeLessThan(600);
  });

  test('L5 multi-agent synthesis', async () => {
    const result = await hekat.execute(
      "mars-innovator → mars-architect || mars-executor",
      L5
    );
    expect(result.agents.length).toBeGreaterThan(2);
    expect(result.tokenUsage).toBeLessThan(12000);
  });

  test('Performance guarantee <100ms parsing', async () => {
    const start = Date.now();
    await hekat.parse(complexQuery);
    const elapsed = Date.now() - start;
    expect(elapsed).toBeLessThan(100);
  });
});
```

### Performance Targets
- **Query Parsing**: < 100ms
- **Agent Selection**: < 200ms
- **Total Execution**: < 5s (excluding agent runtime)
- **Memory Footprint**: < 512MB for parser + orchestrator

---

## HEKAT Variants

### 1. HEKAT DSL (Text)
Pure DSL queries for command-line and programmatic use

### 2. HEKAT TypeScript
Strongly-typed fp-ts implementation with full type inference

### 3. HEKAT TUI
Terminal User Interface for interactive query building

### 4. HEKAT Business OS
Enterprise orchestration with audit trails and governance

### 5. HEKAT HKT (Higher-Kinded Types)
Advanced type-level programming with generics and functors

---

## Resources

- **Specifications**: `.specify/` directory (4 comprehensive documents)
- **Skills**: `.claude/skills/` (3 skills available)
- **Agents**: `.claude/agents/` (5 specialized agents)
- **Constitutional Framework**: `.specify/constitution.md`
- **DSL Reference**: `.specify/hekat-dsl-spec.md`

---

## Status

**Phase**: Specification Complete
**Autonomous Setup**: COMPLETE
**Git Repository**: https://github.com/manutej/hekat (private)
**Ready for Remote Agents**: ✅ YES

---

*This repository is fully autonomous and ready for remote agent development with embedded skills, agents, and constitutional principles.*
