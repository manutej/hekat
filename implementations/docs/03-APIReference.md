# API Reference - Complete Function Documentation

## Table of Contents

1. [BudgetPredictor Class](#budgetpredictor-class)
2. [TrendAnalyzer Class](#trendanalyzer-class)
3. [AdaptiveBudgetSystem Class](#adaptivebudgetsystem-class)
4. [Data Classes](#data-classes)
5. [Constants and Defaults](#constants-and-defaults)

---

## BudgetPredictor Class

The `BudgetPredictor` class provides core token prediction functionality.

### `predict_budget()`

**Description:** Predict tokens for a pattern based on historical data.

**Signature:**
```python
@classmethod
def predict_budget(
    token_history: List[int],
    pattern_query: str,
    pattern_level: int,
    use_trend: bool = True
) -> TokenPrediction
```

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `token_history` | List[int] | Yes | — | Historical token counts (minimum 1, recommend 3+) |
| `pattern_query` | str | Yes | — | Name/description of the pattern |
| `pattern_level` | int | Yes | — | Complexity level (1-3, higher = more complex) |
| `use_trend` | bool | No | True | Include trend adjustment in prediction |

**Returns:**
```python
TokenPrediction(
    pattern_query: str,           # Your pattern name
    pattern_level: int,            # Complexity level
    predicted_tokens: int,         # Predicted token count
    confidence: float,             # 0.0-1.0 confidence score
    min_tokens: int,               # 70% of prediction (safety floor)
    max_tokens: int,               # 130% of prediction (safety ceiling)
    basis: str,                    # "historical_average" or "trend_extrapolation"
    samples: int                   # Number of samples used
)
```

**Examples:**
```python
from adaptive_learning import BudgetPredictor

# Basic prediction
history = [2000, 2100, 2050]
pred = BudgetPredictor.predict_budget(history, "explain_jwt", 1)
print(f"Tokens: {pred.predicted_tokens}")  # ~2050
print(f"Confidence: {pred.confidence:.0%}")  # ~89%

# With trend adjustment disabled
pred_no_trend = BudgetPredictor.predict_budget(
    history, "pattern", 1, use_trend=False
)
```

**Error Handling:**
```python
# Empty history raises ValueError
try:
    BudgetPredictor.predict_budget([], "pattern", 1)
except ValueError:
    print("History cannot be empty")

# Single sample still works (returns low confidence)
pred = BudgetPredictor.predict_budget([2000], "pattern", 1)
print(pred.confidence)  # 0.30 (minimum)
```

---

### `predict_with_context()`

**Description:** Predict tokens with domain-specific context multiplier.

**Signature:**
```python
@classmethod
def predict_with_context(
    token_history: List[int],
    pattern_level: int,
    context: str = "",
    base_budget: int = None
) -> TokenPrediction
```

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `token_history` | List[int] | Yes | — | Historical token counts |
| `pattern_level` | int | Yes | — | Complexity level (1-3) |
| `context` | str | No | "" | Domain context (education, architecture, implementation) |
| `base_budget` | int | No | None | Override base prediction (useful for custom calculations) |

**Context Multipliers:**
| Context | Multiplier | Use Case |
|---------|-----------|----------|
| education | 0.9x | Teaching, explanations, tutorials |
| architecture | 1.2x | System design, complex planning |
| implementation | 1.1x | Code writing, debugging |
| (empty) | 1.0x | Default, no adjustment |

**Returns:**
```python
TokenPrediction (same as predict_budget)
```

**Examples:**
```python
from adaptive_learning import BudgetPredictor

history = [2000, 2100, 2050]

# Education context (10% cheaper)
education = BudgetPredictor.predict_with_context(
    history, 1, "education"
)
print(f"Education: {education.predicted_tokens}")  # ~1845

# Architecture context (20% more)
architecture = BudgetPredictor.predict_with_context(
    history, 1, "architecture"
)
print(f"Architecture: {architecture.predicted_tokens}")  # ~2460

# Implementation context (10% more)
implementation = BudgetPredictor.predict_with_context(
    history, 1, "implementation"
)
print(f"Implementation: {implementation.predicted_tokens}")  # ~2255

# Custom base budget
custom = BudgetPredictor.predict_with_context(
    history, 1, "education", base_budget=3000
)
print(f"Custom: {custom.predicted_tokens}")  # ~2700 (3000 * 0.9)
```

---

## TrendAnalyzer Class

The `TrendAnalyzer` class provides trend detection and analysis.

### `analyze_trend()`

**Description:** Analyze trend in historical token data.

**Signature:**
```python
@classmethod
def analyze_trend(
    token_history: List[int]
) -> TrendAnalysis
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `token_history` | List[int] | Yes | Historical token counts (minimum 2 recommended) |

**Returns:**
```python
TrendAnalysis(
    trend: str,                    # "increasing", "decreasing", or "stable"
    trend_percentage: float,       # Rate of change per execution
    consistency: float,            # 0.0-1.0 predictability score
    forecasted_next: int,          # Predicted next value
    slope: float,                  # Linear regression slope
    intercept: float               # Linear regression intercept
)
```

**Examples:**
```python
from adaptive_learning import TrendAnalyzer

# Increasing trend
increasing = [2000, 2150, 2300, 2450, 2600]
trend = TrendAnalyzer.analyze_trend(increasing)
print(f"Trend: {trend.trend}")  # "increasing"
print(f"Rate: {trend.trend_percentage:.1f}%")  # "7.5%"
print(f"Next: {trend.forecasted_next}")  # 2750

# Stable trend
stable = [2000, 2020, 1990, 2010, 2005]
trend = TrendAnalyzer.analyze_trend(stable)
print(f"Trend: {trend.trend}")  # "stable"
print(f"Rate: {trend.trend_percentage:.1f}%")  # "~0.3%"
print(f"Consistency: {trend.consistency:.1%}")  # "94%"

# Decreasing trend
decreasing = [2600, 2450, 2300, 2150, 2000]
trend = TrendAnalyzer.analyze_trend(decreasing)
print(f"Trend: {trend.trend}")  # "decreasing"
print(f"Rate: {trend.trend_percentage:.1f}%")  # "-7.5%"
```

**Trend Classification:**
```
trend_percentage < -5%   → "decreasing"
-5% ≤ trend_percentage ≤ 5%  → "stable"
trend_percentage > 5%    → "increasing"
```

---

## AdaptiveBudgetSystem Class

The `AdaptiveBudgetSystem` class orchestrates predictions, trends, and alerts across multiple patterns.

### `update_prediction()`

**Description:** Store prediction for a pattern.

**Signature:**
```python
@classmethod
def update_prediction(
    pattern_key: str,
    token_history: List[int],
    pattern_query: str,
    pattern_level: int,
    context: str = ""
) -> None
```

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `pattern_key` | str | Yes | — | Unique identifier for pattern |
| `token_history` | List[int] | Yes | — | Historical token counts |
| `pattern_query` | str | Yes | — | Pattern name/description |
| `pattern_level` | int | Yes | — | Complexity level (1-3) |
| `context` | str | No | "" | Domain context |

**Returns:** None

**Examples:**
```python
from adaptive_learning import AdaptiveBudgetSystem

# Store prediction
history = [2000, 2100, 2050]
AdaptiveBudgetSystem.update_prediction(
    "pattern_1",
    history,
    "Explain JWT",
    1,
    context="education"
)

# Later, retrieve it
pred = AdaptiveBudgetSystem.get_prediction("pattern_1")
print(pred.predicted_tokens)
```

---

### `update_trend()`

**Description:** Store trend analysis for a pattern.

**Signature:**
```python
@classmethod
def update_trend(
    pattern_key: str,
    token_history: List[int],
    pattern_query: str,
    pattern_level: int
) -> None
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pattern_key` | str | Yes | Unique identifier for pattern |
| `token_history` | List[int] | Yes | Historical token counts |
| `pattern_query` | str | Yes | Pattern name/description |
| `pattern_level` | int | Yes | Complexity level |

**Returns:** None

**Examples:**
```python
AdaptiveBudgetSystem.update_trend(
    "pattern_1",
    [2000, 2100, 2200, 2300, 2400],
    "Explain JWT",
    1
)

# Retrieve trend
state = AdaptiveBudgetSystem.dump_state()
trend = state['trends']['pattern_1']
print(trend['trend'])  # "increasing"
```

---

### `get_prediction()`

**Description:** Retrieve stored prediction for a pattern.

**Signature:**
```python
@classmethod
def get_prediction(pattern_key: str) -> TokenPrediction or None
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pattern_key` | str | Yes | Pattern identifier |

**Returns:** `TokenPrediction` object or `None` if not found

**Examples:**
```python
from adaptive_learning import AdaptiveBudgetSystem

# After storing
AdaptiveBudgetSystem.update_prediction("pattern_1", [2000, 2100], "Task", 1)

# Retrieve
pred = AdaptiveBudgetSystem.get_prediction("pattern_1")
if pred:
    print(f"Tokens: {pred.predicted_tokens}")
    print(f"Confidence: {pred.confidence:.0%}")
else:
    print("Pattern not found")
```

---

### `check_budget_violation()`

**Description:** Check if actual usage exceeded prediction and create alert.

**Signature:**
```python
@classmethod
def check_budget_violation(
    pattern_key: str,
    actual_tokens: int,
    predicted_tokens: int = None
) -> BudgetAlert or None
```

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `pattern_key` | str | Yes | — | Pattern identifier |
| `actual_tokens` | int | Yes | — | Actual tokens used |
| `predicted_tokens` | int | No | None | Override predicted (uses stored if None) |

**Returns:** `BudgetAlert` object or `None` if within budget

**Alert Severity:**
- `"info"`: 0-15% over (normal variance)
- `"warning"`: 15-30% over (investigate)
- `"critical"`: >30% over (immediate action)

**Examples:**
```python
from adaptive_learning import AdaptiveBudgetSystem

# Store prediction
AdaptiveBudgetSystem.update_prediction("pattern_1", [2000, 2100], "Task", 1)

# Check actual execution
alert = AdaptiveBudgetSystem.check_budget_violation("pattern_1", 2500)

if alert:
    print(f"Severity: {alert.severity}")
    print(f"Expected: {alert.predicted_budget}")
    print(f"Actual: {alert.actual_budget}")
    print(f"Variance: {alert.variance:.1f}%")
else:
    print("Within budget")
```

---

### `get_alerts()`

**Description:** Retrieve all alerts for a pattern.

**Signature:**
```python
@classmethod
def get_alerts(pattern_key: str = None) -> List[BudgetAlert]
```

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `pattern_key` | str | No | None | Pattern identifier (None = all patterns) |

**Returns:** List of `BudgetAlert` objects

**Examples:**
```python
# Get alerts for specific pattern
alerts = AdaptiveBudgetSystem.get_alerts("pattern_1")
for alert in alerts:
    print(f"{alert.severity}: {alert.variance:.0f}%")

# Get all alerts
all_alerts = AdaptiveBudgetSystem.get_alerts()
critical_alerts = [a for a in all_alerts if a.severity == "critical"]
```

---

### `get_critical_patterns()`

**Description:** Find patterns with critical budget violations.

**Signature:**
```python
@classmethod
def get_critical_patterns() -> List[Tuple[str, BudgetAlert]]
```

**Parameters:** None

**Returns:** List of (pattern_key, alert) tuples where alert is critical

**Examples:**
```python
from adaptive_learning import AdaptiveBudgetSystem

critical = AdaptiveBudgetSystem.get_critical_patterns()
print(f"Critical patterns: {len(critical)}")

for pattern_key, alert in critical:
    print(f"  {pattern_key}: {alert.variance:.0f}% over")
```

---

### `dump_state()`

**Description:** Export complete system state for analysis.

**Signature:**
```python
@classmethod
def dump_state() -> dict
```

**Parameters:** None

**Returns:**
```python
{
    "timestamp": "2025-10-27T14:30:00",
    "predictions": {
        "pattern_key": {
            "predicted_tokens": int,
            "confidence": float,
            "min_tokens": int,
            "max_tokens": int,
            "pattern_query": str,
            "pattern_level": int,
            "samples": int
        },
        ...
    },
    "trends": {
        "pattern_key": {
            "trend": str,
            "trend_percentage": float,
            "consistency": float,
            "forecasted_next": int
        },
        ...
    },
    "alerts": {
        "pattern_key": [
            {
                "severity": str,
                "predicted_budget": int,
                "actual_budget": int,
                "variance": float,
                "timestamp": str
            },
            ...
        ],
        ...
    }
}
```

**Examples:**
```python
import json
from adaptive_learning import AdaptiveBudgetSystem

# Export state
state = AdaptiveBudgetSystem.dump_state()

# Save to file
with open("adaptive_learning_state.json", "w") as f:
    json.dump(state, f, indent=2)

# Analyze
total_patterns = len(state['predictions'])
total_tokens = sum(p['predicted_tokens'] for p in state['predictions'].values())
print(f"Patterns: {total_patterns}, Total tokens: {total_tokens}")
```

---

## Data Classes

### TokenPrediction

**Description:** Result of token prediction.

**Fields:**
```python
@dataclass
class TokenPrediction:
    pattern_query: str      # Pattern name/description
    pattern_level: int      # Complexity level (1-3)
    predicted_tokens: int   # Predicted token count
    confidence: float       # 0.0-1.0 confidence score
    min_tokens: int         # Safety floor (70% of prediction)
    max_tokens: int         # Safety ceiling (130% of prediction)
    basis: str              # "historical_average" or "trend_extrapolation"
    samples: int            # Number of samples used
```

**Usage:**
```python
from adaptive_learning import BudgetPredictor

pred = BudgetPredictor.predict_budget([2000, 2100], "pattern", 1)
print(type(pred))  # <class 'adaptive_learning.TokenPrediction'>
print(pred.predicted_tokens)  # 2050
print(pred.confidence)  # 0.33-0.40
```

---

### TrendAnalysis

**Description:** Result of trend analysis.

**Fields:**
```python
@dataclass
class TrendAnalysis:
    trend: str              # "increasing", "decreasing", or "stable"
    trend_percentage: float # Rate of change per execution
    consistency: float      # 0.0-1.0 predictability score
    forecasted_next: int    # Predicted next value
    slope: float            # Linear regression slope
    intercept: float        # Linear regression intercept
```

**Usage:**
```python
from adaptive_learning import TrendAnalyzer

trend = TrendAnalyzer.analyze_trend([2000, 2100, 2050])
print(trend.trend)  # "stable"
print(trend.consistency)  # 0.92
print(trend.forecasted_next)  # 2075
```

---

### BudgetAlert

**Description:** Budget violation alert.

**Fields:**
```python
@dataclass
class BudgetAlert:
    pattern_query: str      # Pattern name
    predicted_budget: int   # Expected tokens
    actual_budget: int      # Actual tokens used
    variance: float         # Percentage over budget
    severity: str           # "info", "warning", or "critical"
    timestamp: str          # ISO timestamp
```

**Usage:**
```python
from adaptive_learning import AdaptiveBudgetSystem

AdaptiveBudgetSystem.update_prediction("p", [2000], "Task", 1)
alert = AdaptiveBudgetSystem.check_budget_violation("p", 2400)
if alert:
    print(alert.severity)  # "warning"
    print(alert.variance)  # 20.0
```

---

## Constants and Defaults

### BudgetPredictor Constants

```python
class BudgetPredictor:
    MIN_SAMPLES_FOR_PREDICTION = 3      # Samples for reasonable confidence
    CONFIDENCE_THRESHOLD_HIGH = 0.8     # Threshold for "high" confidence
    CONFIDENCE_THRESHOLD_MEDIUM = 0.5   # Threshold for "medium" confidence
    MIN_CONFIDENCE = 0.3                # Minimum confidence floor
    MAX_CONFIDENCE = 1.0                # Maximum confidence ceiling
    CONFIDENCE_BONUS_SAMPLES = {
        1: 0.30,   # 1 sample: 30% bonus
        2: 0.33,   # 2 samples: 33% bonus
        3: 0.50,   # 3 samples: 50% bonus
        5: 0.60,   # 5 samples: 60% bonus
        10: 0.70,  # 10 samples: 70% bonus
        # 20+: 80% bonus
    }
    MIN_TOKENS_SAFETY_RATIO = 0.70      # 70% of prediction (floor)
    MAX_TOKENS_SAFETY_RATIO = 1.30      # 130% of prediction (ceiling)
```

### TrendAnalyzer Constants

```python
class TrendAnalyzer:
    TREND_THRESHOLD = 0.05              # 5% change = trend boundary
    MAX_CONSISTENCY = 1.0               # Perfect consistency score
    MIN_CONSISTENCY = 0.0               # Zero consistency
```

### Context Multipliers

```python
CONTEXT_MULTIPLIERS = {
    "education": 0.9,          # 10% savings
    "architecture": 1.2,       # 20% increase
    "implementation": 1.1,     # 10% increase
    "": 1.0,                   # Default, no change
}
```

### Alert Severity Thresholds

```python
ALERT_THRESHOLDS = {
    "info": 0.15,              # 0-15% over
    "warning": 0.30,           # 15-30% over
    "critical": float('inf'),  # >30% over
}
```

---

## Summary

| Class | Primary Methods | Use Case |
|-------|-----------------|----------|
| `BudgetPredictor` | `predict_budget()`, `predict_with_context()` | Single prediction |
| `TrendAnalyzer` | `analyze_trend()` | Trend detection |
| `AdaptiveBudgetSystem` | All others | Multi-pattern management |

**Common Usage Pattern:**
```python
from adaptive_learning import (
    BudgetPredictor,
    TrendAnalyzer,
    AdaptiveBudgetSystem
)

# Single prediction
pred = BudgetPredictor.predict_budget([2000, 2100], "pattern", 1)

# Track multiple patterns
AdaptiveBudgetSystem.update_prediction("p1", history1, "Task 1", 1)
AdaptiveBudgetSystem.update_prediction("p2", history2, "Task 2", 2)

# Monitor budgets
alert = AdaptiveBudgetSystem.check_budget_violation("p1", actual)

# Export for analysis
state = AdaptiveBudgetSystem.dump_state()
```
