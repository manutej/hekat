# Phase 1-2: Query Classification & Hotkey System

## Overview

**Phase 1-2** is HEKAT's **intelligent query analysis layer**. It answers: "How complex is this query and what approach should I use?"

### Core Functions

```
Input Query: "Build a complete REST API with authentication and database"
                            ↓
Phase 1-2 Analysis: Classify → Suggest Hotkey → Plan Tokens
                            ↓
Output: "This is L7 (Full Ensemble), use Hotkey [E], budget 12,000-22,000 tokens"
```

---

## What It Does

### 1. Query Classification (L1-L7)

Analyzes user queries and classifies them into 7 complexity levels:

| Level | Name | Use Case | Budget |
|-------|------|----------|--------|
| **L1** | Ultra-Fast | Quick explanations, definitions | 600-1,200 |
| **L2** | Fast Chain | Sequential tasks, chained operations | 1,500-3,000 |
| **L3** | Balanced | Single feature implementation | 2,500-4,500 |
| **L4** | Parallel Consensus | Compare options, alternatives, evaluation | 3,000-6,000 |
| **L5** | Hierarchical | System architecture, design | 5,500-9,000 |
| **L6** | Iterative | Optimization, debugging, refinement loops | 8,000-12,000 |
| **L7** | Full Ensemble | Complete platform, from scratch | 12,000-22,000 |

**Example Classifications:**
- "Explain what REST is" → **L1** (quick explanation)
- "Design and implement a login endpoint" → **L3** (balanced feature)
- "Build a complete SaaS platform" → **L7** (full system)
- "Compare React vs Vue vs Angular" → **L4** (parallel evaluation)

### 2. Hotkey System

Suggests keyboard shortcuts for quick level selection:

```
[R]      = Research (L1)
[D]      = Design (L2)
[D>I>T]  = Design→Implement→Test (L3)
[P]      = Parallel (L4)
[Ctrl+H] = Hierarchical (L5)
[Ctrl+I] = Iterative (L6)
[Ctrl+E] = Ensemble (L7)
```

**Or explicit override:**
```
@L5     = Force L5 (manual override any level)
```

### 3. Token Budget Planning

Allocates tokens based on complexity level:

```
L1: 600-1,200 tokens
L2: 1,500-3,000 tokens
L3: 2,500-4,500 tokens
L4: 3,000-6,000 tokens
L5: 5,500-9,000 tokens
L6: 8,000-12,000 tokens
L7: 12,000-22,000 tokens
```

### 4. Confidence Scoring

Indicates how confident the classification is (0.0-1.0):

```
0.95 = Hotkey input (very confident)
0.75 = Keyword match (fairly confident)
1.00 = Explicit override @L5 (certain)
```

---

## Key Concepts

### Classification Methods

**Method 1: Explicit Override**
```python
query = "Do something @L5"
# Result: L5 with 100% confidence
```

**Method 2: Hotkey**
```python
query = "Explain REST with [R]"
# Result: L1 with 95% confidence
```

**Method 3: Keyword Matching**
```python
query = "Build a complete platform from scratch"
# Keywords: "build", "complete", "from scratch" → L7
# Result: L7 with 75% confidence
```

**Method 4: Consciousness Learning (Phase 3)**
```python
# If similar pattern from history matched successfully
# Result: L3 with 75% base + consciousness boost
```

### Confidence Ranges

```
100% = Explicit user override (@L5)
95%  = Hotkey input ([R], [D], etc.)
75%  = Keyword-based classification
0-60% = Low confidence (need more context)
```

---

## Classification Details

### L1: Ultra-Fast (Explain)

**Keywords:** "explain", "what is", "understand", "tell me", "list"

**Use cases:**
- Quick definitions and explanations
- Simple answers to questions
- Summarization
- Clarification

**Token budget:** 600-1,200 tokens

**Hotkey:** `[R]` (Research)

**Example:**
```
Q: "Explain what REST API means"
→ L1 Ultra-Fast
→ Budget: ~900 tokens
```

---

### L2: Fast Chain (Sequential)

**Keywords:** "then", "and then", "next", "followed by"

**Use cases:**
- Sequential multi-step operations
- Step-by-step instructions
- Chained tasks

**Token budget:** 1,500-3,000 tokens

**Hotkey:** `[D]` (Design)

**Example:**
```
Q: "First explain REST, then show me an example"
→ L2 Fast Chain
→ Budget: ~2,250 tokens
```

---

### L3: Balanced (Feature)

**Keywords:** "design", "implement", "test", "build feature", "develop"

**Use cases:**
- Single feature implementation
- Complete feature with tests
- Focused development task

**Token budget:** 2,500-4,500 tokens

**Hotkey:** `[D>I>T]` (Design→Implement→Test)

**Example:**
```
Q: "Implement a user login endpoint with validation and tests"
→ L3 Balanced
→ Budget: ~3,500 tokens
```

---

### L4: Parallel Consensus (Compare)

**Keywords:** "compare", "evaluate", "versus", "pros and cons", "alternatives"

**Use cases:**
- Technology evaluation
- Option comparison
- Multiple perspectives
- Benchmark analysis

**Token budget:** 3,000-6,000 tokens

**Hotkey:** `[P]` (Parallel)

**Example:**
```
Q: "Compare PostgreSQL vs MongoDB for my use case"
→ L4 Parallel Consensus
→ Budget: ~4,500 tokens
```

---

### L5: Hierarchical (Architecture)

**Keywords:** "architect", "design system", "microservices", "infrastructure", "platform design"

**Use cases:**
- System architecture
- Large-scale design
- Microservices patterns
- Infrastructure planning

**Token budget:** 5,500-9,000 tokens

**Hotkey:** `[Ctrl+H]` (Hierarchical)

**Example:**
```
Q: "Design a scalable e-commerce microservices architecture"
→ L5 Hierarchical
→ Budget: ~7,250 tokens
```

---

### L6: Iterative (Optimization)

**Keywords:** "refactor", "optimize", "improve", "debug", "iterate", "enhance"

**Use cases:**
- Code optimization
- Performance tuning
- Bug fixing and debugging
- Iterative refinement
- Convergence loops

**Token budget:** 8,000-12,000 tokens

**Hotkey:** `[Ctrl+I]` (Iterative)

**Example:**
```
Q: "Refactor this code until it's optimized and all tests pass"
→ L6 Iterative
→ Budget: ~10,000 tokens
```

---

### L7: Full Ensemble (Build)

**Keywords:** "build", "from scratch", "complete", "full platform", "production", "entire system", "startup"

**Use cases:**
- Complete platform from scratch
- Full application development
- End-to-end system building
- Production-ready implementation

**Token budget:** 12,000-22,000 tokens

**Hotkey:** `[Ctrl+E]` (Ensemble)

**Example:**
```
Q: "Build a complete task management SaaS platform from scratch"
→ L7 Full Ensemble
→ Budget: ~17,000 tokens
```

---

## API Reference

### ClassificationResult

**Purpose:** Object returned from classification with all metadata

**Fields:**
```python
@dataclass
class ClassificationResult:
    level: int                    # 1-7 complexity level
    confidence: float             # 0.0-1.0 confidence score
    method: str                   # "explicit_override", "hotkey", "keyword"
    reasoning: str                # Explanation of classification
    keyword_level: int = None     # Level suggested by keywords
    hotkey: str = None            # Hotkey if provided
    downgraded: bool = False      # Was level reduced for budget?
    consciousness_boost: float    # Phase 3 boost amount
    consciousness_reason: str     # Why boost was applied
```

### Functions

#### `classify_query()`

**Purpose:** Classify a user query to complexity level

**Signature:**
```python
def classify_query(
    user_input: str,
    available_tokens: int = 50000,
    consciousness_data: Dict = None
) -> ClassificationResult
```

**Parameters:**
- `user_input`: Query string (may include @L5, [R], hotkeys)
- `available_tokens`: Tokens remaining in context
- `consciousness_data`: Historical patterns (Phase 3)

**Returns:** ClassificationResult object

**Example:**
```python
from classifier import classify_query

result = classify_query("Build a REST API with [D>I>T]")
print(f"Level: {result.level}")           # 3
print(f"Confidence: {result.confidence}") # 0.95
print(f"Method: {result.method}")         # "hotkey"
```

---

#### `suggest_hotkey_for_level()`

**Purpose:** Get hotkey suggestion for a complexity level

**Signature:**
```python
def suggest_hotkey_for_level(level: int, query: str = None) -> Dict
```

**Parameters:**
- `level`: Complexity level 1-7
- `query`: Optional query for context

**Returns:** Dictionary with hotkey, name, tier

**Example:**
```python
suggestion = suggest_hotkey_for_level(6)
print(suggestion)
# {'hotkey': '[Ctrl+I]', 'name': 'Iterative', 'tier': 'TIER 2'}
```

---

#### `format_token_display()`

**Purpose:** Format classification result for display

**Signature:**
```python
def format_token_display(
    result: ClassificationResult,
    verbose: bool = False,
    available_tokens: int = 50000
) -> str
```

**Parameters:**
- `result`: Classification result
- `verbose`: Show detailed phase breakdown
- `available_tokens`: Total available tokens

**Returns:** Formatted string for display

**Example (simple):**
```
Selected: L3 Balanced (75% confidence)
Tokens: Est 3500 | Budget 2500-4500 | Status: ✅ Ready
```

**Example (verbose):**
```
SELECTION PHASE:
  Phase 1: Input parsing       [+487 tokens] ✅
  Phase 2: Complexity classify [+892 tokens] ✅
  Phase 3: Hotkey generation   [+507 tokens] ✅
  ─────────────────────────────
  Total overhead: 1886 tokens

EXECUTION PLAN:
  Selected: L3 Balanced
  Token budget: 3500 (range: 2500-4500)
  Confidence: 75%

TOKEN BUDGET ANALYSIS:
  Available: 50000
  Selection: 1886
  Execution: 3500
  Total: 5386
  Remaining: 44614
  Status: ✅ PROCEED
```

---

#### `extract_hotkey()`

**Purpose:** Extract hotkey from user input

**Signature:**
```python
def extract_hotkey(user_input: str) -> Optional[str]
```

**Example:**
```python
hotkey = extract_hotkey("Explain [R] what REST is")
print(hotkey)  # "R"
```

---

#### `extract_explicit_level()`

**Purpose:** Extract explicit level override (@L5)

**Signature:**
```python
def extract_explicit_level(user_input: str) -> Optional[int]
```

**Example:**
```python
level = extract_explicit_level("Do this task @L5")
print(level)  # 5
```

---

## Usage Examples

### Example 1: Simple Classification

```python
from classifier import classify_query

result = classify_query("Explain what a database is")
print(f"Level: {result.level}")           # 1
print(f"Confidence: {result.confidence}") # 0.75
print(f"Method: {result.method}")         # "keyword"
```

### Example 2: Hotkey Selection

```python
result = classify_query("I want to [D>I>T] a new feature")
print(f"Level: {result.level}")           # 3
print(f"Hotkey: {result.hotkey}")         # "D>I>T"
print(f"Confidence: {result.confidence}") # 0.95
```

### Example 3: Explicit Override

```python
result = classify_query("Do this @L7")
print(f"Level: {result.level}")           # 7
print(f"Confidence: {result.confidence}") # 1.0
print(f"Method: {result.method}")         # "explicit_override"
```

### Example 4: Token Budget

```python
result = classify_query("Build a complete platform")
min_tokens, max_tokens = TOKEN_BUDGETS[result.level]
estimated = (min_tokens + max_tokens) // 2

print(f"Estimated tokens: {estimated}")   # ~17000
print(f"Budget range: {min_tokens}-{max_tokens}")  # 12000-22000
```

### Example 5: Display to User

```python
result = classify_query("Implement login feature with tests")
display = format_token_display(result, verbose=False)
print(display)

# Output:
# Selected: L3 Balanced (75% confidence)
# Tokens: Est 3500 | Budget 2500-4500 | Status: ✅ Ready
```

---

## Decision Tree

```
Query: "Build a REST API @L5"
                ↓
Step 1: Check explicit override (@L5)
        → Found: @L5
        → Return: L5 (confidence 100%)
                ↓
Step 2: (Skip - explicit override found)
                ↓
Step 3: (Skip - explicit override found)
                ↓
Output: L5 Hierarchical (100% confidence)
        Budget: 5500-9000 tokens
```

```
Query: "Design and test a feature [D>I>T]"
                ↓
Step 1: Check explicit override (@L*)
        → Not found
                ↓
Step 2: Check hotkey ([...])
        → Found: [D>I>T]
        → Return: L3 (confidence 95%)
                ↓
Output: L3 Balanced (95% confidence)
        Budget: 2500-4500 tokens
        Hotkey: Design→Implement→Test
```

```
Query: "Optimize the database queries"
                ↓
Step 1: Check explicit override
        → Not found
                ↓
Step 2: Check hotkey
        → Not found
                ↓
Step 3: Keyword matching
        → "optimize" found → L6
        → Confidence: 75%
                ↓
Output: L6 Iterative (75% confidence)
        Budget: 8000-12000 tokens
        Method: Keyword classification
```

---

## Integration with Other Phases

### Phase 1-2 → Phase 3 (Consciousness)
- Passes classification result to consciousness system
- Consciousness learns pattern and provides confidence boost

### Phase 1-2 → Phase 4 (Task-Relay)
- Passes level to task-relay for budget planning
- Level determines agent selection and token allocation

### Phase 1-2 → Phase 5 (Adaptive Learning)
- Used by Phase 5 for context-aware predictions
- Provides baseline token expectations per level

---

## Common Issues & Solutions

**Problem:** Always classifying as L1

**Check:**
1. Are keywords present in query?
2. Is query lowercase before matching?
3. Are hotkeys in correct format [X]?

**Solution:**
```python
# Keywords must be exact matches (case-insensitive)
query_lower = query.lower()
for keyword in KEYWORDS[level]:
    if keyword in query_lower:  # substring match
        return level
```

---

## Configuration

### TOKEN_BUDGETS

Adjust per-level token allocations:

```python
TOKEN_BUDGETS = {
    1: (600, 1200),      # L1
    2: (1500, 3000),     # L2
    3: (2500, 4500),     # L3
    4: (3000, 6000),     # L4
    5: (5500, 9000),     # L5
    6: (8000, 12000),    # L6
    7: (12000, 22000)    # L7
}
```

### KEYWORDS

Add or modify keywords that trigger each level:

```python
KEYWORDS = {
    7: {"build", "from scratch", "complete", ...},
    6: {"refactor", "optimize", ...},
    # ... etc
}
```

### HOTKEY_SUGGESTIONS

Map levels to hotkeys:

```python
HOTKEY_SUGGESTIONS = {
    1: {"hotkey": "[R]", "name": "Research", "tier": "TIER 1"},
    2: {"hotkey": "[D]", "name": "Design", "tier": "TIER 1"},
    # ... etc
}
```

---

## Next Steps

1. **Classification** identifies complexity level
2. **Hotkey system** provides quick selection
3. **Token budget** is allocated based on level
4. **Phase 3** (Consciousness) learns from results
5. **Phase 4** (Task-Relay) executes with token tracking
6. **Phase 5** (Adaptive Learning) predicts future costs

---

## Summary

Phase 1-2 is HEKAT's **intelligent query analyzer**:

✅ Classifies queries to 7 complexity levels
✅ Suggests hotkeys for quick selection
✅ Plans token budgets
✅ Calculates confidence scores
✅ Integrates with consciousness learning
✅ Provides explicit override capability

**Output:** Classification with confidence, token budget, and reasoning.
