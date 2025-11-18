# HEKAT DSL fp-ts Implementation Roadmap

**Date**: 2025-11-14
**Timeline**: 2-3 weeks (15-21 days)
**Goal**: Production-ready Claude Code plugin

---

## Quick Start

### Prerequisites

```bash
# Install Node.js 18+ and pnpm
brew install node pnpm

# Verify versions
node --version  # v18.0.0+
pnpm --version  # 8.0.0+
```

### Project Initialization

```bash
# Create project structure
mkdir -p hekat-dsl/{src,tests,examples,docs}
cd hekat-dsl

# Initialize package.json
pnpm init

# Install dependencies
pnpm add fp-ts @effect/data @effect/match

# Install dev dependencies
pnpm add -D typescript @types/node \
  vitest @vitest/ui fast-check \
  prettier eslint @typescript-eslint/parser

# Initialize TypeScript
pnpx tsc --init
```

---

## Week 1: Core Compiler (Days 1-7)

### Day 1: Project Setup & Type System

**Goal**: Create project scaffold with all types defined

#### Tasks

1. **Initialize Project** (2 hours)
   ```bash
   # Create directory structure
   mkdir -p src/{types,lexer,parser,typechecker,dag,compiler,executor,plugin}
   mkdir -p tests/{unit,integration,property}
   mkdir -p examples

   # Create config files
   touch tsconfig.json
   touch vitest.config.ts
   touch .prettierrc
   touch .eslintrc.js
   ```

2. **Configure TypeScript** (1 hour)
   ```json
   // tsconfig.json
   {
     "compilerOptions": {
       "target": "ES2022",
       "module": "ESNext",
       "moduleResolution": "bundler",
       "lib": ["ES2022"],
       "strict": true,
       "esModuleInterop": true,
       "skipLibCheck": true,
       "forceConsistentCasingInFileNames": true,
       "declaration": true,
       "declarationMap": true,
       "sourceMap": true,
       "outDir": "./dist",
       "rootDir": "./src"
     },
     "include": ["src/**/*"],
     "exclude": ["node_modules", "dist", "tests"]
   }
   ```

3. **Define Core Types** (4 hours)
   - ✅ `src/types/Token.ts` - TokenType enum, Token interface
   - ✅ `src/types/AST.ts` - ExpressionNode ADT (7 variants)
   - ✅ `src/types/DAG.ts` - DAGNode, DAG, Phase
   - ✅ `src/types/ExecutionPlan.ts` - ExecutionPlan, CompileError

**Deliverables**:
- ✅ Project compiles with `pnpm build`
- ✅ All types defined with 100% type coverage
- ✅ Exported from `src/index.ts`

**Success Criteria**:
```bash
pnpm build        # ✅ Compiles with 0 errors
pnpm typecheck    # ✅ No type errors
```

---

### Day 2: Lexer Implementation

**Goal**: State monad-based lexer with full token support

#### Tasks

1. **Lexer State Type** (1 hour)
   ```typescript
   // src/lexer/types.ts
   export type LexerState = {
     readonly input: string
     readonly position: number
     readonly tokens: ReadonlyArray<Token>
   }

   export type LexerError = {
     readonly message: string
     readonly position: number
     readonly context: string
   }
   ```

2. **Basic State Operations** (2 hours)
   ```typescript
   // src/lexer/operations.ts
   import * as S from 'fp-ts/State'

   export const currentChar: S.State<LexerState, string>
   export const advance: S.State<LexerState, void>
   export const addToken: (token: Token) => S.State<LexerState, void>
   export const skipWhitespace: S.State<LexerState, void>
   ```

3. **Token Readers** (3 hours)
   - ✅ `readString` - Handle quotes, escapes
   - ✅ `readNumber` - Parse integers
   - ✅ `readIdentifier` - Parse agent/skill names
   - ✅ `readOperator` - Multi-char operators (->   , ||)

4. **Main Tokenizer** (2 hours)
   ```typescript
   // src/lexer/Lexer.ts
   export const tokenize: (input: string) => E.Either<LexerError, ReadonlyArray<Token>>
   ```

**Deliverables**:
- ✅ Lexer tokenizes all 8 query patterns
- ✅ Proper error messages with position context
- ✅ Unit tests for each token type

**Tests**:
```typescript
// tests/unit/lexer.test.ts
describe('Lexer', () => {
  it('tokenizes simple agent', () => {
    const result = tokenize('agent : "prompt"')
    expect(E.isRight(result)).toBe(true)
  })

  it('handles invalid input', () => {
    const result = tokenize('agent @ invalid')
    expect(E.isLeft(result)).toBe(true)
  })
})
```

---

### Day 3: Parser - Part 1 (Basic Patterns)

**Goal**: Parse L1-L3 patterns (Simple, Sequential, Parallel)

#### Tasks

1. **Parser State Type** (1 hour)
   ```typescript
   // src/parser/types.ts
   export type ParserState = {
     readonly tokens: ReadonlyArray<Token>
     readonly position: number
   }

   export type ParseError = {
     readonly message: string
     readonly token: Token
   }

   export type Parser<A> = (
     state: ParserState
   ) => E.Either<ParseError, [A, ParserState]>
   ```

2. **Parser Combinators** (2 hours)
   ```typescript
   // src/parser/combinators.ts
   export const current: Parser<Token>
   export const advance: Parser<void>
   export const expect: (type: TokenType) => Parser<Token>
   export const optional: <A>(p: Parser<A>) => Parser<O.Option<A>>
   export const many: <A>(p: Parser<A>) => Parser<ReadonlyArray<A>>
   ```

3. **Basic Expression Parsers** (4 hours)
   - ✅ `parseSimple` - IDENTIFIER
   - ✅ `parseSequential` - A -> B -> C
   - ✅ `parseParallel` - (A || B || C)
   - ✅ `parseQuery` - expr : "prompt"

**Deliverables**:
- ✅ Parse L1-L3 queries successfully
- ✅ Proper error messages
- ✅ Unit tests for each pattern

---

### Day 4: Parser - Part 2 (Advanced Patterns)

**Goal**: Parse L4-L7 patterns (Fallback, Ensemble, Commanded, Skilled)

#### Tasks

1. **Advanced Parsers** (5 hours)
   - ✅ `parseFallback` - A ? B ? C
   - ✅ `parseEnsemble` - sample^3 ; merge ; synth
   - ✅ `parseCommanded` - @ctx7(agent)
   - ✅ `parseSkilled` - agent + skill1 + skill2

2. **Recursive Descent** (2 hours)
   ```typescript
   // src/parser/Parser.ts
   const parseExpression: Parser<ExpressionNode> = state =>
     parseFallback(state)

   const parseFallback: Parser<ExpressionNode> = state =>
     pipe(
       parseSequential(state),
       E.flatMap(([first, state1]) =>
         // Check for ? operator...
       )
     )
   ```

**Deliverables**:
- ✅ Parse all 8 query patterns
- ✅ Nested expressions work
- ✅ Property tests for parse/unparse

---

### Day 5: Type Checker

**Goal**: Validation applicative with error accumulation

#### Tasks

1. **Config Type** (1 hour)
   ```typescript
   // src/typechecker/Config.ts
   export type Config = {
     readonly agents: ReadonlySet<string>
     readonly skills: ReadonlySet<string>
     readonly commands: ReadonlySet<string>
   }

   export const defaultConfig: Config
   ```

2. **Validation Functions** (3 hours)
   ```typescript
   // src/typechecker/validators.ts
   const validateAgentExists: (
     name: string,
     config: Config
   ) => Validation<string>

   const validateSkillExists: (
     name: string,
     config: Config
   ) => Validation<string>

   const validateExpression: (
     expr: ExpressionNode,
     config: Config
   ) => Validation<ExpressionNode>
   ```

3. **Applicative Composition** (3 hours)
   ```typescript
   // src/typechecker/TypeChecker.ts
   export const validate: (
     ast: QueryNode,
     config: Config
   ) => Validation<QueryNode>
   ```

**Deliverables**:
- ✅ Accumulates all errors (not just first)
- ✅ Validates agents, skills, commands
- ✅ Proper error messages

**Tests**:
```typescript
it('accumulates multiple errors', () => {
  const result = validate(
    parseUnsafe('unknown1 -> unknown2 : "test"'),
    defaultConfig
  )

  expect(E.isLeft(result)).toBe(true)
  expect(E.getLeft(result).length).toBe(2)
})
```

---

### Day 6: DAG Builder

**Goal**: Pure functional DAG construction

#### Tasks

1. **DAG Types** (1 hour)
   ```typescript
   // src/dag/types.ts
   export type DAGNode = {
     readonly id: number
     readonly expr: ExpressionNode
     readonly dependencies: ReadonlySet<number>
     readonly isFallback: boolean
     readonly fallbackOf: O.Option<number>
   }

   export type DAG = {
     readonly nodes: ReadonlyMap<number, DAGNode>
     readonly executionOrder: ReadonlyArray<number>
     readonly parallelPhases: ReadonlyMap<number, ReadonlyArray<number>>
   }
   ```

2. **DAG Builder** (4 hours)
   ```typescript
   // src/dag/DAGBuilder.ts
   type BuildState = {
     nextId: number
     nodes: Map<number, DAGNode>
   }

   const buildNodes: (
     expr: ExpressionNode,
     deps: ReadonlySet<number>
   ) => S.State<BuildState, ReadonlySet<number>>

   export const build: (
     expr: ExpressionNode
   ) => E.Either<string, DAG>
   ```

3. **Graph Algorithms** (2 hours)
   - ✅ Topological sort (Kahn's algorithm)
   - ✅ Cycle detection (DFS)
   - ✅ Phase identification (level-wise traversal)

**Deliverables**:
- ✅ Correct DAG for all patterns
- ✅ Detects cycles (impossible in DSL, but defensive)
- ✅ Identifies parallelism opportunities

---

### Day 7: Compiler Pipeline

**Goal**: Orchestrate full compilation pipeline

#### Tasks

1. **Error Types** (1 hour)
   ```typescript
   // src/compiler/errors.ts
   export type CompileError =
     | { _tag: 'LexerError'; message: string; position: number }
     | { _tag: 'ParseError'; message: string; position: number }
     | { _tag: 'ValidationError'; errors: ReadonlyArray<string> }
     | { _tag: 'DAGBuildError'; message: string }
   ```

2. **Pipeline Composition** (3 hours)
   ```typescript
   // src/compiler/Compiler.ts
   export const compile = (
     dslString: string,
     config: Config
   ): E.Either<CompileError, ExecutionPlan> =>
     pipe(
       dslString,
       tokenize,
       E.mapLeft(toCompileError('LexerError')),
       E.flatMap(parse),
       E.mapLeft(toCompileError('ParseError')),
       E.flatMap(ast => validate(ast, config)),
       E.mapLeft(toCompileError('ValidationError')),
       E.flatMap(ast => buildDAG(ast.expression)),
       E.mapLeft(toCompileError('DAGBuildError')),
       E.map(dag => generatePlan(dag, ast))
     )
   ```

3. **Plan Generation** (3 hours)
   - ✅ Convert DAG phases to Task Relay phases
   - ✅ Estimate token budgets
   - ✅ Classify complexity (L1-L7)
   - ✅ Add metadata

**Deliverables**:
- ✅ End-to-end compilation works
- ✅ Integration tests for all 8 patterns
- ✅ Proper error propagation

**Tests**:
```typescript
describe('Compiler', () => {
  it('compiles L1 query', () => {
    const result = compile('agent : "prompt"', defaultConfig)

    expect(E.isRight(result)).toBe(true)
    const plan = E.getOrThrow(result)
    expect(plan.complexityLevel).toBe('L1')
    expect(plan.phases.length).toBe(1)
  })
})
```

---

## Week 2: Executor & Integration (Days 8-14)

### Day 8-9: HEKAT Executor - Core

**Goal**: TaskEither-based async orchestration

#### Tasks (Day 8)

1. **Executor Types** (2 hours)
   ```typescript
   // src/executor/types.ts
   export type ExecutionError =
     | { _tag: 'AgentExecutionError'; message: string }
     | { _tag: 'TimeoutError'; phase: number }
     | { _tag: 'FallbackExhausted'; attempts: number }

   export type ExecutionResult = {
     readonly output: string
     readonly tokensUsed: number
     readonly duration: number
   }
   ```

2. **Agent Execution** (4 hours)
   ```typescript
   // src/executor/agent.ts
   export const executeAgent: (
     agent: string,
     prompt: string,
     tokenBudget: number
   ) => TE.TaskEither<ExecutionError, ExecutionResult>
   ```

#### Tasks (Day 9)

3. **Phase Execution** (4 hours)
   ```typescript
   // src/executor/phase.ts
   export const executePhase: (
     phase: Phase,
     prompt: string
   ) => TE.TaskEither<ExecutionError, ReadonlyArray<ExecutionResult>>
   ```

4. **Plan Execution** (3 hours)
   ```typescript
   // src/executor/HEKATExecutor.ts
   export const executePlan: (
     plan: ExecutionPlan
   ) => TE.TaskEither<ExecutionError, ReadonlyArray<ExecutionResult>>
   ```

**Deliverables**:
- ✅ Sequential execution works
- ✅ Parallel execution works
- ✅ Token budgets respected

---

### Day 10-11: HEKAT Executor - Advanced

**Goal**: Fallback, retry, timeout logic

#### Tasks (Day 10)

1. **Fallback Chain** (4 hours)
   ```typescript
   // src/executor/fallback.ts
   export const executeWithFallback: (
     alternatives: ReadonlyArray<ExpressionNode>,
     prompt: string
   ) => TE.TaskEither<ExecutionError, ExecutionResult>
   ```

2. **Retry Logic** (3 hours)
   ```typescript
   // src/executor/retry.ts
   export const retry: <E, A>(
     task: TE.TaskEither<E, A>,
     maxRetries: number,
     delay: number
   ) => TE.TaskEither<E, A>
   ```

#### Tasks (Day 11)

3. **Timeout Handling** (3 hours)
   ```typescript
   // src/executor/timeout.ts
   export const withTimeout: <E, A>(
     task: TE.TaskEither<E, A>,
     ms: number
   ) => TE.TaskEither<E | TimeoutError, A>
   ```

4. **Progress Tracking** (4 hours)
   ```typescript
   // src/executor/progress.ts
   export const executeWithProgress: (
     plan: ExecutionPlan,
     onProgress: (phase: number, total: number) => void
   ) => TE.TaskEither<ExecutionError, ExecutionResult>
   ```

**Deliverables**:
- ✅ Fallback works
- ✅ Retry with exponential backoff
- ✅ Timeout protection

---

### Day 12-13: Claude Code Integration

**Goal**: Plugin manifest and Task API integration

#### Tasks (Day 12)

1. **Plugin Manifest** (2 hours)
   ```json
   // src/plugin/manifest.json
   {
     "name": "hekat-dsl",
     "version": "1.0.0",
     "description": "HEKAT DSL orchestration for Claude Code",
     "main": "dist/plugin/index.js",
     "commands": {
       "hekat": {
         "description": "Execute HEKAT DSL query",
         "args": ["<dsl-query>"]
       }
     }
   }
   ```

2. **Task API Client** (4 hours)
   ```typescript
   // src/plugin/TaskAPIClient.ts
   export class TaskAPIClient {
     runAgent(params: {
       agent: string
       prompt: string
       tokenBudget: number
     }): Promise<ExecutionResult>
   }
   ```

#### Tasks (Day 13)

3. **Command Handler** (4 hours)
   ```typescript
   // src/plugin/commands.ts
   export const hekatCommand: (
     args: string[]
   ) => TE.TaskEither<Error, string>
   ```

4. **Plugin Entry Point** (3 hours)
   ```typescript
   // src/plugin/index.ts
   export const plugin: ClaudeCodePlugin = {
     name: 'hekat-dsl',
     version: '1.0.0',
     commands: { hekat: hekatCommand }
   }
   ```

**Deliverables**:
- ✅ Plugin loads in Claude Code
- ✅ `/hekat` command works
- ✅ Integration with Task API

---

### Day 14: Testing & Polish

**Goal**: Comprehensive test coverage

#### Tasks

1. **Property Tests** (3 hours)
   ```typescript
   // tests/property/compiler.test.ts
   fc.assert(
     fc.property(dslQueryArb, query => {
       const result = compile(query, defaultConfig)
       // Properties:
       // - Never throws
       // - If valid, roundtrips
       // - Errors are informative
     })
   )
   ```

2. **Integration Tests** (3 hours)
   ```typescript
   // tests/integration/e2e.test.ts
   it('L5 mixed pattern', async () => {
     const dsl = 'agent1 -> (agent2 || agent3) -> agent4 : "test"'
     const plan = compile(dsl, defaultConfig)
     const result = await executePlan(plan)()

     expect(E.isRight(result)).toBe(true)
   })
   ```

3. **Error Message Polish** (1 hour)
   - Helpful error messages
   - Position context
   - Suggestions

---

## Week 3: Documentation & Release (Days 15-21)

### Day 15-16: Documentation

**Goal**: Comprehensive user-facing docs

#### Tasks

1. **API Reference** (4 hours)
   ```markdown
   # API Reference

   ## Compiler

   ### `compile(dslString: string): Either<CompileError, ExecutionPlan>`

   Compiles HEKAT DSL string to execution plan.

   **Example**:
   ```typescript
   const plan = compile('agent : "prompt"', defaultConfig)
   ```
   ```

2. **User Guide** (4 hours)
   - Quick start
   - Pattern reference
   - Examples (L1-L7)
   - Error handling

3. **Migration Guide** (4 hours)
   - Python → fp-ts comparison
   - API changes
   - Breaking changes

---

### Day 17-18: Beta Testing

**Goal**: Internal dogfooding and bug fixes

#### Tasks

1. **Dogfooding** (Full day)
   - Use HEKAT in real workflows
   - Identify pain points
   - Collect feedback

2. **Bug Fixes** (Full day)
   - Fix critical bugs
   - Improve error messages
   - Performance tuning

---

### Day 19-20: Performance & Optimization

**Goal**: Meet performance targets

#### Tasks

1. **Benchmarking** (3 hours)
   ```typescript
   // benchmark/compiler.bench.ts
   suite
     .add('L1: compile', () => compile('agent : "test"'))
     .add('L5: compile', () => compile('a -> (b || c) -> d : "test"'))
   ```

2. **Optimization** (4 hours)
   - Memoization where beneficial
   - Reduce allocations
   - Parallelize where safe

3. **Load Testing** (3 hours)
   - 1000 compilations/second
   - Memory usage stable
   - No leaks

---

### Day 21: Release

**Goal**: Ship v1.0.0

#### Tasks

1. **Publish to npm** (2 hours)
   ```bash
   pnpm build
   pnpm test
   pnpm publish --access public
   ```

2. **Create Plugin Package** (3 hours)
   ```bash
   # Package for Claude Code
   mkdir -p hekat-plugin
   cp dist/plugin/* hekat-plugin/
   cp manifest.json hekat-plugin/
   zip -r hekat-plugin.zip hekat-plugin/
   ```

3. **Release Announcement** (2 hours)
   - Blog post
   - Documentation site
   - GitHub release

---

## Continuous Activities

### Daily

- ✅ Commit code
- ✅ Run tests
- ✅ Update todo list

### Weekly

- ✅ Code review
- ✅ Update roadmap
- ✅ Check metrics

---

## Success Metrics

### Code Quality

| Metric | Target | Current |
|--------|--------|---------|
| Type Coverage | 100% | - |
| Test Coverage | ≥ 90% | - |
| Property Tests | ≥ 20 | - |
| ESLint Errors | 0 | - |

### Performance

| Metric | Target | Current |
|--------|--------|---------|
| Compile L1 | < 10ms | - |
| Compile L5 | < 100ms | - |
| Execute L1 | < 1s | - |
| Execute L5 | < 5s | - |

### Documentation

| Metric | Target | Current |
|--------|--------|---------|
| API docs | 100% | - |
| Examples | ≥ 20 | - |
| Tutorials | ≥ 3 | - |

---

## Risk Mitigation

### Technical Risks

1. **fp-ts Learning Curve**
   - Mitigation: Pair programming, code reviews
   - Fallback: Simplify monad stack if needed

2. **Claude Code API Changes**
   - Mitigation: Abstract Task API behind interface
   - Fallback: Support multiple API versions

3. **Performance Issues**
   - Mitigation: Early benchmarking
   - Fallback: Optimize hot paths with Bun/Wasm

### Schedule Risks

1. **Scope Creep**
   - Mitigation: Strict MVP scope
   - Fallback: Push L6-L7 to v1.1

2. **Blocked on Dependencies**
   - Mitigation: Stub external APIs
   - Fallback: Continue with mocks

---

## Next Steps

**Immediate** (Today):
1. ✅ Review roadmap
2. ✅ Get approval
3. ✅ Create project repo

**Tomorrow** (Day 1):
4. Initialize project
5. Define types
6. Start lexer

---

**Status**: 🎯 Ready to start
**Timeline**: 15-21 days to v1.0.0
**Next**: Day 1 - Project Setup & Type System
