# Level 6 Examples: Error Handling & Fallback

**Category**: Monadic Meta-Programming - Maybe/Either Monads

---

## Example 1: Simple Fallback Chain

### 🎯 **hekat-dsl**
```
primary ? secondary ? tertiary
```

### 🔧 **hekat-compiler**
```haskell
φ : Query → Maybe Response
φ = try(primary) `orElse` try(secondary) `orElse` try(tertiary)

-- Maybe monad
try       : Agent → (Query → Maybe Response)
orElse    : Maybe a → Maybe a → Maybe a
Nothing `orElse` x = x
Just y  `orElse` _ = Just y
```

### 📊 **hekat-graph**
```json
{
  "dag_id": "fallback_chain_001",
  "nodes": [
    {"id": "n0", "type": "input"},
    {"id": "n1", "type": "agent", "name": "gpt4", "fallible": true},
    {"id": "n2", "type": "decision", "condition": "is_success(n1)"},
    {"id": "n3", "type": "agent", "name": "claude", "fallible": true},
    {"id": "n4", "type": "decision", "condition": "is_success(n3)"},
    {"id": "n5", "type": "agent", "name": "gemini", "fallible": true},
    {"id": "n6", "type": "merge", "strategy": "first_success"},
    {"id": "n7", "type": "output"}
  ],
  "edges": [
    {"from": "n0", "to": "n1"},
    {"from": "n1", "to": "n2"},
    {"from": "n2", "to": "n6", "condition": "success", "label": "Just(r)"},
    {"from": "n2", "to": "n3", "condition": "failure", "label": "Nothing"},
    {"from": "n3", "to": "n4"},
    {"from": "n4", "to": "n6", "condition": "success"},
    {"from": "n4", "to": "n5", "condition": "failure"},
    {"from": "n5", "to": "n6"},
    {"from": "n6", "to": "n7"}
  ],
  "optimization": {
    "short_circuit": true,
    "max_retries": 3,
    "expected_success_rate": 0.95
  }
}
```

### 🏗️ **hekat-architecture**
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🛡️ Fallback Chain (Maybe Monad)                ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                 ┃
┃           📥 Query                              ┃
┃                │                                ┃
┃                ▼                                ┃
┃   ┌─────────────────────────┐                  ┃
┃   │ 🎯 try(primary)         │                  ┃
┃   │    GPT-4                │                  ┃
┃   └──────────┬──────────────┘                  ┃
┃              │                                  ┃
┃         ┌────┴────┐                            ┃
┃         │         │                            ┃
┃    ✅ Just(r)  ❌ Nothing                       ┃
┃         │         │                            ┃
┃         │         ▼                            ┃
┃         │   ┌─────────────────────────┐       ┃
┃         │   │ 🔄 try(secondary)       │       ┃
┃         │   │    Claude               │       ┃
┃         │   └──────────┬──────────────┘       ┃
┃         │              │                       ┃
┃         │         ┌────┴────┐                  ┃
┃         │         │         │                  ┃
┃         │    ✅ Just(r)  ❌ Nothing             ┃
┃         │         │         │                  ┃
┃         │         │         ▼                  ┃
┃         │         │   ┌─────────────────────┐ ┃
┃         │         │   │ 🆘 try(tertiary)   │ ┃
┃         │         │   │    Gemini          │ ┃
┃         │         │   └──────────┬─────────┘ ┃
┃         │         │              │           ┃
┃         │         │         ┌────┴────┐      ┃
┃         │         │         │         │      ┃
┃         │         │    ✅ Just(r) ❌ Nothing  ┃
┃         │         │         │         │      ┃
┃         └─────────┴─────────┴─────────┘      ┃
┃                       │                       ┃
┃                       ▼                       ┃
┃              📤 First Success                 ┃
┃                                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### 🧮 **hekat-monad**
```haskell
fallback_chain :: Query -> Maybe Response
fallback_chain query =
  try_primary query <|> try_secondary query <|> try_tertiary query

-- Alternative operator (<|>)
(<|>) :: Maybe a -> Maybe a -> Maybe a
Just x  <|> _ = Just x
Nothing <|> y = y

-- Monadic do-notation
fallback_chain' query = do
  result <- try_primary query
  case result of
    Just r  -> return r
    Nothing -> do
      result' <- try_secondary query
      case result' of
        Just r  -> return r
        Nothing -> try_tertiary query
```

### 📈 **hekat-optimization**
```
-- Short-circuit: Stop at first success
if is_just(result) then
  skip_remaining_fallbacks()

-- Timeout per attempt
timeout(try_agent, max_time=30s)
```

### 📝 **Summary**

**Shortest Input**: `primary ? secondary ? tertiary`

**Semantics**:
- `?` = "or else" operator (Maybe monad alternative)
- Short-circuits on first success
- Returns `Nothing` only if all fail

**Performance**:
- **Best case**: 1 attempt (primary succeeds)
- **Worst case**: 3 attempts (all tried)
- **Average**: 1.15 attempts (if 85% success rate)

**Use case**: High-availability systems, graceful degradation

---

## Example 2: Typed Error Handling

### 🎯 **hekat-dsl**
```
validate -> process !> rollback
```

### 🔧 **hekat-compiler**
```haskell
φ : Query → Either Error Response
φ = validate `bind` process `catch` rollback

-- Either monad
validate : Query → Either ValidationError ValidQuery
process  : ValidQuery → Either ProcessError Response
rollback : Error → Response

-- Bind for Either
(>>=) :: Either e a -> (a -> Either e b) -> Either e b
Left e  >>= _ = Left e
Right x >>= f = f x

-- Catch (error handler)
catch :: Either e a -> (e -> a) -> a
catch (Right x) _ = x
catch (Left e) handler = handler e
```

### 📊 **hekat-graph**
```json
{
  "dag_id": "typed_error_handling_002",
  "nodes": [
    {"id": "n0", "type": "input"},
    {"id": "n1", "type": "agent", "name": "validator", "error_type": "ValidationError"},
    {"id": "n2", "type": "decision", "condition": "is_right(n1)"},
    {"id": "n3", "type": "agent", "name": "processor", "error_type": "ProcessError"},
    {"id": "n4", "type": "decision", "condition": "is_right(n3)"},
    {"id": "n5", "type": "error_handler", "name": "rollback"},
    {"id": "n6", "type": "merge"},
    {"id": "n7", "type": "output"}
  ],
  "edges": [
    {"from": "n0", "to": "n1"},
    {"from": "n1", "to": "n2"},
    {"from": "n2", "to": "n3", "condition": "Right(valid)", "label": "Success"},
    {"from": "n2", "to": "n5", "condition": "Left(err)", "label": "ValidationError"},
    {"from": "n3", "to": "n4"},
    {"from": "n4", "to": "n6", "condition": "Right(response)"},
    {"from": "n4", "to": "n5", "condition": "Left(err)", "label": "ProcessError"},
    {"from": "n5", "to": "n6"},
    {"from": "n6", "to": "n7"}
  ],
  "error_handling": {
    "typed_errors": true,
    "error_types": ["ValidationError", "ProcessError"],
    "rollback_strategy": "safe_default"
  }
}
```

### 🏗️ **hekat-architecture**
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🧪 Typed Error Handling (Either Monad)         ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                 ┃
┃           📥 Query                              ┃
┃                │                                ┃
┃                ▼                                ┃
┃   ┌─────────────────────────┐                  ┃
┃   │ ✅ validate             │                  ┃
┃   │ Either ValErr ValidQ    │                  ┃
┃   └──────────┬──────────────┘                  ┃
┃              │                                  ┃
┃         ┌────┴────┐                            ┃
┃         │         │                            ┃
┃    Right(v)   Left(err)                        ┃
┃         │         │                            ┃
┃         │         └──────────┐                 ┃
┃         ▼                    │                 ┃
┃   ┌─────────────────────────┐│                 ┃
┃   │ ⚙️ process              ││                 ┃
┃   │ Either ProcErr Response ││                 ┃
┃   └──────────┬──────────────┘│                 ┃
┃              │                │                 ┃
┃         ┌────┴────┐           │                 ┃
┃         │         │           │                 ┃
┃    Right(r)   Left(err)       │                 ┃
┃         │         │           │                 ┃
┃         │         └───────────┼─────┐           ┃
┃         │                     │     │           ┃
┃         │                     ▼     │           ┃
┃         │         ┌─────────────────────┐      ┃
┃         │         │ 🛡️ rollback         │      ┃
┃         │         │ Error → Response    │      ┃
┃         │         └──────────┬──────────┘      ┃
┃         │                    │                 ┃
┃         └────────────────────┘                 ┃
┃                    │                           ┃
┃                    ▼                           ┃
┃           📤 Response                          ┃
┃                                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### 🧮 **hekat-monad**
```haskell
typed_error_handling :: Query -> Either Error Response
typed_error_handling query = do
  valid_query <- validate query
  result <- process valid_query
  return result
  `catch` \err -> rollback err

-- Or using bind explicitly
typed_error_handling' query =
  validate query >>= process >>= return
  `catchError` rollback
```

### 📈 **hekat-optimization**
```
-- Type-driven optimization
if error_type == ValidationError then
  early_exit(ValidationError)  -- Don't try to process

-- Error accumulation
accumulate_errors :: [Either e a] -> Either [e] [a]
```

### 📝 **Summary**

**Shortest Input**: `validate -> process !> rollback`

**Operators**:
- `->` = Sequential bind (Either monad)
- `!>` = Catch operator (error handler)

**Type Safety**:
- `ValidationError` | `ProcessError` → typed errors
- Compiler verifies all error paths handled

**Semantics**:
- **Railway-oriented programming** pattern
- Success path on "right rail"
- Error path on "left rail"
- Rollback handles all error types

---

## Example 3: Retry with Exponential Backoff

### 🎯 **hekat-dsl**
```
retry(3, backoff=exp) { risky_operation }
```

### 🔧 **hekat-compiler**
```haskell
φ : Query → Either Error Response
φ = retry_with_backoff(3, exponential, risky_operation)

-- Retry combinator
retry :: Int -> BackoffStrategy -> Agent -> (Query -> Either Error Response)
retry 0 _ agent = agent
retry n backoff agent = \q ->
  case agent q of
    Right r -> Right r
    Left err -> do
      sleep(backoff n)
      retry (n-1) backoff agent q

-- Exponential backoff
exponential :: Int -> Duration
exponential attempt = Duration (2 ^ attempt) Seconds
```

### 📊 **hekat-graph**
```json
{
  "dag_id": "retry_backoff_003",
  "nodes": [
    {"id": "n0", "type": "input"},
    {"id": "n1", "type": "agent", "name": "risky_op", "attempt": 1},
    {"id": "n2", "type": "decision", "condition": "is_success(n1)"},
    {"id": "n3", "type": "delay", "duration": "2s"},
    {"id": "n4", "type": "agent", "name": "risky_op", "attempt": 2},
    {"id": "n5", "type": "decision", "condition": "is_success(n4)"},
    {"id": "n6", "type": "delay", "duration": "4s"},
    {"id": "n7", "type": "agent", "name": "risky_op", "attempt": 3},
    {"id": "n8", "type": "decision", "condition": "is_success(n7)"},
    {"id": "n9", "type": "error", "final": true},
    {"id": "n10", "type": "merge"},
    {"id": "n11", "type": "output"}
  ],
  "edges": [
    {"from": "n0", "to": "n1"},
    {"from": "n1", "to": "n2"},
    {"from": "n2", "to": "n10", "condition": "success"},
    {"from": "n2", "to": "n3", "condition": "failure"},
    {"from": "n3", "to": "n4"},
    {"from": "n4", "to": "n5"},
    {"from": "n5", "to": "n10", "condition": "success"},
    {"from": "n5", "to": "n6", "condition": "failure"},
    {"from": "n6", "to": "n7"},
    {"from": "n7", "to": "n8"},
    {"from": "n8", "to": "n10", "condition": "success"},
    {"from": "n8", "to": "n9", "condition": "failure"},
    {"from": "n9", "to": "n10"},
    {"from": "n10", "to": "n11"}
  ],
  "retry_config": {
    "max_attempts": 3,
    "backoff_strategy": "exponential",
    "backoff_base": 2,
    "max_delay": "60s"
  }
}
```

### 🏗️ **hekat-architecture**
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🔄 Retry with Exponential Backoff              ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                 ┃
┃  📥 Query                                       ┃
┃      │                                          ┃
┃      ▼                                          ┃
┃  ┌────────────────┐                            ┃
┃  │ 🎲 Attempt 1   │                            ┃
┃  │ risky_op       │                            ┃
┃  └────────┬───────┘                            ┃
┃           │                                     ┃
┃      ┌────┴────┐                               ┃
┃      │         │                               ┃
┃   ✅ Success ❌ Failure                         ┃
┃      │         │                               ┃
┃      │         ▼                               ┃
┃      │    ⏰ Wait 2s (2^1)                     ┃
┃      │         │                               ┃
┃      │         ▼                               ┃
┃      │    ┌────────────────┐                  ┃
┃      │    │ 🎲 Attempt 2   │                  ┃
┃      │    │ risky_op       │                  ┃
┃      │    └────────┬───────┘                  ┃
┃      │             │                           ┃
┃      │        ┌────┴────┐                      ┃
┃      │        │         │                      ┃
┃      │     ✅ Success ❌ Failure                ┃
┃      │        │         │                      ┃
┃      │        │         ▼                      ┃
┃      │        │    ⏰ Wait 4s (2^2)            ┃
┃      │        │         │                      ┃
┃      │        │         ▼                      ┃
┃      │        │    ┌────────────────┐         ┃
┃      │        │    │ 🎲 Attempt 3   │         ┃
┃      │        │    │ risky_op       │         ┃
┃      │        │    └────────┬───────┘         ┃
┃      │        │             │                  ┃
┃      │        │        ┌────┴────┐             ┃
┃      │        │        │         │             ┃
┃      │        │     ✅ Success ❌ Final Failure ┃
┃      │        │        │         │             ┃
┃      └────────┴────────┴─────────┘             ┃
┃                   │                            ┃
┃                   ▼                            ┃
┃          📤 Result or Error                    ┃
┃                                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### 🧮 **hekat-monad**
```haskell
retry_with_backoff :: Int -> (Int -> Duration) -> (Query -> Either Error Response) -> Query -> Either Error Response
retry_with_backoff max_attempts backoff_fn operation = go 1
  where
    go attempt query
      | attempt > max_attempts = Left (MaxRetriesExceeded max_attempts)
      | otherwise = case operation query of
          Right result -> Right result
          Left err -> do
            sleep (backoff_fn attempt)
            go (attempt + 1) query
```

### 📈 **hekat-optimization**
```
-- Circuit breaker: Stop retrying if error is permanent
if is_permanent_error(err) then
  abort_retries()

-- Jitter: Add randomness to avoid thundering herd
backoff = base_backoff * (1 + random(0, 0.1))
```

### 📝 **Summary**

**Shortest Input**: `retry(3, backoff=exp) { risky_operation }`

**Backoff Sequence**:
- Attempt 1: immediate
- Attempt 2: wait 2s (2^1)
- Attempt 3: wait 4s (2^2)
- Attempt 4: wait 8s (2^3) [if max=4]

**Use Cases**:
- **Transient failures**: Network timeouts, rate limits
- **External API calls**: Retry on 503, 429 errors
- **Distributed systems**: Handle temporary unavailability

**Success Rate**:
- If p(success) = 0.7 per attempt
- After 3 attempts: 1 - (0.3)³ = 0.973 = 97.3% success

---
