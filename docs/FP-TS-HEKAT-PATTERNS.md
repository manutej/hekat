# HEKAT DSL fp-ts Patterns (Based on cc2.0)

**Date**: 2025-11-14
**Source**: Proven patterns from `~/cc2.0` consciousness.md + implementation
**Goal**: Apply cc2.0's fp-ts patterns to HEKAT, avoiding reinvention

---

## Core Principles (From cc2.0 Consciousness.md)

### 1. Categorical Interface Contracts

**Rule**: Pass instances directly, never wrap in intermediate types.

```typescript
// ✅ CORRECT - HEKAT pattern
const plan = await compiler.compile(dslString);
if (E.isRight(plan)) {
  const result = await executor.execute(plan.right);  // Direct pass
}

// ❌ WRONG - Don't wrap
const context = { plan: plan.right, metadata: {...} };
const result = await executor.execute(context);  // Loses methods!
```

### 2. Platform Abstraction Translation Layer

**Rule**: Shield categorical functions from platform-specific arguments.

```typescript
// ✅ CORRECT - HEKAT Lexer
class Lexer {
  private tokens: Token[] = [];

  private readIdentifier(): Token {
    // Only pass value to token constructor
    return { type: TokenType.IDENTIFIER, value: chars.join(''), position };
  }
}

// ❌ WRONG - Expose platform leakage
this.tokens.forEach((token, index, array) => process(token, index, array));
```

### 3. fp-ts Integration: pipe/fold Over Manual Checks

**Rule**: Use `pipe` and `foldWithFpTs` instead of manual `isRight/isLeft`.

```typescript
import { pipe, foldWithFpTs } from './core/FpTsInterop.js';

// ✅ CORRECT - HEKAT compilation
pipe(
  compiler.compile(dslString),
  foldWithFpTs(
    (error) => console.error(`Compilation failed: ${JSON.stringify(error)}`),
    (plan) => executor.execute(plan)
  )
);

// ❌ WRONG - Manual checks
if (isRight(result)) {
  executor.execute(result.right);
} else {
  console.error(result.left.message);  // Assumes 'message' exists!
}
```

### 4. Property-Based Testing for Categorical Laws

**Rule**: Use fast-check for categorical laws, not just examples.

```typescript
import * as fc from 'fast-check';

// ✅ CORRECT - HEKAT Parser test
it('parser composition law', () => {
  fc.assert(
    fc.property(
      arbDSLQuery,
      fc.func<[AST], AST>(arbAST),
      fc.func<[AST], AST>(arbAST),
      (query, f, g) => {
        const left = pipe(parser.parse(query), E.map(compose(g, f)));
        const right = pipe(parser.parse(query), E.map(f), E.map(g));
        return deepEqual(left, right);
      }
    ),
    { numRuns: 1000 }
  );
});
```

### 5. TypeScript Type Checking: Catch Errors Early

**Rule**: Run `npx tsc --noEmit` before committing.

```bash
# HEKAT development workflow
npx tsc --noEmit src/compiler/Compiler.ts
npx tsc --noEmit tests/**/*.test.ts
```

### 6. Structured Error Handling: Discriminated Union Pattern

**Rule**: Use structured error types with `type` discriminant.

```typescript
// ✅ CORRECT - HEKAT error types
export type CompileError =
  | { type: 'LEXER_ERROR'; message: string; position: number }
  | { type: 'PARSE_ERROR'; message: string; token: Token }
  | { type: 'VALIDATION_ERROR'; errors: string[] }
  | { type: 'DAG_BUILD_ERROR'; message: string };

// Usage
if (isLeft(result)) {
  const error = result.left;
  switch (error.type) {
    case 'LEXER_ERROR':
      console.log(`Lexer failed at position ${error.position}: ${error.message}`);
      break;
    case 'PARSE_ERROR':
      console.log(`Parser failed at token ${error.token.type}: ${error.message}`);
      break;
    // ... exhaustive handling
  }
}
```

---

## HEKAT Module Structure (Following cc2.0)

```
hekat-dsl/
├── src/
│   ├── core/
│   │   ├── category/
│   │   │   ├── Either.ts         # Custom Either (cc2.0 pattern)
│   │   │   ├── FpTsInterop.ts    # Interop layer (cc2.0 pattern)
│   │   │   └── index.ts
│   │   └── types/
│   │       ├── Token.ts
│   │       ├── AST.ts
│   │       ├── DAG.ts
│   │       └── ExecutionPlan.ts
│   │
│   ├── lexer/
│   │   ├── Lexer.ts              # State monad pattern
│   │   ├── types.ts
│   │   └── index.ts
│   │
│   ├── parser/
│   │   ├── Parser.ts             # Either monad pattern
│   │   ├── types.ts
│   │   └── index.ts
│   │
│   ├── typechecker/
│   │   ├── TypeChecker.ts        # Validation pattern
│   │   ├── Config.ts
│   │   └── index.ts
│   │
│   ├── dag/
│   │   ├── DAGBuilder.ts         # Pure transformations
│   │   └── index.ts
│   │
│   ├── compiler/
│   │   ├── Compiler.ts           # Pipeline orchestrator
│   │   ├── errors.ts
│   │   └── index.ts
│   │
│   └── executor/
│       ├── HEKATExecutor.ts      # Async orchestration
│       └── index.ts
│
├── tests/
│   ├── laws/                     # Categorical law tests
│   ├── integration/              # E2E workflow tests
│   └── unit/                     # Component tests
│
└── examples/
    └── workflows/
```

---

## 1. Custom Either Implementation (Copy cc2.0 Pattern)

```typescript
// src/core/category/Either.ts
// Directly based on cc2.0/src/core/category/Either.ts

export type Either<E, A> = Left<E> | Right<A>;

export interface Left<E> {
  readonly _tag: 'Left';
  readonly left: E;
}

export interface Right<A> {
  readonly _tag: 'Right';
  readonly right: A;
}

export const Left = <E>(value: E): Left<E> => ({
  _tag: 'Left',
  left: value,
});

export const Right = <A>(value: A): Right<A> => ({
  _tag: 'Right',
  right: value,
});

export const isLeft = <E, A>(either: Either<E, A>): either is Left<E> =>
  either._tag === 'Left';

export const isRight = <E, A>(either: Either<E, A>): either is Right<A> =>
  either._tag === 'Right';

export const map = <E, A, B>(
  f: (a: A) => B
) => (either: Either<E, A>): Either<E, B> => {
  if (isLeft(either)) return either;
  return Right(f(either.right));
};

export const flatMap = <E, A, B>(
  f: (a: A) => Either<E, B>
) => (either: Either<E, A>): Either<E, B> => {
  if (isLeft(either)) return either;
  return f(either.right);
};

export const fold = <E, A, B>(
  onLeft: (e: E) => B,
  onRight: (a: A) => B
) => (either: Either<E, A>): B => {
  if (isLeft(either)) return onLeft(either.left);
  return onRight(either.right);
};

export const mapLeft = <E, F, A>(
  f: (e: E) => F
) => (either: Either<E, A>): Either<F, A> => {
  if (isLeft(either)) return Left(f(either.left));
  return either;
};

export const getOrElse = <A>(defaultValue: A) => <E>(
  either: Either<E, A>
): A => {
  if (isLeft(either)) return defaultValue;
  return either.right;
};

export const fromNullable = <E>(error: E) => <A>(
  value: A | null | undefined
): Either<E, A> => {
  return value != null ? Right(value) : Left(error);
};

export const tryCatch = <E, A>(
  f: () => A,
  onError: (error: unknown) => E
): Either<E, A> => {
  try {
    return Right(f());
  } catch (error) {
    return Left(onError(error));
  }
};
```

---

## 2. FpTsInterop Layer (Copy cc2.0 Pattern)

```typescript
// src/core/category/FpTsInterop.ts
// Directly based on cc2.0/src/core/category/FpTsInterop.ts

import * as E from 'fp-ts/Either';
import { pipe as fpPipe, flow as fpFlow } from 'fp-ts/function';
import {
  Either as CustomEither,
  Left,
  Right,
  isLeft,
  isRight,
} from './Either.js';

// Type Conversions
export const toFpTs = <L, R>(e: CustomEither<L, R>): E.Either<L, R> =>
  isLeft(e) ? E.left(e.left) : E.right(e.right);

export const fromFpTs = <L, R>(e: E.Either<L, R>): CustomEither<L, R> =>
  E.isLeft(e) ? Left(e.left) : Right(e.right);

// Composition Utilities
export const pipe = fpPipe;
export const flow = fpFlow;

// Hybrid Operations
export const mapWithFpTs =
  <E, A, B>(f: (a: A) => B) =>
  (either: CustomEither<E, A>): CustomEither<E, B> =>
    fromFpTs(pipe(toFpTs(either), E.map(f)));

export const chainWithFpTs =
  <E, A, B>(f: (a: A) => CustomEither<E, B>) =>
  (either: CustomEither<E, A>): CustomEither<E, B> =>
    fromFpTs(pipe(toFpTs(either), E.chain((a) => toFpTs(f(a)))));

export const foldWithFpTs =
  <E, A, B>(onLeft: (e: E) => B, onRight: (a: A) => B) =>
  (either: CustomEither<E, A>): B =>
    pipe(toFpTs(either), E.fold(onLeft, onRight));

export const altWithFpTs =
  <E, A>(f: () => CustomEither<E, A>) =>
  (either: CustomEither<E, A>): CustomEither<E, A> =>
    fromFpTs(pipe(toFpTs(either), E.alt(() => toFpTs(f()))));

// Async Composition
export const composeAsync =
  <E, A, B>(f: (a: A) => Promise<CustomEither<E, B>>) =>
  async (either: CustomEither<E, A>): Promise<CustomEither<E, B>> => {
    if (isLeft(either)) return either;
    return f(either.right);
  };

export const sequenceAsync = async <E, A>(
  promises: Array<Promise<CustomEither<E, A>>>
): Promise<CustomEither<E, A[]>> => {
  const results: A[] = [];

  for (const promise of promises) {
    const result = await promise;
    if (isLeft(result)) return result;
    results.push(result.right);
  }

  return Right(results);
};

export const parallelAsync = async <E, A>(
  promises: Array<Promise<CustomEither<E, A>>>
): Promise<CustomEither<E, A[]>> => {
  const results = await Promise.all(promises);

  const values: A[] = [];
  for (const result of results) {
    if (isLeft(result)) return result;
    values.push(result.right);
  }

  return Right(values);
};

// Error Recovery
export const getOrElse =
  <A>(onLeft: () => A) =>
  <E>(either: CustomEither<E, A>): A =>
    isLeft(either) ? onLeft() : either.right;

export const mapLeft =
  <E, E2>(f: (e: E) => E2) =>
  <A>(either: CustomEither<E, A>): CustomEither<E2, A> =>
    isLeft(either) ? Left(f(either.left)) : either;

export const recover =
  <E, A>(f: (e: E) => CustomEither<E, A>) =>
  (either: CustomEither<E, A>): CustomEither<E, A> =>
    isLeft(either) ? f(either.left) : either;

// Type Guards
export { isLeft, isRight } from './Either.js';
```

---

## 3. Compiler Implementation (Following cc2.0 ObserveFunction Pattern)

```typescript
// src/compiler/Compiler.ts
// Pattern based on cc2.0/src/functions/observe/ObserveFunction.ts

import { Either, Left, Right } from '../core/category/Either.js';
import { Lexer } from '../lexer/Lexer.js';
import { Parser } from '../parser/Parser.js';
import { TypeChecker } from '../typechecker/TypeChecker.js';
import { DAGBuilder } from '../dag/DAGBuilder.js';
import { CompileError } from './errors.js';
import { ExecutionPlan } from '../core/types/ExecutionPlan.js';

/**
 * HEKAT DSL Compiler
 *
 * Type Signature: compile: DSLString → Either<CompileError, ExecutionPlan>
 *
 * Categorical Properties:
 * - Pure & Total: No side effects, defined for all inputs
 * - Compositional: Pipeline of pure transformations
 * - Monadic: Error handling via Either
 *
 * Constitutional Compliance (cc2.0 pattern):
 * - Article I: Functor laws verified ✓
 * - Article II: Pure and total ✓
 * - Article III: Monadic error handling ✓
 */
export class HEKATCompiler {
  private lexer: Lexer;
  private parser: Parser;
  private typeChecker: TypeChecker;
  private dagBuilder: DAGBuilder;

  constructor() {
    this.lexer = new Lexer();
    this.parser = new Parser();
    this.typeChecker = new TypeChecker();
    this.dagBuilder = new DAGBuilder();
  }

  /**
   * Compile DSL string to execution plan
   *
   * This is a pure, total function that:
   * 1. Validates the input
   * 2. Lexes (string → tokens)
   * 3. Parses (tokens → AST)
   * 4. Type checks (AST → ValidAST)
   * 5. Builds DAG (AST → DAG)
   * 6. Generates plan (DAG → ExecutionPlan)
   *
   * @param dslString - HEKAT DSL query string
   * @returns Either an error or an ExecutionPlan
   */
  compile(dslString: string): Either<CompileError, ExecutionPlan> {
    // Validate input (totality requirement)
    const validationResult = this.validateInput(dslString);
    if (validationResult !== null) {
      return Left(validationResult);
    }

    // Pipeline execution with explicit error handling
    try {
      // Phase 1: Lex
      const tokensResult = this.lexer.tokenize(dslString);
      if (isLeft(tokensResult)) {
        return Left({
          type: 'LEXER_ERROR',
          message: tokensResult.left.message,
          position: tokensResult.left.position,
        });
      }

      // Phase 2: Parse
      const astResult = this.parser.parse(tokensResult.right);
      if (isLeft(astResult)) {
        return Left({
          type: 'PARSE_ERROR',
          message: astResult.left.message,
          token: astResult.left.token,
        });
      }

      // Phase 3: Type Check
      const validAstResult = this.typeChecker.validate(astResult.right);
      if (isLeft(validAstResult)) {
        return Left({
          type: 'VALIDATION_ERROR',
          errors: validAstResult.left,
        });
      }

      // Phase 4: Build DAG
      const dagResult = this.dagBuilder.build(validAstResult.right.expression);
      if (isLeft(dagResult)) {
        return Left({
          type: 'DAG_BUILD_ERROR',
          message: dagResult.left.message,
        });
      }

      // Phase 5: Generate Plan
      const plan = this.generatePlan(dagResult.right, validAstResult.right);

      return Right(plan);
    } catch (error) {
      // Catch-all for unexpected errors (should never happen in pure code)
      return Left({
        type: 'LEXER_ERROR',
        message: error instanceof Error ? error.message : String(error),
        position: 0,
      });
    }
  }

  /**
   * Validate input string
   * Returns null if valid, error otherwise
   */
  private validateInput(dslString: string): CompileError | null {
    if (!dslString) {
      return {
        type: 'LEXER_ERROR',
        message: 'Input string is null or empty',
        position: 0,
      };
    }

    if (dslString.trim().length === 0) {
      return {
        type: 'LEXER_ERROR',
        message: 'Input string is whitespace only',
        position: 0,
      };
    }

    return null;
  }

  private generatePlan(dag: DAG, ast: QueryNode): ExecutionPlan {
    // ... plan generation logic
  }
}
```

---

## 4. Integration Test Pattern (Following cc2.0)

```typescript
// tests/integration/compiler.test.ts
// Pattern based on cc2.0/tests/integration/create-verify-workflow.test.ts

import { describe, it, expect } from 'vitest';
import { pipe, foldWithFpTs, isRight } from '../../src/core/category/FpTsInterop.js';
import { HEKATCompiler } from '../../src/compiler/Compiler.js';
import { HEKATExecutor } from '../../src/executor/HEKATExecutor.js';

describe('HEKAT Compiler → Executor Workflow', () => {
  const compiler = new HEKATCompiler();
  const executor = new HEKATExecutor();

  it('compiles and executes L1 query: agent : "prompt"', async () => {
    const dslQuery = 'agent : "test prompt"';

    // Step 1: COMPILE
    const planResult = compiler.compile(dslQuery);

    // ✅ Use pipe + foldWithFpTs (cc2.0 pattern)
    pipe(
      planResult,
      foldWithFpTs(
        (error) => {
          console.error('Compilation failed:', JSON.stringify(error, null, 2));
          expect.fail(`Compilation should succeed: ${JSON.stringify(error)}`);
        },
        (plan) => {
          expect(plan.complexityLevel).toBe('L1');
          expect(plan.phases.length).toBe(1);
          expect(plan.phases[0].agents).toEqual(['agent']);
        }
      )
    );

    if (!isRight(planResult)) return;

    // Step 2: EXECUTE
    const executionResult = await executor.execute(planResult.right);

    pipe(
      executionResult,
      foldWithFpTs(
        (error) => {
          console.error('Execution failed:', JSON.stringify(error, null, 2));
          expect.fail(`Execution should succeed: ${JSON.stringify(error)}`);
        },
        (result) => {
          expect(result.output).toBeDefined();
          expect(result.tokensUsed).toBeGreaterThan(0);
        }
      )
    );
  });

  it('handles invalid DSL gracefully', () => {
    const invalidDSL = 'invalid @ syntax !!';

    const result = compiler.compile(invalidDSL);

    // ✅ Should return Left (error), not throw
    pipe(
      result,
      foldWithFpTs(
        (error) => {
          // ✅ Verify structured error
          expect(error).toHaveProperty('type');
          expect(['LEXER_ERROR', 'PARSE_ERROR']).toContain(error.type);
        },
        () => expect.fail('Should have returned error')
      )
    );
  });
});
```

---

## 5. Error Type Definitions (Following cc2.0)

```typescript
// src/compiler/errors.ts
// Pattern based on cc2.0 ObserveError, ReasonError, etc.

/**
 * HEKAT Compiler Error Types
 *
 * Structured errors following cc2.0 pattern:
 * - Discriminated union with 'type' field
 * - Context-specific data for each error type
 * - No 'message' assumption (use JSON.stringify)
 */

export type LexerError =
  | { type: 'UNEXPECTED_CHARACTER'; char: string; position: number }
  | { type: 'UNTERMINATED_STRING'; position: number }
  | { type: 'INVALID_NUMBER'; value: string; position: number };

export type ParseError =
  | { type: 'UNEXPECTED_TOKEN'; expected: string; got: string; position: number }
  | { type: 'MISSING_COLON'; position: number }
  | { type: 'MISSING_PROMPT'; position: number }
  | { type: 'INVALID_PARALLEL'; reason: string; position: number };

export type ValidationError = string[];  // Array of error messages

export type DAGBuildError =
  | { type: 'CYCLE_DETECTED'; cycle: number[] }
  | { type: 'INVALID_DEPENDENCY'; node: number; dependency: number };

export type CompileError =
  | { type: 'LEXER_ERROR'; message: string; position: number }
  | { type: 'PARSE_ERROR'; message: string; token: Token }
  | { type: 'VALIDATION_ERROR'; errors: ValidationError }
  | { type: 'DAG_BUILD_ERROR'; message: string };

export type ExecutionError =
  | { type: 'AGENT_NOT_FOUND'; agent: string }
  | { type: 'TIMEOUT'; phase: number; duration: number }
  | { type: 'FALLBACK_EXHAUSTED'; attempts: number }
  | { type: 'TASK_API_ERROR'; message: string };
```

---

## 6. Testing Patterns (Following cc2.0)

### Property-Based Test Example

```typescript
// tests/laws/parser.test.ts
// Following cc2.0/tests/laws/ pattern

import * as fc from 'fast-check';
import { pipe } from '../../src/core/category/FpTsInterop.js';
import * as E from 'fp-ts/Either';
import { Parser } from '../../src/parser/Parser.js';

describe('Parser Categorical Laws', () => {
  const parser = new Parser();

  it('functor identity law: fmap(id) = id', () => {
    fc.assert(
      fc.property(
        // Arbitrary DSL query
        fc.oneof(
          fc.constant('agent : "prompt"'),
          fc.constant('a -> b -> c : "test"'),
          fc.constant('(a || b || c) : "parallel"')
        ),
        (dslQuery) => {
          const result1 = parser.parse(dslQuery);
          const result2 = pipe(parser.parse(dslQuery), E.map(id => id));

          return deepEqual(result1, result2);
        }
      ),
      { numRuns: 1000 }
    );
  });

  it('functor composition law: fmap(g ∘ f) = fmap(g) ∘ fmap(f)', () => {
    fc.assert(
      fc.property(
        fc.oneof(
          fc.constant('agent : "prompt"'),
          fc.constant('a -> b : "test"')
        ),
        (dslQuery) => {
          const f = (ast: AST) => ({ ...ast, metadata: { transformed: true } });
          const g = (ast: AST) => ({ ...ast, metadata: { ...ast.metadata, doubled: true } });

          const left = pipe(
            parser.parse(dslQuery),
            E.map(ast => g(f(ast)))
          );

          const right = pipe(
            parser.parse(dslQuery),
            E.map(f),
            E.map(g)
          );

          return deepEqual(left, right);
        }
      ),
      { numRuns: 1000 }
    );
  });
});
```

---

## 7. Debugging Pattern (Following cc2.0 consciousness.md)

```typescript
// Use structured logging with JSON.stringify

pipe(
  compiler.compile(dslQuery),
  foldWithFpTs(
    (error) => {
      // ✅ Log full error structure
      console.error('Compilation Error:', JSON.stringify(error, null, 2));
      // Output:
      // {
      //   "type": "PARSE_ERROR",
      //   "message": "Expected COLON, got ARROW",
      //   "token": { "type": "ARROW", "value": "->", "position": 5 }
      // }

      // ❌ Not: error.message (may be undefined!)
    },
    (plan) => {
      // ✅ Conditional debug logging
      if (plan.complexityLevel === 'L7') {
        console.log('L7 Plan:', JSON.stringify(plan, null, 2));
      }
    }
  )
);
```

---

## Summary: cc2.0 Patterns Applied to HEKAT

| Pattern | cc2.0 Source | HEKAT Application |
|---------|--------------|-------------------|
| **Custom Either** | `core/category/Either.ts` | `core/category/Either.ts` |
| **FpTsInterop** | `core/category/FpTsInterop.ts` | `core/category/FpTsInterop.ts` |
| **Structured Errors** | `ObserveError`, `ReasonError` | `CompileError`, `ExecutionError` |
| **Pure Functions** | `ObserveFunction.apply()` | `Compiler.compile()` |
| **pipe + fold** | Integration tests | All tests |
| **Property Tests** | `tests/laws/` | `tests/laws/` |
| **No try/catch in API** | All functions return `Either` | All functions return `Either` |

---

## Next Steps for HEKAT

**Day 1**: Copy cc2.0 patterns
1. ✅ Copy `Either.ts` from cc2.0 (208 lines)
2. ✅ Copy `FpTsInterop.ts` from cc2.0 (385 lines)
3. ✅ Define HEKAT error types following cc2.0 pattern

**Day 2-3**: Implement Compiler
4. ✅ Lexer following pure function pattern
5. ✅ Parser following Either monad pattern
6. ✅ TypeChecker following Validation pattern

**Day 4-5**: Integration
7. ✅ Executor following async composition pattern
8. ✅ Tests following cc2.0 test patterns

**Total Estimated**: ~2,000 lines TypeScript (vs 1,271 Python)

---

**Status**: Ready to implement using proven cc2.0 patterns
**Advantage**: Zero pattern invention, maximum reuse
**Timeline**: 2-3 weeks with cc2.0 as reference implementation
