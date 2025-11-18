# HEKAT TypeScript Implementation Specification

**Version**: 1.0.0
**Date**: 2025-11-17
**Status**: Implementation Architecture Specification

---

## 1. Overview

### 1.1 Purpose

This specification defines the TypeScript implementation architecture for HEKAT, focusing on type safety, functional programming patterns, and performance optimization. The implementation leverages `fp-ts` for categorical abstractions and maintains strict TypeScript compliance.

### 1.2 Technology Stack

```yaml
Core:
  language: TypeScript 5.x
  runtime: Node.js 20+
  paradigm: Functional (fp-ts)

Libraries:
  fp-ts: "^2.16"
  io-ts: "^2.2"  # Runtime type validation
  purify-ts: "^2.0"  # Additional FP utilities

Build:
  bundler: esbuild
  testing: vitest
  linting: biome

Type Safety:
  strict: true
  noImplicitAny: true
  strictNullChecks: true
  exactOptionalPropertyTypes: true
```

---

## 2. Core Architecture

### 2.1 Module Structure

```
hekat-ts/
├── src/
│   ├── core/               # Core abstractions
│   │   ├── types/          # Base type definitions
│   │   ├── category/       # Categorical abstractions
│   │   └── monad/          # Monadic patterns
│   │
│   ├── levels/             # L1-L7 implementations
│   │   ├── L1/            # Ultra-fast single
│   │   ├── L2/            # Fast chain
│   │   ├── L3/            # Balanced sequential
│   │   ├── L4/            # Parallel consensus
│   │   ├── L5/            # Hierarchical
│   │   ├── L6/            # Iterative
│   │   └── L7/            # Ensemble
│   │
│   ├── classifier/         # Query classification
│   │   ├── keywords/       # Keyword analysis
│   │   ├── consciousness/  # Pattern matching
│   │   └── selector/       # Level selection
│   │
│   ├── dsl/               # DSL implementation
│   │   ├── lexer/         # Tokenization
│   │   ├── parser/        # AST generation
│   │   ├── typechecker/   # Type validation
│   │   └── compiler/      # Execution plan
│   │
│   ├── executor/          # Execution engine
│   │   ├── dispatcher/    # Agent dispatch
│   │   ├── coordinator/   # Coordination patterns
│   │   └── aggregator/    # Result merging
│   │
│   ├── hotkeys/           # Hotkey system
│   │   ├── tier1/         # Single keys
│   │   ├── tier2/         # Modifiers
│   │   └── tier3/         # Chains
│   │
│   └── consciousness/     # Learning system
│       ├── storage/       # Pattern storage
│       ├── matcher/       # Similarity matching
│       └── learner/       # Pattern learning
```

### 2.2 Layered Architecture

```typescript
// Layer 1: Core Types
export namespace Core {
  export type Level = 1 | 2 | 3 | 4 | 5 | 6 | 7

  export interface Query {
    text: string
    context: Context
    constraints: Constraints
  }

  export interface Classification {
    level: Level
    confidence: number
    reasoning: string[]
    agents: Agent[]
    tokenBudget: TokenBudget
  }
}

// Layer 2: Categorical Abstractions
export namespace Category {
  export type Either<E, A> = E.Either<E, A>
  export type Task<A> = T.Task<A>
  export type TaskEither<E, A> = TE.TaskEither<E, A>
  export type Reader<R, A> = R.Reader<R, A>
  export type State<S, A> = S.State<S, A>
}

// Layer 3: Domain Logic
export namespace Domain {
  export interface Classifier {
    classify: (query: Core.Query) => Category.TaskEither<Error, Core.Classification>
  }

  export interface Executor {
    execute: (classification: Core.Classification) => Category.TaskEither<Error, Result>
  }
}
```

---

## 3. Type System Design

### 3.1 Core Types

```typescript
// Branded types for type safety
type Brand<K, T> = K & { __brand: T }

export type AgentName = Brand<string, 'AgentName'>
export type SkillName = Brand<string, 'SkillName'>
export type TokenCount = Brand<number, 'TokenCount'>

// Level-specific types
export type L1Query = Query & { level: 1 }
export type L2Query = Query & { level: 2 }
// ... etc

// Discriminated unions for coordination patterns
export type CoordinationPattern =
  | { type: 'sequential'; agents: [Agent, Agent, ...Agent[]] }
  | { type: 'parallel'; agents: Agent[] }
  | { type: 'hierarchical'; stages: Stage[] }
  | { type: 'iterative'; loop: Loop }
  | { type: 'ensemble'; groups: Group[] }

// Token budget with phantom types
export interface TokenBudget<L extends Level> {
  readonly level: L
  readonly min: TokenCount
  readonly max: TokenCount
  readonly allocated: TokenCount
}
```

### 3.2 Type Guards

```typescript
// Runtime type validation with io-ts
import * as t from 'io-ts'

const Level = t.union([
  t.literal(1),
  t.literal(2),
  t.literal(3),
  t.literal(4),
  t.literal(5),
  t.literal(6),
  t.literal(7)
])

const Query = t.type({
  text: t.string,
  context: Context,
  constraints: Constraints
})

// Type guard functions
export const isLevel = (x: unknown): x is Level =>
  Level.is(x)

export const isQuery = (x: unknown): x is Query =>
  Query.is(x)

// Refinement types
export const refineToL7 = (
  classification: Classification
): classification is Classification & { level: 7 } =>
  classification.level === 7
```

### 3.3 Dependent Types (Emulated)

```typescript
// Level-dependent token budgets
type TokenBudgetForLevel<L extends Level> =
  L extends 1 ? TokenBudget<1> :
  L extends 2 ? TokenBudget<2> :
  L extends 3 ? TokenBudget<3> :
  L extends 4 ? TokenBudget<4> :
  L extends 5 ? TokenBudget<5> :
  L extends 6 ? TokenBudget<6> :
  L extends 7 ? TokenBudget<7> :
  never

// Level-dependent agent counts
type AgentCountForLevel<L extends Level> =
  L extends 1 ? 1 :
  L extends 2 ? 2 :
  L extends 3 ? 3 :
  L extends 4 ? [2, 3] :
  L extends 5 ? [4, 5] :
  L extends 6 ? [4, 5, 6] :
  L extends 7 ? 7 | 8 | 9 | 10 :
  never
```

---

## 4. Functional Patterns

### 4.1 Monad Stack

```typescript
import { pipe } from 'fp-ts/function'
import * as RTE from 'fp-ts/ReaderTaskEither'
import * as S from 'fp-ts/State'

// Environment for Reader monad
interface HekatEnv {
  readonly config: Config
  readonly registry: AgentRegistry
  readonly consciousness: ConsciousnessDB
  readonly mcp: MCPClients
}

// Error types for Either monad
type HekatError =
  | { type: 'ParseError'; message: string }
  | { type: 'ClassificationError'; reason: string }
  | { type: 'ExecutionError'; agent: string; error: Error }
  | { type: 'TokenLimitError'; required: number; available: number }

// Main computation type
type HekatComputation<A> = RTE.ReaderTaskEither<HekatEnv, HekatError, A>

// Example computation
const classifyQuery = (query: Query): HekatComputation<Classification> =>
  pipe(
    RTE.ask<HekatEnv>(),
    RTE.chainTaskEitherK(env =>
      classifyWithKeywords(query, env.config.keywords)
    ),
    RTE.chainFirst(classification =>
      recordToConsciousness(classification)
    )
  )
```

### 4.2 Optics (Lenses & Prisms)

```typescript
import * as L from 'monocle-ts'

// Lenses for nested updates
const levelLens = L.Lens.fromProp<Classification>()('level')
const confidenceLens = L.Lens.fromProp<Classification>()('confidence')
const agentsLens = L.Lens.fromProp<Classification>()('agents')

// Prisms for sum types
const sequentialPrism = L.Prism.fromPredicate<CoordinationPattern>(
  (p): p is Sequential => p.type === 'sequential'
)

// Usage
const upgradeLevel = (classification: Classification): Classification =>
  pipe(
    classification,
    levelLens.modify(l => Math.min(7, l + 1) as Level)
  )

const extractSequential = (pattern: CoordinationPattern): Option<Sequential> =>
  sequentialPrism.getOption(pattern)
```

### 4.3 Free Monad for DSL

```typescript
// DSL as Free Monad
type DSL<A> =
  | { type: 'Agent'; name: string; next: A }
  | { type: 'Sequential'; left: DSL<A>; right: DSL<A>; next: A }
  | { type: 'Parallel'; agents: DSL<A>[]; next: A }
  | { type: 'Return'; value: A }

// Smart constructors
const agent = (name: string): Free<DSL, string> =>
  liftF({ type: 'Agent', name, next: undefined })

const sequential = <A>(left: Free<DSL, A>, right: Free<DSL, A>): Free<DSL, A> =>
  liftF({ type: 'Sequential', left, right, next: undefined })

// Interpreter
const interpret = <A>(dsl: Free<DSL, A>, env: HekatEnv): Task<A> => {
  // ... interpretation logic
}
```

---

## 5. Level Implementations

### 5.1 L1 Implementation

```typescript
// src/levels/L1/index.ts
export namespace L1 {
  export const TOKEN_BUDGET: TokenBudget<1> = {
    level: 1,
    min: 600 as TokenCount,
    max: 1200 as TokenCount,
    allocated: 0 as TokenCount
  }

  export const classify = (query: Query): TaskEither<Error, L1Query> =>
    pipe(
      validateL1Keywords(query),
      TE.chain(validateTokenBudget),
      TE.map(q => ({ ...q, level: 1 as const }))
    )

  export const execute = (query: L1Query): TaskEither<Error, Result> =>
    pipe(
      selectAgent(query),
      TE.chain(agent => dispatchAgent(agent, query)),
      TE.chain(extractResult)
    )
}
```

### 5.2 L4 Implementation (Parallel)

```typescript
// src/levels/L4/index.ts
export namespace L4 {
  export const TOKEN_BUDGET: TokenBudget<4> = {
    level: 4,
    min: 3000 as TokenCount,
    max: 6000 as TokenCount,
    allocated: 0 as TokenCount
  }

  export const execute = (query: L4Query): TaskEither<Error, Result> =>
    pipe(
      selectParallelAgents(query, 2, 3),
      TE.chain(agents =>
        TE.traverseArray(agent => dispatchAgent(agent, query))(agents)
      ),
      TE.chain(consensusMerge),
      TE.chain(extractFinalResult)
    )

  const consensusMerge = (results: Result[]): TaskEither<Error, MergedResult> =>
    pipe(
      results,
      weightByConfidence,
      findConsensus,
      TE.fromOption(() => new Error('No consensus reached'))
    )
}
```

### 5.3 L7 Implementation (Ensemble)

```typescript
// src/levels/L7/index.ts
export namespace L7 {
  export const TOKEN_BUDGET: TokenBudget<7> = {
    level: 7,
    min: 12000 as TokenCount,
    max: 22000 as TokenCount,
    allocated: 0 as TokenCount
  }

  type Stage = 'research' | 'synthesis' | 'implementation' | 'orchestration'

  export const execute = (query: L7Query): TaskEither<Error, Result> =>
    pipe(
      executeResearchStage(query),
      TE.chain(research => executeSynthesisStage(research)),
      TE.chain(synthesis => executeImplementationStage(synthesis)),
      TE.chain(implementation => executeOrchestrationStage(implementation)),
      TE.chain(extractFinalResult)
    )

  const executeResearchStage = (query: L7Query): TaskEither<Error, ResearchResult> =>
    pipe(
      selectResearchAgents(query, 3, 4),
      TE.chain(agents => parallelSample(agents, 3)),
      TE.chain(statisticalAnalysis)
    )
}
```

---

## 6. DSL Compiler Implementation

### 6.1 Lexer

```typescript
// src/dsl/lexer/index.ts
export class Lexer {
  private readonly input: string
  private position: number = 0
  private readonly tokens: Token[] = []

  tokenize(): Either<LexError, Token[]> {
    return pipe(
      S.of<LexerState, Token[]>([]),
      S.chain(() => this.scanTokens()),
      S.map(tokens => this.addEOF(tokens)),
      state => state(this.initialState()),
      ([tokens, _]) => E.right(tokens)
    )
  }

  private scanTokens(): State<LexerState, Token[]> {
    // State monad for lexer state
    return S.chain<LexerState, Token[], Token[]>(
      tokens => this.hasMore()
        ? pipe(
            this.scanToken(),
            S.map(token => [...tokens, token]),
            S.chain(this.scanTokens.bind(this))
          )
        : S.of(tokens)
    )(S.of([]))
  }
}
```

### 6.2 Parser

```typescript
// src/dsl/parser/index.ts
export class Parser {
  private tokens: Token[]
  private current: number = 0

  parse(tokens: Token[]): Either<ParseError, AST> {
    this.tokens = tokens
    this.current = 0

    return pipe(
      this.parseExpression(),
      E.chain(this.validateAST.bind(this))
    )
  }

  private parseExpression(): Either<ParseError, AST> {
    return this.parseSequential()
  }

  private parseSequential(): Either<ParseError, AST> {
    return pipe(
      this.parseParallel(),
      E.chain(left =>
        this.match(TokenType.ARROW)
          ? pipe(
              this.parseSequential(),
              E.map(right => new SequentialNode(left, right))
            )
          : E.right(left)
      )
    )
  }
}
```

### 6.3 Type Checker

```typescript
// src/dsl/typechecker/index.ts
export class TypeChecker {
  check(ast: AST): TaskEither<TypeError, TypedAST> {
    return pipe(
      this.inferTypes(ast),
      TE.chain(this.checkCompatibility.bind(this)),
      TE.chain(this.checkConstraints.bind(this))
    )
  }

  private checkCompatibility(ast: TypedAST): TaskEither<TypeError, TypedAST> {
    return pipe(
      ast,
      traverseAST(node => {
        switch (node.type) {
          case 'Sequential':
            return this.checkSequentialCompatibility(node)
          case 'Parallel':
            return this.checkParallelCompatibility(node)
          default:
            return TE.right(node)
        }
      })
    )
  }
}
```

---

## 7. Consciousness System

### 7.1 Pattern Storage

```typescript
// src/consciousness/storage/index.ts
export interface ConsciousnessPattern {
  id: PatternId
  query: string
  embedding: Vector  // Semantic embedding
  level: Level
  agents: AgentName[]
  successRate: number
  sampleCount: number
  lastUsed: Date
  tokenVariance: number
}

export class PatternStorage {
  private readonly db: Database<ConsciousnessPattern>

  store(pattern: ConsciousnessPattern): Task<void> {
    return pipe(
      this.validatePattern(pattern),
      T.chain(() => this.db.insert(pattern)),
      T.chain(() => this.updateIndex(pattern))
    )
  }

  findSimilar(query: string, threshold: number = 0.7): Task<ConsciousnessPattern[]> {
    return pipe(
      this.embed(query),
      T.chain(embedding =>
        this.db.vectorSearch(embedding, threshold)
      ),
      T.map(results => results.sort(byRecencyAndSuccess))
    )
  }
}
```

### 7.2 Learning Algorithm

```typescript
// src/consciousness/learner/index.ts
export class PatternLearner {
  learn(execution: ExecutionResult): Task<void> {
    return pipe(
      this.extractPattern(execution),
      T.chain(pattern => this.updateOrCreate(pattern)),
      T.chain(pattern => this.adjustConfidence(pattern)),
      T.chain(pattern => this.propagateToSimilar(pattern))
    )
  }

  private adjustConfidence(pattern: ConsciousnessPattern): Task<ConsciousnessPattern> {
    const newConfidence = this.calculateConfidence(
      pattern.sampleCount,
      pattern.successRate,
      pattern.tokenVariance
    )

    return T.of({
      ...pattern,
      confidence: newConfidence
    })
  }

  private calculateConfidence(samples: number, success: number, variance: number): number {
    // Bayesian confidence with variance penalty
    const base = (success * samples) / (samples + 10)
    const variancePenalty = Math.max(0, 1 - variance / 0.2)
    return base * variancePenalty
  }
}
```

---

## 8. Performance Optimizations

### 8.1 Memoization

```typescript
import memoize from 'fast-memoize'

// Memoize expensive computations
export const memoizedClassify = memoize(
  (query: Query): Classification => classify(query),
  {
    strategy: memoize.strategies.lru,
    maxSize: 100,
    serializer: JSON.stringify
  }
)

// Memoize pattern matching
export const memoizedPatternMatch = memoize(
  (query: string, patterns: ConsciousnessPattern[]): ConsciousnessPattern | null =>
    findBestMatch(query, patterns),
  {
    strategy: memoize.strategies.lru,
    maxSize: 1000
  }
)
```

### 8.2 Lazy Evaluation

```typescript
import { Lazy } from 'fp-ts/function'

// Lazy load heavy resources
export const agentRegistry: Lazy<AgentRegistry> = () => {
  if (!_registry) {
    _registry = loadAgentRegistry()
  }
  return _registry
}

// Lazy consciousness database
export const consciousnessDB: Lazy<ConsciousnessDB> = () => {
  if (!_consciousnessDB) {
    _consciousnessDB = new ConsciousnessDB({
      indexPath: '~/.hekat/consciousness.idx',
      dataPath: '~/.hekat/consciousness.db'
    })
  }
  return _consciousnessDB
}
```

### 8.3 Streaming

```typescript
import { Stream } from 'fp-ts/Stream'

// Stream large result sets
export const streamResults = <A>(
  executor: Executor,
  queries: Query[]
): Stream<TaskEither<Error, Result>> =>
  Stream.unfold<Query[], [TaskEither<Error, Result>, Query[]]>(
    queries,
    qs => qs.length > 0
      ? some([executor.execute(qs[0]), qs.slice(1)])
      : none
  )

// Stream consciousness patterns
export const streamPatterns = (
  threshold: number
): Stream<ConsciousnessPattern> =>
  consciousnessDB().streamAll({ threshold })
```

---

## 9. Testing Strategy

### 9.1 Property-Based Testing

```typescript
import * as fc from 'fast-check'

describe('Level Classification Properties', () => {
  it('should always select valid level', () => {
    fc.assert(
      fc.property(
        fc.string(),
        fc.nat({ max: 100000 }),
        (query, tokens) => {
          const result = classify({ text: query, tokens })
          return result.level >= 1 && result.level <= 7
        }
      )
    )
  })

  it('should respect token constraints', () => {
    fc.assert(
      fc.property(
        arbQuery(),
        query => {
          const classification = classify(query)
          const budget = TOKEN_BUDGETS[classification.level]
          return classification.estimatedTokens <= budget.max
        }
      )
    )
  })
})
```

### 9.2 Generative Testing

```typescript
// Generate test cases for each level
const generateL1Tests = (): TestCase[] =>
  L1_KEYWORDS.flatMap(keyword =>
    generateVariations(keyword).map(text => ({
      input: text,
      expected: 1,
      confidence: 0.8
    }))
  )

// Test all level transitions
const testLevelTransitions = () => {
  for (let from = 1; from <= 7; from++) {
    for (let to = 1; to <= 7; to++) {
      it(`should handle L${from} to L${to} transition`, () => {
        const result = transitionLevel(from as Level, to as Level)
        expect(result).toBeDefined()
      })
    }
  }
}
```

---

## 10. Build Configuration

### 10.1 TypeScript Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "lib": ["ES2022"],
    "moduleResolution": "bundler",

    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "exactOptionalPropertyTypes": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,

    "esModuleInterop": true,
    "skipLibCheck": false,
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

### 10.2 Build Pipeline

```typescript
// build.ts
import { build } from 'esbuild'

await build({
  entryPoints: ['src/index.ts'],
  bundle: true,
  minify: true,
  sourcemap: true,
  target: 'node20',
  platform: 'node',
  outfile: 'dist/hekat.js',

  // Tree shaking
  treeShaking: true,

  // Code splitting
  splitting: true,
  format: 'esm',

  // Optimizations
  pure: ['console.log'],
  drop: ['debugger'],

  // External dependencies
  external: ['fp-ts', 'io-ts']
})
```

---

## Appendix A: Type Definitions

```typescript
// Complete type definitions
export namespace Hekat {
  // Levels
  export type Level = 1 | 2 | 3 | 4 | 5 | 6 | 7

  // Core types
  export interface Query {
    text: string
    context: Context
    constraints: Constraints
  }

  export interface Classification {
    level: Level
    confidence: number
    reasoning: string[]
    agents: Agent[]
    pattern: CoordinationPattern
    tokenBudget: TokenBudget
  }

  export interface Result {
    success: boolean
    output: unknown
    metadata: Metadata
    tokens: TokenUsage
  }

  // Agent types
  export interface Agent {
    name: AgentName
    capabilities: Capability[]
    compatibleSkills: SkillName[]
  }

  // Coordination patterns
  export type CoordinationPattern =
    | Sequential
    | Parallel
    | Hierarchical
    | Iterative
    | Ensemble

  // Token management
  export interface TokenBudget {
    min: TokenCount
    max: TokenCount
    allocated: TokenCount
    consumed: TokenCount
    remaining: TokenCount
  }
}
```

---

**Document Status**: Complete Implementation Specification
**Implementation**: hekat-ts repository
**Next Steps**: Complete missing operators, add TUI interface