# Phase 4: Task-Relay Consciousness Integration

## Overview

**Phase 4** is HEKAT's **execution tracking and efficiency measurement layer**. It monitors token usage during multi-agent execution and tracks pattern efficiency.

### Core Function

```
Multi-Agent Execution with Token Discipline
═════════════════════════════════════════════════

Agent 1 execution
  ├─ Token checkpoint: 50,000 → 47,500
  └─ Delta: 2,500 tokens used
                ↓
Consciousness snapshot captured
  ├─ Pattern matched: "Build API"
  ├─ Level: L3
  ├─ Success rate: 87%
                ↓
Agent 2 execution
  ├─ Token checkpoint: 47,500 → 44,200
  └─ Delta: 3,300 tokens used
                ↓
Efficiency Analysis
  ├─ Expected: 3,500 tokens
  ├─ Actual: 3,300 tokens
  ├─ Variance: -5.7% (EFFICIENT! ✅)
                ↓
Pattern learned: "This pattern is 5.7% more efficient than expected"
```

---

## What It Does

### 1. Token Checkpoints

Captures token state at execution boundaries:

```python
checkpoint = TokenCheckpoint(
    phase="relay_1_researcher",
    pre_tokens=50000,      # Before this agent
    post_tokens=47500,     # After this agent
    description="Researcher agent execution"
)

# Calculate usage
tokens_used = checkpoint.delta  # -2500 (negative = consumed)
```

### 2. Consciousness Integration

Attaches consciousness metadata at execution time:

```python
consciousness = ConsciousnessCheckpoint(
    pattern_matched=True,
    pattern_query="Build a REST API",
    pattern_level=3,
    pattern_success_rate=0.87,
    confidence_boost=0.08,
    context="backend"
)
```

### 3. Variance Analysis

Compares actual token usage to predictions:

```
Expected: 3,500 tokens (from Phase 1-2)
Actual: 3,300 tokens (measured in Phase 4)
Variance: (3,300 - 3,500) / 3,500 = -5.7%

Status:
  -50% to +10% = ✅ Excellent
  +10% to +20% = ⚠️ Warning
  +20%+ = ❌ Critical
```

### 4. Pattern Efficiency Tracking

Records how patterns perform over time:

```python
efficiency = PatternEfficiency(
    pattern_query="Build a REST API",
    pattern_level=3,
    execution_count=5,
    avg_tokens_used=3320,
    avg_tokens_expected=3500,
    avg_efficiency_ratio=0.95,  # 95% of budget
    efficiency_status="🟢 EFFICIENT"
)
```

---

## Key Concepts

### TokenCheckpoint

Records token state at a phase boundary.

```python
@dataclass
class TokenCheckpoint:
    phase: str              # "relay_1_researcher"
    pre_tokens: int         # 50,000 (before)
    post_tokens: int        # 47,500 (after)
    description: str = ""   # Metadata

    # Calculated properties
    delta: int              # -2,500 (consumed)
    percentage_of_budget: float  # 5.0%
```

### ConsciousnessCheckpoint

Captures consciousness state during execution.

```python
@dataclass
class ConsciousnessCheckpoint:
    pattern_matched: bool        # Did we match a pattern?
    pattern_query: str = None    # "Build a REST API"
    pattern_level: int = None    # 3
    pattern_success_rate: float  # 0.87
    confidence_boost: float = 0.0 # +8%
    confidence_reason: str = None # Why boost applied
    context: str = "general"     # Domain context
```

### RelayCheckpoint

Complete checkpoint combining tokens + consciousness + variance.

```python
@dataclass
class RelayCheckpoint:
    relay_number: int           # Which relay step (1, 2, 3, ...)
    agent_name: str             # "researcher", "designer"
    timestamp: str              # ISO timestamp
    token: TokenCheckpoint      # Token state
    consciousness: ConsciousnessCheckpoint  # Pattern data

    # Variance analysis
    expected_tokens: int = None # Budget from Phase 1-2
    variance: float = None      # Actual vs expected %

    def calculate_variance(self) -> float
    def variance_status(self) -> str  # ✅ ⚠️ ❌
    def to_dict(self) -> Dict
```

### PatternEfficiency

Aggregates efficiency data for a pattern over multiple executions.

```python
@dataclass
class PatternEfficiency:
    pattern_query: str              # "Build a REST API"
    pattern_level: int              # 3
    pattern_success_rate: float     # 0.87

    # Tracking
    execution_count: int = 0        # How many times run
    total_tokens_used: int = 0      # Total actual
    total_tokens_expected: int = 0  # Total budget

    # Calculated
    avg_tokens_used: float          # Average actual
    avg_tokens_expected: float      # Average budget
    avg_efficiency_ratio: float     # actual/expected
    efficiency_status: str          # 🟢 🟡 🔴

    def record_execution(actual, expected) -> None
```

---

## API Reference

### TaskRelayConsciousnessIntegration Class

**Purpose:** Manage relay execution with consciousness and token tracking

**Class Methods:**

#### `create_checkpoint()`

Create a complete relay checkpoint with all metadata.

**Signature:**
```python
@classmethod
def create_checkpoint(
    cls,
    relay_number: int,
    agent_name: str,
    pre_tokens: int,
    post_tokens: int,
    expected_tokens: int = None,
    pattern_data: Dict = None,
    context: str = "general"
) -> RelayCheckpoint
```

**Parameters:**
- `relay_number`: Relay step (1, 2, 3, ...)
- `agent_name`: Agent name ("researcher", "designer", etc.)
- `pre_tokens`: Tokens before execution
- `post_tokens`: Tokens after execution
- `expected_tokens`: Budget from Phase 1-2 (optional)
- `pattern_data`: Consciousness pattern match data (optional)
- `context`: Domain context

**Returns:** RelayCheckpoint object

**Example:**
```python
from task_relay_consciousness import TaskRelayConsciousnessIntegration

checkpoint = TaskRelayConsciousnessIntegration.create_checkpoint(
    relay_number=1,
    agent_name="researcher",
    pre_tokens=50000,
    post_tokens=47500,
    expected_tokens=3000,
    pattern_data={
        "pattern_query": "Research a topic",
        "pattern_level": 2,
        "pattern_success_rate": 0.85
    },
    context="backend"
)

print(f"Tokens used: {checkpoint.token.delta}")  # -2,500
print(f"Variance: {checkpoint.calculate_variance():.1f}%")  # -16.7%
print(f"Status: {checkpoint.variance_status()}")  # ✅
```

---

#### `record_pattern_efficiency()`

Record how a pattern performed in this execution.

**Signature:**
```python
@classmethod
def record_pattern_efficiency(
    cls,
    pattern_query: str,
    pattern_level: int,
    pattern_success_rate: float,
    actual_tokens: int,
    expected_tokens: int
) -> PatternEfficiency
```

**Parameters:**
- `pattern_query`: Pattern description
- `pattern_level`: L1-L7
- `pattern_success_rate`: Success rate from Phase 3
- `actual_tokens`: Tokens actually used
- `expected_tokens`: Tokens expected (budget)

**Returns:** Updated PatternEfficiency object

**Example:**
```python
efficiency = TaskRelayConsciousnessIntegration.record_pattern_efficiency(
    pattern_query="Build a REST API",
    pattern_level=3,
    pattern_success_rate=0.87,
    actual_tokens=3300,
    expected_tokens=3500
)

print(f"Efficiency: {efficiency.avg_efficiency_ratio:.0%}")
print(f"Status: {efficiency.efficiency_status}")  # 🟢 EFFICIENT
```

---

#### `get_pattern_efficiency()`

Retrieve efficiency metrics for a pattern.

**Signature:**
```python
@classmethod
def get_pattern_efficiency(cls, pattern_query: str) -> PatternEfficiency
```

**Parameters:**
- `pattern_query`: Pattern to look up

**Returns:** PatternEfficiency object or None

**Example:**
```python
efficiency = TaskRelayConsciousnessIntegration.get_pattern_efficiency(
    "Build a REST API"
)

if efficiency:
    print(f"Executions: {efficiency.execution_count}")
    print(f"Avg tokens: {efficiency.avg_tokens_used:.0f}")
    print(f"Efficiency: {efficiency.efficiency_status}")
else:
    print("Pattern not tracked yet")
```

---

#### `get_checkpoint_history()`

Get all checkpoints for an agent.

**Signature:**
```python
@classmethod
def get_checkpoint_history(cls, agent_name: str) -> List[RelayCheckpoint]
```

**Parameters:**
- `agent_name`: Agent to get history for

**Returns:** List of RelayCheckpoint objects

**Example:**
```python
history = TaskRelayConsciousnessIntegration.get_checkpoint_history(
    "researcher"
)

print(f"Researcher executed {len(history)} times")

total_tokens = sum(abs(cp.token.delta) for cp in history)
print(f"Total tokens used: {total_tokens:,}")

# Show variance trend
for i, cp in enumerate(history):
    variance = cp.calculate_variance()
    print(f"  Execution {i+1}: {variance:+.1f}%")
```

---

#### `analyze_relay_sequence()`

Analyze a complete multi-relay sequence.

**Signature:**
```python
@classmethod
def analyze_relay_sequence(
    cls,
    checkpoints: List[RelayCheckpoint]
) -> Dict
```

**Parameters:**
- `checkpoints`: List of RelayCheckpoint objects from a complete execution

**Returns:** Analysis dictionary with statistics

**Example:**
```python
analysis = TaskRelayConsciousnessIntegration.analyze_relay_sequence(
    checkpoints=[cp1, cp2, cp3, cp4]
)

print(f"Total relays: {analysis['relay_count']}")
print(f"Total tokens: {analysis['total_tokens']:,}")
print(f"Budget adherence: {analysis['budget_adherence']:.1f}%")
print(f"Critical issues: {len(analysis['critical_issues'])}")
```

---

### RelayCheckpoint Methods

#### `calculate_variance()`

Calculate variance percentage: (actual - expected) / expected * 100

**Returns:** Float percentage (negative = under budget, positive = over)

**Example:**
```python
checkpoint.expected_tokens = 3500
checkpoint.token.delta = -3300  # Consumed 3300

variance = checkpoint.calculate_variance()
# (3300 - 3500) / 3500 * 100 = -5.7%
```

---

#### `variance_status()`

Get variance status indicator.

**Returns:** String ("✅", "⚠️", "❌")

**Status Thresholds:**
- ✅ Excellent: -50% to +10% (better than expected or slightly over)
- ⚠️ Warning: +10% to +20% (moderately over budget)
- ❌ Critical: +20%+ (significantly over budget)

**Example:**
```python
if checkpoint.variance_status() == "❌":
    print(f"CRITICAL: {checkpoint.variance:+.1f}% over budget")
    print(f"Expected: {checkpoint.expected_tokens}")
    print(f"Actual: {abs(checkpoint.token.delta)}")
```

---

#### `to_dict()`

Serialize checkpoint to dictionary.

**Returns:** Dictionary with all data

**Example:**
```python
import json

data = checkpoint.to_dict()
print(json.dumps(data, indent=2))

# Output:
# {
#   "relay_number": 1,
#   "agent_name": "researcher",
#   "timestamp": "2025-10-27T14:00:00",
#   "token": { ... },
#   "consciousness": { ... },
#   "variance": -5.7,
#   "variance_status": "✅"
# }
```

---

### PatternEfficiency Methods

#### `record_execution(actual_tokens, expected_tokens)`

Record a new execution and update efficiency metrics.

**Parameters:**
- `actual_tokens`: Tokens actually used
- `expected_tokens`: Tokens expected

**Example:**
```python
efficiency.record_execution(actual=3300, expected=3500)
efficiency.record_execution(actual=3250, expected=3500)
efficiency.record_execution(actual=3400, expected=3500)

print(f"Executions: {efficiency.execution_count}")  # 3
print(f"Avg ratio: {efficiency.avg_efficiency_ratio:.0%}")  # 95%
```

---

#### `to_dict()`

Serialize to dictionary.

**Returns:** Dictionary with all metrics

**Example:**
```python
state = efficiency.to_dict()

# {
#   "pattern_query": "Build a REST API",
#   "pattern_level": 3,
#   "execution_count": 5,
#   "avg_tokens_used": 3320,
#   "avg_tokens_expected": 3500,
#   "avg_efficiency_ratio": 0.95,
#   "efficiency_status": "🟢 EFFICIENT"
# }
```

---

## Usage Examples

### Example 1: Create a Checkpoint

```python
from task_relay_consciousness import TaskRelayConsciousnessIntegration

# Researcher agent just finished execution
checkpoint = TaskRelayConsciousnessIntegration.create_checkpoint(
    relay_number=1,
    agent_name="researcher",
    pre_tokens=50000,
    post_tokens=47500,
    expected_tokens=3000,
    pattern_data={
        "pattern_query": "Research a topic",
        "pattern_level": 2
    }
)

# Check performance
print(f"Tokens consumed: {abs(checkpoint.token.delta)}")
print(f"Budget: {checkpoint.expected_tokens}")
print(f"Variance: {checkpoint.calculate_variance():+.1f}%")
print(f"Status: {checkpoint.variance_status()}")
```

**Output:**
```
Tokens consumed: 2500
Budget: 3000
Variance: -16.7%
Status: ✅
```

---

### Example 2: Track Pattern Efficiency

```python
# Over multiple executions, track how efficient a pattern is

pattern = "Build a REST API endpoint"

# Execution 1
TaskRelayConsciousnessIntegration.record_pattern_efficiency(
    pattern, 3, 0.87, actual=3300, expected=3500
)

# Execution 2
TaskRelayConsciousnessIntegration.record_pattern_efficiency(
    pattern, 3, 0.87, actual=3250, expected=3500
)

# Execution 3
TaskRelayConsciousnessIntegration.record_pattern_efficiency(
    pattern, 3, 0.87, actual=3400, expected=3500
)

# Check overall efficiency
efficiency = TaskRelayConsciousnessIntegration.get_pattern_efficiency(pattern)

print(f"Pattern: {efficiency.pattern_query}")
print(f"Executions: {efficiency.execution_count}")
print(f"Avg tokens: {efficiency.avg_tokens_used:.0f}")
print(f"Budget: {efficiency.avg_tokens_expected:.0f}")
print(f"Efficiency: {efficiency.avg_efficiency_ratio:.0%}")
print(f"Status: {efficiency.efficiency_status}")
```

**Output:**
```
Pattern: Build a REST API endpoint
Executions: 3
Avg tokens: 3317
Budget: 3500
Efficiency: 95%
Status: 🟢 EFFICIENT
```

---

### Example 3: Analyze Complete Relay Sequence

```python
# Execute multiple relays and capture checkpoints
checkpoints = [
    # Relay 1: Researcher
    TaskRelayConsciousnessIntegration.create_checkpoint(
        relay_number=1,
        agent_name="researcher",
        pre_tokens=50000,
        post_tokens=47500,
        expected_tokens=3000
    ),
    # Relay 2: Designer
    TaskRelayConsciousnessIntegration.create_checkpoint(
        relay_number=2,
        agent_name="designer",
        pre_tokens=47500,
        post_tokens=44800,
        expected_tokens=3500
    ),
    # Relay 3: Implementer
    TaskRelayConsciousnessIntegration.create_checkpoint(
        relay_number=3,
        agent_name="implementer",
        pre_tokens=44800,
        post_tokens=41200,
        expected_tokens=4000
    ),
]

# Analyze the complete sequence
analysis = TaskRelayConsciousnessIntegration.analyze_relay_sequence(
    checkpoints
)

print(f"Total relays: {analysis['relay_count']}")
print(f"Total tokens: {analysis['total_tokens']:,}")
print(f"Budget: {analysis['total_budget']:,}")
print(f"Variance: {analysis['total_variance']:+.1f}%")
print(f"Status: {analysis['overall_status']}")
```

---

### Example 4: Agent Performance Comparison

```python
# Compare efficiency across agents

agents = ["researcher", "designer", "implementer"]

for agent in agents:
    history = TaskRelayConsciousnessIntegration.get_checkpoint_history(agent)

    if not history:
        print(f"{agent}: No data")
        continue

    # Calculate statistics
    total_tokens = sum(abs(cp.token.delta) for cp in history)
    avg_tokens = total_tokens / len(history)
    variances = [cp.calculate_variance() for cp in history
                 if cp.expected_tokens]

    print(f"\n{agent.upper()}")
    print(f"  Executions: {len(history)}")
    print(f"  Total tokens: {total_tokens:,}")
    print(f"  Avg per exec: {avg_tokens:.0f}")
    if variances:
        print(f"  Avg variance: {sum(variances)/len(variances):+.1f}%")
```

---

### Example 5: Identify Problematic Patterns

```python
# Find patterns that consistently go over budget

all_patterns = TaskRelayConsciousnessIntegration.get_all_pattern_efficiency()

print("Patterns needing attention:")
for pattern_query, efficiency in all_patterns.items():
    if efficiency.efficiency_status == "🔴 OVER_BUDGET":
        variance = (efficiency.avg_tokens_used -
                   efficiency.avg_tokens_expected) / efficiency.avg_tokens_expected * 100

        print(f"\n  {pattern_query}")
        print(f"    Level: L{efficiency.pattern_level}")
        print(f"    Executions: {efficiency.execution_count}")
        print(f"    Variance: {variance:+.1f}%")
        print(f"    Recommendation: Review and optimize")
```

---

## Variance Thresholds

### Status Indicators

```
Variance Range  | Status | Action
────────────────────────────────────────────
-50% to 0%     | ✅     | EXCELLENT - Better than expected
0% to +10%     | ✅     | EXCELLENT - Slightly over but acceptable
+10% to +15%   | ⚠️     | WARNING - Investigate
+15% to +20%   | ⚠️     | WARNING - Needs optimization
+20% to +30%   | ❌     | CRITICAL - Immediate action
+30%+          | ❌     | CRITICAL - Major issue
```

### Interpretation

```
-30%: Pattern used 70% of budget (very efficient!)
 0%:  Pattern used exactly the budget
+20%: Pattern used 120% of budget (over by 20%)
+50%: Pattern used 150% of budget (over by 50%)
```

---

## State Persistence

### Checkpoints Storage

```python
checkpoints_history = [
    # Relay 1
    {
        "relay_number": 1,
        "agent_name": "researcher",
        "timestamp": "2025-10-27T14:00:00",
        "variance": -16.7,
        "variance_status": "✅"
    },
    # Relay 2
    {
        "relay_number": 2,
        "agent_name": "designer",
        "timestamp": "2025-10-27T14:05:00",
        "variance": -5.7,
        "variance_status": "✅"
    },
    # ... more relays
]
```

### Pattern Efficiency Storage

```python
pattern_efficiency = {
    "Build a REST API endpoint": {
        "pattern_level": 3,
        "execution_count": 5,
        "avg_tokens_used": 3320,
        "avg_tokens_expected": 3500,
        "avg_efficiency_ratio": 0.95,
        "efficiency_status": "🟢 EFFICIENT"
    },
    "Design system architecture": {
        "pattern_level": 5,
        "execution_count": 3,
        "avg_tokens_used": 7850,
        "avg_tokens_expected": 7250,
        "avg_efficiency_ratio": 1.08,
        "efficiency_status": "🟡 ON_BUDGET"
    }
}
```

---

## Integration Flow

```
Phase 1-2 Classification
    ↓ (determines level, sets expected tokens)
Phase 3 Consciousness
    ↓ (matches patterns, provides confidence)
Phase 4 Task-Relay Execution
    ├─ Checkpoint created at each relay
    ├─ Consciousness data captured
    ├─ Variance calculated (actual vs expected)
    ├─ Pattern efficiency recorded
    ↓
Phase 5 Adaptive Learning
    ├─ Actual tokens from Phase 4
    ├─ History for prediction
    ├─ Trend analysis
    ↓
Next Execution
    └─ More accurate budget prediction
```

---

## Summary

Phase 4 is HEKAT's **execution tracker**:

✅ Captures token usage at relay boundaries
✅ Measures variance (actual vs expected)
✅ Tracks pattern efficiency over time
✅ Integrates consciousness at execution time
✅ Provides variance status indicators
✅ Identifies problematic patterns
✅ Feeds efficiency data to Phase 5

**Output:** Token usage tracking, efficiency metrics, variance analysis.
