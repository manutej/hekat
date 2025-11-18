# HEKAT TUI Agent - Minimal Implementation Spec

**Project**: Terminal TUI for Hekat DSL Query Builder
**Status**: Design Phase → Implementation Ready
**Track**: ✅ Production (L1-L4) + ⚠️ Experimental (L5 Optional)
**Timeline**: 3-6 months for production track
**Alignment**: ASTRO HUB vision + Claude Agent SDK + Reality-Based Implementation

---

## Executive Summary

Build a **minimal, production-ready** Terminal User Interface (TUI) that:
1. Uses **Claude Agent SDK** (TypeScript/Python) for LLM integration
2. Implements **Hekat DSL L1-L4** (production track - 95% of use cases)
3. Leverages **AnthropicClientManager** for token budget tracking
4. Provides **voice-accessible** interface (future enhancement)
5. Aligns with **ASTRO HUB** philosophy (intelligent, astrological workflow orchestration)

**Reality Check**: Focus on L1-L4 (proven patterns) before L5+ (experimental).

---

## Architecture: Three-Layer Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    HEKAT TUI AGENT                          │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: TUI Interface                                     │
│  ├─ Input: Hekat DSL queries (L1-L4)                       │
│  ├─ Display: Real-time execution status                    │
│  ├─ Output: Results + token usage                          │
│  └─ Tools: Ink (React for terminal) or Textual (Python)    │
│                                                             │
│  Layer 2: Hekat DSL Parser & Executor                      │
│  ├─ Parser: L1-L4 syntax → AST                            │
│  ├─ Executor: AST → Agent orchestration                    │
│  ├─ Token Budget: Track usage per query                    │
│  └─ State: Persist context between queries                 │
│                                                             │
│  Layer 3: Claude Agent SDK + API Wrapper                   │
│  ├─ AnthropicClientManager: Token-budgeted API calls       │
│  ├─ Agent Registry: Available agents + capabilities        │
│  ├─ Multi-Provider: Fallback support                       │
│  └─ Streaming: Real-time response display                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Minimal Feature Set (L1-L4 Production Track)

### Level 1: Single Agent Invocation ✅

**DSL Syntax**:
```hekat
agent-name: "task description"
```

**Example**:
```hekat
deep-researcher: "Analyze FastAPI async patterns"
```

**Implementation**:
```typescript
// Parse L1 query
const query = parseL1('deep-researcher: "Analyze FastAPI async patterns"');

// Execute with token budget
const result = await budgetManager.createMessageWithBudget(
  query.task,
  {
    model: 'claude-3-5-sonnet-20241022',
    maxTokens: 2000,
    systemPrompt: getAgentPrompt(query.agentName)
  }
);

// Display result + budget status
tui.displayResult(result);
tui.displayBudget(budgetManager.getBudgetStatus());
```

**Features**:
- ✅ Agent validation (check if agent exists)
- ✅ Token estimation before execution
- ✅ Timeout enforcement (2 min max)
- ✅ Cost display (estimated vs actual)
- ✅ Error recovery with user-friendly messages

---

### Level 2: Sequential + Combination ✅

**DSL Syntax**:
```hekat
# Sequential (->)
agent1: "task1" -> agent2: "task2"

# Combination (+)
agent1 + agent2: "combined task"
```

**Example**:
```hekat
deep-researcher: "Analyze FastAPI" -> practical-programmer: "Implement based on research"
```

**Implementation**:
```typescript
// Parse L2 query
const query = parseL2('deep-researcher: "Analyze" -> practical-programmer: "Implement"');

// Execute sequential pipeline with checkpointing
const stage1 = await executeAgent(query.stages[0], budget);
tui.displayCheckpoint('Stage 1 complete', stage1.tokens);

const stage2 = await executeAgent(query.stages[1], budget, stage1.context);
tui.displayCheckpoint('Stage 2 complete', stage2.tokens);

// Display final result + budget
tui.displayPipeline([stage1, stage2]);
tui.displayBudget(budgetManager.getBudgetStatus());
```

**Features**:
- ✅ Checkpointing between stages
- ✅ Context propagation (controlled merge)
- ✅ Token variance tracking
- ✅ Rollback capability on failure
- ✅ Visual progress indicator

---

### Level 3: Parallel Execution ✅

**DSL Syntax**:
```hekat
agent1: "task1" || agent2: "task2" || agent3: "task3"
```

**Example**:
```hekat
deep-researcher: "FastAPI" || deep-researcher: "PostgreSQL" || deep-researcher: "Docker"
```

**Implementation**:
```typescript
// Parse L3 query
const query = parseL3('agent1: "A" || agent2: "B" || agent3: "C"');

// Execute in parallel with progress tracking
const promises = query.parallel.map((task, idx) =>
  executeAgent(task, budget).then(result => {
    tui.updateParallelProgress(idx, 'complete', result.tokens);
    return result;
  })
);

const results = await Promise.all(promises);

// Merge results with conflict resolution
const merged = mergeResults(results);
tui.displayParallelResults(results, merged);
tui.displayBudget(budgetManager.getBudgetStatus());
```

**Features**:
- ✅ Async/await parallelism
- ✅ Partial failure tolerance (continue if some succeed)
- ✅ Resource pooling
- ✅ Result merging with conflict resolution
- ✅ Real-time progress bars for each parallel task

---

### Level 4: Conditional + Retry + Feedback ⚠️

**DSL Syntax**:
```hekat
# Conditional
condition ? agent1: "task1" : agent2: "task2"

# Retry with fallback
(agent1: "task1") >retry(3)> agent2: "fallback"

# Feedback loop
(agent1 -> agent2) >until(convergence)
```

**Example**:
```hekat
needs_research ? deep-researcher: "analyze" : practical-programmer: "implement directly"
```

**Implementation**:
```typescript
// Parse L4 query
const query = parseL4('condition ? agent1: "A" : agent2: "B"');

// Evaluate condition
const condition = await evaluateCondition(query.condition);
tui.displayCondition(condition);

// Execute based on condition
const result = condition
  ? await executeAgent(query.thenBranch, budget)
  : await executeAgent(query.elseBranch, budget);

tui.displayConditionalResult(result);
tui.displayBudget(budgetManager.getBudgetStatus());
```

**Features**:
- ✅ Retry with exponential backoff
- ✅ Circuit breaker pattern
- ✅ Convergence detection (for loops)
- ✅ State management across iterations
- ✅ User-defined conditions with validation

---

## Technology Stack

### Option 1: TypeScript + Ink (React for Terminal) ⭐ RECOMMENDED

**Why**:
- ✅ Aligns with existing microservice (TypeScript)
- ✅ React components → reusable TUI widgets
- ✅ Strong ecosystem for terminal UIs
- ✅ Claude Agent SDK TypeScript support

**Stack**:
```typescript
// Core
- TypeScript 5.x
- @anthropic-ai/sdk
- AnthropicClientManager (from microservice)

// TUI
- Ink (React for terminal)
- ink-text-input (input boxes)
- ink-select-input (menus)
- ink-spinner (loading indicators)
- ink-table (result display)

// Parser
- chevrotain (DSL parser generator)
- typescript-parsec (alternative)

// State
- zustand (lightweight state management)
- immer (immutable state updates)
```

**Directory Structure**:
```
hekat-tui/
├── src/
│   ├── components/          # Ink React components
│   │   ├── QueryInput.tsx   # DSL input box
│   │   ├── ExecutionPanel.tsx  # Live execution status
│   │   ├── ResultDisplay.tsx   # Results + budget
│   │   └── AgentSelector.tsx   # Agent picker
│   ├── parser/              # Hekat DSL parser
│   │   ├── l1.ts            # Level 1 parser
│   │   ├── l2.ts            # Level 2 parser
│   │   ├── l3.ts            # Level 3 parser
│   │   ├── l4.ts            # Level 4 parser
│   │   └── ast.ts           # AST types
│   ├── executor/            # Query executor
│   │   ├── engine.ts        # Main execution engine
│   │   ├── agents.ts        # Agent registry
│   │   ├── budget.ts        # Token budget manager
│   │   └── state.ts         # State persistence
│   ├── sdk/                 # Claude SDK wrapper
│   │   ├── client-manager.ts  # Import from microservice
│   │   └── agent-prompts.ts   # Agent system prompts
│   ├── app.tsx              # Main TUI app
│   └── index.ts             # Entry point
├── tests/
│   ├── parser/              # Parser tests
│   ├── executor/            # Executor tests
│   └── integration/         # E2E tests
├── package.json
├── tsconfig.json
└── README.md
```

---

### Option 2: Python + Textual (Alternative)

**Why**:
- ✅ Rich TUI framework with modern widgets
- ✅ Python Agent SDK support
- ✅ Great for prototyping

**Stack**:
```python
# Core
- Python 3.10+
- anthropic (Python SDK)
- TokenBudgetManager (port from TS)

# TUI
- textual (modern TUI framework)
- rich (beautiful terminal output)

# Parser
- lark (EBNF parser)
- pyparsing (alternative)

# State
- pydantic (data validation)
- sqlite3 (state persistence)
```

---

## Implementation Phases

### Phase 1: MVP (Months 1-2) 🚀 PRIORITY

**Goal**: Ship L1-L2 with basic TUI

**Deliverables**:
1. ✅ L1 parser + executor (single agent)
2. ✅ L2 parser + executor (sequential)
3. ✅ Basic TUI with input/output
4. ✅ Token budget tracking
5. ✅ Agent registry (5-10 agents)
6. ✅ Unit tests (80% coverage)

**Success Metrics**:
- Can execute 95% of L1-L2 queries successfully
- Token budget tracking accurate within 10%
- TUI responsive (<100ms input lag)
- Error messages clear and actionable

**Timeline**: 6-8 weeks

---

### Phase 2: Production Track Complete (Months 2-4)

**Goal**: Ship L3-L4 with advanced features

**Deliverables**:
1. ✅ L3 parser + executor (parallel)
2. ⚠️ L4 parser + executor (conditional/retry)
3. ✅ Enhanced TUI with progress tracking
4. ✅ Multi-provider fallback
5. ✅ State persistence (save/load queries)
6. ✅ Integration tests

**Success Metrics**:
- Can execute 90% of L3-L4 queries successfully
- Parallel execution 2-3x faster than sequential
- Retry logic works >95% of the time
- State persistence reliable

**Timeline**: 8-10 weeks

---

### Phase 3: ASTRO HUB Integration (Months 4-6)

**Goal**: Align with ASTRO HUB vision

**Deliverables**:
1. ✅ Astrological agent prompts
2. ✅ Chart analysis workflows
3. ✅ Transit tracking workflows
4. ✅ Progression calculation workflows
5. ✅ Natural language to DSL translation
6. ✅ Voice interface prototype (experimental)

**Success Metrics**:
- Can execute astro-specific workflows
- Natural language translation >80% accurate
- Voice interface usable (hands-free)

**Timeline**: 8-10 weeks

---

### Phase 4: Experimental (L5) - OPTIONAL (Months 6-12)

**Goal**: Validate meta-controller value

**Deliverables**:
1. ⚠️ L5 parser + executor (meta-controller)
2. ⚠️ Dynamic orchestration engine
3. ⚠️ Benchmarks vs L4 static workflows
4. ⚠️ User studies + feedback

**Decision Gate**:
- If value > cost → promote to production
- If not → keep as experimental or research

**Timeline**: 12-16 weeks

---

## Parser Implementation (Chevrotain Example)

### L1 Parser (Single Agent)

```typescript
import { createToken, Lexer, CstParser } from 'chevrotain';

// Tokens
const AgentName = createToken({ name: 'AgentName', pattern: /[a-z\-]+/ });
const Colon = createToken({ name: 'Colon', pattern: /:/ });
const String = createToken({ name: 'String', pattern: /"[^"]*"/ });

// Lexer
const allTokens = [AgentName, Colon, String];
const lexer = new Lexer(allTokens);

// Parser
class HekatL1Parser extends CstParser {
  constructor() {
    super(allTokens);
    this.performSelfAnalysis();
  }

  public query = this.RULE('query', () => {
    this.CONSUME(AgentName);
    this.CONSUME(Colon);
    this.CONSUME(String);
  });
}

// Usage
const parser = new HekatL1Parser();
const tokens = lexer.tokenize('deep-researcher: "Analyze FastAPI"');
parser.input = tokens.tokens;
const cst = parser.query();

// Convert CST to AST
interface L1Query {
  agentName: string;
  task: string;
}

function cstToAst(cst: any): L1Query {
  return {
    agentName: cst.children.AgentName[0].image,
    task: cst.children.String[0].image.slice(1, -1) // Remove quotes
  };
}
```

---

## Executor Implementation

### L1 Executor

```typescript
import { AnthropicClientManager, TokenBudgetManager } from './sdk/client-manager';
import { getAgentPrompt } from './sdk/agent-prompts';

interface ExecutionContext {
  budget: TokenBudgetManager;
  state: Map<string, any>;
}

async function executeL1(
  query: L1Query,
  context: ExecutionContext
): Promise<ExecutionResult> {
  // 1. Validate agent exists
  const agentPrompt = getAgentPrompt(query.agentName);
  if (!agentPrompt) {
    throw new Error(`Agent "${query.agentName}" not found`);
  }

  // 2. Estimate tokens
  const estimated = context.budget.estimateTokens(query.task, {
    systemPrompt: agentPrompt
  });
  console.log(`Estimated tokens: ${estimated}`);

  // 3. Execute with budget tracking
  const startTime = Date.now();
  const message = await context.budget.createMessageWithBudget(query.task, {
    model: 'claude-3-5-sonnet-20241022',
    maxTokens: 2000,
    systemPrompt: agentPrompt
  });

  // 4. Return result
  return {
    agentName: query.agentName,
    task: query.task,
    result: message.content[0].text,
    tokens: {
      input: message.usage.input_tokens,
      output: message.usage.output_tokens,
      total: message.usage.input_tokens + message.usage.output_tokens
    },
    duration: Date.now() - startTime,
    budget: context.budget.getBudgetStatus()
  };
}
```

---

## TUI Implementation (Ink Example)

### Main App Component

```typescript
import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';
import { QueryInput } from './components/QueryInput';
import { ExecutionPanel } from './components/ExecutionPanel';
import { ResultDisplay } from './components/ResultDisplay';
import { BudgetDisplay } from './components/BudgetDisplay';

const App = () => {
  const [query, setQuery] = useState('');
  const [executing, setExecuting] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (query: string) => {
    setExecuting(true);
    try {
      const parsed = parseQuery(query);
      const result = await executeQuery(parsed);
      setResult(result);
    } catch (error) {
      setResult({ error: error.message });
    } finally {
      setExecuting(false);
    }
  };

  return (
    <Box flexDirection="column" padding={1}>
      <Text bold color="cyan">
        🔮 HEKAT TUI - Astrological Agent Orchestration
      </Text>

      <Box marginTop={1}>
        <QueryInput onSubmit={handleSubmit} disabled={executing} />
      </Box>

      {executing && (
        <Box marginTop={1}>
          <ExecutionPanel />
        </Box>
      )}

      {result && (
        <Box marginTop={1} flexDirection="column">
          <ResultDisplay result={result} />
          <BudgetDisplay status={budgetStatus} />
        </Box>
      )}
    </Box>
  );
};

export default App;
```

---

## Agent Prompts Registry

### Example Agent Prompts

```typescript
const AGENT_PROMPTS = {
  'deep-researcher': `You are a deep research specialist. Analyze topics comprehensively, cite sources, and provide actionable insights. Focus on:
- Technical accuracy
- Recent developments (2024-2025)
- Practical applications
- Code examples when relevant`,

  'practical-programmer': `You are a pragmatic programmer following "The Pragmatic Programmer" philosophy. Write clean, maintainable code that:
- Solves the problem (no excuses)
- Follows DRY, KISS, SOLID principles
- Includes tests
- Is production-ready`,

  'astro-analyst': `You are an astrological analysis specialist. Interpret charts with:
- Traditional and modern techniques
- Dignities and essential qualities
- Aspect patterns and configurations
- Transit timing and progressions
- Practical life guidance`,

  'frontend-architect': `You are a frontend architecture expert. Design React/TypeScript systems with:
- Component composition
- State management (Zustand, Context)
- Performance optimization
- Accessibility (WCAG)
- Testing strategies`,
};

export function getAgentPrompt(agentName: string): string | undefined {
  return AGENT_PROMPTS[agentName];
}

export function listAgents(): string[] {
  return Object.keys(AGENT_PROMPTS);
}
```

---

## ASTRO HUB Alignment

### Astrological Workflow Examples

```hekat
# L1: Single chart analysis
astro-analyst: "Analyze natal chart for Manu born Jan 15, 1985 at 10:30 AM in New York"

# L2: Sequential workflow
deep-researcher: "Research Saturn return timing" -> astro-analyst: "Interpret Saturn return for current transits"

# L3: Parallel research
deep-researcher: "Pluto in Aquarius" || deep-researcher: "Neptune in Pisces" || deep-researcher: "Uranus in Taurus"

# L4: Conditional based on chart type
is_natal_chart ? astro-analyst: "Interpret natal positions" : astro-analyst: "Interpret synastry aspects"
```

### ASTRO HUB Integration Points

1. **Chart Calculation** (via microservice)
   - Use existing `/api/v1/astro/natal-chart` endpoint
   - Hekat TUI orchestrates analysis workflows

2. **Agent Prompts** (astrological expertise)
   - Classical astrology techniques
   - Modern psychological interpretation
   - Evolutionary astrology perspectives

3. **Workflow Templates** (common patterns)
   - `natal-analysis`: Birth chart → houses → aspects → synthesis
   - `transit-timing`: Current transits → aspect analysis → timing forecast
   - `progression-analysis`: Secondary progressions → solar arc → lunar progressions

---

## Success Metrics

### Production Track (L1-L4)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Query Success Rate | >95% | Successful executions / total attempts |
| Token Budget Accuracy | ±10% | Estimated vs actual token usage |
| Response Time | <2 min | P95 latency for L1-L3 queries |
| Error Recovery | >90% | Clear error messages + recovery suggestions |
| User Satisfaction | >4/5 stars | User feedback surveys |
| Code Coverage | >80% | Unit + integration tests |

### Experimental Track (L5)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Value vs Cost | >2x | Dynamic orchestration benefit vs L4 static |
| Correctness | >90% | Generated workflows execute successfully |
| User Adoption | >3 real use cases | Identified production scenarios |
| Decision Gate | 6-12 months | Promote to production OR research-only |

---

## Deployment Strategy

### Local Development

```bash
# Clone repo
git clone https://github.com/yourusername/hekat-tui.git
cd hekat-tui

# Install dependencies
npm install

# Set environment variables
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# Run in development
npm run dev

# Run tests
npm test

# Build for production
npm run build

# Run production build
npm start
```

### Distribution

```bash
# NPM package
npm publish

# NPX execution (no install required)
npx hekat-tui

# Homebrew formula (macOS)
brew install hekat-tui

# Snap package (Linux)
snap install hekat-tui
```

---

## Next Steps

1. **Choose Stack**: TypeScript + Ink (recommended) or Python + Textual
2. **Implement L1**: Single agent parser + executor + basic TUI
3. **Test with Real Queries**: Use ASTRO HUB workflows
4. **Iterate Based on Feedback**: Refine parser and executor
5. **Expand to L2-L4**: Sequential, parallel, conditional
6. **Integrate with Microservice**: Use existing API endpoints
7. **Add Voice Interface**: Natural language → DSL translation

---

## Open Questions

1. **Should we use existing microservice or standalone CLI?**
   - Option A: TUI calls microservice API (separation of concerns)
   - Option B: TUI embeds SDK directly (self-contained)

   **Recommendation**: Option B for MVP (faster), Option A for production (scalable)

2. **How to handle long-running queries (>5 min)?**
   - Option A: Streaming with progress updates
   - Option B: Background execution + notification

   **Recommendation**: Option A (better UX)

3. **Voice interface: local STT or cloud API?**
   - Option A: Whisper API (cloud, accurate)
   - Option B: Mozilla DeepSpeech (local, private)

   **Recommendation**: Option A for MVP, Option B for privacy-conscious users

---

## Summary

This spec defines a **minimal, production-ready** Hekat TUI Agent that:
- ✅ Focuses on L1-L4 (proven patterns serving 95% of use cases)
- ✅ Uses Claude Agent SDK with token budget tracking
- ✅ Provides clean TUI with real-time execution feedback
- ✅ Aligns with ASTRO HUB astrological workflow vision
- ⚠️ Optionally supports L5 (experimental, requires validation)
- 🔬 Leaves L6-L7 for long-term research

**Timeline**: 3-6 months for production track (L1-L4)
**Technology**: TypeScript + Ink + Claude Agent SDK (recommended)
**Focus**: Ship simple things now, complex things carefully, impossible things later

Let's build this! 🚀
