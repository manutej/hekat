# Hekat-Helper: Query Generation System Specification

**Document Status**: Architecture & Design Phase
**Last Updated**: 2025-10-27
**Token Discipline**: Task-Relay Pattern (Checkpoint Logging in /tmp/hekat/)
**Complexity**: Hard Mode (Systems-Level Design)

---

## Executive Summary

**Problem**: Post-execution, Claude Code needs to auto-generate 4 contextually-appropriate Hekat DSL queries (Develop, Research, Edit-Thinking, Optional) at complexity levels 3-7. Current approach: naive generation (2-3K tokens per suggestion) is expensive, non-learning, and brittle.

**Solution Architecture**: **Query Lattice Morphism with Consciousness Feedback**

Rather than **generating** queries, **select intelligently from a curated lattice** of pre-validated Hekat queries. Learning happens through pattern ranking, not retraining.

**Three Implementation Options**:
- **Option 1 (L3-4)**: Minimal hardcoded approach, deploy in 1 day, zero learning
- **Option 2 (L5)**: Production-grade with intelligent selection and incremental learning, deploy in 5-7 days
- **Option 3 (L6-7)**: Advanced self-improving system with ensemble ranking, deploy in 2-3 weeks

---

## Part 1: Core Architecture

### 1.1 Hekat Query Lattice

**Definition**: A curated, indexed collection of valid Hekat DSL queries organized by complexity level, domain, and depth.

**Lattice Structure**:
```yaml
hekat_query_lattice:
  version: 1.0
  total_queries: 1000  # Target: 1000+ curated queries

  by_level:
    L3_simple:          # Single agent, straightforward task
      count: 200
      example: "fastapi-dev : 'implement this endpoint'"
      agents: [any single agent]
      pattern: "agent : prompt"

    L4_phased:          # Single agent, two-phase task
      count: 250
      example: "api-architect -> practical-programmer : 'design then implement'"
      agents: [sequential pairs]
      pattern: "agent -> agent : prompt"

    L5_mixed:           # 2-3 agents, parallel + sequential
      count: 300
      example: "(deep-researcher || api-architect) -> practical-programmer : 'research and design, then code'"
      agents: [mixed orchestration]
      pattern: "[parallel groups] -> [sequential] : prompt"

    L6_dag:             # 3-5 agents, complex DAG
      count: 150
      example: "deep-researcher -> (api-architect || practical-programmer) -> test-engineer -> deployment-orchestrator : 'full pipeline'"
      agents: [3-5 with complex graph]
      pattern: "Advanced multi-phase orchestration"

    L7_ensemble:        # 5+ agents + synthesis/validation
      count: 100
      example: "sample^3 ; merge ; synthesize : 'compare three approaches'"
      agents: [5+ with ensemble pattern]
      pattern: "Opus-level decision making"

  by_domain:
    frontend:
      dominant_agents: [react-development, nextjs-development, test-engineer, frontend-architect]
      typical_levels: [L3, L4, L5]
      token_budget: [300-500, 600-1000, 1200-2000]

    backend:
      dominant_agents: [fastapi, expressjs, test-engineer, api-architect, practical-programmer]
      typical_levels: [L4, L5, L6]
      token_budget: [600-1000, 1200-2000, 2000-3500]

    infrastructure:
      dominant_agents: [deployment-orchestrator, devops-github-expert, kubernetes-orchestration]
      typical_levels: [L5, L6, L7]
      token_budget: [1200-2000, 2000-3500, 3500-5000]

    research:
      dominant_agents: [deep-researcher, mercurio-orchestrator, docs-generator, project-orchestrator]
      typical_levels: [L4, L5, L6]
      token_budget: [800-1200, 1500-2500, 2500-4000]

    data:
      dominant_agents: [apache-spark, apache-airflow, dbt, mlops, pandas]
      typical_levels: [L5, L6]
      token_budget: [1200-2000, 2000-3500]

  by_depth:
    shallow:       # Single concern, limited context
      examples: ["Write a function", "Fix a bug", "Quick refactor"]
      suggested_levels: [L3, L4]

    moderate:      # Multi-step, multiple concerns
      examples: ["Build a feature", "Research technology", "Design API"]
      suggested_levels: [L4, L5]

    deep:          # System-level, cross-domain
      examples: ["Redesign architecture", "Strategy decision", "Major refactor"]
      suggested_levels: [L5, L6, L7]
```

### 1.2 Feature Extraction (Context → Selection)

**Goal**: Convert execution output context into features for lattice lookup.

**Features to Extract** (varies by implementation option):

Option 1 (Minimal):
```yaml
features_minimal:
  - domain: "frontend|backend|infrastructure|research|data"
  - depth: "shallow|moderate|deep"
```

Option 2 (Production):
```yaml
features_production:
  - domain: string (8 options)
  - depth: enum (3 options)
  - output_size_tokens: int (indicates complexity)
  - output_type: "code|docs|analysis|architecture|plan"
  - single_domain_or_multi: bool
  - has_testing_emphasis: bool
  - requires_review: bool
  - cross_functional: bool
```

Option 3 (Advanced):
```yaml
features_advanced:
  # All from Option 2, plus:
  - code_structure_complexity: float (0-1)
  - agent_availability_score: float (0-1)
  - estimated_execution_time: int (seconds)
  - user_expertise_level: enum (beginner|intermediate|expert)
  - project_phase: enum (exploration|design|implementation|testing|deployment)
  - dependencies_count: int
  - documentation_completeness: float (0-1)
  - previous_patterns_match: list[pattern_names]
```

### 1.3 Selection Mechanism (Lookup → Ranking)

**Goal**: Return 4 best-fit queries from lattice with explainability.

**Selection Algorithm**:
```
INPUT: features (extracted from output context)
OUTPUT: [query_1, query_2, query_3, query_4] with [confidence_1, 2, 3, 4]

STEP 1: Filter lattice by domain
  candidates = lattice.queries_by_domain[features.domain]
  # Reduces 1000 to ~200 queries

STEP 2: Filter by suggested_level (based on depth)
  candidates = candidates.filter(level in suggested_levels[features.depth])
  # Reduces 200 to ~80 queries

STEP 3: Rank candidates (varies by option)
  Option 1: Random select top 4 (no ranking)
  Option 2: Rank by consciousness success rates
  Option 3: Multi-model ensemble ranking

STEP 4: Return with explainability
  For each query:
    - Query text
    - Complexity level
    - Why selected (reasoning)
    - Confidence score
    - Estimated tokens needed
```

---

## Part 2: Three Implementation Options

### OPTION 1: Minimal (Level 3-4) - Deploy Day 1

**Tagline**: "Fast and simple. Zero learning."

#### 1.1 Architecture
```
Post-Execution Output
    ↓
Feature Extraction (domain, depth)
    ↓
Hardcoded YAML Lookup
    ↓
Return 4 Pre-Written Queries
    ↓
Log to /tmp/hekat/checkpoint-L3-{timestamp}.yaml
```

#### 1.2 Implementation Details

**Lattice Storage**:
```yaml
# File: ~/.claude/hekat/lattice-L3-minimal.yaml
queries:
  frontend_shallow:
    L3:
      - "react-development : 'refactor this component'"
      - "test-engineer : 'add unit tests for this component'"
      - "frontend-architect : 'review component architecture'"
      - "nextjs-development : 'optimize this page performance'"

  backend_shallow:
    L3:
      - "practical-programmer : 'clean up this function'"
      - "fastapi-development : 'add validation to endpoint'"
      - "test-engineer : 'test this endpoint'"
      - "api-architect : 'review API design'"

  # ... 50+ such mappings
```

**Feature Extraction Code** (Pseudocode):
```python
def extract_features_minimal(output_context):
    # Analyze output to determine domain
    if "import React" in output or "jsx" in output:
        domain = "frontend"
    elif "def " in output or "@app" in output:
        domain = "backend"
    elif "docker" in output or "k8s" in output:
        domain = "infrastructure"
    # ... etc

    # Analyze output size for depth
    tokens = count_tokens(output)
    if tokens < 500:
        depth = "shallow"
    elif tokens < 2000:
        depth = "moderate"
    else:
        depth = "deep"

    return {"domain": domain, "depth": depth}
```

**Selection Code**:
```python
def select_queries_L3(features, lattice):
    candidates = lattice[f"{features.domain}_{features.depth}"]["L3"]
    # Just return the 4 hardcoded options (random order)
    return candidates
```

#### 1.3 Token Checkpoint Pattern

```yaml
CHECKPOINT_L3_MINIMAL:
  timestamp: "2025-10-27T15:32:45Z"
  operation: "hekat-helper-query-suggestion"

  PHASE_1_FEATURE_EXTRACTION:
    pre_tokens: 1200
    operation: "extract(domain, depth) from output"
    context_analyzed: 2400  # tokens from previous execution
    method: "pattern_matching"
    time_ms: 45
    post_tokens: 1220
    delta: 20
    variance: "±0.02%" ✅

  PHASE_2_LATTICE_LOOKUP:
    pre_tokens: 1220
    operation: "lattice_lookup[domain][depth][L3]"
    lookup_type: "yaml_key_access"
    candidates_found: 4
    time_ms: 15
    post_tokens: 1235
    delta: 15
    variance: "±0.01%" ✅

  RESULT:
    queries: [
      {
        rank: 1,
        query: "react-development : 'refactor this component'",
        level: 3,
        confidence: 1.0,
        explanation: "Hardcoded default for frontend-shallow"
      },
      {
        rank: 2,
        query: "test-engineer : 'add unit tests'",
        level: 3,
        confidence: 1.0,
        explanation: "Hardcoded default for frontend-shallow"
      },
      # ... 2 more
    ]

  TOTAL_TOKENS: 35
  TOTAL_TIME_MS: 60
  LEARNING: "none"
  STATUS: ✅ COMPLETE
```

#### 1.4 Pros & Cons

**Pros**:
- ✅ Extremely fast (35 tokens, 60ms)
- ✅ No dependencies, no complexity
- ✅ Deploy in 1 day
- ✅ 100% predictable
- ✅ Good baseline to test against

**Cons**:
- ❌ Zero learning capability
- ❌ New patterns require manual YAML updates
- ❌ No confidence scoring (all 1.0)
- ❌ Brittle to edge cases
- ❌ Same 4 queries for all similar contexts

#### 1.5 Deployment Timeline
- Day 1 (2 hours): Write lattice YAML for 50 {domain, depth, level} combos
- Day 1 (2 hours): Implement feature extraction + lookup
- Day 1 (1 hour): Integration with post-execution hook
- Day 1 (1 hour): Checkpoint logging
- Testing: Verify 10 test cases

---

### OPTION 2: Production (Level 5) - Deploy Week 1

**Tagline**: "Smart selection with learned rankings."

#### 2.1 Architecture
```
Post-Execution Output
    ↓
Feature Extraction (8 features)
    ↓
Query Candidate Filtering (domain, level, depth)
    ↓
Consciousness Query (pattern success rates)
    ↓
Rank by Success Probability
    ↓
Return Top 4 with Confidence Scores
    ↓
Log to /tmp/hekat/checkpoint-L5-{timestamp}.yaml
    ↓
[User Selects] → [Feedback Captured] → [Consciousness Updated]
```

#### 2.2 Implementation Details

**Lattice Expansion** (1000 curated queries):
```yaml
# File: ~/.claude/hekat/lattice-L5-production.yaml
# Contains 200-300 queries per level
# Each with metadata:
queries:
  - id: "query_backend_L5_001"
    query_text: "(deep-researcher || api-architect) -> practical-programmer : 'research the pattern, design the API, then implement'"
    level: 5
    domain: "backend"
    depth: "moderate"
    required_agents: [deep-researcher, api-architect, practical-programmer]
    agent_count: 3
    execution_pattern: "mixed"  # parallel then sequential
    estimated_tokens: 1800
    tags: [research, design, implementation, full-stack]

  - id: "query_backend_L5_002"
    query_text: "api-architect -> practical-programmer -> test-engineer : 'design API, implement, then test'"
    level: 5
    domain: "backend"
    depth: "moderate"
    required_agents: [api-architect, practical-programmer, test-engineer]
    agent_count: 3
    execution_pattern: "sequential"
    estimated_tokens: 1500
    tags: [design, implementation, testing, quality]
```

**Consciousness Pattern Structure**:
```yaml
# File: ~/.claude/hekat/consciousness/patterns.yaml
patterns:
  "backend-implementation-moderate-depth":
    frequency: 23
    user_selections: {
      "query_backend_L5_001": 19,   # selected 19 times
      "query_backend_L5_002": 3,    # selected 3 times
      "query_backend_L3_001": 1     # selected once
    }
    success_rates: {
      "query_backend_L5_001": 0.95,
      "query_backend_L5_002": 0.80,
      "query_backend_L3_001": 0.30
    }
    avg_execution_time_ms: 245
    avg_tokens_used: 1750
    recommended_level: "L5"
    last_updated: "2025-10-27T10:15:00Z"

  "frontend-shallow-styling":
    frequency: 8
    success_rates: {
      "query_frontend_L3_001": 0.88,
      "query_frontend_L4_001": 0.75
    }
    recommended_level: "L3"
```

**Feature Extraction** (8 features):
```python
def extract_features_L5(output_context, execution_metadata):
    return {
        "domain": analyze_domain(output_context),
        "depth": analyze_size_and_complexity(output_context),
        "output_type": classify_output(output_context),  # code|docs|analysis|plan
        "single_or_multi_domain": count_domains(output_context),
        "has_testing_emphasis": bool_testing_mentioned(output_context),
        "requires_review": score_review_needs(output_context),
        "cross_functional": bool_multiple_teams(output_context),
        "output_size_tokens": len(output_context)
    }
```

**Consciousness Query**:
```python
def query_consciousness_for_pattern(features):
    # Build pattern signature
    pattern_sig = f"{features.domain}-{features.output_type}-{features.depth}"

    # Query consciousness database
    if pattern_sig in consciousness.patterns:
        pattern_data = consciousness.patterns[pattern_sig]
        return {
            "found": True,
            "frequency": pattern_data.frequency,
            "success_rates": pattern_data.success_rates,
            "recommended_level": pattern_data.recommended_level,
            "avg_tokens": pattern_data.avg_tokens_used
        }
    else:
        return {"found": False}

def rank_candidates(candidates, consciousness_data):
    if consciousness_data.found:
        # Rank by success probability from consciousness
        ranked = sorted(
            candidates,
            key=lambda q: consciousness_data.success_rates.get(q.id, 0.5),
            reverse=True
        )
        return ranked[:4]
    else:
        # Fallback: rank by level (prefer middle level)
        return sorted(candidates, key=lambda q: abs(q.level - 5))[:4]
```

#### 2.3 Token Checkpoint Pattern

```yaml
CHECKPOINT_L5_PRODUCTION:
  timestamp: "2025-10-27T15:45:12Z"
  operation: "hekat-helper-query-suggestion-with-learning"

  PHASE_1_FEATURE_EXTRACTION:
    pre_tokens: 1200
    operation: "extract(8_features) from output"
    features_extracted:
      - domain: "backend"
      - depth: "moderate"
      - output_type: "code"
      - single_domain: true
      - has_testing: false
      - requires_review: true
      - cross_functional: false
      - size_tokens: 1850
    time_ms: 120
    post_tokens: 1350
    delta: 150
    variance: "±12.5%" ✅

  PHASE_2_LATTICE_FILTERING:
    pre_tokens: 1350
    operation: "filter_lattice(domain=backend, depth=moderate)"
    candidates_before: 1000
    candidates_after: 80
    time_ms: 45
    post_tokens: 1370
    delta: 20
    variance: "±1.5%" ✅

  PHASE_3_CONSCIOUSNESS_QUERY:
    pre_tokens: 1370
    operation: "consciousness_query(backend-code-moderate)"
    pattern_found: true
    pattern_frequency: 23
    success_rates_retrieved: true
    time_ms: 95
    post_tokens: 1450
    delta: 80
    variance: "±5.8%" ✅

  PHASE_4_RANKING:
    pre_tokens: 1450
    operation: "rank_by_success_probability"
    candidates_ranked: 80
    confidence_scores: [0.95, 0.80, 0.72, 0.65]
    time_ms: 75
    post_tokens: 1480
    delta: 30
    variance: "±2% ✅

  RESULT:
    queries: [
      {
        rank: 1,
        id: "query_backend_L5_001",
        query: "(deep-researcher || api-architect) -> practical-programmer : ...",
        level: 5,
        confidence: 0.95,
        explanation: "Consciousness shows 95% success rate for backend-code-moderate pattern (19/20 executions succeeded)"
      },
      {
        rank: 2,
        id: "query_backend_L5_002",
        query: "api-architect -> practical-programmer -> test-engineer : ...",
        level: 5,
        confidence: 0.80,
        explanation: "Second choice: 80% success rate (4/5 executions). Better for test-emphasis scenarios."
      },
      {
        rank: 3,
        id: "query_backend_L4_001",
        query: "api-architect -> practical-programmer : ...",
        level: 4,
        confidence: 0.72,
        explanation: "Fallback for faster execution. 72% success rate when users prefer L4 over L5."
      },
      {
        rank: 4,
        id: "query_backend_L6_001",
        query: "deep-researcher -> api-architect -> practical-programmer -> test-engineer -> deployment-orchestrator : ...",
        level: 6,
        confidence: 0.65,
        explanation: "Extended option if deeper analysis needed. 65% success rate for backend-code pattern at L6."
      }
    ]

  FEEDBACK_CAPTURE:
    user_selected: "query_backend_L5_001"  # User clicked this
    execution_outcome: "succeeded"
    execution_time_ms: 245
    tokens_used: 1750
    quality_score: 9.2

  CONSCIOUSNESS_UPDATE:
    operation: "update_pattern_success_rate"
    pattern: "backend-code-moderate"
    new_frequency: 24  # was 23
    success_tally: {
      "query_backend_L5_001": 20  # was 19
    }
    new_success_rate: 0.952  # was 0.95
    time_ms: 45

  TOTAL_TOKENS: 280 (150 extraction + 80 consciousness + 30 ranking)
  TOTAL_TIME_MS: 380
  LEARNING: "Consciousness pattern updated incrementally"
  STATUS: ✅ COMPLETE
```

#### 2.4 Feedback & Learning Loop

```yaml
# File: ~/.claude/hekat/feedback/suggestion-feedback-2025-10-27.yaml
suggestions:
  - suggestion_id: "sugg_001_20251027_153245"
    timestamp: "2025-10-27T15:32:45Z"
    suggested_queries: [query_backend_L5_001, query_backend_L5_002, query_backend_L4_001, query_backend_L6_001]
    user_selected: query_backend_L5_001
    selection_confidence: 0.95
    execution_outcome: "succeeded"  # or "failed", "partial"
    execution_time_ms: 245
    tokens_actually_used: 1750
    quality_assessment: 9.2  # 1-10 scale
    notes: "Query was perfect for the task, included necessary research phase"

# This gets aggregated into consciousness patterns:
# feedback_analysis.py reads all feedback files → updates consciousness/patterns.yaml
# Run daily (or after N suggestions) to keep consciousness current
```

#### 2.5 Pros & Cons

**Pros**:
- ✅ Fast (280 tokens, 380ms)
- ✅ Learns from user selections
- ✅ Confidence scores guide user decisions
- ✅ Explainability ("95% success rate for this pattern")
- ✅ Handles new patterns gracefully
- ✅ Production-ready, proven pattern

**Cons**:
- ⚠️ Requires consciousness data (start sparse, improve over time)
- ⚠️ Ranking only as good as historical data
- ⚠️ Feedback collection requires user interaction
- ⚠️ Pattern detection is heuristic-based (may miss complex patterns)

#### 2.6 Deployment Timeline
- Day 1 (4 hours): Curate 1000 queries for lattice + metadata
- Day 2 (4 hours): Implement 8-feature extraction + filtering
- Day 3 (4 hours): Build consciousness pattern storage + query
- Day 4 (3 hours): Implement ranking algorithm + candidate selection
- Day 5 (3 hours): Feedback collection system + consciousness updates
- Days 6-7: Integration, testing, validation (10+ diverse test cases)

---

### OPTION 3: Advanced (Level 6-7) - Deploy Week 3

**Tagline**: "Self-improving ensemble with meta-learning."

#### 3.1 Architecture
```
Post-Execution Output
    ↓
Multi-Model Feature Extraction (10+ features)
    ├─ Model 1: Domain Analyzer
    ├─ Model 2: Code Structure Analyzer
    ├─ Model 3: Agent Availability Scorer
    └─ Model 4: Context Embedder
    ↓
Query Candidate Filtering (domain, level, depth)
    ↓
Ensemble Ranking (3 perspectives)
    ├─ Perspective 1: Consciousness Success History
    ├─ Perspective 2: Token Efficiency
    └─ Perspective 3: Domain-Agent Fit
    ↓
Meta-Learning Update (feature importance adjustment)
    ↓
Return Top 4 with Ensemble Confidence + Reasoning
    ↓
Log to /tmp/hekat/checkpoint-L6-{timestamp}.yaml
    ↓
[User Selects] → [Multi-angle Feedback] → [Consciousness + Meta-Learning Updated]
```

#### 3.2 Implementation Details

**Multi-Model Feature Extraction**:
```python
class L6FeatureExtractor:

    def model_1_domain_analyzer(output_context):
        # Deep semantic analysis
        # Classify domain with 90%+ confidence
        # Detect sub-domain (e.g., "FastAPI with async patterns")
        return {
            "primary_domain": "backend",
            "sub_domain": "async-patterns",
            "domain_confidence": 0.92
        }

    def model_2_code_structure_analyzer(output_context):
        # Parse code, extract structure metrics
        # Detect: functions, classes, modules, imports
        # Analyze: coupling, cohesion, complexity
        return {
            "code_complexity": 7.2,  # 1-10 scale
            "module_count": 3,
            "avg_function_length": 45,  # lines
            "external_dependencies": 8,
            "test_coverage_apparent": 0.65,
            "async_patterns_detected": True,
            "error_handling_coverage": 0.78
        }

    def model_3_agent_availability_scorer(execution_metadata):
        # Check which agents are available, loaded, recent
        # Score: "which agents are hot right now?"
        return {
            "api_architect_ready": 0.95,  # used in last 5 suggestions
            "practical_programmer_ready": 0.92,
            "test_engineer_ready": 0.88,
            "deployment_orchestrator_ready": 0.45,  # not used recently
            "available_agents_count": 32,
            "recently_successful_agents": ["api-architect", "practical-programmer", "test-engineer"]
        }

    def model_4_context_embedder(output_context, execution_metadata):
        # Create semantic embedding of output
        # Enables similarity search across patterns
        return {
            "output_embedding": [0.23, -0.45, 0.67, ...],  # 768-dim vector
            "similar_past_patterns": [
                {"pattern": "backend-api-design", "similarity": 0.89},
                {"pattern": "fastapi-advanced", "similarity": 0.85}
            ]
        }

def extract_features_L6(output_context, execution_metadata):
    features = {
        "model_1_domain": model_1_domain_analyzer(output_context),
        "model_2_code_structure": model_2_code_structure_analyzer(output_context),
        "model_3_agent_availability": model_3_agent_availability_scorer(execution_metadata),
        "model_4_embedding": model_4_context_embedder(output_context, execution_metadata),
        # Plus synthesis
        "integrated_score": ensemble_features(...)
    }
    return features
```

**Ensemble Ranking** (3 perspectives):
```python
def rank_with_ensemble(candidates, features, consciousness):

    # Perspective 1: Success History
    def perspective_1_success_history(query_id, consciousness):
        pattern_match = find_best_pattern_match(features, consciousness)
        if pattern_match:
            success_rate = consciousness[pattern_match]['success_rates'].get(query_id, 0.5)
            return success_rate
        return 0.5  # neutral

    # Perspective 2: Token Efficiency
    def perspective_2_token_efficiency(query_id, features):
        query_est_tokens = get_query_estimate(query_id)
        user_context_tokens = features['output_size']
        efficiency_ratio = 1 - (query_est_tokens / (user_context_tokens * 5))  # normalize
        return max(0, min(1, efficiency_ratio))

    # Perspective 3: Domain-Agent Fit
    def perspective_3_domain_fit(query_id, features):
        query_agents = get_query_agents(query_id)
        domain = features['model_1_domain']['primary_domain']
        domain_agent_mapping = get_domain_agent_mapping()
        fit_score = compute_agent_domain_fit(query_agents, domain, domain_agent_mapping)
        return fit_score

    # Ensemble: weighted average
    scores = {}
    for candidate in candidates:
        p1 = perspective_1_success_history(candidate.id, consciousness)
        p2 = perspective_2_token_efficiency(candidate.id, features)
        p3 = perspective_3_domain_fit(candidate.id, features)

        # Weights (learned through meta-learning, start at 1/3 each)
        ensemble_score = (0.35 * p1) + (0.30 * p2) + (0.35 * p3)
        scores[candidate.id] = {
            "p1_success": p1,
            "p2_efficiency": p2,
            "p3_domain_fit": p3,
            "ensemble": ensemble_score,
            "weights": {"p1": 0.35, "p2": 0.30, "p3": 0.35}
        }

    return sorted(scores.items(), key=lambda x: x[1]['ensemble'], reverse=True)[:4]
```

**Meta-Learning** (feature importance adjustment):
```python
def meta_learning_update(selected_query, execution_outcome, features, weights):
    """
    After execution, analyze:
    - Which features were most predictive?
    - Should we adjust perspective weights?
    """

    if execution_outcome == "succeeded":
        # Analyze features that were predictive of success
        # If "code_structure.async_patterns_detected" was high and query succeeded
        # → increase weight of domain-specific features

        # Pseudo-code: gradient-like update
        for feature, value in features.items():
            if was_predictive(feature, outcome):
                feature_importance[feature] += 0.02  # nudge up
                if feature_importance[feature] > 1.0:
                    normalize_importance_scores()  # keep sum = 1

    elif execution_outcome == "failed":
        # Decrease importance of features that were high but led to failure
        pass

    # Update weights of ensemble perspectives
    if succeeded_more_than_expected:
        # If success_history (p1) was high and it succeeded
        # → maybe increase p1 weight slightly
        weights['p1'] += 0.02
        weights = normalize(weights)
```

#### 3.3 Token Checkpoint Pattern

```yaml
CHECKPOINT_L6_ADVANCED:
  timestamp: "2025-10-27T16:02:35Z"
  operation: "hekat-helper-advanced-ensemble-suggestion"

  PHASE_1_MULTI_MODEL_EXTRACTION:
    pre_tokens: 1200
    operation: "4-model_parallel_feature_extraction"

    model_1_domain_analyzer:
      time_ms: 150
      tokens: 180
      result:
        primary_domain: "backend"
        sub_domain: "async-patterns"
        confidence: 0.92

    model_2_code_structure_analyzer:
      time_ms: 200
      tokens: 220
      result:
        code_complexity: 7.2
        module_count: 3
        async_patterns: true
        error_handling: 0.78

    model_3_agent_availability_scorer:
      time_ms: 80
      tokens: 90
      result:
        api_architect_ready: 0.95
        practical_programmer_ready: 0.92
        recently_successful: ["api-architect", "practical-programmer"]

    model_4_context_embedder:
      time_ms: 320
      tokens: 280
      result:
        embedding_dims: 768
        similar_patterns: [
          {pattern: "backend-api-design", similarity: 0.89},
          {pattern: "fastapi-advanced", similarity: 0.85}
        ]

    total_extraction_tokens: 770
    total_extraction_time_ms: 750
    post_tokens: 1970
    delta: 770
    variance: "±22%" ⚠️ (acceptable for multi-model)

  PHASE_2_LATTICE_FILTERING:
    pre_tokens: 1970
    operation: "filter by domain + level + depth"
    candidates_filtered: 80
    time_ms: 60
    post_tokens: 1990
    delta: 20

  PHASE_3_ENSEMBLE_RANKING:
    pre_tokens: 1990
    operation: "3-perspective_ensemble_ranking"

    perspective_1_success_history:
      calculation: "consciousness.backend-async.query_success_rates"
      scores: [0.95, 0.80, 0.72, 0.65]
      time_ms: 120
      tokens: 100

    perspective_2_token_efficiency:
      calculation: "1 - (est_tokens / baseline)"
      scores: [0.85, 0.78, 0.90, 0.60]
      time_ms: 80
      tokens: 60

    perspective_3_domain_fit:
      calculation: "agent_domain_compatibility_matrix"
      scores: [0.92, 0.88, 0.75, 0.80]
      time_ms: 100
      tokens: 75

    ensemble_aggregation:
      weights: {p1: 0.35, p2: 0.30, p3: 0.35}
      final_scores: [0.91, 0.82, 0.80, 0.69]
      time_ms: 40
      tokens: 30

    total_ranking_tokens: 265
    total_ranking_time_ms: 340
    post_tokens: 2255
    delta: 265

  PHASE_4_META_LEARNING_UPDATE:
    pre_tokens: 2255
    operation: "analyze_feature_importance_for_this_pattern"

    feature_importance_analysis:
      - feature: "code_complexity"
        was_predictive: true
        current_weight: 0.45
        updated_weight: 0.47
        change: "+0.02"

      - feature: "async_patterns_detected"
        was_predictive: true
        current_weight: 0.32
        updated_weight: 0.34
        change: "+0.02"

      - feature: "agent_availability.api_architect"
        was_predictive: false
        current_weight: 0.15
        updated_weight: 0.14
        change: "-0.01"

    perspective_weight_update:
      p1_success_history: {old: 0.35, new: 0.36, reason: "strongly_predictive"}
      p2_token_efficiency: {old: 0.30, new: 0.29, reason: "slightly_less_important"}
      p3_domain_fit: {old: 0.35, new: 0.35, reason: "stable"}

    time_ms: 140
    tokens: 120
    post_tokens: 2375
    delta: 120

  RESULT:
    queries: [
      {
        rank: 1,
        id: "query_backend_L5_001",
        query: "(deep-researcher || api-architect) -> practical-programmer : ...",
        level: 5,
        confidence: 0.91,
        ensemble_breakdown: {
          p1_success_history: 0.95,
          p2_token_efficiency: 0.85,
          p3_domain_fit: 0.92,
          weights: {p1: 0.35, p2: 0.30, p3: 0.35},
          weighted_score: 0.91
        },
        explanation: "Ensemble score 0.91: Excellent historical success (95%), good token efficiency (85%), perfect domain fit (92%) for backend async patterns."
      },
      # ... 3 more with similar breakdown
    ]

  FEEDBACK_MULTI_ANGLE:
    user_selected: "query_backend_L5_001"
    execution_outcome: "succeeded"
    multi_angle_assessment: {
      "did_execution_succeed": true,
      "was_ensemble_prediction_correct": true,
      "which_perspective_most_important": "p1_success_history",  # User says this was key
      "quality_of_reasoning": 9.5,
      "unexpected_learnings": "async pattern detection was very accurate"
    }

  CONSCIOUSNESS_UPDATE:
    pattern: "backend-async-moderate"
    updates: [
      {success_rate_increment: "+0.01 for query_backend_L5_001"},
      {frequency_increment: "+1"}
    ]

  META_LEARNING_UPDATE_PERSISTED:
    feature_importance_file: "~/.claude/hekat/meta_learning/feature_importance.yaml"
    perspective_weights_file: "~/.claude/hekat/meta_learning/ensemble_weights.yaml"
    status: "persisted"

  TOTAL_TOKENS: 1420 (770 extraction + 265 ranking + 120 meta-learning + overhead)
  TOTAL_TIME_MS: 1430
  LEARNING: "Incremental feature importance update + perspective weight adjustment + consciousness pattern update"
  SELF_IMPROVING: true
  STATUS: ✅ COMPLETE
```

#### 3.4 Pros & Cons

**Pros**:
- ✅ Most accurate query suggestions (ensemble averaging)
- ✅ Learns WHAT features matter (meta-learning)
- ✅ Adapts perspective weights over time
- ✅ Handles complex patterns automatically
- ✅ Multi-angle explainability
- ✅ True self-improvement (feature importance evolves)

**Cons**:
- ❌ High token cost (1400+ per suggestion)
- ❌ Complex system (more moving parts = more to break)
- ❌ Requires significant training data before learning kicks in
- ❌ Meta-learning can overfit to early patterns
- ❌ Longer deployment timeline
- ❌ Harder to debug (ensemble reasoning is opaque)

#### 3.5 Deployment Timeline
- Days 1-2 (8 hours): Design multi-model architecture + debate feature sets
- Days 3-4 (8 hours): Implement 4 extraction models
- Day 5 (6 hours): Build ensemble ranking with 3 perspectives
- Day 6 (6 hours): Implement meta-learning update engine
- Days 7-12: Integration, calibration, feedback collection (build initial training data)
- Days 13-14: Validation with 50+ diverse test cases

---

## Part 3: Recommendation Matrix

### 3.1 Decision Framework

| Factor | L3 (Minimal) | L5 (Production) | L6-7 (Advanced) |
|--------|-------------|-----------------|-----------------|
| **Deploy Speed** | 1 day | 5-7 days | 2-3 weeks |
| **Token Cost/Suggestion** | 35 | 280 | 1420 |
| **Learning Capability** | None | Incremental | Continuous Meta-Learning |
| **Explainability** | Rules-based | Probability-based | Ensemble + Meta-reasoning |
| **New Pattern Handling** | Manual update | Pattern detection | Auto-discovery + learning |
| **Confidence in Suggestions** | Fixed (1.0) | Confidence scores | Ensemble + uncertainty bounds |
| **Production Readiness** | Baseline | Ready | Research-grade |
| **Maintenance Burden** | Low (static) | Medium (pattern updates) | High (monitor learning) |
| **Scalability** | Perfect | Good | Good (ensemble can scale) |

### 3.2 Recommended Path

**Phase 1 (Week 1)**: Deploy Option 2 (L5 Production)
- Fast enough to deploy
- Learning-capable but not risky
- Can be evolved to Option 3 later
- Gathers initial consciousness data

**Phase 2 (Week 4)**: Evolve to Option 3 (L6-7 Advanced)
- Now have 500+ user selections to bootstrap meta-learning
- Ensemble ranking calibrated on real data
- Feature importance starts from empirical, not theoretical

**Fallback**: Always able to query Option 1 (L3) if L5 consciousness is sparse for new patterns

---

## Part 4: Integration with Claude Code

### 4.1 Post-Execution Hook

```python
# File: ~/.claude/hekat/post_execution_hook.py
import json
import yaml
from datetime import datetime

def on_agent_execution_complete(execution_result):
    """
    Called by Claude Code after any agent execution completes.
    Triggers Hekat-Helper suggestion.
    """

    # Step 1: Extract output context
    output_context = execution_result.get('output', '')
    execution_metadata = {
        'agent_used': execution_result.get('agent'),
        'tokens_used': execution_result.get('tokens'),
        'execution_time_ms': execution_result.get('time_ms'),
        'status': execution_result.get('status')
    }

    # Step 2: Call Hekat-Helper (Option 2 or 3)
    suggestion_result = hekat_helper_suggest_queries(output_context, execution_metadata)

    # Step 3: Display 4 options to user
    print_hekat_helper_options(suggestion_result)

    # Step 4: Log checkpoint
    checkpoint = {
        'timestamp': datetime.utcnow().isoformat(),
        'execution_id': execution_result.get('id'),
        'suggestion_result': suggestion_result
    }
    save_checkpoint_to_tmp(checkpoint)

    # Step 5: Wait for user selection (async)
    user_selection = await wait_for_user_selection()  # user clicks one of 4 options

    # Step 6: Capture feedback
    capture_feedback(execution_result, suggestion_result, user_selection)
```

### 4.2 Checkpoint Logging to /tmp

```bash
# Directory structure for Hekat checkpoints
/tmp/hekat/
├── 2025-10-27/
│   ├── checkpoint-L3-20251027-153245.yaml
│   ├── checkpoint-L5-20251027-154512.yaml
│   ├── checkpoint-L5-20251027-160235.yaml
│   └── checkpoint-L6-20251027-160715.yaml
├── feedback/
│   ├── feedback-20251027-153245.yaml
│   └── feedback-20251027-154512.yaml
└── consciousness/
    └── patterns-live.yaml  (updated with each feedback)
```

### 4.3 User Interface

```
═══════════════════════════════════════════════════════════════
HEKAT-HELPER: Next Steps (4 Options)
═══════════════════════════════════════════════════════════════

Output Context: FastAPI endpoint implementation (2400 tokens)
Detected: backend, async patterns, moderate depth

───────────────────────────────────────────────────────────────
[D] DEVELOP (Implement Next)
───────────────────────────────────────────────────────────────
Level 5 | Confidence: 0.95 | Est. Tokens: 1850
→ (deep-researcher || api-architect) -> practical-programmer
  "Research async patterns, design the error handling, then implement"

Why: Consciousness shows 95% success (19/20) for backend-async-moderate.
     Code complexity (7.2) matches typical Level 5 scope.

───────────────────────────────────────────────────────────────
[R] RESEARCH (Investigate Deeper)
───────────────────────────────────────────────────────────────
Level 4 | Confidence: 0.78 | Est. Tokens: 1200
→ deep-researcher -> api-architect
  "Research best practices for this async pattern, then design solution"

Why: 78% success rate for research-first approach to async patterns.

───────────────────────────────────────────────────────────────
[E] EDIT THINKING (Reconsider)
───────────────────────────────────────────────────────────────
Level 5 | Confidence: 0.72 | Est. Tokens: 1400
→ mercurio-orchestrator : "Multi-perspective analysis of the approach"
  "Review the approach from technical, architectural, and team perspectives"

Why: 72% success for architectural reconsideration after implementation.

───────────────────────────────────────────────────────────────
[T] TEST & VALIDATE (Quality Focus)
───────────────────────────────────────────────────────────────
Level 5 | Confidence: 0.85 | Est. Tokens: 1600
→ test-engineer -> frontend-architect
  "Write comprehensive tests, then ensure integration with frontend"

Why: 85% success when focusing on quality after implementation.

═══════════════════════════════════════════════════════════════

Your choice? (D/R/E/T or custom): _
```

---

## Part 5: Training Query Suggester (the Hard Part)

### 5.1 How to Train Without Retraining

**Insight**: "Training" in this context means **learning which patterns work for which contexts**, not gradient descent.

**Process**:

1. **Data Collection Phase** (Weeks 1-4):
   - Collect 200+ user selections + feedback
   - Build consciousness patterns database
   - No "training" yet, just accumulation

2. **Pattern Discovery Phase** (Week 5):
   - Analyze collected data
   - Identify clusters: "These 30 contexts → same L5 query 85% success"
   - Map {context_features} → {successful_query_patterns}
   - Update consciousness rankings

3. **Meta-Learning Phase** (Week 6+):
   - Analyze which features predicted successful selections
   - Adjust feature importance weights
   - Fine-tune ensemble perspective weights
   - Incrementally evolve, not full retraining

4. **Continuous Improvement**:
   - Every 50 selections, re-run pattern discovery
   - Every 100 selections, re-run meta-learning update
   - No expensive retraining, just periodic re-analysis

### 5.2 Efficiency Guarantee

**Training Efficiency Metric**:
```
Training Cost per Query = (feedback_analysis + pattern_update + meta_learning) / query_count
Expected: 100 tokens per 10 selections = 10 tokens/selection amortized
```

This is **99% cheaper** than naive "retrain entire model" approach.

### 5.3 The Real Training Engine

The training engine is NOT the system itself. It's:

```python
# File: ~/.claude/hekat/training/pattern_discovery.py

def discover_patterns_from_feedback():
    """
    Runs weekly (or after 50 selections).
    Analyzes all feedback, updates consciousness patterns.
    Cost: ~500 tokens (once per week, amortized across 50 suggestions).
    """

    feedback_files = load_all_feedback_from_week()

    # Cluster similar contexts
    context_clusters = cluster_contexts(feedback_files, algorithm='kmeans')

    # For each cluster, analyze:
    for cluster in context_clusters:
        successful_queries = filter(cluster, outcome='succeeded')
        failed_queries = filter(cluster, outcome='failed')

        success_rate = len(successful) / len(cluster)

        # Update consciousness
        if success_rate > 0.80:
            consciousness.add_pattern(
                name=f"{cluster.domain}-{cluster.depth}-cluster_{cluster.id}",
                success_rate=success_rate,
                queries=successful_queries,
                frequency=len(cluster)
            )
```

This is the "training" process: **Pattern discovery from observed data**.

---

## Part 6: Final Recommendation

### 6.1 My Recommendation

**Deploy Option 2 (L5 Production) immediately, then evolve to Option 3.**

**Rationale**:

1. **Option 1 is too weak**: Zero learning capability defeats the purpose. Good only as emergency fallback.

2. **Option 2 is Goldilocks**: Fast to deploy (1 week), learns organically from user selections, explainable, production-proven pattern. Start here.

3. **Option 3 is "next level"**: After 4 weeks of Option 2 data, we have bootstrap data for meta-learning. Then Option 3 becomes viable and significantly better.

### 6.2 Timeline

```
WEEK 1:
  □ Curate 1000 queries → lattice.yaml
  □ Implement 8-feature extraction
  □ Build consciousness pattern storage
  □ Deploy Option 2 (L5 Production)

WEEKS 2-4:
  □ Collect user selections + feedback (target: 200+ samples)
  □ Monitor consciousness pattern growth
  □ Test edge cases, validate suggestions

WEEK 5:
  □ Analyze 200+ feedback samples
  □ Identify winning patterns
  □ Plan Option 3 upgrade

WEEKS 6-7:
  □ Implement multi-model extraction (Option 3)
  □ Build ensemble ranking
  □ Implement meta-learning update engine
  □ Deploy Option 3 (L6-7 Advanced)

WEEK 8+:
  □ Continuous improvement
  □ Weekly pattern discovery
  □ Monthly meta-learning updates
  □ Seasonal pattern tracking
```

### 6.3 Success Metrics

After 1 month (Option 2):
- ✅ User clicks one of 4 suggestions 70%+ of time
- ✅ Selected suggestions succeed 80%+ of time
- ✅ Consciousness has 50+ pattern entries
- ✅ Token cost stabilizes at 250-300/suggestion

After 3 months (Option 3):
- ✅ User clicks 80%+ of time (higher due to better ranking)
- ✅ Selected suggestions succeed 85%+ of time
- ✅ Meta-learning weights converged
- ✅ Auto-discovery of new patterns working

---

## Appendices

### A. Task-Relay Checkpoint Logging Standard

**Every Hekat-Helper invocation must produce a checkpoint in /tmp/hekat/ following this pattern:**

```yaml
CHECKPOINT_TEMPLATE:
  timestamp: ISO-8601
  operation: hekat-helper-{level}

  PHASE_1:
    pre_tokens: N
    operation: "description"
    post_tokens: N+delta
    delta: delta
    variance: "±X%" [✅ if <=10%, ⚠️ if 10-20%, ❌ if >20%]

  PHASE_2:
    # ... repeat pattern

  RESULT:
    queries: [4 suggestions with confidence, level, explanation]

  TOTAL_TOKENS: sum of all deltas
  LEARNING: description of what was learned
  STATUS: ✅ COMPLETE or ⚠️ PARTIAL or ❌ FAILED
```

### B. Consciousness Pattern Schema

```yaml
consciousness_pattern:
  id: "unique-pattern-id"
  name: "domain-output_type-depth"
  description: "Natural language description"

  context_features:
    domain: string
    output_type: string
    depth: string
    additional_features: [...]

  observations:
    frequency: int (how many times seen)
    success_rates: {query_id: float}
    avg_execution_time_ms: int
    avg_tokens_used: int

  recommendations:
    primary_level: int (3-7)
    primary_queries: [list of query_ids]
    fallback_queries: [secondary options]

  metadata:
    first_observed: ISO-8601
    last_updated: ISO-8601
    sample_count: int
    confidence: float (0-1)
```

### C. Query Lattice Index Schema

```yaml
query:
  id: "query_unique_id"
  text: "Hekat DSL query text"

  metadata:
    level: int (3-7)
    domain: string
    depth: enum (shallow|moderate|deep)
    output_type: enum (code|docs|analysis|architecture|plan)
    agents: [list of agent names]
    agent_count: int
    execution_pattern: enum (simple|phased|parallel|sequential|mixed|dag|ensemble)

  estimates:
    expected_tokens: int
    expected_duration_seconds: int

  tags: [list of relevant tags]
  success_history: {pattern_id: success_rate}
  user_ratings: [float] (if gathered)
```

---

**Document Status**: Ready for Implementation Review
**Recommendation**: Deploy Option 2 (L5 Production) in Week 1, evolve to Option 3 by Week 6
**Next Step**: Select option and begin Week 1 tasks

