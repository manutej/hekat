# Hekat DSL Implementation Plan

**Status**: Ready to Begin Phase 1
**Based On**: Production-ready specifications and research
**Timeline**: 6 phases, estimated 12-16 weeks

---

## Overview

This implementation plan converts the complete Hekat DSL research and design into a working compiler, runtime, and voice interface. Each phase builds on the previous, with clear deliverables and success criteria.

**Key Resources**:
- Design Spec: `../design/DSL-ORCHESTRATION-REFINED.md`
- Voice Spec: `../docs/DSL-VERBAL-INTERFACE.md`
- Grammar: `../design/dsl-specification.md`
- Examples: `../docs/dsl-examples.md`

---

## Phase 1: Compiler Foundation ⏳

**Duration**: 3-4 weeks
**Goal**: Parse DSL expressions and build typed execution DAG

### Deliverables

#### 1.1 Lexer (Week 1)
**Input**: DSL source code
**Output**: Token stream

**Implementation**:
```python
# hekat/compiler/lexer.py
from enum import Enum
from dataclasses import dataclass

class TokenType(Enum):
    # Operators
    SEQUENTIAL = "->"
    PARALLEL = "||"
    COMBINATION = "+"
    SPECIFICATION = ":"

    # Literals
    IDENTIFIER = "identifier"
    AGENT_LITERAL = "/agent"
    STRING = "string"
    NUMBER = "number"

    # Grouping
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"

    # Keywords
    WORKFLOW = "workflow"
    IF = "if"
    ELSE = "else"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> list[Token]:
        tokens = []
        while not self.is_eof():
            tokens.append(self.next_token())
        return tokens

    def next_token(self) -> Token:
        self.skip_whitespace()

        if self.peek() == '/':
            return self.agent_literal()

        if self.peek().isalpha():
            return self.identifier_or_keyword()

        if self.peek() == '"':
            return self.string_literal()

        # ... operator matching
```

**Tests**:
- [ ] Tokenize simple expressions: `a -> b`
- [ ] Handle whitespace and comments
- [ ] Recognize all operators
- [ ] Parse agent literals: `/ctx7`, `/deep`
- [ ] String and number literals

**Success Criteria**:
- All token types recognized
- Line/column tracking accurate
- Error messages helpful

---

#### 1.2 Parser (Week 1-2)
**Input**: Token stream
**Output**: Abstract Syntax Tree (AST)

**Implementation** (Precedence Climbing):
```python
# hekat/compiler/parser.py
from dataclasses import dataclass
from typing import Union

# AST Node Types (from DSL-ORCHESTRATION-REFINED.md section 4.2)
@dataclass
class Expression:
    pass

@dataclass
class Agent(Expression):
    name: str

@dataclass
class Sequential(Expression):
    left: Expression
    right: Expression

@dataclass
class Parallel(Expression):
    branches: list[Expression]

@dataclass
class Combination(Expression):
    agent: Expression
    skills: list[Expression]

@dataclass
class Binding(Expression):
    agent: Expression
    task: str

class Parser:
    PRECEDENCE = {
        ":": 5,   # Highest (specification)
        "||": 4,  # Parallel
        "->": 3,  # Sequential
        "+": 2,   # Combination
    }

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> Expression:
        return self.parse_expression(0)

    def parse_expression(self, min_prec: int) -> Expression:
        """Precedence climbing algorithm"""
        left = self.parse_primary()

        while self.is_binary_op() and self.precedence() >= min_prec:
            op = self.consume()
            prec = self.precedence(op)

            # Right-associative: ->, :
            # Left-associative: ||, +
            next_prec = prec if self.is_right_assoc(op) else prec + 1

            right = self.parse_expression(next_prec)
            left = self.make_binary_op(op, left, right)

        return left

    def parse_primary(self) -> Expression:
        if self.match("LPAREN"):
            expr = self.parse_expression(0)
            self.expect("RPAREN")
            return expr

        if self.match("SLASH"):
            name = self.expect("IDENTIFIER")
            return Agent(name=f"/{name}")

        if self.match("IDENTIFIER"):
            return Agent(name=self.previous())

        raise ParseError(f"Expected expression at {self.peek()}")
```

**Reference**: DSL-ORCHESTRATION-REFINED.md lines 623-708 (Parser implementation)

**Tests**:
- [ ] Parse Level 1: `agent : "task"`
- [ ] Parse Level 2: `a -> b`, `a || b`, `a + s`
- [ ] Parse Level 3: `(a + b) || (c -> d) : "task"`
- [ ] Operator precedence correct
- [ ] Associativity correct
- [ ] Error recovery

**Success Criteria**:
- AST correctly represents all complexity levels
- Precedence and associativity match specification
- Parse errors with helpful messages

---

#### 1.3 Type Checker (Week 2-3)
**Input**: AST
**Output**: Typed AST with validation

**Implementation**:
```python
# hekat/compiler/type_checker.py
from typing import TypeVar, Generic

A = TypeVar('A')
B = TypeVar('B')

@dataclass
class AgentType(Generic[A, B]):
    input: Type[A]
    output: Type[B]

class TypeChecker:
    def __init__(self, env: TypeEnv):
        self.env = env

    def check(self, expr: Expression) -> AgentType:
        match expr:
            case Agent(name):
                return self.env.lookup(name)

            case Sequential(left, right):
                left_type = self.check(left)
                right_type = self.check(right)

                if left_type.output != right_type.input:
                    raise TypeError(
                        f"Type mismatch: {left_type.output} ≠ {right_type.input}\n"
                        f"Agent '{left.name}' outputs {left_type.output}\n"
                        f"Agent '{right.name}' expects {right_type.input}"
                    )

                return AgentType(
                    input=left_type.input,
                    output=right_type.output
                )

            case Parallel(branches):
                types = [self.check(branch) for branch in branches]

                # All must accept same input
                input_type = types[0].input
                if not all(t.input == input_type for t in types):
                    raise TypeError("Parallel agents must accept same input type")

                return AgentType(
                    input=input_type,
                    output=tuple(t.output for t in types)
                )

            # ... other cases
```

**Reference**: DSL-ORCHESTRATION-REFINED.md lines 481-556 (Type system and checking)

**Tests**:
- [ ] Valid sequential: `String->String` → `String->String` ✓
- [ ] Invalid sequential: `String->Number` → `Number->Bool` ✗
- [ ] Valid parallel: Same input types
- [ ] Invalid parallel: Different input types
- [ ] Skill combination type preservation

**Success Criteria**:
- Type errors caught at compile time
- Clear error messages with location
- Type inference works for complex expressions

---

#### 1.4 DAG Builder (Week 3-4)
**Input**: Typed AST
**Output**: Directed Acyclic Graph (DAG)

**Implementation**:
```python
# hekat/compiler/dag_builder.py
from dataclasses import dataclass
import networkx as nx

@dataclass
class Node:
    id: str
    type: str  # "agent" | "join" | "fork"
    agent_name: str = None
    estimated_time: int = 0
    estimated_tokens: int = 0

@dataclass
class Edge:
    source: Node
    target: Node
    edge_type: str  # "sequential" | "parallel"

class DAGBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.node_counter = 0

    def build(self, expr: Expression) -> nx.DiGraph:
        """Convert AST to DAG"""
        final_node = self.visit(expr)

        # Validate DAG properties
        self.validate()

        return self.graph

    def visit(self, expr: Expression) -> Node:
        match expr:
            case Agent(name):
                node = Node(
                    id=self.next_id(),
                    type="agent",
                    agent_name=name,
                    **self.lookup_metadata(name)
                )
                self.graph.add_node(node.id, **node.__dict__)
                return node

            case Sequential(left, right):
                left_node = self.visit(left)
                right_node = self.visit(right)

                self.graph.add_edge(
                    left_node.id,
                    right_node.id,
                    edge_type="sequential"
                )

                return right_node  # Final node

            case Parallel(branches):
                # Create fork and join nodes
                fork = self.create_node("fork")
                join = self.create_node("join")

                # Visit all branches
                for branch in branches:
                    branch_node = self.visit(branch)

                    # Fork → Branch
                    self.graph.add_edge(fork.id, branch_node.id)
                    # Branch → Join
                    self.graph.add_edge(branch_node.id, join.id)

                return join

    def validate(self):
        """Validate DAG properties"""
        # Check acyclicity
        if not nx.is_directed_acyclic_graph(self.graph):
            cycle = nx.find_cycle(self.graph)
            raise ValueError(f"Circular dependency detected: {cycle}")

        # Check connectivity
        if not nx.is_weakly_connected(self.graph):
            raise ValueError("DAG contains disconnected components")
```

**Reference**: DSL-ORCHESTRATION-REFINED.md lines 714-826 (DAG construction)

**Tests**:
- [ ] Simple sequence: `a -> b` produces 2-node DAG
- [ ] Parallel: `a || b` produces fork-join DAG
- [ ] Complex: `(a || b) -> c` correct structure
- [ ] Cycle detection: `a -> b -> a` raises error
- [ ] Metadata preserved (time, token estimates)

**Success Criteria**:
- DAG correctly represents all expression types
- Cycle detection works
- Metadata attached to nodes
- Visualization possible (DOT format)

---

### Phase 1 Success Criteria

**Compiler works end-to-end**:
```python
from hekat.compiler import compile_dsl

# Input
source = """
workflow research_pipeline:
  (/deep || /ctx7) -> synthesize : "DSL design"
"""

# Compile
dag = compile_dsl(source)

# Output
assert dag.nodes_count == 4  # /deep, /ctx7, join, synthesize
assert dag.is_valid()
assert dag.estimated_time > 0
```

**Deliverables**:
- [x] Working lexer with all token types
- [x] Precedence-climbing parser
- [x] Type checker with error messages
- [x] DAG builder with validation
- [x] Test suite (90%+ coverage)
- [x] CLI tool: `hekat compile workflow.dsl`

---

## Phase 2: Runtime Execution ⏳

**Duration**: 2-3 weeks
**Goal**: Execute DAGs with stratified parallelism and resource management

### Deliverables

#### 2.1 Stratification Algorithm (Week 1)
**Input**: DAG
**Output**: Levels for parallel execution

**Implementation**:
```python
# hekat/runtime/stratifier.py
from collections import defaultdict

def stratify(dag: nx.DiGraph) -> list[set[Node]]:
    """
    Topological stratification for parallel execution.
    Reference: DSL-ORCHESTRATION-REFINED.md lines 836-872
    """
    levels = []
    in_degree = {node: 0 for node in dag.nodes}

    # Calculate in-degrees
    for edge in dag.edges:
        in_degree[edge[1]] += 1

    remaining = set(dag.nodes)

    while remaining:
        # Level = nodes with in-degree 0
        level = {node for node in remaining if in_degree[node] == 0}

        if not level:
            raise CycleError("Cycle detected during stratification")

        levels.append(level)

        # Update in-degrees
        for node in level:
            for successor in dag.successors(node):
                in_degree[successor] -= 1

        remaining -= level

    return levels
```

**Tests**:
- [ ] Linear DAG: `a -> b -> c` produces 3 levels
- [ ] Parallel DAG: `a || b || c` produces 1 level
- [ ] Diamond: `a -> (b||c) -> d` produces 3 levels
- [ ] Complex: Correct stratification for Level 4 examples

**Success Criteria**:
- Optimal parallelism detected
- Levels respect dependencies
- Deterministic ordering within levels

---

#### 2.2 Execution Engine (Week 1-2)
**Input**: Stratified DAG
**Output**: Execution results

**Implementation**:
```python
# hekat/runtime/executor.py
import asyncio
from typing import Any

class Executor:
    def __init__(self, dag: nx.DiGraph):
        self.dag = dag
        self.levels = stratify(dag)

    async def execute(self, initial_state: dict[str, Any]) -> dict[str, Any]:
        """
        Execute DAG level by level.
        Reference: DSL-ORCHESTRATION-REFINED.md lines 896-923
        """
        state = initial_state.copy()

        for level_idx, level in enumerate(self.levels):
            print(f"Executing level {level_idx}: {len(level)} agents")

            # Launch all agents in level (parallel)
            tasks = [
                self.execute_agent(node, state)
                for node in sorted(level, key=lambda n: n.id)  # Deterministic
            ]

            # SYNCHRONIZATION BARRIER
            results = await asyncio.gather(*tasks)

            # Merge results
            state = self.merge_results(state, level, results)

            print(f"Level {level_idx} complete")

        return state

    async def execute_agent(self, node: Node, state: dict) -> Any:
        """Execute single agent"""
        agent = self.load_agent(node.agent_name)

        # Get input from state
        input_data = state.get(node.id + "_input", state.get("global_input"))

        # Execute with timeout
        result = await asyncio.wait_for(
            agent.execute(input_data),
            timeout=node.estimated_time * 2  # 2x estimate
        )

        return result

    def merge_results(
        self,
        state: dict,
        level: set[Node],
        results: list[Any]
    ) -> dict:
        """Merge results into state (deterministic)"""
        new_state = state.copy()

        for node, result in zip(sorted(level, key=lambda n: n.id), results):
            new_state[node.id] = result

        return new_state
```

**Tests**:
- [ ] Sequential execution preserves order
- [ ] Parallel execution runs concurrently
- [ ] Synchronization barrier works
- [ ] Results merged correctly
- [ ] Timeouts enforced

**Success Criteria**:
- Executes all complexity levels correctly
- Deterministic results (same DAG + input = same output)
- Proper error handling

---

#### 2.3 Resource Manager (Week 2-3)
**Input**: DAG + budget constraints
**Output**: Resource allocation

**Implementation**:
```python
# hekat/runtime/resource_manager.py

class ResourceManager:
    def __init__(self, total_tokens: int, max_concurrent: int):
        self.total_tokens = total_tokens
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    def allocate_budget(self, dag: nx.DiGraph) -> dict[str, int]:
        """
        Proportional token allocation.
        Reference: DSL-ORCHESTRATION-REFINED.md lines 1008-1040
        """
        reserve = int(self.total_tokens * 0.1)  # 10% reserve
        available = self.total_tokens - reserve

        total_estimated = sum(
            node.estimated_tokens
            for node in dag.nodes.values()
        )

        allocation = {}
        for node in dag.nodes.values():
            proportion = node.estimated_tokens / total_estimated
            allocation[node.id] = int(available * proportion)

        return allocation

    async def execute_with_limit(self, fn):
        """Concurrency limiter"""
        async with self.semaphore:
            return await fn()
```

**Tests**:
- [ ] Budget allocated proportionally
- [ ] Reserve maintained
- [ ] Concurrency limited
- [ ] Token tracking accurate

**Success Criteria**:
- Budget constraints respected
- Fair allocation
- No resource exhaustion

---

### Phase 2 Success Criteria

**Runtime works end-to-end**:
```python
from hekat.runtime import execute_workflow

# Compiled DAG from Phase 1
dag = compile_dsl(source)

# Execute with constraints
results = await execute_workflow(
    dag,
    initial_state={"topic": "DSL design"},
    budget=50000,  # tokens
    max_concurrent=3
)

assert results["status"] == "success"
assert results["token_usage"] < 50000
```

**Deliverables**:
- [x] Stratification algorithm
- [x] Async execution engine
- [x] Resource manager
- [x] Timeout handling
- [x] Error recovery
- [x] CLI tool: `hekat run workflow.dsl`

---

## Phase 3: Voice Interface ⏳

**Duration**: 3 weeks
**Goal**: Natural language → DSL compilation with voice support

### Deliverables

#### 3.1 Intent Recognition (Week 1)
**Input**: Natural language text
**Output**: Structured intent

**Implementation**:
```python
# hekat/voice/intent_recognizer.py
import re
from anthropic import Anthropic

class IntentRecognizer:
    """
    Reference: DSL-VERBAL-INTERFACE.md lines 492-537
    """
    PATTERNS = {
        "sequential": [
            r"(.*) then (.*) then (.*)",
            r"(.*) followed by (.*)",
            r"first (.*) then (.*)"
        ],
        "parallel": [
            r"parallel: (.*), (.*), (.*)",
            r"(.*) and (.*) together",
            r"run (.*) and (.*) at the same time"
        ],
        "combination": [
            r"(.*) with (.*) and (.*)",
            r"(.*) plus (.*)"
        ],
        "task_spec": [
            r"(.*) task: (.*)",
            r"(.*) on topic (.*)"
        ]
    }

    def __init__(self):
        self.client = Anthropic()

    def recognize(self, text: str) -> dict:
        """Pattern matching + Claude fallback"""
        # Try regex patterns first
        for intent_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                match = re.match(pattern, text, re.IGNORECASE)
                if match:
                    return {
                        "type": intent_type,
                        "groups": match.groups()
                    }

        # Fallback to Claude
        return self.claude_parse(text)

    def claude_parse(self, text: str) -> dict:
        """Use Claude for complex intent recognition"""
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            messages=[{
                "role": "user",
                "content": f"""Parse this voice command into structured intent:
                "{text}"

                Return JSON with:
                - type: sequential | parallel | combination | task_spec
                - agents: list of agent names
                - task: task description (if any)
                """
            }]
        )

        return parse_json(response.content[0].text)
```

**Tests**:
- [ ] Recognize sequential: "A then B"
- [ ] Recognize parallel: "A and B together"
- [ ] Recognize combination: "A with skill B"
- [ ] Recognize task: "A on topic X"
- [ ] Claude fallback for complex queries

---

#### 3.2 DSL Translator (Week 1-2)
**Input**: Structured intent
**Output**: Formal DSL

**Implementation**:
```python
# hekat/voice/dsl_translator.py

class DSLTranslator:
    """
    Reference: DSL-VERBAL-INTERFACE.md lines 539-566
    """
    AGENT_ALIASES = {
        "context seven": "/ctx7",
        "context lookup": "/ctx7",
        "deep research": "/deep",
        "deep researcher": "/deep",
        "A P I architect": "api-architect",
        "skill builder": "/meta-skill-builder"
    }

    def translate(self, intent: dict) -> str:
        """Convert intent to formal DSL"""
        match intent["type"]:
            case "sequential":
                agents = [self.resolve_agent(a) for a in intent["agents"]]
                return " -> ".join(agents)

            case "parallel":
                agents = [self.resolve_agent(a) for a in intent["agents"]]
                return " || ".join(agents)

            case "combination":
                agent = self.resolve_agent(intent["agents"][0])
                skills = [self.resolve_agent(s) for s in intent["agents"][1:]]
                return f"{agent} + {' + '.join(skills)}"

            case "task_spec":
                agent = self.resolve_agent(intent["agents"][0])
                task = intent["task"]
                return f'{agent} : "{task}"'

    def resolve_agent(self, name: str) -> str:
        """Map speakable names to formal names"""
        return self.AGENT_ALIASES.get(name.lower(), name)
```

---

#### 3.3 Speech Integration (Week 2-3)
**Input**: Voice audio
**Output**: Compiled DSL

**Implementation**:
```python
# hekat/voice/speech_pipeline.py
import speech_recognition as sr

class VoicePipeline:
    """
    Complete voice → DSL pipeline.
    Reference: DSL-VERBAL-INTERFACE.md lines 1022-1145
    """
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.intent_parser = IntentRecognizer()
        self.translator = DSLTranslator()

    def listen(self) -> str:
        """Capture speech and convert to text"""
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
            text = self.recognizer.recognize_google(audio)
            print(f"Heard: {text}")
            return text

    def compile_from_voice(self, audio_or_text: str) -> str:
        """Complete pipeline"""
        # 1. Speech to text (if audio)
        if isinstance(audio_or_text, bytes):
            text = self.speech_to_text(audio_or_text)
        else:
            text = audio_or_text

        # 2. Remove wake word
        if text.lower().startswith("claude"):
            text = text[7:].strip()

        # 3. Parse intent
        intent = self.intent_parser.recognize(text)

        # 4. Translate to DSL
        dsl = self.translator.translate(intent)

        return dsl
```

**Tests**:
- [ ] Speech recognition accuracy > 90%
- [ ] Wake word detection
- [ ] Intent parsing
- [ ] DSL generation
- [ ] End-to-end: voice → executable DAG

---

### Phase 3 Success Criteria

**Voice interface works**:
```python
from hekat.voice import VoicePipeline

pipeline = VoicePipeline()

# User says: "Claude, run deep research and context lookup in parallel,
#             then synthesize findings on DSL design"

dsl = pipeline.compile_from_voice()
# Result: "(/deep || /ctx7) -> synthesize : \"DSL design\""

dag = compile_dsl(dsl)
results = execute_workflow(dag)
```

**Deliverables**:
- [x] Intent recognition (regex + Claude)
- [x] DSL translator
- [x] Speech-to-text integration
- [x] Voice modes (family time, focus)
- [x] CLI tool: `hekat voice`

---

## Phase 4: MCP Server ⏳

**Duration**: 2 weeks
**Goal**: MCP server for Claude Code integration

### Deliverables

#### 4.1 MCP Server (Week 1)

**Implementation**:
```typescript
// hekat/mcp/server.ts
import { Server } from '@modelcontextprotocol/sdk/server';

const server = new Server({
  name: "hekat-dsl",
  version: "1.0.0"
});

// Tool: Compile DSL
server.tool(
  "compile_dsl",
  {
    source: { type: "string", description: "DSL source code" }
  },
  async (args) => {
    const { dag, errors } = await compileDSL(args.source);

    if (errors.length > 0) {
      return { success: false, errors };
    }

    return {
      success: true,
      dag: serialize(dag),
      estimated_tokens: dag.estimatedTokens,
      estimated_time: dag.estimatedTime
    };
  }
);

// Tool: Execute workflow
server.tool(
  "execute_workflow",
  {
    dag: { type: "object" },
    initial_state: { type: "object" },
    budget: { type: "number" }
  },
  async (args) => {
    const results = await executeWorkflow(
      deserialize(args.dag),
      args.initial_state,
      { budget: args.budget }
    );

    return results;
  }
);
```

**Reference**: DSL-ORCHESTRATION-REFINED.md lines 1236-1284

---

### Phase 4 Success Criteria

**MCP server working**:
```bash
# Start server
hekat serve

# Test from Claude Code
mcp__hekat-dsl__compile_dsl(source="a -> b")
mcp__hekat-dsl__execute_workflow(dag=..., budget=50000)
```

**Deliverables**:
- [x] MCP server implementation
- [x] Tool: compile_dsl
- [x] Tool: execute_workflow
- [x] Tool: validate_dsl
- [x] Claude Code integration guide

---

## Phase 5: Claude Code Integration ⏳

**Duration**: 1-2 weeks
**Goal**: Generate Claude Code artifacts from DSL

### Deliverables

#### 5.1 Artifact Generator

**Implementation**:
```python
# hekat/codegen/artifact_generator.py

class ArtifactGenerator:
    """
    Generate .claude/ artifacts from DAG.
    Reference: DSL-ORCHESTRATION-REFINED.md lines 1096-1167
    """
    def generate(self, dag: nx.DiGraph, output_dir: Path):
        """Generate all artifacts"""
        # Generate agents
        for node in dag.nodes.values():
            if node.type == "agent":
                self.generate_agent(node, output_dir / "agents")

        # Generate command
        self.generate_command(dag, output_dir / "commands")

    def generate_agent(self, node: Node, agents_dir: Path):
        """Generate agent markdown"""
        content = f"""---
name: {node.agent_name}
model: claude-3-sonnet-20240229
tools:
  - read
  - write
  - task
---

# {node.agent_name.title()}

You are {node.agent_name}.

Task: {node.task}

Execute this task thoroughly and return results.
"""
        (agents_dir / f"{node.agent_name}.md").write_text(content)

    def generate_command(self, dag: nx.DiGraph, commands_dir: Path):
        """Generate workflow command"""
        levels = stratify(dag)

        execution_steps = []
        for level_idx, level in enumerate(levels):
            if len(level) == 1:
                node = list(level)[0]
                execution_steps.append(
                    f"Use Task tool to invoke `{node.agent_name}` agent"
                )
            else:
                agents = [n.agent_name for n in level]
                execution_steps.append(
                    f"Use Task tool in parallel for: {', '.join(agents)}"
                )

        content = f"""---
description: Generated workflow
---

Execute workflow:

{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(execution_steps))}

Return final results.
"""
        (commands_dir / "workflow.md").write_text(content)
```

---

### Phase 5 Success Criteria

**Artifact generation works**:
```bash
hekat compile workflow.dsl --output .claude/

# Generates:
# .claude/agents/deep_researcher.md
# .claude/agents/synthesizer.md
# .claude/commands/research_workflow.md

# Use in Claude Code
/research_workflow
```

**Deliverables**:
- [x] Agent generator
- [x] Command generator
- [x] Skill generator (optional)
- [x] Integration tests

---

## Phase 6: Production Hardening ⏳

**Duration**: 2 weeks
**Goal**: Production-ready deployment

### Deliverables

#### 6.1 Performance Optimization
- [ ] Critical path analysis
- [ ] Caching layer
- [ ] Lazy evaluation
- [ ] Parallel optimization

#### 6.2 Error Handling
- [ ] Retry with exponential backoff
- [ ] Circuit breaker
- [ ] Graceful degradation
- [ ] Comprehensive logging

#### 6.3 Security
- [ ] Input validation
- [ ] Sandbox execution
- [ ] Rate limiting
- [ ] Audit logging

#### 6.4 Documentation
- [ ] API documentation
- [ ] User guides
- [ ] Video tutorials
- [ ] Example gallery

#### 6.5 Testing
- [ ] Unit tests (90%+ coverage)
- [ ] Integration tests
- [ ] Property-based tests (hypothesis)
- [ ] Performance benchmarks

---

## Success Metrics

### Phase 1-2: Compiler + Runtime
- [ ] Compile all 6 complexity levels
- [ ] Execute all patterns correctly
- [ ] Type errors caught at compile time
- [ ] Deterministic execution

### Phase 3: Voice
- [ ] 90%+ intent recognition accuracy
- [ ] Support all 6 complexity levels
- [ ] < 500ms latency (text → DSL)

### Phase 4-5: Integration
- [ ] MCP server stable
- [ ] Claude Code artifacts valid
- [ ] Workflows execute correctly

### Phase 6: Production
- [ ] Performance benchmarks met
- [ ] Security audit passed
- [ ] Documentation complete
- [ ] User adoption

---

## Timeline

```
Week  1-2:  Phase 1.1-1.2  Lexer + Parser
Week  3-4:  Phase 1.3-1.4  Type Checker + DAG Builder
Week  5-6:  Phase 2.1-2.2  Stratifier + Executor
Week  7:    Phase 2.3      Resource Manager
Week  8-9:  Phase 3.1-3.2  Intent + Translation
Week 10:    Phase 3.3      Speech Integration
Week 11-12: Phase 4        MCP Server
Week 13:    Phase 5        Claude Code Integration
Week 14-16: Phase 6        Production Hardening
```

**Total**: 12-16 weeks for complete implementation

---

## Risk Mitigation

### Technical Risks
1. **Voice accuracy** < 90%
   - Mitigation: Multiple recognition engines, Claude fallback

2. **Performance** slower than manual
   - Mitigation: Aggressive caching, lazy evaluation, parallel execution

3. **Type system** too complex
   - Mitigation: Start simple, add gradually

### Dependency Risks
1. **Claude API** rate limits
   - Mitigation: Local intent patterns first, Claude fallback

2. **MCP protocol** changes
   - Mitigation: Abstract MCP layer, version pinning

---

## Next Steps

**Immediate (This Week)**:
1. Set up project structure: `hekat/compiler/`, `hekat/runtime/`, `hekat/voice/`
2. Install dependencies: `lark-parser`, `networkx`, `speech_recognition`, `anthropic`
3. Create basic CLI: `hekat --help`
4. Start Phase 1.1: Lexer implementation

**First Milestone (Week 4)**:
- Working compiler (Phases 1.1-1.4)
- Can compile all examples from docs/
- CLI tool functional

**Second Milestone (Week 7)**:
- Working runtime (Phases 2.1-2.3)
- Can execute compiled DAGs
- Resource management working

**Third Milestone (Week 10)**:
- Voice interface (Phase 3)
- Natural language → DSL working
- Accessibility features implemented

**Final Milestone (Week 16)**:
- Production release
- Full Claude Code integration
- Documentation complete

---

**Status**: Ready to begin Phase 1.1 (Lexer)
**Owner**: TBD
**Started**: TBD
**Estimated Completion**: 12-16 weeks from start
