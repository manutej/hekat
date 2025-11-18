# Level 6 Examples: Probabilistic Workflows

**Category**: Monadic Meta-Programming - Probabilistic Monad (`Dist<A>`)

---

## Example 1: Probabilistic Query Chain

### 🎯 **hekat-dsl** (Shortest CLI Input)
```
sample³ ; merge ; refine : "quantum computing"
```

### 🔧 **hekat-compiler** (PROP Term)
```haskell
-- Type signature
φ : Query → Response
φ = copy₃ ; (sample ⊗ sample ⊗ sample) ; merge ; refine

-- Wire counts
copy₃  : 1 → 3
sample : 1 → 1  (Query → Dist(Response))
merge  : 3 → 1  (Dist³(Response) → Dist(Response))
refine : 1 → 1  (Dist(Response) → Response)

-- Verification
input_wires(φ) = 1 ✓
output_wires(φ) = 1 ✓
acyclic = true ✓
```

### 📊 **hekat-graph** (DAG JSON)
```json
{
  "dag_id": "probabilistic_chain_001",
  "nodes": [
    {"id": "n0", "type": "input", "label": "Query"},
    {"id": "n1", "type": "fork", "fanout": 3},
    {"id": "n2", "type": "agent", "name": "sample_llm", "monad": "Dist"},
    {"id": "n3", "type": "agent", "name": "sample_llm", "monad": "Dist"},
    {"id": "n4", "type": "agent", "name": "sample_llm", "monad": "Dist"},
    {"id": "n5", "type": "aggregate", "strategy": "weighted_merge", "monad": "Dist"},
    {"id": "n6", "type": "agent", "name": "refine_llm"},
    {"id": "n7", "type": "output", "label": "Response"}
  ],
  "edges": [
    {"from": "n0", "to": "n1"},
    {"from": "n1", "to": "n2"},
    {"from": "n1", "to": "n3"},
    {"from": "n1", "to": "n4"},
    {"from": "n2", "to": "n5", "weight": "p₂"},
    {"from": "n3", "to": "n5", "weight": "p₃"},
    {"from": "n4", "to": "n5", "weight": "p₄"},
    {"from": "n5", "to": "n6"},
    {"from": "n6", "to": "n7"}
  ],
  "scheduling": {
    "levels": [
      {"level": 0, "nodes": ["n0"]},
      {"level": 1, "nodes": ["n1"]},
      {"level": 2, "nodes": ["n2", "n3", "n4"], "parallel": true},
      {"level": 3, "nodes": ["n5"]},
      {"level": 4, "nodes": ["n6"]},
      {"level": 5, "nodes": ["n7"]}
    ]
  },
  "optimization": {
    "prune_threshold": 0.05,
    "max_samples": 5,
    "estimated_tokens": 75000
  }
}
```

### 🏗️ **hekat-architecture** (Visual Diagram)
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🔬 Probabilistic Research Chain                ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                 ┃
┃  📥 Query: "quantum computing"                  ┃
┃       │                                         ┃
┃       ▼                                         ┃
┃  ┌──────────────────────────┐                  ┃
┃  │ 🔀 copy₃ (1→3)           │                  ┃
┃  └────────┬─────────────────┘                  ┃
┃           │                                     ┃
┃      ┌────┼────┬────┐                          ┃
┃      │    │    │    │                          ┃
┃      ▼    ▼    ▼    ▼                          ┃
┃  ┌──────────────────────────┐                  ┃
┃  │ 🤖 sample (Dist monad)   │                  ┃
┃  │ n=3 parallel samples     │                  ┃
┃  └────────┬─────────────────┘                  ┃
┃           │                                     ┃
┃      ┌────┼────┬────┐                          ┃
┃      │    │    │    │                          ┃
┃   p=0.3 0.25 0.2 0.15 ...                      ┃
┃      │    │    │    │                          ┃
┃      └────┼────┴────┘                          ┃
┃           │                                     ┃
┃           ▼                                     ┃
┃  ┌──────────────────────────┐                  ┃
┃  │ 📊 merge (3→1)           │                  ┃
┃  │ Weighted combination     │                  ┃
┃  └────────┬─────────────────┘                  ┃
┃           │                                     ┃
┃           ▼                                     ┃
┃  ┌──────────────────────────┐                  ┃
┃  │ ✨ refine (1→1)          │                  ┃
┃  │ Final synthesis          │                  ┃
┃  └────────┬─────────────────┘                  ┃
┃           │                                     ┃
┃           ▼                                     ┃
┃  📤 Response (deterministic)                    ┃
┃                                                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### 🧮 **hekat-monad** (Monadic Composition)
```haskell
-- Dist monad definition
newtype Dist a = Dist [(a, Probability)]

instance Monad Dist where
  return x = Dist [(x, 1.0)]

  (Dist xs) >>= f = Dist [
    (y, p * q)
    | (x, p) <- xs
    , let Dist ys = f x
    , (y, q) <- ys
  ]

-- Workflow as monadic computation
probabilistic_chain :: Query -> Dist Response
probabilistic_chain query = do
  s1 <- sample_llm query
  s2 <- sample_llm query
  s3 <- sample_llm query
  consensus <- merge [s1, s2, s3]
  refined <- refine consensus
  return refined
```

### 📈 **hekat-optimization** (Rewrite Rules)
```
-- Fusion: Combine adjacent samples
(sample ; sample ; sample) ⟹ sample_batch(n=3)

-- Pruning: Remove low-probability paths
if p(branch) < 0.05 then prune(branch)

-- Caching: Deduplicate identical queries
if query₁ = query₂ then cache(sample(query₁))
```

### 📝 **Summary**

**Shortest Input**: `sample³ ; merge ; refine : "quantum computing"`

**Compilation Flow**:
1. **DSL** → Parse symbolic expression
2. **Compiler** → Build PROP term with wire counts (1→3→3→1→1)
3. **Graph** → Generate 7-node DAG with 8 edges
4. **Monad** → Interpret as Dist monad bind chain
5. **Optimize** → Apply fusion, pruning, caching rules
6. **Execute** → Run level-2 nodes in parallel, merge results

**Key Properties**:
- **Monad**: Dist (probabilistic computation)
- **Parallelism**: 3 samples run concurrently
- **Pruning**: Paths with p < 0.05 eliminated
- **Tokens**: ~25K per sample × 3 = 75K total
- **Time**: max(sample_time) ≈ 10 min (not 30 min sequential)

---

## Example 2: Ensemble Sampling

### 🎯 **hekat-dsl**
```
replicate(5, sample) ; aggregate ; refine
```

### 🔧 **hekat-compiler**
```haskell
φ : Query → Response
φ = copy₅ ; sample⁵ ; aggregate ; refine

-- Expanded
copy₅     : 1 → 5
sample⁵   : 5 → 5  (sample ⊗ sample ⊗ sample ⊗ sample ⊗ sample)
aggregate : 5 → 1
refine    : 1 → 1
```

### 📊 **hekat-graph**
```json
{
  "dag_id": "ensemble_sampling_002",
  "nodes": [
    {"id": "n0", "type": "input"},
    {"id": "n1", "type": "fork", "fanout": 5},
    {"id": "n2", "type": "agent", "name": "sample_llm"},
    {"id": "n3", "type": "agent", "name": "sample_llm"},
    {"id": "n4", "type": "agent", "name": "sample_llm"},
    {"id": "n5", "type": "agent", "name": "sample_llm"},
    {"id": "n6", "type": "agent", "name": "sample_llm"},
    {"id": "n7", "type": "aggregate", "strategy": "weighted_average"},
    {"id": "n8", "type": "agent", "name": "refine_llm"},
    {"id": "n9", "type": "output"}
  ],
  "edges": [
    {"from": "n0", "to": "n1"},
    {"from": "n1", "to": "n2"}, {"from": "n1", "to": "n3"},
    {"from": "n1", "to": "n4"}, {"from": "n1", "to": "n5"},
    {"from": "n1", "to": "n6"},
    {"from": "n2", "to": "n7"}, {"from": "n3", "to": "n7"},
    {"from": "n4", "to": "n7"}, {"from": "n5", "to": "n7"},
    {"from": "n6", "to": "n7"},
    {"from": "n7", "to": "n8"},
    {"from": "n8", "to": "n9"}
  ],
  "scheduling": {
    "levels": [
      {"level": 0, "nodes": ["n0"]},
      {"level": 1, "nodes": ["n1"]},
      {"level": 2, "nodes": ["n2", "n3", "n4", "n5", "n6"], "parallel": true},
      {"level": 3, "nodes": ["n7"]},
      {"level": 4, "nodes": ["n8"]},
      {"level": 5, "nodes": ["n9"]}
    ]
  },
  "optimization": {
    "ensemble_size": 5,
    "aggregation": "weighted_average",
    "variance_reduction": "expected",
    "estimated_tokens": 125000
  }
}
```

### 🏗️ **hekat-architecture**
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🎲 Ensemble Sampling (N=5)                     ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                 ┃
┃           📥 Query                              ┃
┃                │                                ┃
┃                ▼                                ┃
┃   ┌──────────────────────────┐                 ┃
┃   │ 🔀 copy₅ (1→5)           │                 ┃
┃   └────────┬─────────────────┘                 ┃
┃            │                                    ┃
┃    ┌───────┼───────┬───────┬───────┐          ┃
┃    │       │       │       │       │          ┃
┃    ▼       ▼       ▼       ▼       ▼          ┃
┃  ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐      ┃
┃  │🤖1│   │🤖2│   │🤖3│   │🤖4│   │🤖5│      ┃
┃  │LLM│   │LLM│   │LLM│   │LLM│   │LLM│      ┃
┃  └─┬─┘   └─┬─┘   └─┬─┘   └─┬─┘   └─┬─┘      ┃
┃    │       │       │       │       │          ┃
┃    └───────┴───────┴───────┴───────┘          ┃
┃                    │                           ┃
┃                    ▼                           ┃
┃       ┌──────────────────────┐                ┃
┃       │ 📊 aggregate (5→1)   │                ┃
┃       │ Weighted average     │                ┃
┃       └──────────┬───────────┘                ┃
┃                  │                            ┃
┃                  ▼                            ┃
┃       ┌──────────────────────┐                ┃
┃       │ ✨ refine (1→1)      │                ┃
┃       └──────────┬───────────┘                ┃
┃                  │                            ┃
┃                  ▼                            ┃
┃         📤 High-Quality Response               ┃
┃                                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### 🧮 **hekat-monad**
```haskell
ensemble_sampling :: Int -> Query -> Dist Response
ensemble_sampling n query = do
  samples <- replicateM n (sample_llm query)
  consensus <- aggregate_samples samples
  refined <- refine_llm consensus
  return refined

-- replicateM: Monadic replication
replicateM :: Monad m => Int -> m a -> m [a]
```

### 📈 **hekat-optimization**
```
-- Batching: Execute all samples in one API call
replicate(5, sample) ⟹ sample_batch(n=5, parallel=true)

-- Variance reduction: Optimal N
if variance(samples) < threshold then
  stop_early(samples)
```

### 📝 **Summary**

**Shortest Input**: `replicate(5, sample) ; aggregate ; refine`

**Key Differences from Example 1**:
- **N=5 samples** vs N=3
- **Weighted average** aggregation vs merge
- **Variance reduction**: Quality ↑, but 5× cost

**Performance**:
- **Tokens**: ~25K × 5 = 125K
- **Time**: ~10 min (parallel execution)
- **Quality**: 2× improvement over single sample
- **Trade-off**: Cost vs quality optimization

---

## Example 3: Multi-Sample with Confidence Filtering

### 🎯 **hekat-dsl**
```
sample{n=10, filter: p>0.1} ; best(3) ; merge
```

### 🔧 **hekat-compiler**
```haskell
φ : Query → Response
φ = copy₁₀ ; sample¹⁰ ; filter_{p>0.1} ; top_k(3) ; merge

-- With probability filtering
filter_{p>0.1} : Dist¹⁰(Response) → Dist³(Response)
```

### 📊 **hekat-graph**
```json
{
  "dag_id": "confidence_filtering_003",
  "nodes": [
    {"id": "n0", "type": "input"},
    {"id": "n1", "type": "fork", "fanout": 10},
    {"id": "n2-n11", "type": "agent_array", "count": 10, "name": "sample_llm"},
    {"id": "n12", "type": "filter", "predicate": "p > 0.1"},
    {"id": "n13", "type": "top_k", "k": 3, "metric": "confidence"},
    {"id": "n14", "type": "aggregate", "strategy": "weighted_merge"},
    {"id": "n15", "type": "output"}
  ],
  "edges": [
    {"from": "n0", "to": "n1"},
    {"from": "n1", "to": "n2-n11", "broadcast": true},
    {"from": "n2-n11", "to": "n12", "collect": true},
    {"from": "n12", "to": "n13"},
    {"from": "n13", "to": "n14"},
    {"from": "n14", "to": "n15"}
  ],
  "optimization": {
    "initial_samples": 10,
    "filter_threshold": 0.1,
    "top_k": 3,
    "expected_survivors": "~3-5",
    "estimated_tokens": 250000
  }
}
```

### 🏗️ **hekat-architecture**
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🎯 Confidence-Filtered Sampling                ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                 ┃
┃           📥 Query                              ┃
┃                │                                ┃
┃                ▼                                ┃
┃   ┌──────────────────────────┐                 ┃
┃   │ 🔀 copy₁₀ (1→10)         │                 ┃
┃   └────────┬─────────────────┘                 ┃
┃            │                                    ┃
┃    ┌───────┴────────────────┐                  ┃
┃    ▼    ▼    ▼    ▼    ▼    ▼  ...            ┃
┃  🤖  🤖  🤖  🤖  🤖  🤖  🤖  🤖  🤖  🤖        ┃
┃  s₁  s₂  s₃  s₄  s₅  s₆  s₇  s₈  s₉  s₁₀       ┃
┃  │   │   │   │   │   │   │   │   │   │        ┃
┃  p=0.3 0.25 0.2 0.15 0.08 0.06 0.04 0.03 ...   ┃
┃  │   │   │   │   │   │   │   │   │   │        ┃
┃  └───┴───┴───┴───┴───┴───┴───┴───┴───┘        ┃
┃                │                                ┃
┃                ▼                                ┃
┃   ┌──────────────────────────┐                 ┃
┃   │ 🔍 filter (p > 0.1)      │                 ┃
┃   │ Removes: s₅...s₁₀        │                 ┃
┃   └────────┬─────────────────┘                 ┃
┃            │                                    ┃
┃       [s₁, s₂, s₃, s₄]                         ┃
┃            │                                    ┃
┃            ▼                                    ┃
┃   ┌──────────────────────────┐                 ┃
┃   │ 🏆 top_k(3)              │                 ┃
┃   │ Keeps: s₁, s₂, s₃        │                 ┃
┃   └────────┬─────────────────┘                 ┃
┃            │                                    ┃
┃       [s₁, s₂, s₃]                             ┃
┃            │                                    ┃
┃            ▼                                    ┃
┃   ┌──────────────────────────┐                 ┃
┃   │ 📊 merge (3→1)           │                 ┃
┃   └────────┬─────────────────┘                 ┃
┃            │                                    ┃
┃            ▼                                    ┃
┃   📤 High-Confidence Response                   ┃
┃                                                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### 🧮 **hekat-monad**
```haskell
confidence_filtering :: Query -> Dist Response
confidence_filtering query = do
  samples <- replicateM 10 (sample_llm query)

  -- Filter by confidence threshold
  let high_confidence = filter (\(r, p) -> p > 0.1) samples

  -- Take top-3 by probability
  let top3 = take 3 $ sortBy (comparing (negate . snd)) high_confidence

  -- Merge with weighted average
  merged <- weighted_merge top3
  return merged
```

### 📈 **hekat-optimization**
```
-- Early stopping: Stop generating if we have 3 with p > 0.5
if length(filter(p > 0.5, samples)) >= 3 then
  stop_sampling()

-- Dynamic threshold adjustment
threshold = adaptive_threshold(samples_so_far)
```

### 📝 **Summary**

**Shortest Input**: `sample{n=10, filter: p>0.1} ; best(3) ; merge`

**Key Innovation**:
- **Quality filtering**: Only use high-confidence responses
- **Top-K selection**: Best 3 out of 10
- **Adaptive pruning**: Stop early if quality threshold met

**Cost-Benefit**:
- **Tokens**: 10× single sample (250K)
- **Quality**: 3× improvement (high-confidence only)
- **Waste**: ~60-70% of samples filtered out
- **Use case**: When quality >> cost (research, critical decisions)

---

