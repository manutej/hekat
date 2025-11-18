# Patterns 5-13: Sequential, Hierarchical, and Advanced Comonadic Workflows

---

## Pattern 5: Sequential Pipeline

**Comonadic Form**: `agent1 → agent2 → agent3 → final`

Each agent receives:
- The immediate output from previous agent
- Full context history of all prior stages

```python
def sequential_pipeline(input_data):
    """Pipeline: Research → Analyze → Synthesize"""
    ctx = Context(focus=input_data, history=[])

    # Stage 1: Research
    research = deep_researcher_agent(ctx)
    ctx = ctx.extend(lambda _: research)

    # Stage 2: Analysis
    analysis = api_architect_agent(ctx.focus)
    ctx = ctx.extend(lambda _: analysis)

    # Stage 3: Synthesis
    synthesis = mercurio_orchestrator_agent(
        f"Prior research: {research}\nAnalysis: {analysis}"
    )

    return synthesis
```

**Agents**: deep-researcher → api-architect → mercurio-orchestrator
**Token Cost**: ~2K per stage = 6K total
**When to use**: Sequential dependencies with each stage building on prior

---

## Pattern 6: Hierarchical Cascade

**Comonadic Form**: `stage1 → {agents*} → aggregate → stage2 → {agents*} → aggregate`

Multi-level parallel processing where each level aggregates before proceeding.

```python
def hierarchical_cascade(problem):
    """Multi-tier: individual experts → team leads → executive"""

    # Tier 1: Individual specialist analysis
    specialists = {
        "backend": api_architect_agent(problem),
        "frontend": frontend_architect_agent(problem),
        "devops": deployment_orchestrator_agent(problem),
    }

    # Aggregate to team leads
    backend_lead = practical_programmer_agent(
        f"Backend analysis: {specialists['backend']}"
    )
    frontend_lead = practical_programmer_agent(
        f"Frontend analysis: {specialists['frontend']}"
    )

    # Aggregate to executive summary
    executive = mercurio_orchestrator_agent(
        f"Backend lead: {backend_lead}\nFrontend lead: {frontend_lead}"
    )

    return executive
```

**Pattern**: Level 1 parallel → aggregate → Level 2 parallel → aggregate
**Token Cost**: ~5K (2K specialists + 1.5K leads + 1.5K executive)

---

## Pattern 7: Bidirectional Window & Attention

**Comonadic Form**: `◄► context → focus:current ↔ history`

Sliding context window with full bidirectional access.

```python
@dataclass
class WindowContext:
    """Sliding window with bilateral access"""
    full_history: list
    window_position: int
    window_size: int = 5

    def extract(self):
        """Get current window"""
        start = max(0, self.window_position - self.window_size//2)
        end = min(len(self.full_history), self.window_position + self.window_size//2)
        return self.full_history[start:end]

    def slide_forward(self):
        """Move window forward"""
        return WindowContext(
            full_history=self.full_history,
            window_position=self.window_position + 1,
            window_size=self.window_size
        )

def process_long_document(doc_sections):
    """Process document with sliding attention"""
    ctx = WindowContext(full_history=doc_sections, window_position=0)

    results = []
    while ctx.window_position < len(ctx.full_history):
        window = ctx.extract()
        # Agent sees: current section + 2 before + 2 after
        analysis = analyze_section_with_context(window)
        results.append(analysis)
        ctx = ctx.slide_forward()

    return results
```

**Use Case**: Processing long documents, conversations, code files
**Token Cost**: Per window ~400 tokens (bounded by window size)

---

## Pattern 8: Research Synthesis

**Comonadic Form**: `⟲ collect:research → validate:fact-check → critique → synthesize`

Iterative research with validation and refinement.

```python
def research_synthesis_loop(topic):
    """Research with validation and critique"""
    ctx = ResearchContext(topic=topic, iterations=[])

    for iteration in range(3):
        # Collect research
        findings = deep_researcher_agent(topic, iteration=iteration)

        # Fact-check findings
        validated = context7_doc_reviewer_agent(
            findings,
            task="cross-reference claims against sources"
        )

        # Critique quality
        critique = debug_detective_agent(
            f"Research findings: {findings}\nValidation: {validated}",
            task="identify gaps and weaknesses"
        )

        # Synthesize
        synthesis = docs_generator_agent(
            f"Findings: {findings}\nValidation: {validated}\nCritique: {critique}",
            task="create polished synthesis"
        )

        ctx.iterations.append({
            "findings": findings,
            "validated": validated,
            "critique": critique,
            "synthesis": synthesis
        })

        if is_converged(synthesis):
            return synthesis

    return ctx.iterations[-1]["synthesis"]
```

**Pattern**: Collect → Validate → Critique → Synthesize → Repeat
**Token Cost**: ~3K per iteration
**Best for**: Deep understanding with high confidence

---

## Pattern 9: Error Recovery Loop

**Comonadic Form**: `try:agent → catch:error → backtrack → alternative → retry`

Intelligent failure handling with graceful degradation.

```python
@dataclass
class RecoveryContext:
    """Context for error recovery"""
    original_input: str
    attempts: list[dict]
    fallback_agent: str

    def execute_with_recovery(self, agents: list):
        """Try agents sequentially, with recovery"""
        for agent in agents:
            try:
                result = agent(self.original_input)
                return result
            except Exception as e:
                self.attempts.append({
                    "agent": agent.__name__,
                    "error": str(e),
                    "fallback_tried": False
                })

        # Recovery: use fallback agent
        recovery = practical_programmer_agent(
            f"Primary approaches failed:\n{self.attempts}\n"
            f"Try alternative approach"
        )
        return recovery

def resilient_analysis(query):
    """Try multiple agents with intelligent fallback"""
    ctx = RecoveryContext(original_input=query, attempts=[], fallback_agent="practical-programmer")

    agents = [
        api_architect_agent,
        frontend_architect_agent,
        practical_programmer_agent,
    ]

    result = ctx.execute_with_recovery(agents)
    if len(ctx.attempts) > 0:
        print(f"✓ Recovered from {len(ctx.attempts)} failures")

    return result
```

**Pattern**: Primary → Error → Fallback → Alternative → Success
**Token Cost**: Varies, but graceful degradation prevents total failure

---

## Pattern 10: Consensus Formation

**Comonadic Form**: `⟲ {experts} → ◄► weighted → aggregate:decision`

Multi-expert consensus with weighting by reliability.

```python
def expert_consensus(question):
    """Get consensus from multiple weighted experts"""

    experts = {
        "api": (api_architect_agent, 1.2),  # Higher expertise weight
        "practical": (practical_programmer_agent, 1.0),
        "test": (test_engineer_agent, 0.9),
    }

    opinions = {}
    weights = {}

    # Gather opinions
    for expert_name, (agent, weight) in experts.items():
        opinion = agent(question)
        opinions[expert_name] = opinion
        weights[expert_name] = weight

    # Build consensus
    consensus = mercurio_orchestrator_agent(
        f"Expert opinions:\n{opinions}\n\n"
        f"Expert weights (reliability):\n{weights}\n\n"
        f"Form consensus that respects expertise levels"
    )

    return {
        "opinions": opinions,
        "weights": weights,
        "consensus": consensus,
        "confidence": calculate_agreement(opinions)
    }
```

**Pattern**: Broadcast → Weight by expertise → Weighted consensus
**Token Cost**: ~3K tokens
**When to use**: High-stakes decisions needing expert input

---

## Pattern 11: Streaming Aggregation

**Comonadic Form**: `stream → fold:accumulate → extract:checkpoint`

Process infinite streams with bounded memory.

```python
@dataclass
class StreamAggregator:
    """Aggregate streaming data with bounded memory"""
    window: list
    accumulated_result: dict
    window_size: int = 100

    def process_item(self, item):
        """Process one item from stream"""
        self.window.append(item)

        if len(self.window) >= self.window_size:
            # Process accumulated window
            batch_result = analyze_batch(self.window)
            self._merge_results(batch_result)
            self.window = []  # Reset for next batch

        return self.accumulated_result

    def _merge_results(self, new_result):
        """Merge batch result into accumulated results"""
        # Incrementally update, don't store all history
        self.accumulated_result.update(new_result)

def stream_processor(data_stream):
    """Process infinite stream with bounded memory"""
    agg = StreamAggregator(window=[], accumulated_result={}, window_size=100)

    for item in data_stream:
        result = agg.process_item(item)
        if should_checkpoint(agg):
            yield result
```

**Pattern**: Window → Process → Merge → Extract checkpoint → Continue
**Token Cost**: O(window_size), not O(total_items)

---

## Pattern 12: Knowledge Validation

**Comonadic Form**: `⟲ fact-check → cross-ref → verify:dependencies`

Iterative fact verification with dependency tracking.

```python
def validate_knowledge_graph(claims: dict[str, str]) -> dict:
    """Verify claims with cross-references and dependencies"""

    verified = {}
    fact_queue = list(claims.items())
    iterations = 0

    while fact_queue and iterations < 5:
        claim_id, claim_text = fact_queue.pop(0)

        # Fact check
        check = context7_doc_reviewer_agent(
            claim_text,
            task="verify this claim with sources"
        )

        # Cross-reference
        cross_ref = debug_detective_agent(
            f"Claim: {claim_text}\nVerification: {check}",
            task="identify dependencies on other claims"
        )

        verified[claim_id] = {
            "claim": claim_text,
            "verification": check,
            "dependencies": extract_dependencies(cross_ref)
        }

        # Re-verify dependent claims
        dependent_claims = [c for c in claims if c in extract_dependencies(cross_ref)]
        fact_queue.extend(dependent_claims)

        iterations += 1

    return verified
```

**Pattern**: Verify → Check dependencies → Re-verify affected claims → Converge
**Token Cost**: ~500 tokens per claim
**Use for**: High-trust information (research, documentation, specs)

---

## Pattern 13: Adaptive Orchestration

**Comonadic Form**: `⟲ monitor:metrics → optimize:strategy → adapt:agents`

Self-adjusting workflows that optimize based on performance metrics.

```python
@dataclass
class AdaptiveOrchestration:
    """Workflow that adapts agents based on performance"""
    agents: dict[str, callable]
    agent_scores: dict[str, float]
    current_strategy: str

    def select_best_agent(self, task):
        """Select agent with highest success rate for this task"""
        scores_for_task = self.agent_scores  # Could be task-specific
        best_agent = max(scores_for_task.items(), key=lambda x: x[1])
        return self.agents[best_agent[0]]

    def execute_and_monitor(self, task) -> dict:
        """Execute task, measure performance, adapt"""
        agent = self.select_best_agent(task)

        result = agent(task)

        # Measure success
        success_score = evaluate_result(result)

        # Update agent score (exponential moving average)
        agent_name = agent.__name__
        old_score = self.agent_scores.get(agent_name, 0.5)
        new_score = 0.7 * old_score + 0.3 * success_score
        self.agent_scores[agent_name] = new_score

        # Adapt strategy if needed
        if success_score < 0.6:
            self.current_strategy = "fallback"
        else:
            self.current_strategy = "optimal"

        return {
            "result": result,
            "agent_used": agent_name,
            "success": success_score,
            "new_score": new_score
        }

def adaptive_workflow(tasks: list[str]) -> list:
    """Process tasks with adaptive agent selection"""
    orch = AdaptiveOrchestration(
        agents={
            "api": api_architect_agent,
            "practical": practical_programmer_agent,
            "test": test_engineer_agent,
        },
        agent_scores={"api": 0.5, "practical": 0.5, "test": 0.5},
        current_strategy="optimal"
    )

    results = []
    for task in tasks:
        result = orch.execute_and_monitor(task)
        results.append(result)

        # Every 10 tasks, log strategy adjustment
        if len(results) % 10 == 0:
            print(f"Agent scores: {orch.agent_scores}")
            print(f"Strategy: {orch.current_strategy}")

    return results
```

**Pattern**: Execute → Monitor → Score → Adapt selection → Continue
**Token Cost**: ~1K overhead for monitoring/adaptation
**Use for**: Long-running workflows where performance matters

---

## Pattern Composition Matrix

```
Sequential (5) + Broadcast (3)  → Parallel stages
Perpetual (1) + Self-Critique (4) → Iterative improvement
Extract (2) + Broadcast (3)  → Memory-efficient parallel
Consensus (10) + Validation (12) → Verified agreement
Adaptive (13) + any pattern  → Self-optimizing workflow
```

---

**Status**: All 13 patterns documented with examples
**Next**: Deploy to real Claude Code workflows
**Integration**: Ready for hekat DSL implementation

Created: 2025-10-23
