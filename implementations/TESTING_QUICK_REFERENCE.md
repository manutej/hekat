# Adaptive Learning System - Testing Quick Reference

## Quick Start

```bash
# Run all tests
python3 test_adaptive_learning.py          # 29 basic tests, 100% pass rate
python3 advanced_testing_guide.py          # 12 advanced scenarios
```

## Interactive Python Testing

### Test 1: Simple Prediction
```python
from adaptive_learning import *

history = [2000, 2100, 2050, 2150, 2080]
pred = BudgetPredictor.predict_budget(history, "explain_jwt", 1)

print(f"Predicted: {pred.predicted_tokens} tokens")
print(f"Confidence: {pred.confidence:.0%}")
print(f"Range: {pred.min_tokens}-{pred.max_tokens}")
```

### Test 2: Trend Analysis
```python
from adaptive_learning import *

history = [2000, 2200, 2400, 2600, 2800]  # Increasing
trend = TrendAnalyzer.analyze_trend(history)

print(f"Trend: {trend.trend}")
print(f"Rate: {trend.trend_percentage:.1f}% per step")
print(f"Forecast next: {trend.forecasted_next}")
```

### Test 3: Volatility Detection
```python
from adaptive_learning import *

volatile = [1000, 5000, 800, 4500, 900, 4800, 1100]
stable = [2000, 2100, 2050, 2150, 2080]

v_trend = TrendAnalyzer.analyze_trend(volatile)
s_trend = TrendAnalyzer.analyze_trend(stable)

print(f"Volatile consistency: {v_trend.consistency:.1%}")
print(f"Stable consistency:   {s_trend.consistency:.1%}")
```

### Test 4: Context-Aware Prediction
```python
from adaptive_learning import *

history = [2000, 2100, 2050]

for context in ["education", "architecture", "implementation"]:
    pred = BudgetPredictor.predict_with_context(history, 2, context)
    print(f"{context:15s} -> {pred.predicted_tokens:5d} tokens")
```

### Test 5: Budget Violation Alert
```python
from adaptive_learning import *

# Set up pattern
history = [2000, 2100, 2050, 2150]
AdaptiveBudgetSystem.update_prediction(
    "test_pattern", history, "explain JWT", 1
)

# Simulate execution over budget
actual_tokens = 2500
alert = AdaptiveBudgetSystem.check_budget_violation(
    "test_pattern", actual_tokens
)

if alert:
    print(f"Alert: {alert.severity}")
    print(f"Expected: {alert.predicted_budget}")
    print(f"Actual: {alert.actual_budget}")
    print(f"Variance: {alert.variance:.1f}%")
```

### Test 6: Multi-Pattern Tracking
```python
from adaptive_learning import *

patterns = {
    "query_a": [2000, 2100, 2050],
    "query_b": [3000, 3200, 2900],
    "query_c": [4000, 3900, 4100],
}

for name, history in patterns.items():
    AdaptiveBudgetSystem.update_prediction(
        name, history, f"Query {name}", 1
    )

state = AdaptiveBudgetSystem.dump_state()
print(f"Total patterns: {len(state['predictions'])}")
print(f"Total tokens: {sum(p['predicted_tokens'] for p in state['predictions'].values())}")
```

### Test 7: Confidence Growth
```python
from adaptive_learning import *

initial = [2000, 2100]
additions = [2050, 2150, 2080, 2090, 2110, 2070, 2095]

print("Confidence improvement as data grows:")
for i, new_val in enumerate(additions):
    current = initial + additions[:i+1]
    pred = BudgetPredictor.predict_budget(current, "test", 1)
    print(f"  {len(current)} samples: {pred.confidence:.1%}")
```

### Test 8: State Export
```python
from adaptive_learning import *

# Build some state
AdaptiveBudgetSystem.update_prediction(
    "pattern_1", [2000, 2100], "Query 1", 1
)
AdaptiveBudgetSystem.update_trend(
    "pattern_1", [2000, 2100], "Query 1", 1
)

# Export
state = AdaptiveBudgetSystem.dump_state()

import json
print(json.dumps(state, indent=2))
```

### Test 9: Anomaly Detection
```python
from adaptive_learning import *

normal = [2000, 2100, 2050, 2150, 2080]
anomaly = 5500

pred = BudgetPredictor.predict_budget(normal, "test", 1)

exceeds_max = anomaly > pred.max_tokens
variance = ((anomaly - pred.predicted_tokens) / pred.predicted_tokens) * 100

print(f"Normal expected: {pred.predicted_tokens}")
print(f"Anomalous value: {anomaly}")
print(f"Exceeds pessimistic max: {exceeds_max}")
print(f"Variance: {variance:.1f}%")
```

### Test 10: Phase 4 Integration
```python
from adaptive_learning import *
from task_relay_consciousness import TaskRelayConsciousnessIntegration

# Simulate Phase 4 checkpoint data
checkpoint = TaskRelayConsciousnessIntegration.create_checkpoint(
    relay_number=1,
    agent_name="researcher",
    pre_tokens=50000,
    post_tokens=47500,
    expected_tokens=2500
)

# Extract tokens used
actual_tokens = abs(checkpoint.token.delta)

# Feed to Phase 5
AdaptiveBudgetSystem.update_prediction(
    "researcher_phase",
    [actual_tokens, actual_tokens + 100, actual_tokens - 50],
    "Researcher execution",
    2
)

# Check prediction
pred = AdaptiveBudgetSystem.get_prediction("researcher_phase")
print(f"Researcher predicted: {pred.predicted_tokens}")
```

## Test Result Interpretation Guide

### Confidence Ranges
```
0.0-0.3   = Minimal data, high uncertainty
0.3-0.5   = Limited samples or volatile data
0.5-0.7   = Reasonable prediction, some variance
0.7-0.9   = Good data quality, reliable prediction
0.9-1.0   = Excellent consistency, very reliable
```

### Trend Classification
```
Increasing  = trend_percentage > 5%   (getting less efficient)
Stable      = -5% ≤ trend_percentage ≤ 5%  (consistent)
Decreasing  = trend_percentage < -5%  (getting more efficient)
```

### Alert Severity
```
Info        = 0-15% over budget    (normal variance, monitor)
Warning     = 15-30% over budget   (investigate, optimize)
Critical    = >30% over budget     (immediate action)
```

### Consistency Score
```
0.0-0.3   = Highly volatile, unpredictable
0.3-0.7   = Moderate volatility
0.7-0.9   = Low volatility, fairly predictable
0.9-1.0   = Very stable, highly predictable
```

## Common Testing Scenarios

### Scenario 1: Find Inefficient Patterns
```python
from adaptive_learning import *

state = AdaptiveBudgetSystem.dump_state()

# Find patterns over 5000 tokens
expensive = [
    (k, v) for k, v in state['predictions'].items()
    if v['predicted_tokens'] > 5000
]

for pattern_key, pred in expensive:
    print(f"{pattern_key}: {pred['predicted_tokens']} tokens")
```

### Scenario 2: Monitor Degradation
```python
from adaptive_learning import *

trends = AdaptiveBudgetSystem.PATTERN_TRENDS

for pattern_key, trend in trends.items():
    if trend.trend == "increasing" and trend.trend_percentage > 5:
        print(f"⚠️ Degrading: {pattern_key}")
        print(f"  Rate: {trend.trend_percentage:.1f}% per step")
```

### Scenario 3: Compare Contexts
```python
from adaptive_learning import *

history = [2000, 2100, 2050, 2150]

baseline = BudgetPredictor.predict_with_context(history, 2, "general")
optimized = BudgetPredictor.predict_with_context(history, 2, "education")

savings = baseline.predicted_tokens - optimized.predicted_tokens
print(f"Potential savings by optimizing context: {savings} tokens")
```

### Scenario 4: Confidence Analysis
```python
from adaptive_learning import *

pred = BudgetPredictor.predict_budget([2000, 2100], "test", 1)

if pred.confidence > 0.8:
    print("High confidence - can safely reduce budget safety margin")
elif pred.confidence < 0.5:
    print("Low confidence - need more execution data")
else:
    print("Medium confidence - monitor before optimizing")
```

## Stress Testing

### Test with Many Patterns
```python
from adaptive_learning import *

# Clear state
AdaptiveBudgetSystem.PATTERN_PREDICTIONS.clear()

# Create 1000 patterns
for i in range(1000):
    history = [2000 + j * 100 for j in range(5)]
    AdaptiveBudgetSystem.update_prediction(
        f"pattern_{i}", history, f"Query {i}", 1
    )

# Verify performance
state = AdaptiveBudgetSystem.dump_state()
print(f"Stored patterns: {len(state['predictions'])}")
```

### Test with Large History
```python
from adaptive_learning import *

# Pattern with 1000 executions
long_history = [2000 + i * 10 for i in range(1000)]

pred = BudgetPredictor.predict_budget(long_history, "test", 1)
trend = TrendAnalyzer.analyze_trend(long_history)

print(f"Large history confidence: {pred.confidence:.1%}")
print(f"Trend detection accuracy: {trend.consistency:.1%}")
```

## Debugging Tips

### Check if Prediction is Reasonable
```python
history = [...]
pred = BudgetPredictor.predict_budget(history, "test", 1)

min_history = min(history)
max_history = max(history)
avg_history = sum(history) / len(history)

# Prediction should be near average
print(f"Min: {min_history}, Avg: {avg_history}, Max: {max_history}")
print(f"Predicted: {pred.predicted_tokens}")
assert min_history < pred.predicted_tokens < max_history
```

### Check Confidence Calculation
```python
pred = BudgetPredictor.predict_budget([2000, 2100, 2050], "test", 1)

print(f"Samples: {pred.samples}")
print(f"Confidence: {pred.confidence:.1%}")

# Rule of thumb:
# More samples = higher confidence (if consistent)
# High volatility = lower confidence
```

### Check Alert Generation
```python
# Set up
AdaptiveBudgetSystem.update_prediction("test", [2000, 2100, 2050], "q", 1)
pred = AdaptiveBudgetSystem.get_prediction("test")

# Test at each severity threshold
print(f"Budget: {pred.predicted_tokens}")
print(f"  5% under: {int(pred.predicted_tokens * 0.95)}")
print(f"  10% over: {int(pred.predicted_tokens * 1.10)}")
print(f"  20% over: {int(pred.predicted_tokens * 1.20)}")
print(f"  40% over: {int(pred.predicted_tokens * 1.40)}")
```

## Expected Results

### Good System Behavior
- Confidence ≥ 0.7 with 5+ samples of consistent data
- Trend detection accurate within ±1%
- Alerts trigger at correct thresholds
- Multi-pattern tracking has no cross-contamination
- 100-1000 patterns tracked without degradation

### Warning Signs
- Confidence stuck at 0.3 despite many samples → High volatility
- Trend reversal not detected → Algorithm issue
- Alerts triggering too frequently → Thresholds too strict
- Predictions consistently too high/low → Context issue

## Files for Testing

- `test_adaptive_learning.py` - 29 unit tests (100% pass rate)
- `advanced_testing_guide.py` - 12 advanced scenarios (92%+ pass rate)
- `ADAPTIVE_LEARNING_SYSTEM.md` - Complete system documentation
- `adaptive_learning.py` - Implementation (production-ready)

## Next Steps After Testing

1. ✓ Verify basic functionality (unit tests)
2. ✓ Test advanced scenarios (advanced tests)
3. Integrate with your application
4. Monitor predictions vs. actual execution
5. Adjust thresholds based on real-world data
6. Phase 6: Multi-Agent Optimization (coming next)
