# HEKAT DSL → fp-ts Migration Specification

**Date**: 2025-11-14
**Goal**: Migrate Python HEKAT compiler (~1,271 lines) to TypeScript with fp-ts
**Timeline**: 2-3 weeks
**Target**: Production-ready Claude Code plugin

---

## Executive Summary

### Why fp-ts?

**Decision Matrix** (from `/tmp/HEKAT-IMPLEMENTATION-LANGUAGE-ANALYSIS.md`):

| Metric             | Python | Go   | Rust | **fp-ts** |
|--------------------|--------|------|------|-----------|
| FP Support         | 6/10   | 4/10 | 8/10 | **10/10** ✅ |
| Claude Integration | 5/10   | 6/10 | 5/10 | **10/10** ✅ |
| Migration Time     | N/A    | 3-4w | 4-6w | **2-3w** ✅  |
| Performance        | 4/10   | 9/10 | 10/10| 6/10      |
| **Total Score**    | 50%    | 71%  | 81%  | **87%** 🏆 |

**Winner**: fp-ts (TypeScript)
**Rationale**: Best FP support, seamless Claude Code integration, fastest migration, sufficient performance.

---

## Architecture Overview

### Python → fp-ts Monad Mapping

```typescript
// Python (imperative, exceptions)          →  fp-ts (functional, type-safe)
// ─────────────────────────────────────────────────────────────────────────

class Lexer:                                →  type LexerState = State<string, Token[]>
  def tokenize() -> List[Token]:           →  const tokenize: LexerState = pipe(...)
    # Mutable self.position                →  // Immutable state threading

class Parser:                               →  type Parser<A> = Either<ParseError, A>
  def parse() -> QueryNode:                →  const parse: Parser<QueryNode> = pipe(...)
    # Try/catch, raise ParseError          →  // Left(error) | Right(value)

class TypeChecker:                          →  type Validation<A> = Either<NonEmptyArray<Error>, A>
  def validate() -> Dict:                  →  const validate: Validation<ValidAST> = pipe(...)
    # errors.append(...)                   →  // Applicative: accumulates all errors

class DAGBuilder:                           →  type DAGBuilder = Reader<Config, DAG>
  def build() -> DAG:                      →  const buildDAG: DAGBuilder = pipe(...)
    # self.nodes = {}                      →  // Pure transformations, no mutation

class Compiler:                             →  type Compiler = Either<CompileError, ExecutionPlan>
  def compile() -> ExecutionPlan:          →  const compile = pipe(lex, parse, validate, buildDAG, plan)
    # Pipeline with try/catch              →  // Monadic composition with auto error propagation
```

---

## Module Structure

```
hekat-dsl/
├── package.json
├── tsconfig.json
├── src/
│   ├── types/                    # Core types & ADTs
│   │   ├── Token.ts             # TokenType enum, Token type
│   │   ├── AST.ts               # ExpressionNode ADT (7 variants)
│   │   ├── DAG.ts               # DAGNode, DAG, Phase
│   │   └── ExecutionPlan.ts     # Final output types
│   │
│   ├── lexer/
│   │   ├── Lexer.ts             # State<string, Token[]>
│   │   └── Lexer.test.ts
│   │
│   ├── parser/
│   │   ├── Parser.ts            # Either<ParseError, QueryNode>
│   │   └── Parser.test.ts
│   │
│   ├── typechecker/
│   │   ├── TypeChecker.ts       # Validation<ValidAST>
│   │   └── TypeChecker.test.ts
│   │
│   ├── dag/
│   │   ├── DAGBuilder.ts        # Reader<Config, DAG>
│   │   └── DAGBuilder.test.ts
│   │
│   ├── compiler/
│   │   ├── Compiler.ts          # Main pipeline orchestrator
│   │   └── Compiler.test.ts
│   │
│   ├── executor/
│   │   ├── HEKATExecutor.ts     # TaskEither<Error, Result>
│   │   └── HEKATExecutor.test.ts
│   │
│   ├── plugin/
│   │   ├── ClaudeCodePlugin.ts  # Claude Code integration layer
│   │   └── manifest.json
│   │
│   └── index.ts                 # Public API exports
│
├── examples/
│   ├── basic.ts
│   ├── parallel.ts
│   └── ensemble.ts
│
└── docs/
    ├── API.md
    ├── DESIGN.md
    └── EXAMPLES.md
```

---

## Type System Design

### 1. Token Types (Lexer)

```typescript
// types/Token.ts
import { Enum } from '@effect/data/Enum'

export const TokenType = Enum.make<{
  // Identifiers
  IDENTIFIER: 'IDENTIFIER',

  // Operators
  COLON: 'COLON',           // :
  PLUS: 'PLUS',             // +
  ARROW: 'ARROW',           // ->
  PIPE: 'PIPE',             // ||
  QUESTION: 'QUESTION',     // ?
  SEMICOLON: 'SEMICOLON',   // ;
  CARET: 'CARET',           // ^

  // Grouping
  LPAREN: 'LPAREN',         // (
  RPAREN: 'RPAREN',         // )

  // Literals
  STRING: 'STRING',
  NUMBER: 'NUMBER',

  // Special
  AT: 'AT',                 // @
  EOF: 'EOF'
}>()

export type TokenType = typeof TokenType.Type

export type Token = {
  readonly type: TokenType
  readonly value: unknown
  readonly position: number
}
```

### 2. AST Types (Parser)

```typescript
// types/AST.ts
import { Data } from '@effect/data/Data'

// Algebraic Data Type (ADT) for expressions
export type ExpressionNode =
  | SimpleNode
  | SequentialNode
  | ParallelNode
  | FallbackNode
  | EnsembleNode
  | CommandedNode
  | SkilledNode

// Tagged union variants
export interface SimpleNode extends Data.Case {
  readonly _tag: 'Simple'
  readonly name: string
}

export interface SequentialNode extends Data.Case {
  readonly _tag: 'Sequential'
  readonly steps: ReadonlyArray<ExpressionNode>
}

export interface ParallelNode extends Data.Case {
  readonly _tag: 'Parallel'
  readonly branches: ReadonlyArray<ExpressionNode>
}

export interface FallbackNode extends Data.Case {
  readonly _tag: 'Fallback'
  readonly alternatives: ReadonlyArray<ExpressionNode>
}

export interface EnsembleNode extends Data.Case {
  readonly _tag: 'Ensemble'
  readonly base: string
  readonly count: number
  readonly mergeStep: string
  readonly synthStep: string
}

export interface CommandedNode extends Data.Case {
  readonly _tag: 'Commanded'
  readonly command: string
  readonly agents: ReadonlyArray<string>
}

export interface SkilledNode extends Data.Case {
  readonly _tag: 'Skilled'
  readonly agent: string
  readonly skills: ReadonlyArray<string>
}

// Query node (complete AST)
export interface QueryNode {
  readonly expression: ExpressionNode
  readonly prompt: string
}

// Constructors
export const Simple = Data.tagged<SimpleNode>('Simple')
export const Sequential = Data.tagged<SequentialNode>('Sequential')
export const Parallel = Data.tagged<ParallelNode>('Parallel')
export const Fallback = Data.tagged<FallbackNode>('Fallback')
export const Ensemble = Data.tagged<EnsembleNode>('Ensemble')
export const Commanded = Data.tagged<CommandedNode>('Commanded')
export const Skilled = Data.tagged<SkilledNode>('Skilled')
```

### 3. DAG Types

```typescript
// types/DAG.ts
import { Data } from '@effect/data/Data'
import { ExpressionNode } from './AST'

export interface DAGNode {
  readonly id: number
  readonly expr: ExpressionNode
  readonly dependencies: ReadonlySet<number>
  readonly isFallback: boolean
  readonly fallbackOf: Option<number>
}

export interface DAG {
  readonly nodes: ReadonlyMap<number, DAGNode>
  readonly executionOrder: ReadonlyArray<number>
  readonly parallelPhases: ReadonlyMap<number, ReadonlyArray<number>>
}
```

### 4. Execution Plan Types

```typescript
// types/ExecutionPlan.ts
export interface Phase {
  readonly num: number
  readonly agents: ReadonlyArray<string>
  readonly tokenBudget: number
  readonly canParallelize: boolean
  readonly skills: ReadonlyArray<string>
}

export interface ExecutionPlan {
  readonly patternType: string
  readonly complexityLevel: string  // L1-L7
  readonly phases: ReadonlyArray<Phase>
  readonly totalTokens: number
  readonly prompt: string
  readonly metadata: {
    readonly totalAgents: number
    readonly executionDepth: number
    readonly hasParallelism: boolean
    readonly hasFallback: boolean
  }
}
```

---

## Compiler Pipeline

### Main Compilation Flow

```typescript
// compiler/Compiler.ts
import * as E from 'fp-ts/Either'
import * as TE from 'fp-ts/TaskEither'
import { pipe } from 'fp-ts/function'
import { Lexer } from '../lexer/Lexer'
import { Parser } from '../parser/Parser'
import { TypeChecker } from '../typechecker/TypeChecker'
import { DAGBuilder } from '../dag/DAGBuilder'
import { ExecutionPlan } from '../types/ExecutionPlan'

export type CompileError =
  | { readonly _tag: 'LexerError'; readonly message: string; readonly position: number }
  | { readonly _tag: 'ParseError'; readonly message: string; readonly position: number }
  | { readonly _tag: 'ValidationError'; readonly errors: ReadonlyArray<string> }
  | { readonly _tag: 'DAGBuildError'; readonly message: string }

export const compile = (
  dslString: string
): E.Either<CompileError, ExecutionPlan> =>
  pipe(
    // 1. Lex
    dslString,
    Lexer.tokenize,
    E.mapLeft((err): CompileError => ({
      _tag: 'LexerError',
      message: err.message,
      position: err.position
    })),

    // 2. Parse
    E.flatMap(tokens =>
      pipe(
        Parser.parse(tokens),
        E.mapLeft((err): CompileError => ({
          _tag: 'ParseError',
          message: err.message,
          position: err.token.position
        }))
      )
    ),

    // 3. Type Check
    E.flatMap(ast =>
      pipe(
        TypeChecker.validate(ast),
        E.mapLeft((errors): CompileError => ({
          _tag: 'ValidationError',
          errors
        }))
      )
    ),

    // 4. Build DAG
    E.flatMap(validAst =>
      pipe(
        DAGBuilder.build(validAst.expression),
        E.mapLeft((err): CompileError => ({
          _tag: 'DAGBuildError',
          message: err.message
        }))
      )
    ),

    // 5. Generate Plan
    E.map(dag => generateExecutionPlan(dag, validAst))
  )
```

---

## Lexer Implementation

### State Monad for Scanning

```typescript
// lexer/Lexer.ts
import * as S from 'fp-ts/State'
import * as E from 'fp-ts/Either'
import * as A from 'fp-ts/Array'
import { pipe } from 'fp-ts/function'
import { Token, TokenType } from '../types/Token'

type LexerState = {
  readonly input: string
  readonly position: number
  readonly tokens: ReadonlyArray<Token>
}

type LexerError = {
  readonly message: string
  readonly position: number
  readonly context: string
}

type LexerResult = E.Either<LexerError, ReadonlyArray<Token>>

// State monad operations
const currentChar: S.State<LexerState, string> = S.gets(
  state => state.input[state.position] ?? ''
)

const advance: S.State<LexerState, void> = S.modify(
  state => ({ ...state, position: state.position + 1 })
)

const addToken = (token: Token): S.State<LexerState, void> =>
  S.modify(state => ({
    ...state,
    tokens: [...state.tokens, token]
  }))

// Tokenizer combinators
const skipWhitespace: S.State<LexerState, void> = pipe(
  currentChar,
  S.flatMap(char =>
    char && /\s/.test(char)
      ? pipe(advance, S.flatMap(() => skipWhitespace))
      : S.of(undefined)
  )
)

const readString: S.State<LexerState, E.Either<LexerError, Token>> = pipe(
  S.Do,
  S.bind('startPos', () => S.gets(s => s.position)),
  S.bind('quote', () => currentChar),
  S.chainFirst(() => advance), // Skip opening quote
  S.bind('value', () => readStringChars),
  S.flatMap(({ startPos, quote, value }) =>
    pipe(
      currentChar,
      S.flatMap(char =>
        char === quote
          ? pipe(
              advance,
              S.map(() =>
                E.right({
                  type: TokenType.STRING,
                  value,
                  position: startPos
                })
              )
            )
          : S.of(
              E.left({
                message: `Unterminated string`,
                position: startPos,
                context: ''
              })
            )
      )
    )
  )
)

// Main tokenize function
export const tokenize = (
  input: string
): E.Either<LexerError, ReadonlyArray<Token>> => {
  const initialState: LexerState = {
    input,
    position: 0,
    tokens: []
  }

  const tokenizeLoop: S.State<
    LexerState,
    E.Either<LexerError, void>
  > = pipe(
    S.gets((s: LexerState) => s.position < s.input.length),
    S.flatMap(hasMore =>
      hasMore
        ? pipe(
            skipWhitespace,
            S.flatMap(() => tokenizeOne),
            S.flatMap(result =>
              E.isLeft(result)
                ? S.of(result)
                : tokenizeLoop
            )
          )
        : S.of(E.right(undefined))
    )
  )

  const [finalState, result] = tokenizeLoop(initialState)

  return pipe(
    result,
    E.map(() => [
      ...finalState.tokens,
      { type: TokenType.EOF, value: null, position: finalState.position }
    ])
  )
}
```

---

## Parser Implementation

### Either Monad for Error Handling

```typescript
// parser/Parser.ts
import * as E from 'fp-ts/Either'
import * as A from 'fp-ts/Array'
import { pipe } from 'fp-ts/function'
import { Token, TokenType } from '../types/Token'
import { ExpressionNode, QueryNode, Simple, Sequential } from '../types/AST'

type ParseError = {
  readonly message: string
  readonly token: Token
}

type ParserState = {
  readonly tokens: ReadonlyArray<Token>
  readonly position: number
}

type Parser<A> = (state: ParserState) => E.Either<ParseError, [A, ParserState]>

// Parser combinators
const current: Parser<Token> = state =>
  E.right([state.tokens[state.position], state])

const advance: Parser<void> = state =>
  E.right([undefined, { ...state, position: state.position + 1 }])

const expect = (tokenType: TokenType): Parser<Token> =>
  pipe(
    current,
    E.flatMap(([token, state]) =>
      token.type === tokenType
        ? pipe(
            advance(state),
            E.map(([_, nextState]) => [token, nextState])
          )
        : E.left({
            message: `Expected ${tokenType}, got ${token.type}`,
            token
          })
    )
  )

// Recursive descent parsers
const parseSimple: Parser<ExpressionNode> = pipe(
  expect(TokenType.IDENTIFIER),
  E.map(([token, state]) => [Simple({ name: token.value as string }), state])
)

const parseSequential: Parser<ExpressionNode> = state => {
  const parseStep = parseParallelOrAtom

  return pipe(
    parseStep(state),
    E.flatMap(([firstStep, state1]) => {
      const steps: ExpressionNode[] = [firstStep]
      let currentState = state1

      while (currentState.tokens[currentState.position]?.type === TokenType.ARROW) {
        const result = pipe(
          advance(currentState),
          E.flatMap(([_, state2]) => parseStep(state2))
        )

        if (E.isLeft(result)) return result

        const [step, nextState] = result.right
        steps.push(step)
        currentState = nextState
      }

      return E.right([
        steps.length === 1
          ? steps[0]
          : Sequential({ steps }),
        currentState
      ])
    })
  )
}

// Main parse function
export const parse = (
  tokens: ReadonlyArray<Token>
): E.Either<ParseError, QueryNode> => {
  const initialState: ParserState = { tokens, position: 0 }

  return pipe(
    parseExpression(initialState),
    E.flatMap(([expression, state1]) =>
      pipe(
        expect(TokenType.COLON)(state1),
        E.flatMap(([_, state2]) =>
          pipe(
            expect(TokenType.STRING)(state2),
            E.flatMap(([promptToken, state3]) =>
              pipe(
                expect(TokenType.EOF)(state3),
                E.map(() => ({
                  expression,
                  prompt: promptToken.value as string
                }))
              )
            )
          )
        )
      )
    )
  )
}
```

---

## Type Checker Implementation

### Validation Applicative

```typescript
// typechecker/TypeChecker.ts
import * as E from 'fp-ts/Either'
import * as A from 'fp-ts/Array'
import * as NEA from 'fp-ts/NonEmptyArray'
import { pipe } from 'fp-ts/function'
import { sequenceT } from 'fp-ts/Apply'
import { QueryNode, ExpressionNode } from '../types/AST'

type ValidationError = string
type Validation<A> = E.Either<NEA.NonEmptyArray<ValidationError>, A>

// Applicative instance for accumulating errors
const getValidationApplicative = () => ({
  ...E.Applicative,
  ap: <A, B>(
    fab: Validation<(a: A) => B>,
    fa: Validation<A>
  ): Validation<B> =>
    pipe(
      fab,
      E.fold(
        errorsF =>
          pipe(
            fa,
            E.fold(
              errorsA => E.left(NEA.concat(errorsF)(errorsA)),
              () => E.left(errorsF)
            )
          ),
        f =>
          pipe(
            fa,
            E.map(f)
          )
      )
    )
})

// Validation functions
const validateAgentExists = (
  name: string,
  agents: ReadonlySet<string>
): Validation<string> =>
  agents.has(name)
    ? E.right(name)
    : E.left(NEA.of(`Agent '${name}' not found`))

const validateExpression = (
  expr: ExpressionNode,
  config: Config
): Validation<ExpressionNode> => {
  // Pattern match on expression type
  switch (expr._tag) {
    case 'Simple':
      return pipe(
        validateAgentExists(expr.name, config.agents),
        E.map(() => expr)
      )

    case 'Sequential':
      return pipe(
        expr.steps,
        A.traverse(getValidationApplicative())(step =>
          validateExpression(step, config)
        ),
        E.map(() => expr)
      )

    case 'Parallel':
      return pipe(
        expr.branches,
        A.traverse(getValidationApplicative())(branch =>
          validateExpression(branch, config)
        ),
        E.map(() => expr)
      )

    // ... other cases
  }
}

export const validate = (
  ast: QueryNode
): Validation<QueryNode> =>
  pipe(
    sequenceT(getValidationApplicative())(
      validateExpression(ast.expression, config),
      validatePromptNotEmpty(ast.prompt)
    ),
    E.map(() => ast)
  )
```

---

## Executor Implementation

### TaskEither for Async Orchestration

```typescript
// executor/HEKATExecutor.ts
import * as TE from 'fp-ts/TaskEither'
import * as T from 'fp-ts/Task'
import * as A from 'fp-ts/Array'
import { pipe } from 'fp-ts/function'
import { ExecutionPlan, Phase } from '../types/ExecutionPlan'

type ExecutionError =
  | { readonly _tag: 'AgentExecutionError'; readonly message: string }
  | { readonly _tag: 'TimeoutError'; readonly phase: number }
  | { readonly _tag: 'FallbackExhausted'; readonly attempts: number }

type ExecutionResult = {
  readonly output: string
  readonly tokensUsed: number
  readonly duration: number
}

// Execute single agent
const executeAgent = (
  agent: string,
  prompt: string,
  tokenBudget: number
): TE.TaskEither<ExecutionError, ExecutionResult> =>
  TE.tryCatch(
    async () => {
      // Call Claude Code Task API
      const result = await claudeCodeAPI.runAgent({
        agent,
        prompt,
        tokenBudget
      })

      return {
        output: result.output,
        tokensUsed: result.tokensUsed,
        duration: result.duration
      }
    },
    (reason): ExecutionError => ({
      _tag: 'AgentExecutionError',
      message: String(reason)
    })
  )

// Execute phase (parallel or sequential)
const executePhase = (
  phase: Phase,
  prompt: string
): TE.TaskEither<ExecutionError, ReadonlyArray<ExecutionResult>> =>
  phase.canParallelize
    ? // Parallel execution
      pipe(
        phase.agents,
        A.traverse(TE.ApplicativePar)(agent =>
          executeAgent(agent, prompt, phase.tokenBudget)
        )
      )
    : // Sequential execution
      pipe(
        phase.agents,
        A.traverse(TE.ApplicativeSeq)(agent =>
          executeAgent(agent, prompt, phase.tokenBudget)
        )
      )

// Execute entire plan
export const executePlan = (
  plan: ExecutionPlan
): TE.TaskEither<ExecutionError, ReadonlyArray<ExecutionResult>> =>
  pipe(
    plan.phases,
    A.reduce(
      TE.right<ExecutionError, ReadonlyArray<ExecutionResult>>([]),
      (prevResults, phase) =>
        pipe(
          prevResults,
          TE.flatMap(results =>
            pipe(
              executePhase(phase, plan.prompt),
              TE.map(phaseResults => [...results, ...phaseResults])
            )
          )
        )
    )
  )

// Execute with fallback support
export const executePlanWithFallback = (
  plan: ExecutionPlan,
  maxRetries: number = 3
): TE.TaskEither<ExecutionError, ExecutionResult> => {
  const retry = (n: number): TE.TaskEither<ExecutionError, ExecutionResult> =>
    pipe(
      executePlan(plan),
      TE.flatMap(results => TE.right(results[results.length - 1])),
      TE.orElse(error =>
        n > 0
          ? pipe(
              T.delay(1000)(T.of(undefined)),
              TE.fromTask,
              TE.flatMap(() => retry(n - 1))
            )
          : TE.left({ _tag: 'FallbackExhausted', attempts: maxRetries })
      )
    )

  return retry(maxRetries)
}
```

---

## Claude Code Plugin Integration

```typescript
// plugin/ClaudeCodePlugin.ts
import { compile } from '../compiler/Compiler'
import { executePlan } from '../executor/HEKATExecutor'
import * as E from 'fp-ts/Either'
import * as TE from 'fp-ts/TaskEither'
import { pipe } from 'fp-ts/function'

export interface ClaudeCodePlugin {
  readonly name: string
  readonly version: string
  readonly commands: Record<string, Command>
}

type Command = (args: string[]) => TE.TaskEither<Error, string>

const hekatCommand: Command = args =>
  pipe(
    // Parse DSL string from args
    E.fromNullable(new Error('No DSL string provided'))(args[0]),

    // Compile to execution plan
    TE.fromEither,
    TE.flatMap(dslString =>
      pipe(
        compile(dslString),
        E.mapLeft(err => new Error(`Compilation failed: ${JSON.stringify(err)}`)),
        TE.fromEither
      )
    ),

    // Execute plan
    TE.flatMap(plan =>
      pipe(
        executePlan(plan),
        TE.mapLeft(err => new Error(`Execution failed: ${JSON.stringify(err)}`)),
        TE.map(results =>
          results.map(r => r.output).join('\n\n')
        )
      )
    )
  )

export const plugin: ClaudeCodePlugin = {
  name: 'hekat-dsl',
  version: '1.0.0',
  commands: {
    hekat: hekatCommand
  }
}
```

---

## Testing Strategy

### Property-Based Testing with fast-check

```typescript
// lexer/Lexer.test.ts
import * as fc from 'fast-check'
import { tokenize } from './Lexer'
import * as E from 'fp-ts/Either'

describe('Lexer', () => {
  // Property: tokenizing valid DSL never throws
  it('tokenize always returns Either', () => {
    fc.assert(
      fc.property(fc.string(), input => {
        const result = tokenize(input)
        expect(E.isLeft(result) || E.isRight(result)).toBe(true)
      })
    )
  })

  // Property: tokenizing then detokenizing preserves meaning
  it('lex(unlex(tokens)) === tokens', () => {
    fc.assert(
      fc.property(
        fc.array(tokenArb),
        tokens => {
          const str = untokenize(tokens)
          const result = tokenize(str)
          expect(E.getOrElse(() => [])(result)).toEqual(tokens)
        }
      )
    )
  })

  // Unit tests
  it('tokenizes simple agent invocation', () => {
    const result = tokenize('agent : "prompt"')
    expect(result).toEqual(
      E.right([
        { type: 'IDENTIFIER', value: 'agent', position: 0 },
        { type: 'COLON', value: ':', position: 6 },
        { type: 'STRING', value: 'prompt', position: 8 },
        { type: 'EOF', value: null, position: 16 }
      ])
    )
  })
})
```

---

## Migration Timeline

### Week 1: Core Compiler

**Days 1-2**: Setup & Type System
- ✅ Initialize TypeScript project
- ✅ Configure tsconfig, fp-ts, fast-check
- ✅ Define types (Token, AST, DAG, ExecutionPlan)
- ✅ Create ADT constructors with `@effect/data`

**Days 3-4**: Lexer & Parser
- ✅ Port Lexer with State monad
- ✅ Port Parser with Either monad
- ✅ Write unit tests + property tests

**Days 5-7**: Type Checker & DAG Builder
- ✅ Port TypeChecker with Validation applicative
- ✅ Port DAGBuilder with Reader monad
- ✅ Integration tests for full compiler pipeline

### Week 2: Executor & Integration

**Days 1-3**: HEKATExecutor
- ✅ Build TaskEither-based executor
- ✅ Parallel vs sequential execution
- ✅ Fallback & retry logic
- ✅ Token budget management

**Days 4-5**: Claude Code Plugin
- ✅ Create plugin manifest
- ✅ Integrate with Claude Code Task API
- ✅ Command interface (`/hekat`)

**Days 6-7**: Testing & Polish
- ✅ End-to-end tests
- ✅ Performance benchmarks
- ✅ Error message polish

### Week 3: Documentation & Release

**Days 1-2**: Documentation
- ✅ API reference
- ✅ User guide with examples
- ✅ Migration guide (Python → fp-ts)

**Days 3-4**: Beta Testing
- ✅ Internal dogfooding
- ✅ Bug fixes
- ✅ Performance tuning

**Days 5-7**: Release Preparation
- ✅ Publish to npm
- ✅ Create Claude Code plugin package
- ✅ Release announcement

---

## Success Metrics

### Quality Gates

| Metric | Target |
|--------|--------|
| Type Coverage | 100% |
| Test Coverage | ≥ 90% |
| Property Tests | ≥ 20 properties |
| Compilation Speed | < 100ms for L1-L5 queries |
| Execution Overhead | < 50ms vs direct Task calls |

### Performance Benchmarks

```typescript
// benchmark/compiler.bench.ts
import Benchmark from 'benchmark'
import { compile } from '../src/compiler/Compiler'

const suite = new Benchmark.Suite()

suite
  .add('L1: Simple agent', () => {
    compile('agent : "prompt"')
  })
  .add('L3: Parallel', () => {
    compile('(agent1 || agent2 || agent3) : "prompt"')
  })
  .add('L5: Sequential + Parallel', () => {
    compile('agent1 -> (agent2 || agent3) -> agent4 : "prompt"')
  })
  .on('cycle', (event: any) => {
    console.log(String(event.target))
  })
  .run()
```

---

## Next Steps

**Immediate**:
1. ✅ Review this spec
2. ✅ Get approval on fp-ts approach
3. ✅ Start Week 1 implementation

**After Beta**:
4. Gather user feedback
5. Iterate on DSL ergonomics
6. Add L6-L7 advanced features (probabilistic, comonadic)

---

## References

- **fp-ts Documentation**: https://gcanti.github.io/fp-ts/
- **Effect-TS Ecosystem**: https://effect.website/
- **Python Implementation**: `/Users/manu/Documents/LUXOR/PROJECTS/hekat/`
- **Language Analysis**: `/tmp/HEKAT-IMPLEMENTATION-LANGUAGE-ANALYSIS.md`
- **Comonadic Synthesis**: `/tmp/COMONADIC-EXTRACT-FINAL.md`

---

**Status**: 🎯 Ready for implementation
**Next**: Create project scaffold and start Week 1
