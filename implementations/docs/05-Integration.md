# Integration Guide - Phase 4, 5, and 6

## Architecture Overview

The Adaptive Learning System (Phase 5) sits in the middle of a three-phase pipeline:

```
Phase 4 (Task-Relay)              Phase 5 (Adaptive Learning)    Phase 6 (Multi-Agent)
═══════════════════════════════════════════════════════════════════════════════════════

Tracks execution               Learns from patterns          Optimizes agent selection
Measures token usage       →   Predicts future costs     →   Routes to cheapest agent

Input: Relay checkpoints    Input: Token history         Input: Prediction data
Output: Token deltas        Output: Predictions           Output: Agent selection
```

---

## Phase 4 → Phase 5 Integration

### What Phase 4 Provides

Phase 4 (Task-Relay) executes multi-agent workflows with checkpoint tracking at each step.

Each checkpoint captures:
```python
{
    "relay_number": 1,
    "agent_name": "researcher",
    "timestamp": "2025-10-27T14:00:00",
    "token": {
        "pre_tokens": 50000,      # Tokens at start of step
        "post_tokens": 47500,     # Tokens at end of step
        "delta": 2500             # Tokens used in this step
    },
    "status": "completed"
}
```

### How Phase 5 Consumes Phase 4 Data

**Step 1: Extract Token Delta**

The token delta represents how many tokens that specific agent execution consumed:

```python
from task_relay_consciousness import TaskRelayConsciousnessIntegration
from adaptive_learning import AdaptiveBudgetSystem

# Get Phase 4 checkpoint
checkpoint = TaskRelayConsciousnessIntegration.get_checkpoint(relay_id=1)

# Extract tokens used
tokens_used = abs(checkpoint.token.delta)  # 2500 tokens

# Extract metadata
agent_name = checkpoint.agent_name         # "researcher"
relay_num = checkpoint.relay_number        # 1
```

**Step 2: Feed to Phase 5**

Create a pattern key combining agent name and query, then feed historical data:

```python
# After collecting multiple executions of the same pattern
historical_tokens = [2500, 2480, 2520, 2490, 2510]

# Store in Phase 5
AdaptiveBudgetSystem.update_prediction(
    pattern_key=f"agent_{agent_name}_relay_{relay_num}",
    token_history=historical_tokens,
    pattern_query=f"Researcher - Relay {relay_num}",
    pattern_level=relay_num
)

# Get prediction for next execution
pred = AdaptiveBudgetSystem.get_prediction(f"agent_{agent_name}_relay_{relay_num}")
print(f"Next researcher execution expected: {pred.predicted_tokens} tokens")
```

### Data Flow Diagram

```
Phase 4 Checkpoint:
  ┌─────────────────────────────────┐
  │ Relay 1: researcher_agent       │
  │ pre_tokens: 50,000              │
  │ post_tokens: 47,500             │
  │ delta: 2,500 tokens ← EXTRACT   │
  └─────────────────────────────────┘
           │
           ↓
Phase 5 Learning:
  ┌─────────────────────────────────┐
  │ history = [2500, 2480, ...]     │
  │ predicted_tokens = 2495         │
  │ confidence = 92%                │
  │ trend = stable                  │
  └─────────────────────────────────┘
           │
           ↓ (Used by Phase 6)
Phase 6 Agent Routing:
  ┌─────────────────────────────────┐
  │ Agent A cost: 2495 tokens       │
  │ Agent B cost: 2200 tokens       │
  │ Agent C cost: 2800 tokens       │
  │ → Choose: Agent B (cheapest)    │
  └─────────────────────────────────┘
```

### Real-World Integration Example

```python
from task_relay_consciousness import TaskRelayConsciousnessIntegration
from adaptive_learning import AdaptiveBudgetSystem

# Scenario: Running the same researcher query 5 times with Phase 4

for execution_num in range(1, 6):
    print(f"\nExecution {execution_num}")
    print("-" * 40)

    # Phase 4: Run the task with task-relay
    checkpoint = TaskRelayConsciousnessIntegration.create_checkpoint(
        relay_number=1,
        agent_name="researcher",
        pre_tokens=50000,
        post_tokens=50000 - (2500 + (execution_num * 50)),  # Slight increase
        expected_tokens=2500
    )

    # Extract token usage
    tokens_used = abs(checkpoint.token.delta)

    # Phase 5: Collect historical data
    pattern_key = f"agent_researcher_relay_1"
    query_description = f"Research query - Relay 1"

    # After first execution
    if execution_num == 1:
        history = [tokens_used]
    else:
        # Get existing history and add new execution
        existing_pred = AdaptiveBudgetSystem.get_prediction(pattern_key)
        if existing_pred:
            # In real system, would maintain full history
            history = [2500, 2550, 2600, 2650, tokens_used]
        else:
            history = [tokens_used]

    # Update Phase 5 with new data
    AdaptiveBudgetSystem.update_prediction(
        pattern_key,
        history,
        query_description,
        1
    )

    # Get prediction for next execution
    pred = AdaptiveBudgetSystem.get_prediction(pattern_key)

    print(f"  Tokens used: {tokens_used}")
    print(f"  Predicted next: {pred.predicted_tokens} (confidence: {pred.confidence:.0%})")
    print(f"  Trend: {AdaptiveBudgetSystem.PATTERN_TRENDS.get(pattern_key, 'N/A')}")
```

---

## Phase 5 → Phase 6 Integration

### What Phase 6 Needs

Phase 6 (Multi-Agent Optimization) will use Phase 5 predictions to:
1. Compare token efficiency across different agents
2. Select the most efficient agent for each pattern
3. Route future executions to cost-optimized agents

### How Phase 5 Supports Phase 6

**Method 1: Direct State Access**

```python
from adaptive_learning import AdaptiveBudgetSystem

# Phase 6 queries Phase 5 state
state = AdaptiveBudgetSystem.dump_state()

# Compare agents for same task
agents_for_task = {
    "agent_a": state['predictions']['agent_a_research']['predicted_tokens'],
    "agent_b": state['predictions']['agent_b_research']['predicted_tokens'],
    "agent_c": state['predictions']['agent_c_research']['predicted_tokens'],
}

# Choose cheapest
cheapest_agent = min(agents_for_task, key=agents_for_task.get)
print(f"Route to: {cheapest_agent}")
```

**Method 2: Trend-Based Decision**

```python
# Use trend data to predict future costs
trends = state['trends']

for agent_key, trend in trends.items():
    if trend['trend'] == "increasing":
        # Warn: this agent getting more expensive
        print(f"⚠️  {agent_key} cost increasing ({trend['trend_percentage']:+.1f}%/step)")
    elif trend['trend'] == "decreasing":
        # Good: this agent getting cheaper
        print(f"✅ {agent_key} cost decreasing ({trend['trend_percentage']:.1f}%/step)")
```

**Method 3: Confidence-Based Safety**

```python
# Phase 6 uses confidence to decide optimization aggressiveness

for pattern_key, pred_data in state['predictions'].items():
    confidence = pred_data['confidence']

    if confidence >= 0.9:
        # Use for critical cost optimization decisions
        action = "aggressive_optimization"
    elif confidence >= 0.7:
        # Use for moderate optimization
        action = "standard_optimization"
    else:
        # Collect more data first
        action = "monitor_only"

    print(f"{pattern_key}: {action}")
```

### Data Flow Diagram

```
Phase 5 Analysis:
  ┌────────────────────────────────────────┐
  │ Pattern: agent_a_documentation         │
  │ Predicted: 1800 tokens                 │
  │ Confidence: 95%                        │
  │ Trend: stable                          │
  │ Samples: 15                            │
  └────────────────────────────────────────┘

  ┌────────────────────────────────────────┐
  │ Pattern: agent_b_documentation         │
  │ Predicted: 2100 tokens                 │
  │ Confidence: 92%                        │
  │ Trend: stable                          │
  │ Samples: 12                            │
  └────────────────────────────────────────┘

  ┌────────────────────────────────────────┐
  │ Pattern: agent_c_documentation         │
  │ Predicted: 1950 tokens                 │
  │ Confidence: 88%                        │
  │ Trend: decreasing (-2%/step)           │
  │ Samples: 10                            │
  └────────────────────────────────────────┘
           │
           ↓
Phase 6 Decision:
  ┌────────────────────────────────────────┐
  │ Compare efficiency for documentation:   │
  │ • Agent A: 1800 tokens (best!)         │
  │ • Agent C: 1950 tokens (improving)     │
  │ • Agent B: 2100 tokens (avoid)         │
  │                                        │
  │ Decision: Route documentation to A     │
  │ Reason: Cheapest + highest confidence  │
  └────────────────────────────────────────┘
           │
           ↓
Execution:
  ┌────────────────────────────────────────┐
  │ Pattern query: "document_feature"      │
  │ → Route to: agent_a                    │
  │ → Expected cost: 1800 tokens           │
  │ → Budget: 2340 tokens (30% safety)     │
  └────────────────────────────────────────┘
```

### Phase 6 Implementation Pattern

```python
from adaptive_learning import AdaptiveBudgetSystem
from phase6_router import AgentRouter  # Hypothetical Phase 6

class Phase6MultiAgentOptimizer:
    """Demonstrates how Phase 6 will use Phase 5"""

    @staticmethod
    def select_best_agent(task_type, available_agents):
        """
        Select most token-efficient agent for a task.

        Args:
            task_type: "research", "documentation", "implementation", etc.
            available_agents: List of agent names ["agent_a", "agent_b", ...]

        Returns:
            (best_agent, predicted_tokens, confidence)
        """

        # Get Phase 5 predictions
        state = AdaptiveBudgetSystem.dump_state()

        # Find predictions for this task type with these agents
        costs = {}
        for agent in available_agents:
            pattern_key = f"{agent}_{task_type}"

            if pattern_key in state['predictions']:
                pred = state['predictions'][pattern_key]
                costs[agent] = {
                    'tokens': pred['predicted_tokens'],
                    'confidence': pred['confidence'],
                }
            else:
                # No data yet, estimate higher
                costs[agent] = {
                    'tokens': 5000,  # Default high estimate
                    'confidence': 0.0,
                }

        # Score agents: prefer lower tokens, then higher confidence
        scores = {}
        for agent, data in costs.items():
            # Base score on tokens (lower is better)
            token_score = 100000 / data['tokens']  # Inverse

            # Confidence bonus (higher is better)
            confidence_bonus = data['confidence'] * 20

            scores[agent] = token_score + confidence_bonus

        # Select highest scoring agent
        best_agent = max(scores, key=scores.get)

        return (
            best_agent,
            costs[best_agent]['tokens'],
            costs[best_agent]['confidence']
        )

    @staticmethod
    def should_optimize_agent_selection(task_type):
        """
        Check if we have enough data to optimize agent selection.

        Returns True if confidence >= 80% for at least one agent.
        """

        state = AdaptiveBudgetSystem.dump_state()

        for pattern_key, pred in state['predictions'].items():
            if task_type in pattern_key:
                if pred['confidence'] >= 0.80:
                    return True

        return False

# Usage in Phase 6
agents = ["agent_a", "agent_b", "agent_c"]

# Select best agent for research task
best, tokens, confidence = Phase6MultiAgentOptimizer.select_best_agent(
    "research", agents
)

print(f"Selected: {best}")
print(f"Expected tokens: {tokens}")
print(f"Confidence: {confidence:.0%}")

# Check if ready for optimization
if Phase6MultiAgentOptimizer.should_optimize_agent_selection("documentation"):
    print("✅ Ready to optimize documentation routing")
else:
    print("🟡 Need more data before optimizing")
```

---

## Complete Three-Phase Workflow

### Full Example: From Task-Relay to Agent Routing

```python
from task_relay_consciousness import TaskRelayConsciousnessIntegration
from adaptive_learning import AdaptiveBudgetSystem

# SCENARIO: You have 3 agents that can research a topic
# Over 5 days, you run each agent 5 times
# You want to select the best one going forward

AGENTS = ["researcher_alpha", "researcher_beta", "researcher_gamma"]
DAYS = 5
RUNS_PER_AGENT = 5

print("🔄 Three-Phase Integration Demo\n")
print("=" * 70)

# Simulate token data for each agent
agent_token_patterns = {
    "researcher_alpha": [2400, 2420, 2380, 2410, 2400],
    "researcher_beta": [2800, 2850, 2750, 2900, 2800],
    "researcher_gamma": [2100, 2110, 2090, 2120, 2100],
}

# Phase 4: Simulate task-relay executions
print("\nPHASE 4: Task-Relay Executions")
print("-" * 70)

for day in range(1, DAYS + 1):
    print(f"\nDay {day}:")

    for agent_name in AGENTS:
        # Simulate Phase 4 checkpoint
        base_tokens = agent_token_patterns[agent_name][0]
        actual_tokens = agent_token_patterns[agent_name][(day - 1) % 5]

        checkpoint = TaskRelayConsciousnessIntegration.create_checkpoint(
            relay_number=day,
            agent_name=agent_name,
            pre_tokens=50000,
            post_tokens=50000 - actual_tokens,
            expected_tokens=base_tokens
        )

        print(f"  {agent_name:20s}: {actual_tokens:5d} tokens")

# Phase 5: Learn patterns
print("\n\nPHASE 5: Adaptive Learning")
print("-" * 70)

for agent_name, token_history in agent_token_patterns.items():
    AdaptiveBudgetSystem.update_prediction(
        pattern_key=f"agent_{agent_name}",
        token_history=token_history,
        pattern_query=f"Research with {agent_name}",
        pattern_level=1
    )

print("\nLearned Predictions:")

state = AdaptiveBudgetSystem.dump_state()
for agent_name in AGENTS:
    pred = state['predictions'][f"agent_{agent_name}"]
    print(f"  {agent_name:20s}: {pred['predicted_tokens']:5d} tokens "
          f"(confidence: {pred['confidence']:.0%})")

# Phase 6: Make optimization decision
print("\n\nPHASE 6: Multi-Agent Optimization")
print("-" * 70)

agent_costs = {}
for agent_name in AGENTS:
    pred = state['predictions'][f"agent_{agent_name}"]
    agent_costs[agent_name] = {
        'tokens': pred['predicted_tokens'],
        'confidence': pred['confidence'],
    }

# Find best agent
best_agent = min(agent_costs, key=lambda a: agent_costs[a]['tokens'])
best_cost = agent_costs[best_agent]['tokens']
best_confidence = agent_costs[best_agent]['confidence']

print("\nAgent Comparison:")
for agent_name in sorted(AGENTS):
    cost = agent_costs[agent_name]['tokens']
    conf = agent_costs[agent_name]['confidence']
    marker = "✅ BEST" if agent_name == best_agent else "  "

    print(f"  {marker} {agent_name:20s}: {cost:5d} tokens "
          f"(confidence: {conf:.0%})")

print()
print(f"RECOMMENDATION:")
print(f"  Use: {best_agent}")
print(f"  Expected cost: {best_cost} tokens")
print(f"  Confidence: {best_confidence:.0%}")
print(f"  Savings vs worst agent: "
      f"{max(agent_costs[a]['tokens'] for a in AGENTS) - best_cost} tokens/query")

print("\n" + "=" * 70)
```

---

## Configuration for Phase Boundaries

### Phase 4 → Phase 5 Configuration

```python
# In your Phase 4 execution handler
from adaptive_learning import AdaptiveBudgetSystem

def handle_phase4_completion(relay_checkpoint):
    """
    Called when Phase 4 relay completes
    Feeds token data into Phase 5
    """

    # Extract data from Phase 4
    tokens_used = abs(relay_checkpoint.token.delta)
    agent_name = relay_checkpoint.agent_name
    relay_number = relay_checkpoint.relay_number
    timestamp = relay_checkpoint.timestamp

    # Create pattern key
    pattern_key = f"agent_{agent_name}_relay_{relay_number}"

    # Get historical data (from your database/cache)
    # Example: last 20 executions of this pattern
    history = get_pattern_history(pattern_key)
    history.append(tokens_used)

    # Feed to Phase 5
    AdaptiveBudgetSystem.update_prediction(
        pattern_key=pattern_key,
        token_history=history[-20:],  # Last 20 executions
        pattern_query=f"{agent_name} - Relay {relay_number}",
        pattern_level=relay_number,
        context="implementation"  # or other context
    )
```

### Phase 5 → Phase 6 Configuration

```python
# In your Phase 6 agent routing logic
from adaptive_learning import AdaptiveBudgetSystem

def route_to_best_agent(task_type, available_agents):
    """
    Called when deciding which agent to use
    Queries Phase 5 predictions to select cheapest
    """

    state = AdaptiveBudgetSystem.dump_state()

    # Minimum confidence required to use prediction
    MIN_CONFIDENCE = 0.70

    agent_scores = {}
    for agent in available_agents:
        pattern_key = f"agent_{agent}_{task_type}"

        if pattern_key in state['predictions']:
            pred = state['predictions'][pattern_key]

            if pred['confidence'] >= MIN_CONFIDENCE:
                # Use predicted cost for routing
                score = pred['predicted_tokens']
            else:
                # Not confident, use higher estimate
                score = pred['predicted_tokens'] * 1.5
        else:
            # No data, skip this agent or use default
            score = 10000

        agent_scores[agent] = score

    # Return agent with lowest score
    best_agent = min(agent_scores, key=agent_scores.get)
    return best_agent
```

---

## Troubleshooting Integration

### Problem: No data flowing from Phase 4 to Phase 5

**Check:**
1. Is Phase 4 creating checkpoints correctly?
2. Is the token delta being extracted?
3. Is `AdaptiveBudgetSystem.update_prediction()` being called?

**Debug:**
```python
# Verify Phase 4 checkpoint
checkpoint = TaskRelayConsciousnessIntegration.get_latest_checkpoint()
print(f"Tokens: {checkpoint.token.delta}")

# Verify Phase 5 received it
state = AdaptiveBudgetSystem.dump_state()
print(f"Patterns in Phase 5: {len(state['predictions'])}")
```

### Problem: Phase 6 not finding predictions

**Check:**
1. Pattern keys must match exactly
2. Confidence must be >= required threshold
3. Sufficient data points collected

**Debug:**
```python
# List all available patterns
state = AdaptiveBudgetSystem.dump_state()
for pattern_key in state['predictions'].keys():
    print(f"Available: {pattern_key}")

# Check specific pattern
pattern_key = "agent_researcher_alpha_research"
if pattern_key in state['predictions']:
    print(f"Found: {state['predictions'][pattern_key]}")
else:
    print(f"Not found: {pattern_key}")
```

---

## Summary

| Phase | Input | Processing | Output |
|-------|-------|-----------|--------|
| 4 | Task execution | Run relay, measure tokens | Token checkpoints |
| 5 | Token history | Predict, analyze trends | Predictions & confidence |
| 6 | Predictions | Compare agents | Best agent selection |

**Key Integration Points:**
- Phase 4 → Phase 5: Extract token delta, feed to `update_prediction()`
- Phase 5 → Phase 6: Query `dump_state()` for predictions, use in routing logic
- Data flow: Task execution → Token measurement → Pattern learning → Agent optimization
