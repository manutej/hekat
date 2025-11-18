# Getting Started with Adaptive Learning System

## Installation & Setup

### Step 1: Verify Files Are Present

The system requires two files in your HEKAT implementations directory:

```bash
ls -la /Users/manu/Documents/LUXOR/PROJECTS/hekat/implementations/

adaptive_learning.py              # Core system (500+ lines)
test_adaptive_learning.py         # Unit tests (100% pass rate)
advanced_testing_guide.py         # Advanced scenarios (92%+ pass rate)
```

### Step 2: Verify Tests Pass

Run the basic test suite to confirm everything works:

```bash
cd /Users/manu/Documents/LUXOR/PROJECTS/hekat/implementations/
python3 test_adaptive_learning.py
```

**Expected output:**
```
🧠 HEKAT ADAPTIVE LEARNING SYSTEM TESTS
✓ Test 1: Token Prediction - Simple
✓ Test 2: Token Prediction - Minimal Data
...
✓ Test 29: State Export

TEST SUMMARY
Total Tests: 29
✓ Passed: 29
❌ Failed: 0
Success Rate: 100%
```

If all tests pass, you're ready to go!

---

## Your First Prediction (5 minutes)

### The Simplest Example

Open a Python terminal in the implementations directory:

```bash
cd /Users/manu/Documents/LUXOR/PROJECTS/hekat/implementations/
python3
```

Now type this code:

```python
from adaptive_learning import *

# Your historical token data (from previous executions)
history = [2000, 2100, 2050, 2150, 2080]

# Get a prediction
prediction = BudgetPredictor.predict_budget(history, "explain_jwt", 1)

# Print results
print(f"Predicted tokens: {prediction.predicted_tokens}")
print(f"Confidence: {prediction.confidence:.0%}")
print(f"Safe budget: {prediction.max_tokens}")
```

**Output:**
```
Predicted tokens: 2076
Confidence: 89%
Safe budget: 2699
```

**What this means:**
- Next execution will likely use ~2,076 tokens
- The system is 89% confident in this prediction
- To be safe, budget 2,699 tokens (30% safety margin)

---

## The Three Core Functions

### 1. Make a Prediction

```python
from adaptive_learning import BudgetPredictor

history = [2000, 2100, 2050]
pred = BudgetPredictor.predict_budget(history, "my_pattern", 1)

print(f"Prediction: {pred.predicted_tokens}")
print(f"Confidence: {pred.confidence:.1%}")
print(f"Min safe: {pred.min_tokens}")
print(f"Max safe: {pred.max_tokens}")
```

### 2. Analyze Trends

```python
from adaptive_learning import TrendAnalyzer

history = [2000, 2200, 2400, 2600, 2800]  # Increasing
trend = TrendAnalyzer.analyze_trend(history)

print(f"Trend: {trend.trend}")  # "increasing"
print(f"Rate: {trend.trend_percentage:.1f}%")  # Rate per execution
print(f"Consistency: {trend.consistency:.1%}")  # Predictability
print(f"Next forecast: {trend.forecasted_next}")  # Predicted next value
```

### 3. Track Multiple Patterns

```python
from adaptive_learning import AdaptiveBudgetSystem

# Pattern 1
pattern1_history = [2000, 2100, 2050]
AdaptiveBudgetSystem.update_prediction(
    "pattern_1", pattern1_history, "Explain JWT", 1
)

# Pattern 2
pattern2_history = [3000, 3100, 2950]
AdaptiveBudgetSystem.update_prediction(
    "pattern_2", pattern2_history, "Build API", 2
)

# Get a prediction for pattern 1
pred = AdaptiveBudgetSystem.get_prediction("pattern_1")
print(f"Pattern 1 prediction: {pred.predicted_tokens}")

# Get a prediction for pattern 2
pred = AdaptiveBudgetSystem.get_prediction("pattern_2")
print(f"Pattern 2 prediction: {pred.predicted_tokens}")
```

---

## Common Tasks

### Task 1: Predict with Context

Different domains use different amounts of tokens. Adjust for context:

```python
from adaptive_learning import BudgetPredictor

history = [2000, 2100, 2050]

# Without context (baseline)
baseline = BudgetPredictor.predict_budget(history, "my_pattern", 1)
print(f"Baseline: {baseline.predicted_tokens}")  # 2050

# With education context (10% cheaper)
education = BudgetPredictor.predict_with_context(history, 1, "education")
print(f"Education: {education.predicted_tokens}")  # ~1845

# With architecture context (20% more expensive)
architecture = BudgetPredictor.predict_with_context(history, 1, "architecture")
print(f"Architecture: {architecture.predicted_tokens}")  # ~2460
```

**Context multipliers:**
- `education`: 0.9x (10% savings)
- `architecture`: 1.2x (20% more)
- `implementation`: 1.1x (10% more)
- (default): 1.0x (no change)

### Task 2: Detect Budget Violations

Check if execution exceeded predicted budget:

```python
from adaptive_learning import AdaptiveBudgetSystem

# Set up pattern
history = [2000, 2100, 2050, 2150]
AdaptiveBudgetSystem.update_prediction("my_pattern", history, "Task", 1)

# Simulate execution that used more tokens
actual_tokens = 2500

# Check for violation
alert = AdaptiveBudgetSystem.check_budget_violation("my_pattern", actual_tokens)

if alert:
    print(f"Alert: {alert.severity}")  # "warning" or "critical"
    print(f"Expected: {alert.predicted_budget}")
    print(f"Actual: {alert.actual_budget}")
    print(f"Variance: {alert.variance:.1f}%")
else:
    print("No alert - within budget")
```

**Severity levels:**
- `info`: 0-15% over (monitor)
- `warning`: 15-30% over (investigate)
- `critical`: >30% over (immediate action)

### Task 3: Find Inefficient Patterns

Get all patterns and their costs:

```python
from adaptive_learning import AdaptiveBudgetSystem

# Get complete system state
state = AdaptiveBudgetSystem.dump_state()

# Sort by cost (most expensive first)
expensive = sorted(
    state['predictions'].items(),
    key=lambda x: x[1]['predicted_tokens'],
    reverse=True
)

print("Most expensive patterns:")
for pattern_key, pred in expensive[:5]:
    print(f"  {pattern_key}: {pred['predicted_tokens']} tokens")
```

### Task 4: Track Confidence Growth

See how confidence improves with more data:

```python
from adaptive_learning import BudgetPredictor

data = [2000, 2100, 2050, 2150, 2080, 2090, 2110, 2070, 2095]

print("Confidence as samples increase:")
for i in range(2, len(data) + 1):
    history = data[:i]
    pred = BudgetPredictor.predict_budget(history, "test", 1)
    print(f"  {i} samples: {pred.confidence:.0%} confidence")
```

**Expected output:**
```
Confidence as samples increase:
  2 samples: 33% confidence
  3 samples: 89% confidence
  4 samples: 90% confidence
  5 samples: 91% confidence
  ...
  9 samples: 95% confidence
```

### Task 5: Compare Two Versions

See if an optimization reduced token usage:

```python
from adaptive_learning import BudgetPredictor, AdaptiveBudgetSystem

# Version 1 (before optimization)
history_v1 = [2500, 2520, 2480, 2510, 2490]
pred_v1 = BudgetPredictor.predict_budget(history_v1, "pattern_v1", 1)

# Version 2 (after optimization)
history_v2 = [2100, 2120, 2080, 2110, 2090]
pred_v2 = BudgetPredictor.predict_budget(history_v2, "pattern_v2", 1)

# Calculate savings
tokens_saved = pred_v1.predicted_tokens - pred_v2.predicted_tokens
percent_saved = (tokens_saved / pred_v1.predicted_tokens) * 100

print(f"Before: {pred_v1.predicted_tokens} tokens")
print(f"After: {pred_v2.predicted_tokens} tokens")
print(f"Saved: {tokens_saved} tokens ({percent_saved:.1f}%)")
```

---

## Understanding the Numbers

### Confidence Score Guide

```
0-30%   | ⚠️  RED ZONE - Need more data
        | Don't make decisions yet, need 5+ samples

30-50%  | 🟡 YELLOW - Limited confidence
        | Use with caution, monitor closely

50-70%  | 🟢 GREEN - Reasonable confidence
        | Good for general planning

70-90%  | 💚 GOOD - High confidence
        | Safe for optimization decisions

90-100% | 🎯 EXCELLENT - Very high confidence
        | Can optimize aggressively
```

### Trend Interpretation

```
Trend              | Trend %  | Meaning
───────────────────────────────────────────────
Increasing         | >5%      | Getting worse (less efficient)
Stable             | -5% - 5% | Consistent, predictable
Decreasing         | <-5%     | Getting better (optimizing)
```

### Consistency Interpretation

```
Consistency Score | Meaning
──────────────────────────────────────────
0.0 - 0.3        | Highly unpredictable (avoid optimizing)
0.3 - 0.7        | Moderate variance (be cautious)
0.7 - 0.9        | Fairly consistent (reasonable for planning)
0.9 - 1.0        | Very stable (safe to optimize)
```

---

## Quick Reference Checklist

**Before deploying to production:**

- [ ] Run `python3 test_adaptive_learning.py` - All tests pass
- [ ] Have at least 3-5 historical data points per pattern
- [ ] Confidence score is > 70% for key patterns
- [ ] Trend is stable (not increasing)
- [ ] Budget alert levels are tuned to your needs
- [ ] Understand what each metric means

**When making optimization decisions:**

- [ ] Confidence > 70% (safe to optimize)
- [ ] Consistency > 0.7 (predictable pattern)
- [ ] Trend is stable (not degrading)
- [ ] Have 2+ versions to compare
- [ ] Track before/after metrics

---

## Troubleshooting

### Problem: Low Confidence (30%)

**Cause:** Not enough data points
**Solution:** Collect 5-10 historical data points instead of 2-3

```python
# Too little data (low confidence)
history = [2000, 2100]
pred = BudgetPredictor.predict_budget(history, "test", 1)
print(pred.confidence)  # 30-40%

# Better - more data (higher confidence)
history = [2000, 2100, 2050, 2150, 2080, 2090, 2110]
pred = BudgetPredictor.predict_budget(history, "test", 1)
print(pred.confidence)  # 70-80%+
```

### Problem: Confidence Stuck at Low Level Despite Many Samples

**Cause:** Data is volatile (inconsistent)
**Solution:** Check trend and consistency

```python
trend = TrendAnalyzer.analyze_trend(history)
print(f"Consistency: {trend.consistency}")  # If < 0.5, data is volatile

# If volatile, pattern may be inherently unpredictable
# Either accept lower confidence or look for causes of volatility
```

### Problem: Prediction Seems Wrong

**Check:**
1. Is min < prediction < max? ✓
2. Is prediction near average of history? ✓
3. Are you looking at the right pattern? ✓

```python
print(f"Min: {min(history)}, Avg: {sum(history)/len(history)}, Max: {max(history)}")
print(f"Prediction: {pred.predicted_tokens}")
# Prediction should be close to average
```

---

## Next Steps

1. **Run the basic examples above** (5-10 minutes)
2. **Add your own data** - Use token counts from your patterns
3. **Track a pattern over time** - See confidence grow as you add samples
4. **Make a decision** - Use high-confidence predictions for optimization
5. **Read the advanced docs** - See more complex use cases

**Recommended reading order:**
1. ✅ **This file** (Getting Started)
2. **02-Concepts.md** (Understand how it works)
3. **04-UsageExamples.md** (Copy-paste ready examples)
4. **03-APIReference.md** (All functions reference)
5. **05-Integration.md** (Phase 4/6 integration)

---

## Get Help

- **What does this concept mean?** → Read **02-Concepts.md**
- **How do I do X?** → Check **04-UsageExamples.md**
- **What functions are available?** → See **03-APIReference.md**
- **Something isn't working** → Check **06-Troubleshooting.md**
- **How does it integrate?** → Read **05-Integration.md**
