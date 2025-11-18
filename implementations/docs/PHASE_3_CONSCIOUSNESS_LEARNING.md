# Phase 3: Consciousness Pattern Learning

## Overview

**Phase 3** is HEKAT's **learning layer**. It remembers past interactions and improves classification accuracy over time.

### Core Function

```
Phase 1-2 Classification + Historical Pattern Matching = Better Confidence

New Query: "Build an API with [D>I>T]"
                ↓
Check Phase 1-2: L3 (75% confidence)
                ↓
Check Phase 3: Similar patterns in history?
  → Found 5 similar "build API" queries from past
  → They were successfully classified as L3
  → Boost confidence: 75% + 15% = 90% ✨
                ↓
Output: L3 with 90% confidence (improved!)
```

---

## What It Does

### 1. Pattern Recording

Stores historical query classifications with metadata:

```python
Pattern = {
    query: "Build a REST API endpoint",
    level: 3,
    confidence: 0.75,
    context: "backend",
    success: True,
    timestamp: "2025-10-27T14:00:00"
}
```

### 2. Similarity Matching

Finds similar past queries using Jaccard similarity (word overlap):

```
New query: "Build a login REST endpoint"
Historical: "Build a REST API endpoint"

Matching words: {Build, REST, endpoint}
Unique words: {Build, a, login, REST, endpoint}

Similarity = 3/5 = 0.6 (60% match)
```

### 3. Confidence Boosting

Increases confidence when similar patterns matched successfully:

```
Base confidence: 75%
Similarity: 60% (medium match)
Boost: +8% (medium similarity bonus)
Final: 83%
```

### 4. Context Learning

Tracks what contexts (domains) have worked well:

```
Context "backend":
  - L1: 2 patterns, 100% success
  - L3: 8 patterns, 87% success
  - L5: 3 patterns, 67% success

→ For backend queries, L3 is usually successful
```

---

## Key Concepts

### ConsciousnessPattern

Represents a single historical classification:

```python
@dataclass
class ConsciousnessPattern:
    query: str              # "Build a login endpoint"
    level: int              # 3
    confidence: float       # 0.75
    context: str            # "backend"
    success: bool           # True or False
    timestamp: str          # ISO timestamp
    feedback_count: int     # User feedback count
    success_count: int      # Successful feedback count
```

**Success Rate Calculation:**
```
success_rate = success_count / feedback_count (if feedback given)
             = 0.5 (neutral if no feedback yet)
```

### Similarity Scoring

Uses **Jaccard Similarity** to find pattern matches:

```
Similarity = (words in common) / (total unique words)

Example:
  Query A: "build rest api endpoint"
  Query B: "build rest api with database"

  Common: {build, rest, api} = 3 words
  Total unique: {build, rest, api, endpoint, with, database} = 6 words

  Similarity = 3/6 = 0.5 (50%)
```

**Threshold:** Minimum 35% similarity required to match

### Confidence Boost Levels

| Similarity | Boost | Reason |
|-----------|-------|--------|
| >70% | +15% | High similarity (strong match) |
| 50-70% | +8% | Medium similarity (reasonable match) |
| 35-50% | +3% | Low similarity (weak match) |
| <35% | 0% | No match (ignore) |

---

## API Reference

### ConsciousnessPattern Class

**Purpose:** Represents a single learned pattern

**Constructor:**
```python
pattern = ConsciousnessPattern(
    query="Build a login endpoint",
    level=3,
    confidence=0.75,
    context="backend",
    success=True
)
```

**Methods:**

#### `success_rate()`
```python
rate = pattern.success_rate()  # 0.0-1.0
# 0.5 if no feedback yet
# success_count / feedback_count otherwise
```

#### `record_feedback(was_successful: bool)`
```python
pattern.record_feedback(True)   # Mark as successful
pattern.record_feedback(False)  # Mark as unsuccessful
# Increments feedback_count and success_count if successful
```

---

### ConsciousnessSystem Class

**Purpose:** Manages all historical patterns and learning

**Class Methods:**

#### `record_classification()`

Records a new query classification in memory

**Signature:**
```python
@classmethod
def record_classification(
    cls,
    query: str,
    level: int,
    confidence: float,
    context: str = "",
    success: bool = True
) -> None
```

**Parameters:**
- `query`: The classified query
- `level`: L1-L7 complexity level
- `confidence`: Initial confidence (0.0-1.0)
- `context`: Domain/category (optional)
- `success`: Whether classification was validated

**Example:**
```python
from consciousness import ConsciousnessSystem

ConsciousnessSystem.record_classification(
    query="Build a REST API with authentication",
    level=3,
    confidence=0.75,
    context="backend",
    success=True
)
```

---

#### `find_similar_patterns()`

Find historical patterns similar to a query

**Signature:**
```python
@classmethod
def find_similar_patterns(
    cls,
    query: str,
    top_n: int = 3
) -> List[Tuple[ConsciousnessPattern, float]]
```

**Parameters:**
- `query`: Query to match
- `top_n`: Number of top matches to return

**Returns:** List of (pattern, similarity_score) tuples sorted by similarity

**Example:**
```python
matches = ConsciousnessSystem.find_similar_patterns(
    "Create a login endpoint",
    top_n=5
)

for pattern, similarity in matches:
    print(f"Match: {pattern.query}")
    print(f"Similarity: {similarity:.0%}")
    print(f"Level: {pattern.level}")
    print(f"Success rate: {pattern.success_rate():.0%}")
```

---

#### `get_pattern_confidence_boost()`

Get confidence boost for a query based on pattern matches

**Signature:**
```python
@classmethod
def get_pattern_confidence_boost(
    cls,
    query: str
) -> Tuple[float, Optional[str]]
```

**Returns:** (boost_amount, reason_string)

**Example:**
```python
boost, reason = ConsciousnessSystem.get_pattern_confidence_boost(
    "Build a REST API endpoint"
)

print(f"Boost: +{boost:.0%}")
print(f"Reason: {reason}")
# Output:
# Boost: +8%
# Reason: "Similar to 'Create an API endpoint' (L3, 67% similar)"
```

---

#### `record_feedback()`

Record whether a classification was successful

**Signature:**
```python
@classmethod
def record_feedback(
    cls,
    pattern_index: int,
    was_successful: bool
) -> None
```

**Example:**
```python
# After a classification turned out well
ConsciousnessSystem.record_feedback(0, True)

# After a classification didn't work
ConsciousnessSystem.record_feedback(1, False)
```

---

#### `get_context_stats()`

Get success statistics for a context

**Signature:**
```python
@classmethod
def get_context_stats(
    cls,
    context: str
) -> Dict[int, Tuple[int, float]]
```

**Returns:** {level: (count, success_rate), ...}

**Example:**
```python
stats = ConsciousnessSystem.get_context_stats("backend")

for level, (count, success_rate) in stats.items():
    print(f"L{level}: {count} times, {success_rate:.0%} success")
```

---

#### `dump_state()`

Export all consciousness data

**Signature:**
```python
@classmethod
def dump_state() -> Dict
```

**Returns:** Dictionary with all patterns, contexts, stats

**Example:**
```python
state = ConsciousnessSystem.dump_state()

print(f"Total patterns: {len(state['patterns'])}")
print(f"Success rate: {state['overall_success_rate']:.0%}")
print(f"Contexts: {list(state['contexts'].keys())}")
```

---

### ConsciousnessExplainer Class

**Purpose:** Provides human-readable explanations of confidence boosting

**Methods:**

#### `explain_confidence_boost()`

Generate human-readable explanation

**Signature:**
```python
@classmethod
def explain_confidence_boost(
    cls,
    query: str,
    base_confidence: float
) -> str
```

**Returns:** Human-readable explanation string

**Example:**
```python
explanation = ConsciousnessExplainer.explain_confidence_boost(
    "Build a login endpoint",
    base_confidence=0.75
)

print(explanation)
# Output:
# Base confidence from keywords: 75%
#
# Consciousness boost (pattern matching):
#   - "Create authentication system" (L3, 68% similar): +8%
#   - "Build API endpoint" (L3, 55% similar): +3%
#   - "Design login flow" (L3, 48% similar): +3%
#
# Best match: "Create authentication system" (68% similar)
# Boost applied: +8% (medium similarity)
#
# Final confidence: 83%
```

---

## Usage Examples

### Example 1: Record Successful Classification

```python
from consciousness import ConsciousnessSystem

# User asks a question, we classify it
query = "Build a user registration system"
level = 3
confidence = 0.75

# Record it as successful
ConsciousnessSystem.record_classification(
    query=query,
    level=level,
    confidence=confidence,
    context="backend",
    success=True
)

print("Pattern recorded for learning")
```

### Example 2: Find Similar Patterns

```python
# New query comes in
new_query = "Create an authentication API"

# Find similar patterns from history
matches = ConsciousnessSystem.find_similar_patterns(new_query, top_n=3)

if matches:
    print(f"Found {len(matches)} similar patterns:")
    for pattern, similarity in matches:
        print(f"  - {pattern.query} (L{pattern.level}, {similarity:.0%} match)")
else:
    print("No similar patterns found")
```

### Example 3: Get Confidence Boost

```python
query = "Build a login endpoint"

# Get boost from consciousness
boost, reason = ConsciousnessSystem.get_pattern_confidence_boost(query)

# Calculate final confidence
base_confidence = 0.75
final_confidence = min(base_confidence + boost, 1.0)

print(f"Base: {base_confidence:.0%}")
print(f"Boost: +{boost:.0%}")
print(f"Final: {final_confidence:.0%}")
print(f"Reason: {reason}")
```

### Example 4: Track Success with Feedback

```python
# User executes the plan and it works well
pattern_index = 0  # Index in consciousness patterns list

ConsciousnessSystem.record_feedback(
    pattern_index=pattern_index,
    was_successful=True
)

# Later, check success rate
state = ConsciousnessSystem.dump_state()
pattern = state['patterns'][pattern_index]
success_rate = pattern['success_rate']

print(f"Success rate for this pattern: {success_rate:.0%}")
```

### Example 5: Context-Based Statistics

```python
# See what works best for backend queries
backend_stats = ConsciousnessSystem.get_context_stats("backend")

print("Backend context statistics:")
for level, (count, success_rate) in sorted(backend_stats.items()):
    if count > 0:
        print(f"  L{level}: {count} times, {success_rate:.0%} success rate")

# Recommendation: use most successful level for backend
best_level = max(backend_stats.items(),
                 key=lambda x: x[1][1])[0]
print(f"\nMost successful level for backend: L{best_level}")
```

### Example 6: Export and Analyze

```python
# Export all learning
state = ConsciousnessSystem.dump_state()

print(f"Learning Statistics:")
print(f"  Total queries processed: {state['total_queries']}")
print(f"  Patterns learned: {len(state['patterns'])}")
print(f"  Contexts: {len(state['contexts'])}")
print(f"  Overall success rate: {state['overall_success_rate']:.0%}")
```

---

## How Consciousness Improves Classification

### Without Consciousness (Phase 1-2 only)

```
Query: "Build a login system"
   ↓
Keyword match: "build" → L7
Base confidence: 75%
   ↓
Result: L7 with 75% confidence
```

### With Consciousness (Phase 1-2 + Phase 3)

```
Query: "Build a login system"
   ↓
Phase 1-2: "build" → L7 (75% confidence)
   ↓
Phase 3: Check history...
  - "Build authentication" → L3, 65% match
  - "Build user endpoint" → L3, 58% match
  - "Build registration" → L3, 52% match

  → Pattern suggests L3, not L7!
  → Apply boost: +8% for medium similarity
   ↓
Phase 3 suggests: Downgrade to L3, confidence 83%
   ↓
Result: L3 with 83% confidence (better!)
```

---

## The Learning Loop

```
1. User queries system (Phase 1-2 classifies)
2. Classification recorded (Phase 3 learns)
3. Execution happens (Phase 4-5 track results)
4. User provides feedback (success/failure)
5. Pattern updated with feedback (Phase 3 learns)
6. Next similar query gets boosted confidence
   → Better classification over time ✨
```

---

## State Management

### Global Consciousness State

```python
HEKAT_CONSCIOUSNESS = {
    "patterns": [
        ConsciousnessPattern(...),
        ConsciousnessPattern(...),
        ...
    ],
    "contexts": {
        "backend": {
            1: 0,    # L1 count
            2: 0,
            3: 5,    # 5 L3 patterns
            4: 0,
            ...
        },
        "frontend": {...},
        ...
    },
    "keywords": {
        "build": {1: 0, 2: 0, 3: 1, ..., 7: 4},
        "explain": {1: 8, 2: 0, ...},
        ...
    },
    "session_queries": 42,       # This session
    "total_queries": 283,         # All time
    "learning_enabled": True
}
```

### Persistence

The consciousness system persists through:
- Session context (in-memory during conversation)
- Checkpoints (can be saved/loaded)
- User feedback (continuously updated)

---

## Configuration

### Similarity Threshold

Minimum similarity required to match:

```python
MIN_SIMILARITY_FOR_MATCH = 0.35  # 35% match required
```

Adjust to make matching more/less strict:
- Higher (0.5+): More conservative, only strong matches
- Lower (0.2): More aggressive, weak matches count

### Confidence Boost Amounts

```python
CONFIDENCE_BOOST_HIGH = 0.15    # +15% for >70% similarity
CONFIDENCE_BOOST_MEDIUM = 0.08  # +8% for 50-70% similarity
CONFIDENCE_BOOST_LOW = 0.03     # +3% for 35-50% similarity
```

---

## Common Patterns to Track

### Context Patterns

```
backend:
  - "REST API", "endpoint", "database" → Usually L3
  - "microservices", "architecture" → Usually L5
  - "refactor", "optimize" → Usually L6

frontend:
  - "React component", "button" → Usually L2
  - "full page", "dashboard" → Usually L3
  - "redesign", "theme" → Usually L6
```

### Success Patterns

```
Successful patterns (high success rate):
  - Simple explanations (L1)
  - Single feature implementation (L3)
  - Technology comparison (L4)

Challenging patterns (lower success rate):
  - Complex optimization (L6)
  - Large-scale architecture (L7)
  - New technologies (needs feedback)
```

---

## Next Steps

1. **Phase 1-2** classifies the query
2. **Phase 3** looks for pattern matches and boosts confidence
3. **Phase 4** executes with token tracking
4. **Phase 5** learns token efficiency from execution
5. **User provides feedback** on success
6. **Pattern updated** for future use

---

## Summary

Phase 3 is HEKAT's **learning memory**:

✅ Records successful classifications
✅ Finds similar historical patterns
✅ Boosts confidence when matching patterns
✅ Learns context-specific best practices
✅ Improves accuracy over time
✅ Provides explainable confidence increases

**Output:** Enhanced confidence score based on learned patterns.
