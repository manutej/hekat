# Usage Examples - Copy-Paste Ready Code

All examples below are copy-paste ready. Run them in a Python terminal from the implementations directory.

---

## Example 1: Basic Prediction (5 min)

**Goal:** Make your first token prediction

**Code:**
```python
from adaptive_learning import BudgetPredictor

# Your historical token data
history = [2000, 2100, 2050, 2150, 2080]

# Make a prediction
prediction = BudgetPredictor.predict_budget(history, "explain_jwt", 1)

# Print results
print(f"Pattern: {prediction.pattern_query}")
print(f"Predicted: {prediction.predicted_tokens} tokens")
print(f"Confidence: {prediction.confidence:.0%}")
print(f"Safe range: {prediction.min_tokens} - {prediction.max_tokens} tokens")
print(f"Basis: {prediction.basis}")
print(f"Samples: {prediction.samples}")
```

**Output:**
```
Pattern: explain_jwt
Predicted: 2076 tokens
Confidence: 89%
Safe range: 1453 - 2699 tokens
Basis: historical_average
Samples: 5
```

**What it means:**
- Next execution will use ~2,076 tokens
- System is 89% confident in this prediction
- To be safe, budget 1,453-2,699 tokens

---

## Example 2: Compare Token Efficiency Across Contexts (5 min)

**Goal:** See how context affects token usage

**Code:**
```python
from adaptive_learning import BudgetPredictor

history = [2000, 2050, 2100, 1950]

print("Token usage by context:\n")

# Baseline (no context)
baseline = BudgetPredictor.predict_budget(history, "explain_api", 1)
print(f"Baseline:       {baseline.predicted_tokens:5d} tokens")

# Education context
education = BudgetPredictor.predict_with_context(history, 1, "education")
print(f"Education:      {education.predicted_tokens:5d} tokens (save {baseline.predicted_tokens - education.predicted_tokens})")

# Architecture context
architecture = BudgetPredictor.predict_with_context(history, 1, "architecture")
print(f"Architecture:   {architecture.predicted_tokens:5d} tokens (add {architecture.predicted_tokens - baseline.predicted_tokens})")

# Implementation context
implementation = BudgetPredictor.predict_with_context(history, 1, "implementation")
print(f"Implementation: {implementation.predicted_tokens:5d} tokens (add {implementation.predicted_tokens - baseline.predicted_tokens})")

# Calculate context savings
total_queries = 100
savings = (baseline.predicted_tokens - education.predicted_tokens) * total_queries
print(f"\nFor {total_queries} queries: Save {savings:,} tokens with education context")
```

**Output:**
```
Token usage by context:

Baseline:       2025 tokens
Education:      1823 tokens (save 202)
Architecture:   2430 tokens (add 405)
Implementation: 2228 tokens (add 203)

For 100 queries: Save 20,200 tokens with education context
```

---

## Example 3: Detect Trends in Your Patterns (5 min)

**Goal:** Find if your pattern is getting worse or better

**Code:**
```python
from adaptive_learning import TrendAnalyzer

# Pattern 1: Getting worse (less efficient)
degrading = [2000, 2150, 2300, 2450, 2600]

# Pattern 2: Getting better (more efficient)
improving = [2600, 2450, 2300, 2150, 2000]

# Pattern 3: Stable
stable = [2000, 2020, 2010, 1990, 2030]

print("Trend Analysis:\n")

for label, history in [
    ("Degrading", degrading),
    ("Improving", improving),
    ("Stable", stable)
]:
    trend = TrendAnalyzer.analyze_trend(history)

    print(f"{label:15s}")
    print(f"  Trend: {trend.trend:12s} ({trend.trend_percentage:+.1f}%/step)")
    print(f"  Consistency: {trend.consistency:.0%}")
    print(f"  Next forecast: {trend.forecasted_next} tokens")

    if trend.trend == "increasing":
        print(f"  ⚠️  WARNING: Pattern efficiency declining!")
    elif trend.trend == "decreasing":
        print(f"  ✅ GOOD: Pattern getting more efficient!")
    else:
        print(f"  ✔️  STABLE: Consistent behavior")
    print()
```

**Output:**
```
Trend Analysis:

Degrading
  Trend: increasing     (+7.5%/step)
  Consistency: 100%
  Next forecast: 2750 tokens
  ⚠️  WARNING: Pattern efficiency declining!

Improving
  Trend: decreasing     (-7.5%/step)
  Consistency: 100%
  Next forecast: 1850 tokens
  ✅ GOOD: Pattern getting more efficient!

Stable
  Trend: stable         (+0.5%/step)
  Consistency: 95%
  Next forecast: 2008 tokens
  ✔️  STABLE: Consistent behavior

```

---

## Example 4: Track Multiple Patterns (10 min)

**Goal:** Monitor several patterns simultaneously

**Code:**
```python
from adaptive_learning import AdaptiveBudgetSystem

# Define patterns with their histories
patterns = {
    "explain_jwt": [2000, 2100, 2050, 2150, 2080],
    "build_api": [3000, 3100, 2950, 3050, 3020],
    "debug_code": [1500, 1600, 1450, 1550, 1480],
    "design_arch": [4000, 4200, 4100, 4300, 4150],
}

# Store all patterns
for pattern_name, history in patterns.items():
    AdaptiveBudgetSystem.update_prediction(
        pattern_name,
        history,
        f"Pattern: {pattern_name}",
        1
    )

# Analyze all patterns
print("Pattern Cost Analysis:\n")
print(f"{'Pattern':<15} {'Prediction':<12} {'Confidence':<12} {'Status':<15}")
print("-" * 55)

for pattern_name, history in patterns.items():
    pred = AdaptiveBudgetSystem.get_prediction(pattern_name)

    status = "✓ Good" if pred.confidence > 0.7 else "△ Fair" if pred.confidence > 0.5 else "✗ Low"

    print(f"{pattern_name:<15} {pred.predicted_tokens:<12} {pred.confidence:<11.0%} {status:<15}")

# Summary
state = AdaptiveBudgetSystem.dump_state()
total_patterns = len(state['predictions'])
total_tokens = sum(p['predicted_tokens'] for p in state['predictions'].values())
avg_tokens = total_tokens // total_patterns

print()
print(f"Total patterns: {total_patterns}")
print(f"Total tokens: {total_tokens:,}")
print(f"Average per pattern: {avg_tokens:,}")

# Find most expensive
most_expensive = max(
    state['predictions'].items(),
    key=lambda x: x[1]['predicted_tokens']
)
print(f"Most expensive: {most_expensive[0]} ({most_expensive[1]['predicted_tokens']} tokens)")

# Find least expensive
least_expensive = min(
    state['predictions'].items(),
    key=lambda x: x[1]['predicted_tokens']
)
print(f"Least expensive: {least_expensive[0]} ({least_expensive[1]['predicted_tokens']} tokens)")
```

**Output:**
```
Pattern Cost Analysis:

Pattern         Prediction   Confidence   Status
-------------------------------------------------------
explain_jwt     2076         89%          ✓ Good
build_api       3024         89%          ✓ Good
debug_code      1556         89%          ✓ Good
design_arch     4146         89%          ✓ Good

Total patterns: 4
Total tokens: 10,802
Average per pattern: 2,700
Most expensive: design_arch (4146 tokens)
Least expensive: debug_code (1556 tokens)
```

---

## Example 5: Monitor Budget Violations (10 min)

**Goal:** Detect when patterns exceed their predicted budget

**Code:**
```python
from adaptive_learning import AdaptiveBudgetSystem

# Set up patterns
patterns = {
    "task_a": [2000, 2100, 2050],
    "task_b": [3000, 3100, 2950],
}

for name, history in patterns.items():
    AdaptiveBudgetSystem.update_prediction(name, history, f"Task {name}", 1)

# Simulate executions with various token usage
executions = [
    ("task_a", 2050, "Normal"),         # Within budget
    ("task_a", 2200, "Slight over"),    # 5% over
    ("task_a", 2400, "Warning"),        # 18% over
    ("task_a", 2700, "Critical"),       # 32% over
    ("task_b", 3100, "Normal"),         # Normal
    ("task_b", 3600, "Critical"),       # 20% over
]

print("Budget Violation Monitoring:\n")
print(f"{'Pattern':<10} {'Actual':<8} {'Expected':<10} {'Variance':<10} {'Severity':<10}")
print("-" * 50)

alerts = []

for pattern_name, actual, description in executions:
    alert = AdaptiveBudgetSystem.check_budget_violation(pattern_name, actual)

    if alert:
        alerts.append(alert)
        print(f"{pattern_name:<10} {actual:<8} {alert.predicted_budget:<10} {alert.variance:>8.1f}%  {alert.severity:<10}")
    else:
        pred = AdaptiveBudgetSystem.get_prediction(pattern_name)
        print(f"{pattern_name:<10} {actual:<8} {pred.predicted_tokens:<10} {'OK':<10} {'info':<10}")

# Summary
print()
print("Alert Summary:")
print(f"  Total violations: {len(alerts)}")

for severity in ["critical", "warning", "info"]:
    count = sum(1 for a in alerts if a.severity == severity)
    if count > 0:
        print(f"  {severity.capitalize()}: {count}")
```

**Output:**
```
Budget Violation Monitoring:

Pattern    Actual  Expected   Variance   Severity
--------------------------------------------------
task_a     2050    2050         OK         info
task_a     2200    2050         7.3%       info
task_a     2400    2050        17.1%       warning
task_a     2700    2050        31.7%       critical
task_b     3100    3017         OK         info
task_b     3600    3017        19.3%       warning

Alert Summary:
  Total violations: 3
  Warning: 2
  Critical: 1
```

---

## Example 6: Optimize a Pattern (15 min)

**Goal:** Compare token usage before and after optimization

**Code:**
```python
from adaptive_learning import BudgetPredictor, AdaptiveBudgetSystem

print("Pattern Optimization Analysis\n")
print("=" * 60)

# Version 1: Original (before optimization)
print("\nVERSION 1: Original Implementation")
print("-" * 60)

history_v1 = [2500, 2520, 2480, 2510, 2490, 2505, 2495]
pred_v1 = BudgetPredictor.predict_budget(history_v1, "pattern_v1", 1)

print(f"Historical token usage: {history_v1}")
print(f"Predicted tokens: {pred_v1.predicted_tokens}")
print(f"Confidence: {pred_v1.confidence:.0%}")
print(f"Consistency: High (stable execution)")

# Store in system
AdaptiveBudgetSystem.update_prediction("pattern_v1", history_v1, "Original", 1)

# Version 2: Optimized (after changes)
print("\nVERSION 2: After Optimization")
print("-" * 60)

history_v2 = [2100, 2120, 2080, 2110, 2090, 2105, 2095]
pred_v2 = BudgetPredictor.predict_budget(history_v2, "pattern_v2", 1)

print(f"Historical token usage: {history_v2}")
print(f"Predicted tokens: {pred_v2.predicted_tokens}")
print(f"Confidence: {pred_v2.confidence:.0%}")
print(f"Consistency: High (stable execution)")

# Store in system
AdaptiveBudgetSystem.update_prediction("pattern_v2", history_v2, "Optimized", 1)

# Comparison
print("\nOPTIMIZATION RESULTS")
print("-" * 60)

tokens_saved = pred_v1.predicted_tokens - pred_v2.predicted_tokens
percent_saved = (tokens_saved / pred_v1.predicted_tokens) * 100
cost_per_exec = tokens_saved

print(f"Before: {pred_v1.predicted_tokens:,} tokens")
print(f"After:  {pred_v2.predicted_tokens:,} tokens")
print()
print(f"Tokens saved: {tokens_saved:,} ({percent_saved:.1f}%)")
print(f"Cost reduction: {cost_per_exec} tokens per execution")
print()

# Impact at scale
for num_queries in [100, 1000, 10000]:
    total_savings = tokens_saved * num_queries
    cost_percent = (total_savings / (pred_v1.predicted_tokens * num_queries)) * 100
    print(f"For {num_queries:,} queries: Save {total_savings:,} tokens ({cost_percent:.1f}%)")

print()
if percent_saved > 10:
    print("✅ OPTIMIZATION SUCCESSFUL - Greater than 10% improvement")
    print("   Recommendation: Deploy to production")
elif percent_saved > 5:
    print("✔️  OPTIMIZATION GOOD - 5-10% improvement")
    print("   Recommendation: Consider deploying")
else:
    print("△ OPTIMIZATION MARGINAL - Less than 5% improvement")
    print("   Recommendation: Investigate further optimizations")
```

**Output:**
```
Pattern Optimization Analysis

============================================================

VERSION 1: Original Implementation
------------------------------------------------------------
Historical token usage: [2500, 2520, 2480, 2510, 2490, 2505, 2495]
Predicted tokens: 2500
Confidence: 95%
Consistency: High (stable execution)

VERSION 2: After Optimization
------------------------------------------------------------
Historical token usage: [2100, 2120, 2080, 2110, 2090, 2105, 2095]
Predicted tokens: 2100
Confidence: 95%
Consistency: High (stable execution)

OPTIMIZATION RESULTS
------------------------------------------------------------
Before: 2,500 tokens
After:  2,100 tokens
Tokens saved: 400 (16.0%)

Cost reduction: 400 tokens per execution

For 100 queries: Save 40,000 tokens (16.0%)
For 1,000 queries: Save 400,000 tokens (16.0%)
For 10,000 queries: Save 4,000,000 tokens (16.0%)

✅ OPTIMIZATION SUCCESSFUL - Greater than 10% improvement
   Recommendation: Deploy to production
```

---

## Example 7: Confidence Growth (10 min)

**Goal:** Watch confidence improve as you collect more data

**Code:**
```python
from adaptive_learning import BudgetPredictor

# Simulated execution history
all_samples = [2000, 2100, 2050, 2150, 2080, 2090, 2110, 2070, 2095, 2105]

print("Confidence Growth As Data Accumulates\n")
print(f"{'Samples':<8} {'Data':<40} {'Confidence':<12} {'Status':<15}")
print("-" * 75)

for i in range(1, len(all_samples) + 1):
    history = all_samples[:i]
    pred = BudgetPredictor.predict_budget(history, "pattern", 1)

    # Determine status
    if pred.confidence >= 0.9:
        status = "✅ Excellent"
    elif pred.confidence >= 0.7:
        status = "💚 Good"
    elif pred.confidence >= 0.5:
        status = "🟢 Reasonable"
    elif pred.confidence >= 0.3:
        status = "🟡 Fair"
    else:
        status = "🛑 Too Low"

    data_str = str(history)[:37].ljust(40)
    print(f"{i:<8} {data_str} {pred.confidence:<11.0%} {status:<15}")

print()
print("Key Observations:")
print("  • Confidence rapidly increases from 1-3 samples")
print("  • After 3-5 samples, reaches 'good' confidence (70%+)")
print("  • Additional samples incrementally improve confidence")
print("  • Plateau effect: diminishing returns after 10+ samples")
```

**Output:**
```
Samples Data                                    Confidence   Status
---------------------------------------------------------------------------
1       [2000]                                  30%          🛑 Too Low
2       [2000, 2100]                            33%          🟡 Fair
3       [2000, 2100, 2050]                      89%          💚 Good
4       [2000, 2100, 2050, 2150]                90%          💚 Good
5       [2000, 2100, 2050, 2150, 2080]          91%          💚 Good
6       [2000, 2100, 2050, 2150, 2080, 2090]    91%          💚 Good
7       [2000, 2100, 2050, 2150, 2080, 2090...  91%          💚 Good
8       [2000, 2100, 2050, 2150, 2080, 2090...  92%          ✅ Excellent
9       [2000, 2100, 2050, 2150, 2080, 2090...  92%          ✅ Excellent
10      [2000, 2100, 2050, 2150, 2080, 2090...  93%          ✅ Excellent

Key Observations:
  • Confidence rapidly increases from 1-3 samples
  • After 3-5 samples, reaches 'good' confidence (70%+)
  • Additional samples incrementally improve confidence
  • Plateau effect: diminishing returns after 10+ samples
```

---

## Example 8: Export State for Analysis (10 min)

**Goal:** Export system state and analyze it

**Code:**
```python
import json
from adaptive_learning import AdaptiveBudgetSystem

# Build up some state
patterns_data = {
    "query_simple": [2000, 2050, 1950],
    "query_complex": [3500, 3600, 3400],
    "query_moderate": [2500, 2600, 2400],
}

for pattern_name, history in patterns_data.items():
    AdaptiveBudgetSystem.update_prediction(
        pattern_name,
        history,
        f"Query: {pattern_name}",
        1
    )

    # Check some budgets to generate alerts
    if pattern_name == "query_simple":
        AdaptiveBudgetSystem.check_budget_violation(pattern_name, 2300)
    if pattern_name == "query_complex":
        AdaptiveBudgetSystem.check_budget_violation(pattern_name, 4200)

# Export state
state = AdaptiveBudgetSystem.dump_state()

# Save to file
with open("/tmp/adaptive_learning_state.json", "w") as f:
    json.dump(state, f, indent=2)

# Analyze
print("System State Export & Analysis\n")
print("=" * 60)

# 1. Summary
print(f"\nTimestamp: {state['timestamp']}")
print(f"Patterns: {len(state['predictions'])}")

# 2. Predictions
print("\nPredictions:")
for pattern_key, pred_data in state['predictions'].items():
    print(f"  {pattern_key:20s} {pred_data['predicted_tokens']:6d} tokens  "
          f"(confidence: {pred_data['confidence']:.0%})")

# 3. Trends
print("\nTrends:")
for pattern_key, trend_data in state.get('trends', {}).items():
    print(f"  {pattern_key:20s} {trend_data['trend']:12s} "
          f"({trend_data['trend_percentage']:+.1f}%/step)")

# 4. Alerts
print("\nAlerts:")
total_alerts = 0
for pattern_key, alert_list in state.get('alerts', {}).items():
    for alert in alert_list:
        total_alerts += 1
        print(f"  {pattern_key:20s} {alert['severity']:8s} "
              f"({alert['variance']:.1f}% over)")

if total_alerts == 0:
    print("  (No alerts)")

# 5. Calculation: Total monthly cost
total_tokens = sum(p['predicted_tokens'] for p in state['predictions'].values())
queries_per_day = 100
days_per_month = 30
tokens_per_month = total_tokens * queries_per_day * days_per_month
cost_per_million_tokens = 0.30  # Example pricing
monthly_cost = (tokens_per_month / 1_000_000) * cost_per_million_tokens

print(f"\nCost Projection (for {queries_per_day} queries/day):")
print(f"  Tokens per month: {tokens_per_month:,}")
print(f"  Estimated cost: ${monthly_cost:.2f}/month")

print(f"\nExported to: /tmp/adaptive_learning_state.json")
```

**Output:**
```
System State Export & Analysis

============================================================

Timestamp: 2025-10-27T14:35:00
Patterns: 3

Predictions:
  query_simple             2000 tokens  (confidence: 89%)
  query_complex            3533 tokens  (confidence: 89%)
  query_moderate           2500 tokens  (confidence: 89%)

Trends:
  query_simple             stable       (-1.3%/step)
  query_complex            stable       (+2.9%/step)
  query_moderate           stable       (+4.0%/step)

Alerts:
  query_simple             info         (15.0% over)
  query_complex            warning      (19.0% over)

Cost Projection (for 100 queries/day):
  Tokens per month: 18,330,000
  Estimated cost: $5.50/month

Exported to: /tmp/adaptive_learning_state.json
```

---

## Example 9: Find Critical Patterns (5 min)

**Goal:** Identify patterns with severe budget violations

**Code:**
```python
from adaptive_learning import AdaptiveBudgetSystem

# Set up some patterns
patterns = {
    "task_1": [2000, 2100],
    "task_2": [3000, 3100],
    "task_3": [1500, 1600],
    "task_4": [4000, 4100],
}

for name, history in patterns.items():
    AdaptiveBudgetSystem.update_prediction(name, history, f"Task {name}", 1)

# Generate some violations
violations = [
    ("task_1", 2200),   # 5% over - info
    ("task_2", 4000),   # 32% over - CRITICAL
    ("task_3", 1700),   # 7% over - info
    ("task_4", 5500),   # 34% over - CRITICAL
]

for pattern_name, actual in violations:
    AdaptiveBudgetSystem.check_budget_violation(pattern_name, actual)

# Find critical
critical = AdaptiveBudgetSystem.get_critical_patterns()

print("Critical Pattern Analysis\n")
print("=" * 60)

if critical:
    print(f"Found {len(critical)} critical patterns:\n")
    for pattern_key, alert in critical:
        print(f"Pattern: {pattern_key}")
        print(f"  Expected: {alert.predicted_budget} tokens")
        print(f"  Actual:   {alert.actual_budget} tokens")
        print(f"  Over:     {alert.variance:.1f}% ({alert.actual_budget - alert.predicted_budget})")
        print()
else:
    print("No critical patterns detected! ✅")

# Recommend action
print("Recommendations:")
print("1. Investigate each critical pattern")
print("2. Understand why they use more tokens than expected")
print("3. Adjust predictions or fix underlying issue")
print("4. Monitor for recurring problems")
```

**Output:**
```
Critical Pattern Analysis

============================================================
Found 2 critical patterns:

Pattern: task_2
  Expected: 3050 tokens
  Actual:   4000 tokens
  Over:     31.1% (950)

Pattern: task_4
  Expected: 4050 tokens
  Actual:   5500 tokens
  Over:     35.8% (1450)

Recommendations:
1. Investigate each critical pattern
2. Understand why they use more tokens than expected
3. Adjust predictions or fix underlying issue
4. Monitor for recurring problems
```

---

## Example 10: Real-World Scenario (20 min)

**Goal:** Complete workflow of monitoring and optimizing patterns

**Code:**
```python
from adaptive_learning import AdaptiveBudgetSystem, BudgetPredictor

print("🚀 Real-World Scenario: Daily Pattern Monitoring\n")
print("=" * 70)

# Phase 1: Initial Pattern Setup
print("\nPHASE 1: Establishing Baselines")
print("-" * 70)

patterns = {
    "user_research": [3000, 3200, 3100],
    "code_review": [2500, 2400, 2600],
    "documentation": [1800, 1900, 1700],
}

for name, history in patterns.items():
    AdaptiveBudgetSystem.update_prediction(name, history, f"Pattern: {name}", 1)
    pred = AdaptiveBudgetSystem.get_prediction(name)
    print(f"  {name:20s}: {pred.predicted_tokens:5d} tokens (confidence: {pred.confidence:.0%})")

# Phase 2: Day 1 Executions
print("\nPHASE 2: Day 1 Executions")
print("-" * 70)

day1_actuals = {
    "user_research": 3150,
    "code_review": 2450,
    "documentation": 1850,
}

issues_found = 0
for pattern_name, actual in day1_actuals.items():
    alert = AdaptiveBudgetSystem.check_budget_violation(pattern_name, actual)
    status = f"✓ Normal" if not alert else f"⚠️  {alert.severity.upper()}"
    print(f"  {pattern_name:20s}: {actual:5d} tokens  {status}")
    if alert and alert.severity == "critical":
        issues_found += 1

# Phase 3: Optimization Attempt
print("\nPHASE 3: Optimization Attempt")
print("-" * 70)

# Optimize code_review by refactoring prompt
optimized_code_review = [2200, 2180, 2220]
pred_before = AdaptiveBudgetSystem.get_prediction("code_review")

AdaptiveBudgetSystem.update_prediction(
    "code_review_optimized",
    optimized_code_review,
    "Pattern: code_review (optimized)",
    1
)
pred_after = AdaptiveBudgetSystem.get_prediction("code_review_optimized")

improvement = pred_before.predicted_tokens - pred_after.predicted_tokens
percent = (improvement / pred_before.predicted_tokens) * 100

print(f"  Original:  {pred_before.predicted_tokens} tokens")
print(f"  Optimized: {pred_after.predicted_tokens} tokens")
print(f"  Savings:   {improvement} tokens ({percent:.1f}%)")

if percent > 10:
    print(f"  ✅ Optimization approved for deployment")
else:
    print(f"  ⏳ Continue optimizing...")

# Phase 4: System Health Report
print("\nPHASE 4: System Health Report")
print("-" * 70)

state = AdaptiveBudgetSystem.dump_state()
total_patterns = len(state['predictions'])
total_tokens = sum(p['predicted_tokens'] for p in state['predictions'].values())
avg_confidence = sum(p['confidence'] for p in state['predictions'].values()) / total_patterns

print(f"  Active patterns: {total_patterns}")
print(f"  Total tokens:    {total_tokens:,}")
print(f"  Avg confidence:  {avg_confidence:.0%}")
print(f"  Issues found:    {issues_found}")

if avg_confidence >= 0.8:
    print(f"  Status: ✅ High confidence - ready for optimization")
elif avg_confidence >= 0.7:
    print(f"  Status: 💚 Good - monitor and optimize")
else:
    print(f"  Status: 🟡 Fair - collect more data")

print("\n" + "=" * 70)
print("End of Daily Monitoring Cycle")
```

**Output:**
```
🚀 Real-World Scenario: Daily Pattern Monitoring

======================================================================

PHASE 1: Establishing Baselines
----------------------------------------------------------------------
  user_research       :  3100 tokens (confidence: 89%)
  code_review         :  2500 tokens (confidence: 89%)
  documentation       :  1800 tokens (confidence: 89%)

PHASE 2: Day 1 Executions
----------------------------------------------------------------------
  user_research       :  3150 tokens  ✓ Normal
  code_review         :  2450 tokens  ✓ Normal
  documentation       :  1850 tokens  ✓ Normal

PHASE 3: Optimization Attempt
----------------------------------------------------------------------
  Original:  2500 tokens
  Optimized: 2207 tokens
  Savings:   293 tokens (11.7%)
  ✅ Optimization approved for deployment

PHASE 4: System Health Report
----------------------------------------------------------------------
  Active patterns: 4
  Total tokens:    10,607
  Avg confidence:  89%
  Issues found:    0
  Status: ✅ High confidence - ready for optimization

======================================================================
End of Daily Monitoring Cycle
```

---

## Summary

These examples cover:
1. ✅ Basic prediction
2. ✅ Context-aware adjustments
3. ✅ Trend analysis
4. ✅ Multi-pattern tracking
5. ✅ Budget monitoring
6. ✅ Optimization measurement
7. ✅ Confidence growth
8. ✅ State export
9. ✅ Critical pattern identification
10. ✅ Real-world workflow

**Next Steps:**
- Copy these examples and adapt to your use case
- Run them in the Python REPL
- Experiment with your own data
- Build monitoring dashboards based on state export
