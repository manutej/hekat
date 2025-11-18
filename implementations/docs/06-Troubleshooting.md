# Troubleshooting Guide

Common issues, diagnosis steps, and solutions.

---

## Confidence Issues

### Problem: Confidence stuck at 30% despite having 10+ samples

**Diagnosis:**
1. High volatility in data
2. Data actually unpredictable
3. Algorithm issue (less likely)

**Debugging:**
```python
from adaptive_learning import TrendAnalyzer

history = [2000, 5000, 800, 4500, 900, 4800, 1100, 5200]
trend = TrendAnalyzer.analyze_trend(history)

print(f"Consistency: {trend.consistency}")  # Should be 0.0-0.3 if volatile
print(f"Trend: {trend.trend}")  # Check if trending
```

**Solution:**
```
If consistency < 0.4:
  1. Data is naturally volatile
  2. Pattern may have variable token cost (affected by input size, etc.)
  3. Increase safety margins
  4. Investigate what causes variance
  5. Consider splitting pattern into sub-patterns

If consistency >= 0.4:
  1. Likely algorithm issue
  2. Email support with history data
  3. Meanwhile, use minimum 0.3 confidence for decisions
```

**Prevention:**
- Collect at least 3-5 consistent samples before making decisions
- Monitor consistency score, not just confidence
- If consistency low, isolate variable factors

---

### Problem: Confidence lower than expected for amount of data

**Example:** 20 samples but only 60% confidence (expect 80%+)

**Diagnosis:**
1. Data is actually volatile
2. Trending pattern (increasing/decreasing)
3. Different execution contexts mixed

**Solution:**
```python
from adaptive_learning import TrendAnalyzer, AdaptiveBudgetSystem

history = get_pattern_history()

# 1. Check consistency
trend = TrendAnalyzer.analyze_trend(history)
print(f"Consistency: {trend.consistency}")

# 2. Check for trend
if trend.trend != "stable":
    print(f"Trend detected: {trend.trend} ({trend.trend_percentage:+.1f}%/step)")
    # Trending patterns have lower confidence

# 3. Check for mixed contexts
recent_avg = sum(history[-5:]) / 5
older_avg = sum(history[:-5]) / 5
if abs(recent_avg - older_avg) > 500:
    print("⚠️ Average changed significantly - may have mixed contexts")

# 4. Accept lower confidence if natural
pred = AdaptiveBudgetSystem.get_prediction(pattern_key)
if pred.confidence >= 0.5:
    print("Confidence is acceptable for most decisions")
```

---

## Prediction Accuracy Issues

### Problem: Predictions consistently too high

**Diagnosis:**
1. Pattern is getting more efficient (trend is decreasing)
2. Context not factored in correctly
3. Historical data includes old, less efficient runs

**Debugging:**
```python
from adaptive_learning import TrendAnalyzer

history = [2500, 2400, 2300, 2200, 2100]
trend = TrendAnalyzer.analyze_trend(history)

print(f"Trend: {trend.trend}")          # Should be "decreasing"
print(f"Trend %: {trend.trend_percentage:.1f}%")
print(f"Forecast: {trend.forecasted_next}")
```

**Solutions:**

1. **If trend is decreasing (optimizations working):**
   ```python
   # Use recent data only
   history = get_recent_executions(pattern_key, count=5)
   pred = BudgetPredictor.predict_budget(history, pattern_query, level)
   # This will give lower prediction reflecting optimization
   ```

2. **If context wrong:**
   ```python
   # Predictions for education context should be lower
   pred = BudgetPredictor.predict_with_context(history, 1, "education")
   # Compare to baseline to verify 10% reduction
   ```

3. **If old data included:**
   ```python
   # Clear old history and start fresh
   AdaptiveBudgetSystem.update_prediction(
       pattern_key,
       history[-10:],  # Only last 10 executions
       pattern_query,
       level
   )
   ```

---

### Problem: Predictions consistently too low

**Diagnosis:**
1. Pattern is degrading (trend is increasing)
2. Wrong context or assumptions
3. Input changed (queries getting harder)

**Debugging:**
```python
from adaptive_learning import TrendAnalyzer

history = [2000, 2100, 2200, 2300, 2400]
trend = TrendAnalyzer.analyze_trend(history)

if trend.trend == "increasing":
    print(f"⚠️ Pattern degrading at {trend.trend_percentage:.1f}%/step")
    print(f"Next execution forecast: {trend.forecasted_next}")
```

**Solution:**
```python
# Increase safety margins for degrading patterns
from adaptive_learning import AdaptiveBudgetSystem

pred = AdaptiveBudgetSystem.get_prediction(pattern_key)

# Check if increasing
state = AdaptiveBudgetSystem.dump_state()
trend = state['trends'].get(pattern_key)

if trend and trend['trend'] == "increasing":
    # Use forecast as basis instead of average
    safe_budget = trend['forecasted_next'] * 1.3
    print(f"Degrading pattern - use budget: {safe_budget}")
else:
    safe_budget = pred.max_tokens
    print(f"Normal pattern - use budget: {safe_budget}")
```

---

## Budget Alert Issues

### Problem: Alerts trigger too frequently (false positives)

**Diagnosis:**
1. Thresholds too strict for pattern volatility
2. Safety margin too small
3. Pattern naturally has high variance

**Solution:**
```python
# Check consistency to understand volatility
from adaptive_learning import TrendAnalyzer

history = get_pattern_history()
trend = TrendAnalyzer.analyze_trend(history)

if trend.consistency < 0.5:
    print("Pattern has high natural variance")
    print("Consider accepting ±35% variance as normal")

# Manually check if alert is justified
pred = AdaptiveBudgetSystem.get_prediction(pattern_key)
print(f"Prediction: {pred.predicted_tokens}")
print(f"Safety range: {pred.min_tokens} - {pred.max_tokens}")
print(f"Variance is normal if within ±30%")
```

**Action:**
1. Review alert thresholds (currently 15% warning, 30% critical)
2. If pattern naturally volatile, increase thresholds
3. Or split pattern if some executions are different type

---

### Problem: Alerts not triggering when they should

**Diagnosis:**
1. Pattern not set up in system
2. Prediction not stored correctly
3. Budget violation checker not called

**Debugging:**
```python
from adaptive_learning import AdaptiveBudgetSystem

# 1. Check if pattern exists
state = AdaptiveBudgetSystem.dump_state()
if "pattern_key" not in state['predictions']:
    print("Pattern not found in system")
    # Need to call update_prediction first

# 2. Verify prediction stored correctly
pred = AdaptiveBudgetSystem.get_prediction("pattern_key")
if pred is None:
    print("Prediction not stored")
else:
    print(f"Stored prediction: {pred.predicted_tokens}")

# 3. Manually check budget violation
alert = AdaptiveBudgetSystem.check_budget_violation("pattern_key", 2500)
if alert:
    print(f"Alert triggered: {alert.severity}")
else:
    print("No alert - within budget")
```

**Solution:**
```python
# Ensure pattern is set up
from adaptive_learning import AdaptiveBudgetSystem

history = [2000, 2100, 2050]
AdaptiveBudgetSystem.update_prediction(
    "my_pattern",
    history,
    "My Task",
    1
)

# Verify it's stored
pred = AdaptiveBudgetSystem.get_prediction("my_pattern")
assert pred is not None, "Prediction not stored!"

# Now check alerts
alert = AdaptiveBudgetSystem.check_budget_violation("my_pattern", 2500)
```

---

## Data Quality Issues

### Problem: Single outlier skewing prediction

**Example:** 4 samples of ~2000 tokens, 1 sample of 5000 tokens (outlier)

**Diagnosis:**
1. Anomalous execution
2. Different context or input
3. System issue during that run

**Solution:**
```python
# Option 1: Remove outlier
history = [2000, 2100, 2050, 2150, 5000]  # 5000 is outlier
history_clean = [x for x in history if x < 3000]  # Remove > 3000
pred = BudgetPredictor.predict_budget(history_clean, "pattern", 1)

# Option 2: Use recent data only
history_recent = history[-4:]  # Exclude outlier if it's old
pred = BudgetPredictor.predict_budget(history_recent, "pattern", 1)

# Option 3: Split into patterns
# If outlier was different context, split:
# pattern_normal = [2000, 2100, 2050, 2150]
# pattern_complex = [5000]
```

---

### Problem: Too little data to start predictions

**Diagnosis:**
1. Only 1-2 samples collected
2. Pattern too new
3. Not enough executions yet

**Solution:**
```python
from adaptive_learning import BudgetPredictor

history = [2000, 2100]  # Only 2 samples
pred = BudgetPredictor.predict_budget(history, "pattern", 1)

print(f"Confidence: {pred.confidence:.0%}")  # Will be ~33%

if pred.confidence < 0.5:
    print("⚠️ Need more data - minimum 3-5 samples for reliable prediction")
    print("Recommendation: Collect 3 more executions before making decisions")
```

**Action:**
1. Continue collecting data
2. After 3-5 samples, confidence will improve to 70%+
3. Then safe for planning decisions

---

## Context-Related Issues

### Problem: Context adjustment not having expected effect

**Example:** Education context should reduce by 10%, but barely changed

**Diagnosis:**
1. Check context multiplier value
2. Verify context parameter is being passed
3. Base prediction might be at minimum threshold

**Debugging:**
```python
from adaptive_learning import BudgetPredictor

history = [2000, 2100, 2050]

baseline = BudgetPredictor.predict_budget(history, "pattern", 1)
education = BudgetPredictor.predict_with_context(history, 1, "education")
architecture = BudgetPredictor.predict_with_context(history, 1, "architecture")

print(f"Baseline:       {baseline.predicted_tokens}")
print(f"Education:      {education.predicted_tokens}")
print(f"Architecture:   {architecture.predicted_tokens}")

# Verify math
expected_education = baseline.predicted_tokens * 0.9
print(f"Expected education: {expected_education}")
```

**Solution:**
```python
# Ensure you're using context parameter correctly
correct = BudgetPredictor.predict_with_context(
    history,
    pattern_level=1,
    context="education"  # Named parameter
)

# If still not working, manually apply multiplier
multiplier = 0.9
manual = baseline.predicted_tokens * multiplier
```

---

### Problem: Unknown context being ignored

**Diagnosis:**
1. Context not in built-in list
2. No error raised (silent failure)
3. Prediction returned with default multiplier (1.0x)

**Solution:**
```python
# Built-in contexts
VALID_CONTEXTS = ["education", "architecture", "implementation", ""]

context = "unknown_context"
if context not in VALID_CONTEXTS:
    print(f"⚠️ Context '{context}' not recognized")
    print(f"Valid contexts: {VALID_CONTEXTS}")
    context = ""  # Use default

pred = BudgetPredictor.predict_with_context(history, 1, context)
```

---

## State Export Issues

### Problem: State export is empty or incomplete

**Diagnosis:**
1. No patterns stored yet
2. `update_prediction()` not called
3. Wrong pattern keys in state vs usage

**Debugging:**
```python
from adaptive_learning import AdaptiveBudgetSystem

state = AdaptiveBudgetSystem.dump_state()

print(f"Patterns: {len(state['predictions'])}")
print(f"Trends: {len(state.get('trends', {}))}")
print(f"Alerts: {len(state.get('alerts', {}))}")

for key in state['predictions'].keys():
    print(f"  - {key}")
```

**Solution:**
```python
# Ensure you've called update_prediction()
AdaptiveBudgetSystem.update_prediction(
    "my_pattern",
    [2000, 2100],
    "Task",
    1
)

# Now export should show it
state = AdaptiveBudgetSystem.dump_state()
assert "my_pattern" in state['predictions']
```

---

## Performance Issues

### Problem: System slow with many patterns (100+)

**Diagnosis:**
1. Each prediction recalculates from scratch
2. No caching of trend calculations
3. Large state export operation

**Solution:**
```python
# Option 1: Batch operations
# Instead of updating one at a time
for pattern, history in patterns.items():
    AdaptiveBudgetSystem.update_prediction(pattern, history, "", 1)

# Option 2: Selective state export
# Don't dump entire state, query specific patterns
pred = AdaptiveBudgetSystem.get_prediction("specific_pattern")
# Much faster than dump_state()

# Option 3: Cache frequently accessed patterns
# Store last 50 pattern states in memory
cached_state = {}
```

**Expected Performance:**
- Single prediction: < 1ms
- 100 patterns: < 100ms total
- State export: ~10-50ms depending on size

---

## Integration Issues

### Problem: Phase 4 data not reaching Phase 5

**Diagnosis:**
1. Phase 4 checkpoints not created
2. Token extraction code missing
3. update_prediction() not called

**Solution:**
```python
from task_relay_consciousness import TaskRelayConsciousnessIntegration
from adaptive_learning import AdaptiveBudgetSystem

# Check Phase 4 produces checkpoint
checkpoint = TaskRelayConsciousnessIntegration.create_checkpoint(...)
print(f"Checkpoint created: {checkpoint is not None}")
print(f"Token delta: {checkpoint.token.delta}")

# Extract and feed to Phase 5
tokens_used = abs(checkpoint.token.delta)
pattern_key = f"agent_{checkpoint.agent_name}"

AdaptiveBudgetSystem.update_prediction(
    pattern_key,
    [tokens_used],  # First execution
    f"Agent {checkpoint.agent_name}",
    checkpoint.relay_number
)

# Verify in Phase 5
state = AdaptiveBudgetSystem.dump_state()
print(f"Pattern stored: {pattern_key in state['predictions']}")
```

---

### Problem: Phase 6 not finding Phase 5 predictions

**Diagnosis:**
1. Pattern key mismatch
2. Insufficient data in Phase 5
3. Confidence below minimum threshold

**Solution:**
```python
# 1. Check pattern keys match exactly
# Phase 5 stores: "agent_researcher_relay_1"
# Phase 6 queries: "agent_researcher_relay_1"
# They must match character-for-character

# 2. Ensure sufficient data
state = AdaptiveBudgetSystem.dump_state()
if len(state['predictions']) < 1:
    print("No predictions in Phase 5 yet")

# 3. Check confidence threshold
MIN_CONFIDENCE = 0.70
for pattern_key, pred in state['predictions'].items():
    if pred['confidence'] < MIN_CONFIDENCE:
        print(f"Low confidence: {pattern_key} ({pred['confidence']:.0%})")
```

---

## Getting Help

### Quick Diagnostics

Run this to check system health:

```python
from adaptive_learning import AdaptiveBudgetSystem, BudgetPredictor, TrendAnalyzer

def diagnose_system():
    print("🔍 System Diagnostics\n")

    # 1. Core functions work
    try:
        pred = BudgetPredictor.predict_budget([2000, 2100], "test", 1)
        print("✅ BudgetPredictor works")
    except Exception as e:
        print(f"❌ BudgetPredictor error: {e}")

    try:
        trend = TrendAnalyzer.analyze_trend([2000, 2100])
        print("✅ TrendAnalyzer works")
    except Exception as e:
        print(f"❌ TrendAnalyzer error: {e}")

    # 2. State management works
    try:
        AdaptiveBudgetSystem.update_prediction("test", [2000, 2100], "Test", 1)
        pred = AdaptiveBudgetSystem.get_prediction("test")
        print("✅ State management works")
    except Exception as e:
        print(f"❌ State management error: {e}")

    # 3. Export works
    try:
        state = AdaptiveBudgetSystem.dump_state()
        print(f"✅ State export works ({len(state['predictions'])} patterns)")
    except Exception as e:
        print(f"❌ Export error: {e}")

diagnose_system()
```

### Common Fixes Checklist

- [ ] Ran `python3 test_adaptive_learning.py` - all pass?
- [ ] Have 3+ historical data points for predictions?
- [ ] Checked confidence score > 50% before making decisions?
- [ ] Verified pattern keys match between calls?
- [ ] Checked for trends (increasing/decreasing patterns)?
- [ ] Confirmed data is from same context?
- [ ] Isolated any outlier data points?
- [ ] Reviewed consistency score for volatility?

---

## Report Issues

If you can't resolve an issue:

1. **Run diagnostics** (see above)
2. **Include in report:**
   - Exact error message (if any)
   - Code that reproduces issue
   - Diagnostic output
   - What you expected vs. actual behavior
3. **Provide:**
   - Sample data (history, predictions, etc.)
   - System state export
   - Steps to reproduce

Example issue report:
```
Problem: Prediction seems wrong
Code: pred = BudgetPredictor.predict_budget([2000, 2100, 3000], "task", 1)
Expected: ~2367 (average)
Actual: 2050
System state: [dump_state() output]
Diagnostics: [diagnose_system() output]
```
