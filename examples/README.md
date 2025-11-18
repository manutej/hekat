# Hekat DSL Level 6 Examples

This directory contains comprehensive examples showing the **full layered interpretation** of Level 6 monadic workflows, from shortest CLI input to complete execution architecture.

---

## 📁 **Example Categories**

### **1. Probabilistic Workflows** (`level6-examples-probabilistic.md`)
**Monad**: `Dist<A>` (Probability Distribution)

Examples:
- **Probabilistic Query Chain**: `sample³ ; merge ; refine`
- **Ensemble Sampling**: `replicate(5, sample) ; aggregate ; refine`
- **Confidence Filtering**: `sample{n=10, filter: p>0.1} ; best(3) ; merge`

**Use Cases**: Non-deterministic LLM outputs, quality optimization, variance reduction

---

### **2. Error Handling & Fallback** (`level6-examples-error-handling.md`)
**Monads**: `Maybe<A>`, `Either<E, A>`

Examples:
- **Simple Fallback Chain**: `primary ? secondary ? tertiary`
- **Typed Error Handling**: `validate -> process !> rollback`
- **Retry with Backoff**: `retry(3, backoff=exp) { risky_operation }`

**Use Cases**: High-availability systems, graceful degradation, resilience

---

### **3. State Management** (`level6-examples-state.md`) [TODO]
**Monad**: `State<S, A>`

Examples:
- Stateful Conversation
- Context Accumulation
- Multi-Turn Dialog

**Use Cases**: Conversational AI, session management, history tracking

---

### **4. Context-Aware Pipelines** (`level6-examples-context.md`) [TODO]
**Monad**: `Reader<Env, A>`

Examples:
- Global Configuration
- Dependency Injection
- Environment Propagation

**Use Cases**: Configuration management, shared context, read-only state

---

### **5. Lazy Evaluation** (`level6-examples-lazy.md`) [TODO]
**Monad**: `Lazy<A>`

Examples:
- Deferred Computation
- Conditional Execution
- Caching Strategies

**Use Cases**: Performance optimization, pay-as-you-go computation

---

### **6. Multi-Response** (`level6-examples-list.md`) [TODO]
**Monad**: `List<A>`

Examples:
- Voting Mechanisms
- Consensus Building
- Parallel Aggregation

**Use Cases**: Multi-agent systems, ensemble methods

---

## 📊 **Layered Interpretation Structure**

Each example provides **7 layers** of interpretation:

### **Layer 1: hekat-dsl** (Shortest CLI Input)
- **Minimal keystrokes** representing the workflow
- Pure mathematical symbolic notation
- Example: `sample³ ; merge ; refine : "quantum computing"`

### **Layer 2: hekat-compiler** (PROP Term)
- Algebraic encoding with **wire counts**
- Type signatures and verification
- Example: `copy₃ ; (sample ⊗ sample ⊗ sample) ; merge : 1→3→3→1→1`

### **Layer 3: hekat-graph** (DAG JSON)
- Complete **executable graph** representation
- Nodes, edges, scheduling levels
- Optimization metadata

### **Layer 4: hekat-architecture** (Visual Diagram)
- **Emoji-enhanced ASCII art**
- Box-drawing characters
- Intuitive flow visualization

### **Layer 5: hekat-monad** (Monadic Composition)
- **Haskell-style** do-notation
- Explicit bind operations
- Monad laws and properties

### **Layer 6: hekat-optimization** (Rewrite Rules)
- **Graph optimization** passes
- Fusion, pruning, caching
- Performance transformations

### **Layer 7: Summary** (High-Level Explanation)
- **What it does** in plain language
- Key properties and trade-offs
- Use cases and performance metrics

---

## 🎯 **Quick Navigation**

| Workflow Type | Monad | Shortest Syntax | Example File |
|---------------|-------|----------------|--------------|
| **Probabilistic** | `Dist` | `sample³ ; merge` | [probabilistic.md](level6-examples-probabilistic.md) |
| **Error Handling** | `Maybe/Either` | `primary ? secondary` | [error-handling.md](level6-examples-error-handling.md) |
| **Stateful** | `State` | `get ; process ; put` | state.md [TODO] |
| **Context** | `Reader` | `ask ; compute` | context.md [TODO] |
| **Lazy** | `Lazy` | `defer ; force` | lazy.md [TODO] |
| **Multi-Response** | `List` | `vote ; consensus` | list.md [TODO] |

---

## 🔬 **Mathematical Foundations**

### **Category Theory**
- **Objects**: Types (Query, Response, Error, etc.)
- **Morphisms**: Agents (functions between types)
- **Composition**: Sequential `(;)` and Parallel `(⊗)`
- **Identity**: `id : A → A`

### **Monad Laws**
All examples satisfy the three monad laws:

1. **Left Identity**: `return a >>= f ≡ f a`
2. **Right Identity**: `m >>= return ≡ m`
3. **Associativity**: `(m >>= f) >>= g ≡ m >>= (λx → f x >>= g)`

### **PROP (Product and Permutation) Category**
- **Objects**: ℕ (wire counts)
- **Morphisms**: `f : m → n` (m input wires, n output wires)
- **Tensor**: `f ⊗ g : (m+p) → (n+q)`
- **Composition**: `f ; g : m → p` (when `output(f) = input(g)`)

---

## 🚀 **Usage Examples**

### **Running a Workflow**

```bash
# CLI invocation
$ hekat run "sample³ ; merge ; refine" --input "quantum computing"

# Compiles to:
# 1. Parse symbolic expression
# 2. Build PROP term
# 3. Generate DAG
# 4. Optimize graph
# 5. Execute with scheduler

# Output:
# ✓ Compilation successful
# ✓ DAG generated (7 nodes, 8 edges)
# ✓ Optimization: fused 3 samples into batch
# ⚡ Executing level-2 (parallel)...
# ✓ Completed in 12.3s (75K tokens)
```

### **Viewing Intermediate Representations**

```bash
# Show PROP term
$ hekat compile "sample³ ; merge" --show-prop
copy₃ ; (sample ⊗ sample ⊗ sample) ; merge : 1 → 1

# Show DAG JSON
$ hekat compile "sample³ ; merge" --show-dag > workflow.json

# Show architecture diagram
$ hekat compile "sample³ ; merge" --show-arch
```

### **Optimization Passes**

```bash
# Enable specific optimizations
$ hekat run "sample³" --optimize=fusion,pruning,caching

# Optimization report
Fusion:   3 samples → 1 batched call (3× speedup)
Pruning:  Removed 4 low-probability paths (<0.05)
Caching:  Deduplicated 2 identical subgraphs
```

---

## 📚 **Learning Path**

1. **Start with Probabilistic** (`level6-examples-probabilistic.md`)
   - Simplest monad to understand
   - Visual probability distributions
   - Clear performance trade-offs

2. **Move to Error Handling** (`level6-examples-error-handling.md`)
   - Practical reliability patterns
   - Maybe/Either monads
   - Railway-oriented programming

3. **Explore State Management** (TODO)
   - Conversational workflows
   - History tracking
   - State threading

4. **Advanced: Monad Transformers** (Future)
   - Combining multiple effects
   - `StateT + DistT + Maybe`
   - Complex real-world scenarios

---

## 🔗 **Related Documentation**

- **Level 6 Specification**: [../docs/DSL-COMPLEXITY-LEVELS.md](../docs/DSL-COMPLEXITY-LEVELS.md)
- **Formal Encodings**: [../docs/FORMAL-SYMBOLIC-ENCODINGS-WORKFLOW-DSLS.md](../docs/FORMAL-SYMBOLIC-ENCODINGS-WORKFLOW-DSLS.md)
- **Markov Categories**: [../docs/MARKOV-CATEGORIES-PROBABILISTIC-ORCHESTRATION.md](../docs/MARKOV-CATEGORIES-PROBABILISTIC-ORCHESTRATION.md)
- **Comonads**: [../docs/COMONADS-LLM-ORCHESTRATION-ANALYSIS.md](../docs/COMONADS-LLM-ORCHESTRATION-ANALYSIS.md)

---

## 🤝 **Contributing Examples**

To add a new example:

1. Choose the appropriate monad category
2. Follow the 7-layer structure:
   - hekat-dsl (shortest input)
   - hekat-compiler (PROP term)
   - hekat-graph (DAG JSON)
   - hekat-architecture (visual diagram)
   - hekat-monad (Haskell-style)
   - hekat-optimization (rewrite rules)
   - Summary (explanation)
3. Include emoji-enhanced ASCII diagrams
4. Provide performance metrics
5. Add to the category index

---

## 📊 **Example Statistics**

```
Total Examples: 6 (across 2 categories, 4 TODO)
Total Layers: 7 per example
Diagrams: Emoji-enhanced ASCII art
Code Examples: Haskell, JSON, DSL syntax

Current Coverage:
✅ Probabilistic (3 examples)
✅ Error Handling (3 examples)
⏳ State Management (TODO)
⏳ Context-Aware (TODO)
⏳ Lazy Evaluation (TODO)
⏳ Multi-Response (TODO)
```

---

**The examples demonstrate that Hekat DSL provides the shortest possible syntax while maintaining complete mathematical rigor and full traceability through all compilation layers.**
