# Core Concepts - Deep Dive

## 1. Token Prediction

### What Is It?

Token prediction is the core output of the Adaptive Learning System. It's a numerical estimate of how many tokens the next execution will use, calculated from historical data.

### How It's Calculated

**Step 1: Historical Average**
```
history = [2000, 2100, 2050, 2150, 2080]
sum = 2000 + 2100 + 2050 + 2150 + 2080 = 10,380
average = 10,380 / 5 = 2,076
```

The average is the base prediction: **2,076 tokens**

**Step 2: Adjust for Trend**
If the pattern is increasing, the prediction gets bumped up. If decreasing, it goes down.

```
If trend is +6% per execution: adjustment = +125 tokens
If trend is stable: adjustment = 0 tokens
If trend is -4% per execution: adjustment = -82 tokens
```

**Step 3: Create Safety Range**
The system provides min/max safety margins (±30%):

```
Prediction: 2,076 tokens
Min safe: 2,076 * 0.70 = 1,453 tokens
Max safe: 2,076 * 1.30 = 2,699 tokens
```

### Factors That Influence Accuracy

| Factor | Impact | How to Improve |
|--------|--------|---|
| Sample size | More samples = more accurate | Collect 10+ executions |
| Consistency | Volatile data = less accurate | Ensure stable inputs |
| Trend | Trending patterns need adjustment | Track over time |
| Context | Different contexts have different costs | Use context multipliers |

### Typical Accuracy

```
With 3-5 samples:  ±30% (reasonable)
With 10+ samples:  ±15% (good)
With 50+ samples:  ±5%  (excellent)
```

### When It Fails

Prediction quality suffers when:
- **Too little data** (1-2 samples) - inherent uncertainty
- **Volatile patterns** - high variability makes predictions unreliable
- **Trending patterns** - algorithm adjusts but may lag behind
- **Structural changes** - if the task fundamentally changes, historical data becomes irrelevant

---

## 2. Confidence Score

### What Is It?

Confidence is a 0-100% score indicating how sure the system is about its prediction.

**Not** the margin of error (that's the prediction range).
**Rather** the likelihood that the prediction is in the right ballpark.

### How It's Calculated

Confidence combines three factors:

**Factor 1: Sample Size Bonus**
```
Samples  | Bonus
─────────────────
1-2      | 30%
3-5      | 50%
6-10     | 60%
11-20    | 70%
20+      | 80%
```

**Factor 2: Consistency Bonus**
```
Consistency Score | Bonus
──────────────────────────
0.0-0.3          | 0%
0.3-0.5          | 5%
0.5-0.7          | 10%
0.7-0.9          | 15%
0.9-1.0          | 20%
```

**Factor 3: Trend Confidence Bonus**
```
Trend Type | Bonus
───────────────────
Stable     | 10%
Increasing | 5%
Decreasing | 5%
```

**Final Formula:**
```
confidence = sample_bonus + consistency_bonus + trend_bonus
capped to [0.30, 1.00]
```

**Example:**
```
5 samples: 50% bonus
Consistency 0.92: 20% bonus
Stable trend: 10% bonus
Total: 50% + 20% + 10% = 80% confidence
```

### Decision Thresholds

Use confidence to decide how aggressively to optimize:

```
Confidence Range | Action
─────────────────────────────────────────────────
0-30%           | 🛑 STOP - Gather more data
                | - Need 5+ samples minimum
                | - Don't make decisions yet

30-50%          | ⚠️ CAUTION - Limited confidence
                | - Use as rough estimate only
                | - Monitor closely
                | - Gather more data

50-70%          | 🟢 REASONABLE - Acceptable
                | - Good for general planning
                | - Base budgets on this
                | - Monitor for changes

70-90%          | 💚 GOOD - High confidence
                | - Safe to optimize
                | - Make budget decisions
                | - Plan capacity

90-100%         | 🎯 EXCELLENT - Very confident
                | - Optimize aggressively
                | - Use for critical planning
                | - Basis for cost predictions
```

### Factors That Increase Confidence

1. **More samples** - Each additional execution improves confidence
2. **Consistency** - Stable, predictable patterns are more confident
3. **Stable trends** - Patterns that don't trend up/down are more reliable

### Factors That Decrease Confidence

1. **Few samples** - 1-2 data points always low confidence
2. **High volatility** - Inconsistent data reduces confidence
3. **Trending patterns** - Increasing/decreasing patterns are less reliable

---

## 3. Trend Analysis

### What Is Trend?

Trend answers: "Is token usage going up, down, or staying the same?"

### Three Categories

**Increasing Trend** (trend > 5% per execution)
```
history = [2000, 2150, 2300, 2450, 2600]  # +150 each step
trend = "increasing"
trend_percentage = 7.5%  # Growing 7.5% per step
```

**Implications:**
- Pattern is getting less efficient
- Budget requirements growing
- Investigation needed - why more tokens?

**Stable Trend** (-5% to +5% per execution)
```
history = [2000, 2050, 2030, 2080, 2040]  # Random variation
trend = "stable"
trend_percentage = 0.3%  # Almost no growth
```

**Implications:**
- Pattern behavior consistent
- Budget predictable
- Safe for planning

**Decreasing Trend** (trend < -5% per execution)
```
history = [2600, 2450, 2300, 2150, 2000]  # -150 each step
trend = "decreasing"
trend_percentage = -7.5%  # Shrinking 7.5% per step
```

**Implications:**
- Pattern getting more efficient
- Optimization working
- Budget requirements decreasing

### How Trend Is Detected

The system uses **linear regression** to fit a line through historical data:

```
Linear Regression Line:
    y = m*x + b

Where:
    m = slope (trend_percentage)
    b = intercept
    x = execution number
    y = tokens used

Example:
    history = [2000, 2100, 2200, 2300]
    slope = 100 tokens per execution
    trend_percentage = 100/2000 = 5.0%
```

### Forecasting (Predicting Next Value)

Trend analysis also forecasts the next value:

```
Last value: 2,300 tokens
Trend: +5% per step
Forecasted next: 2,300 * 1.05 = 2,415 tokens
```

This forecast is incorporated into the prediction algorithm.

### Using Trend Information

**When trend is increasing:**
- Increase budget safety margin
- Investigate cause of efficiency loss
- Look for code changes that added complexity

**When trend is stable:**
- Use prediction with high confidence
- Plan budgets knowing usage is consistent
- Monitor for changes

**When trend is decreasing:**
- Great! Optimization is working
- Can gradually reduce budget
- Track which change caused improvement

---

## 4. Consistency Measurement

### What Is Consistency?

Consistency (0.0-1.0 scale) measures how predictable a pattern is. It's the opposite of volatility.

**High consistency** = Predictable, low variance
**Low consistency** = Unpredictable, high variance

### How It's Calculated

The system uses **coefficient of variation (CV)**:

```
CV = (standard_deviation / average) * 100%

Example:
    history = [2000, 2050, 2100, 1950, 2000]
    average = 2020
    standard_deviation = 62.4
    CV = (62.4 / 2020) * 100% = 3.1%

    consistency = 1.0 - min(CV/100, 1.0) = 0.97 (very consistent)
```

### Interpreting Consistency

```
Consistency | CV    | Pattern Type
───────────────────────────────────────
0.9-1.0    | <5%   | Very stable (predictable)
0.7-0.9    | 5-10% | Fairly consistent
0.5-0.7    | 10-20%| Moderate volatility
0.3-0.5    | 20-40%| Highly volatile
0.0-0.3    | >40%  | Unpredictable
```

### Why Consistency Matters

**High Consistency Benefits:**
- Predictions are more reliable
- Confidence scores increase
- Safe to optimize aggressively
- Budget can be tighter

**Low Consistency Warnings:**
- Predictions less reliable
- Confidence scores lower
- Need larger safety margins
- Investigation needed - find variance source

### Example: Comparing Two Patterns

**Pattern A: Consistent**
```
history = [2000, 2020, 1990, 2010, 2005]
average = 2005
deviation = 12.3
consistency = 0.94
confidence = 88%
```
→ Safe to optimize, budget is predictable

**Pattern B: Volatile**
```
history = [1500, 2800, 1200, 3000, 1800]
average = 2060
deviation = 762
consistency = 0.37
confidence = 42%
```
→ Cannot optimize reliably, need investigation

### Finding Causes of Low Consistency

When consistency is low, investigate:

1. **Input variation** - Do inputs vary in size/complexity?
2. **Time variation** - Is execution time slower some times?
3. **External factors** - API latency, system load, etc.?
4. **Code changes** - Did logic change affecting path complexity?

---

## 5. Context-Aware Adjustment

### What Is Context?

Context is information about the domain or task type that influences token usage.

Some domains are inherently more complex and use more tokens. Some are simpler and use fewer tokens.

### Built-In Contexts

**Education Context (0.9x multiplier)**
```
Use when: Explaining concepts, teaching, tutorial creation
Cost reduction: 10% cheaper
Reasoning: Structured explanations use fewer tokens
Example:
    base: 2000 tokens
    education: 2000 * 0.9 = 1800 tokens (save 200)
```

**Architecture Context (1.2x multiplier)**
```
Use when: System design, architecture, complex planning
Cost increase: 20% more expensive
Reasoning: Complex discussions use more tokens
Example:
    base: 2000 tokens
    architecture: 2000 * 1.2 = 2400 tokens (add 400)
```

**Implementation Context (1.1x multiplier)**
```
Use when: Code implementation, debugging
Cost increase: 10% more expensive
Reasoning: Code discussion requires more detail
Example:
    base: 2000 tokens
    implementation: 2000 * 1.1 = 2200 tokens (add 200)
```

### How to Use Contexts

```python
history = [2000, 2100, 2050]
base = BudgetPredictor.predict_budget(history, "pattern", 1)  # 2050

education = BudgetPredictor.predict_with_context(
    history, 1, "education"
)  # 1845

architecture = BudgetPredictor.predict_with_context(
    history, 1, "architecture"
)  # 2460
```

### Custom Contexts

The system uses built-in contexts, but you can calculate your own multipliers:

```
If "code_review" uses 15% more than baseline:
custom_cost = base_prediction * 1.15
```

---

## 6. Budget Alerts

### What Are Budget Alerts?

Budget alerts notify you when an execution deviates significantly from the prediction.

They help catch:
- Anomalies (unexpected token usage)
- Regression (pattern getting worse)
- Configuration issues

### Alert Severity Levels

Severity is determined by how far over budget the execution went:

**Info Alert (0-15% over)**
```
predicted: 2000 tokens
actual: 2200 tokens
variance: 10%
severity: info

Action: Monitor, normal variance
```

**Warning Alert (15-30% over)**
```
predicted: 2000 tokens
actual: 2400 tokens
variance: 20%
severity: warning

Action: Investigate, might indicate issue
```

**Critical Alert (>30% over)**
```
predicted: 2000 tokens
actual: 2700 tokens
variance: 35%
severity: critical

Action: Immediate investigation required
```

### How Severity Is Calculated

```
variance_percent = ((actual - predicted) / predicted) * 100

If variance_percent <= 15:
    severity = "info"
Elif variance_percent <= 30:
    severity = "warning"
Else:
    severity = "critical"
```

### Using Alerts

**Info Alerts:** Normal operation, expected variance within safety margin

**Warning Alerts:** Something changed, investigate:
- Input data grew larger than expected
- Code path changed
- External service slower
- System resources constrained

**Critical Alerts:** Stop and investigate:
- System misconfiguration
- Data quality issue
- Code regression
- Resource exhaustion

---

## 7. The Prediction Algorithm

### Complete Algorithm Flow

```
Input: token_history (list of previous tokens)

Step 1: Validate
  - If fewer than 3 samples: use minimal confidence (0.3)

Step 2: Calculate Base Prediction
  - Average = sum(history) / len(history)
  - min = Average * 0.70
  - max = Average * 1.30

Step 3: Analyze Trend
  - Calculate linear regression slope
  - Determine trend type (increasing/decreasing/stable)
  - Calculate trend percentage

Step 4: Adjust for Trend
  - If increasing: bump prediction up
  - If decreasing: bump prediction down
  - If stable: no adjustment

Step 5: Calculate Consistency
  - Standard deviation of data
  - Coefficient of variation
  - Convert to consistency score (0-1)

Step 6: Calculate Confidence
  - Sample bonus (based on number of data points)
  - Consistency bonus (based on volatility)
  - Trend bonus (stable trends increase confidence)
  - Cap to [0.30, 1.00]

Step 7: Validate Output
  - Ensure: min <= predicted <= max
  - Ensure: confidence in [0.30, 1.00]
  - Ensure: consistency in [0.0, 1.0]

Output: TokenPrediction object
  - predicted_tokens
  - confidence
  - min_tokens
  - max_tokens
  - basis
  - samples
```

### Special Cases

**Single Sample**
```
history = [2000]
prediction = 2000
confidence = 30% (minimum)
trend = "stable" (can't determine)
consistency = 1.0 (single point, perfect "consistency")
```

**Two Samples**
```
history = [2000, 2100]
prediction = 2050
confidence = 33-40% (low)
trend = "increasing" (6% growth)
consistency = high (only 2 points)
```

**Volatile Data**
```
history = [1000, 5000, 800, 4500, 900, 4800]
prediction = 2683 (average)
confidence = 50% (reduced due to low consistency)
consistency = 0.35 (high volatility)
```

---

## 8. The Pattern Lifecycle

### Phase 1: Data Collection (1-5 Executions)

```
Execution 1: 2000 tokens → confidence 30%
Execution 2: 2100 tokens → confidence 33%
Execution 3: 2050 tokens → confidence 89%
Execution 4: 2150 tokens → confidence 90%
Execution 5: 2080 tokens → confidence 91%
```

**What happens:**
- System gathers baseline data
- Confidence rapidly increases
- Pattern becomes predictable

### Phase 2: Stable Prediction (5-20 Executions)

```
Executions 6-20: 2050-2150 tokens
Confidence: 92-95%
Trend: Stable
Consistency: 0.92+
```

**What happens:**
- System confident in predictions
- Ready for optimization decisions
- Can plan budgets accurately

### Phase 3: Optimization (20+ Executions)

```
Original: [2000, 2100, 2050, ...]
Optimized: [1800, 1820, 1810, ...]

System tracks:
- Before: 2050 tokens (original)
- After: 1813 tokens (optimized)
- Saved: 237 tokens (11.6%)
```

**What happens:**
- Compare versions with high confidence
- Measure optimization impact quantitatively
- Decide to deploy or revert

### Phase 4: Monitoring (Ongoing)

```
Constant monitoring for:
- Trend changes (efficiency degradation)
- Consistency changes (new volatility)
- Budget violations (anomalies)
```

**What happens:**
- System alerts on deviations
- Early warning of problems
- Data for capacity planning

---

## 9. Related Concepts

### Standard Deviation

Measure of spread in data.

```
Consistent pattern: σ = 30
Volatile pattern: σ = 500
```

### Coefficient of Variation (CV)

Standard deviation as % of mean. Makes comparison easier.

```
Pattern A: mean=2000, σ=50, CV=2.5%
Pattern B: mean=3000, σ=150, CV=5%
→ Pattern A more consistent (lower CV)
```

### Linear Regression

Fitting a line to data to find trend.

```
y = m*x + b

m = slope (trend)
b = intercept
```

### Safety Margin

Buffer added to prediction for safety.

```
Prediction: 2050
Safety margin: ±30%
Min safe: 1435 (prediction * 0.70)
Max safe: 2665 (prediction * 1.30)
```

---

## Key Takeaways

1. **Prediction** = Historical average, adjusted for trend
2. **Confidence** = How sure we are (depends on data + consistency)
3. **Trend** = Direction of change (up/down/stable)
4. **Consistency** = How predictable the pattern is
5. **Context** = Domain-specific multiplier
6. **Alerts** = Notification when actual deviates from prediction
7. **Algorithm** = Mathematical approach combining all above

Each concept works together to provide increasingly accurate, confident predictions over time.
