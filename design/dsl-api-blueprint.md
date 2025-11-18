# CCAO-DSL: API Implementation Blueprint

**Companion to**: dsl-specification.md, dsl-examples.md
**Version**: 1.0.0
**Date**: 2025-10-19
**Purpose**: Detailed API contracts and implementation guidance

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Core Interfaces](#2-core-interfaces)
3. [Implementation Modules](#3-implementation-modules)
4. [Data Flow](#4-data-flow)
5. [Extension Points](#5-extension-points)

---

## 1. Architecture Overview

### 1.1 System Layers

```
┌─────────────────────────────────────────────────┐
│              DSL Layer                          │
│  ┌───────────────────────────────────────────┐ │
│  │   Workflow Definition (.dsl files)        │ │
│  └───────────────────────────────────────────┘ │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│           Compiler Layer                        │
│  ┌─────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Lexer   │─→│  Parser  │─→│ Type Checker │  │
│  └─────────┘  └──────────┘  └──────────────┘  │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│          Optimizer Layer                        │
│  ┌─────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ DAG     │─→│ Parallel │─→│ Resource     │  │
│  │ Builder │  │ Detector │  │ Allocator    │  │
│  └─────────┘  └──────────┘  └──────────────┘  │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│          Runtime Layer                          │
│  ┌─────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Executor│─→│ Agent    │─→│ Result       │  │
│  │         │  │ Registry │  │ Aggregator   │  │
│  └─────────┘  └──────────┘  └──────────────┘  │
└─────────────────────────────────────────────────┘
```

### 1.2 Component Interaction

```python
# High-level execution flow

# 1. Parse DSL
ast = parser.parse(dsl_source)

# 2. Type check
typed_ast = typechecker.check(ast, registry)

# 3. Optimize
dag = optimizer.build_dag(typed_ast)
plan = optimizer.create_execution_plan(dag)

# 4. Execute
result = await executor.execute(plan, context)

# 5. Return
return result
```

---

## 2. Core Interfaces

### 2.1 Parser Interface

```python
from typing import Protocol, List, Optional
from dataclasses import dataclass
from enum import Enum

# Token types
class TokenType(Enum):
    IDENTIFIER = "IDENTIFIER"
    AGENT = "AGENT"
    SKILL = "SKILL"
    COMMAND = "COMMAND"
    ARROW = "->"
    PARALLEL = "||"
    PLUS = "+"
    LPAREN = "("
    RPAREN = ")"
    LBRACKET = "["
    RBRACKET = "]"
    LBRACE = "{"
    RBRACE = "}"
    COLON = ":"
    EQUALS = "="
    COMMA = ","
    STRING = "STRING"
    NUMBER = "NUMBER"
    WORKFLOW = "workflow"
    AGENT_DEF = "agent"
    EOF = "EOF"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

@dataclass
class SourceLocation:
    line: int
    column: int
    length: int

# AST Nodes
class ASTNode:
    location: SourceLocation

@dataclass
class AgentNode(ASTNode):
    name: str
    skills: List[str]

@dataclass
class SequenceNode(ASTNode):
    left: ASTNode
    right: ASTNode

@dataclass
class ParallelNode(ASTNode):
    branches: List[ASTNode]

@dataclass
class CombinationNode(ASTNode):
    base: ASTNode
    additions: List[ASTNode]

@dataclass
class CommandNode(ASTNode):
    name: str
    arguments: List[Any]

@dataclass
class WorkflowNode(ASTNode):
    name: str
    metadata: dict
    body: ASTNode

# Parser protocol
class Parser(Protocol):
    """DSL parser with complete lexical and syntactic analysis"""

    def tokenize(self, source: str) -> List[Token]:
        """
        Tokenize source code into token stream.

        Args:
            source: DSL source code

        Returns:
            List of tokens

        Raises:
            LexicalError: If invalid characters found
        """
        ...

    def parse(self, source: str) -> ASTNode:
        """
        Parse source code into Abstract Syntax Tree.

        Args:
            source: DSL source code

        Returns:
            Root AST node

        Raises:
            ParseError: If syntax invalid
        """
        ...

    def parse_workflow(self) -> WorkflowNode:
        """Parse workflow definition"""
        ...

    def parse_expression(self) -> ASTNode:
        """Parse expression"""
        ...

    def parse_pipeline(self) -> ASTNode:
        """Parse sequential pipeline (->)"""
        ...

    def parse_parallel(self) -> ASTNode:
        """Parse parallel execution (||)"""
        ...

    def parse_combination(self) -> ASTNode:
        """Parse combination (+)"""
        ...

    def parse_primary(self) -> ASTNode:
        """Parse primary expression"""
        ...

    def expect(self, token_type: TokenType) -> Token:
        """
        Expect specific token type, advance if matches.

        Raises:
            ParseError: If token doesn't match
        """
        ...
```

### 2.2 Type Checker Interface

```python
from typing import Protocol, Set, Dict
from dataclasses import dataclass

# Type system
@dataclass
class Type:
    """Base type"""
    name: str

@dataclass
class AgentType(Type):
    """Agent type with capabilities"""
    capabilities: Set[str]
    compatible_skills: Set[str]
    input_types: Set[Type]
    output_types: Set[Type]

@dataclass
class SkillType(Type):
    """Skill type"""
    domain: str
    requires: Set[str]
    provides: Set[str]

@dataclass
class WorkflowType(Type):
    """Workflow type"""
    input_type: Type
    output_type: Type

@dataclass
class TypedAST:
    """AST node with type annotation"""
    node: ASTNode
    type: Type
    children: List['TypedAST']

# Type checker protocol
class TypeChecker(Protocol):
    """Type checking and validation"""

    def check(self, ast: ASTNode, registry: 'AgentRegistry') -> TypedAST:
        """
        Perform type checking on AST.

        Args:
            ast: Abstract Syntax Tree
            registry: Agent registry for lookups

        Returns:
            Typed AST with type annotations

        Raises:
            TypeError: If type mismatch detected
        """
        ...

    def infer_type(self, node: ASTNode) -> Type:
        """
        Infer type of AST node.

        Args:
            node: AST node

        Returns:
            Inferred type

        Raises:
            TypeInferenceError: If type cannot be inferred
        """
        ...

    def check_compatibility(
        self,
        agent: AgentType,
        skills: List[SkillType]
    ) -> bool:
        """
        Check if agent compatible with skills.

        Args:
            agent: Agent type
            skills: List of skill types

        Returns:
            True if compatible, False otherwise
        """
        ...

    def check_sequence(
        self,
        left_type: Type,
        right_type: Type
    ) -> WorkflowType:
        """
        Check sequential composition types.

        Args:
            left_type: Type of left operand
            right_type: Type of right operand

        Returns:
            Workflow type for composition

        Raises:
            TypeError: If types incompatible
        """
        ...

    def unify_parallel(
        self,
        types: List[Type]
    ) -> Type:
        """
        Unify types from parallel execution.

        Args:
            types: List of parallel branch types

        Returns:
            Unified type (typically tuple)
        """
        ...
```

### 2.3 Executor Interface

```python
from typing import Protocol, AsyncIterator
from dataclasses import dataclass
import asyncio

@dataclass
class ExecutionContext:
    """Runtime execution context"""
    working_dir: Path
    environment: Dict[str, str]
    state: Dict[str, Any]
    mcp_servers: List[str]
    agent_instances: Dict[str, Any]
    skill_cache: Dict[str, Any]

@dataclass
class ExecutionPlan:
    """Optimized execution plan"""
    dag: 'DAG'
    parallel_groups: List[List['Task']]
    resource_allocation: Dict[str, 'Resource']

@dataclass
class Task:
    """Execution task"""
    id: str
    agent: str
    skills: List[str]
    input: Any
    dependencies: List[str]
    timeout: Optional[int]
    retries: int

@dataclass
class Result:
    """Task execution result"""
    task_id: str
    output: Any
    context: ExecutionContext
    metadata: Dict[str, Any]
    errors: List[Exception]
    duration: float

@dataclass
class ResourceLimits:
    """Resource constraints"""
    max_parallel: int = 5
    max_memory_mb: int = 4096
    max_time_seconds: int = 300
    max_retries: int = 3

class Executor(Protocol):
    """Workflow execution engine"""

    async def execute(
        self,
        plan: ExecutionPlan,
        context: ExecutionContext,
        limits: ResourceLimits
    ) -> Result:
        """
        Execute workflow with given plan.

        Args:
            plan: Execution plan from optimizer
            context: Execution context
            limits: Resource constraints

        Returns:
            Final execution result

        Raises:
            RuntimeError: If execution fails
            TimeoutError: If time limit exceeded
            ResourceError: If resource limit exceeded
        """
        ...

    async def execute_task(
        self,
        task: Task,
        context: ExecutionContext
    ) -> Result:
        """
        Execute single task.

        Args:
            task: Task to execute
            context: Execution context

        Returns:
            Task result
        """
        ...

    async def execute_parallel(
        self,
        tasks: List[Task],
        context: ExecutionContext
    ) -> List[Result]:
        """
        Execute tasks in parallel.

        Args:
            tasks: List of independent tasks
            context: Shared execution context

        Returns:
            List of results (order preserved)
        """
        ...

    async def execute_with_retry(
        self,
        task: Task,
        context: ExecutionContext,
        max_retries: int
    ) -> Result:
        """
        Execute task with retry logic.

        Args:
            task: Task to execute
            context: Execution context
            max_retries: Maximum retry attempts

        Returns:
            Task result
        """
        ...

    def cancel(self, execution_id: str) -> None:
        """Cancel running execution"""
        ...

    async def stream_results(
        self,
        plan: ExecutionPlan,
        context: ExecutionContext
    ) -> AsyncIterator[Result]:
        """
        Stream results as they complete.

        Args:
            plan: Execution plan
            context: Execution context

        Yields:
            Results as tasks complete
        """
        ...
```

### 2.4 Agent Registry Interface

```python
from typing import Protocol, List, Optional
from dataclasses import dataclass

@dataclass
class AgentSpec:
    """Agent specification"""
    name: str
    description: str
    version: str
    capabilities: List[str]
    compatible_skills: List[str]
    input_types: List[str]
    output_types: List[str]
    dependencies: List[str]
    constraints: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class SkillSpec:
    """Skill specification"""
    name: str
    description: str
    domain: str
    requires: List[str]
    provides: List[str]
    compatible_agents: List[str]
    metadata: Dict[str, Any]

@dataclass
class CompatibilityResult:
    """Compatibility check result"""
    compatible: bool
    reasons: List[str]
    warnings: List[str]

class AgentRegistry(Protocol):
    """Agent and skill registry"""

    def register_agent(self, spec: AgentSpec) -> None:
        """
        Register agent with registry.

        Args:
            spec: Agent specification

        Raises:
            DuplicateAgentError: If agent already registered
            ValidationError: If spec invalid
        """
        ...

    def register_skill(self, spec: SkillSpec) -> None:
        """
        Register skill with registry.

        Args:
            spec: Skill specification

        Raises:
            DuplicateSkillError: If skill already registered
            ValidationError: If spec invalid
        """
        ...

    def get_agent(self, name: str) -> AgentSpec:
        """
        Get agent specification.

        Args:
            name: Agent name

        Returns:
            Agent specification

        Raises:
            AgentNotFoundError: If agent not found
        """
        ...

    def get_skill(self, name: str) -> SkillSpec:
        """
        Get skill specification.

        Args:
            name: Skill name

        Returns:
            Skill specification

        Raises:
            SkillNotFoundError: If skill not found
        """
        ...

    def list_agents(
        self,
        capability: Optional[str] = None
    ) -> List[AgentSpec]:
        """
        List all agents, optionally filtered by capability.

        Args:
            capability: Optional capability filter

        Returns:
            List of agent specifications
        """
        ...

    def list_skills(
        self,
        domain: Optional[str] = None
    ) -> List[SkillSpec]:
        """
        List all skills, optionally filtered by domain.

        Args:
            domain: Optional domain filter

        Returns:
            List of skill specifications
        """
        ...

    def check_compatibility(
        self,
        agent: str,
        skills: List[str]
    ) -> CompatibilityResult:
        """
        Check agent-skill compatibility.

        Args:
            agent: Agent name
            skills: List of skill names

        Returns:
            Compatibility result with details
        """
        ...

    def find_agents_for_task(
        self,
        task_description: str,
        required_skills: List[str]
    ) -> List[AgentSpec]:
        """
        Find suitable agents for task.

        Args:
            task_description: Natural language task description
            required_skills: Required skills

        Returns:
            Ranked list of suitable agents
        """
        ...
```

---

## 3. Implementation Modules

### 3.1 Lexer Implementation

```python
import re
from typing import List, Iterator
from dataclasses import dataclass

class Lexer:
    """Tokenize DSL source code"""

    # Token patterns
    PATTERNS = [
        (r'workflow\b', TokenType.WORKFLOW),
        (r'agent\b', TokenType.AGENT_DEF),
        (r'->', TokenType.ARROW),
        (r'\|\|', TokenType.PARALLEL),
        (r'\+', TokenType.PLUS),
        (r'\(', TokenType.LPAREN),
        (r'\)', TokenType.RPAREN),
        (r'\[', TokenType.LBRACKET),
        (r'\]', TokenType.RBRACKET),
        (r'\{', TokenType.LBRACE),
        (r'\}', TokenType.RBRACE),
        (r':', TokenType.COLON),
        (r'=', TokenType.EQUALS),
        (r',', TokenType.COMMA),
        (r'"[^"]*"', TokenType.STRING),
        (r'\d+\.?\d*', TokenType.NUMBER),
        (r'/[a-zA-Z][a-zA-Z0-9-]*', TokenType.COMMAND),
        (r'[a-zA-Z][a-zA-Z0-9_-]*', TokenType.IDENTIFIER),
        (r'//[^\n]*', None),  # Comment, skip
        (r'/\*.*?\*/', None),  # Multi-line comment, skip
        (r'\s+', None),  # Whitespace, skip
    ]

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> List[Token]:
        """Tokenize entire source"""
        tokens = []
        while self.pos < len(self.source):
            token = self.next_token()
            if token:
                tokens.append(token)
        tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return tokens

    def next_token(self) -> Optional[Token]:
        """Get next token"""
        if self.pos >= len(self.source):
            return None

        for pattern, token_type in self.PATTERNS:
            regex = re.compile(pattern)
            match = regex.match(self.source, self.pos)
            if match:
                value = match.group(0)
                token = None
                if token_type:
                    token = Token(
                        token_type,
                        value,
                        self.line,
                        self.column
                    )

                # Update position
                self.pos = match.end()
                self.column += len(value)

                # Handle newlines
                if '\n' in value:
                    self.line += value.count('\n')
                    self.column = len(value.split('\n')[-1])

                return token

        raise LexicalError(
            f"Unexpected character '{self.source[self.pos]}' "
            f"at line {self.line}, column {self.column}"
        )

    def peek(self, offset: int = 0) -> str:
        """Peek ahead without consuming"""
        pos = self.pos + offset
        if pos < len(self.source):
            return self.source[pos]
        return ''
```

### 3.2 Parser Implementation (Recursive Descent)

```python
class RecursiveDescentParser:
    """Recursive descent parser for DSL"""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def current_token(self) -> Token:
        """Get current token"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF

    def advance(self) -> Token:
        """Consume and return current token"""
        token = self.current_token()
        self.pos += 1
        return token

    def expect(self, token_type: TokenType) -> Token:
        """Expect specific token type"""
        token = self.current_token()
        if token.type != token_type:
            raise ParseError(
                f"Expected {token_type}, got {token.type} "
                f"at line {token.line}, column {token.column}"
            )
        return self.advance()

    def parse(self) -> ASTNode:
        """Parse program"""
        statements = []
        while self.current_token().type != TokenType.EOF:
            statements.append(self.parse_statement())
        return ProgramNode(statements)

    def parse_statement(self) -> ASTNode:
        """Parse statement"""
        token = self.current_token()

        if token.type == TokenType.WORKFLOW:
            return self.parse_workflow()
        elif token.type == TokenType.AGENT_DEF:
            return self.parse_agent_def()
        else:
            return self.parse_expression()

    def parse_workflow(self) -> WorkflowNode:
        """Parse workflow definition"""
        self.expect(TokenType.WORKFLOW)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LBRACE)

        metadata = {}
        body = None

        while self.current_token().type != TokenType.RBRACE:
            if self.current_token().value in ['name', 'description', 'version']:
                # Parse metadata
                key = self.advance().value
                self.expect(TokenType.COLON)
                value = self.expect(TokenType.STRING).value.strip('"')
                metadata[key] = value
            else:
                # Parse body
                body = self.parse_expression()

        self.expect(TokenType.RBRACE)

        return WorkflowNode(name, metadata, body)

    def parse_expression(self) -> ASTNode:
        """Parse expression (pipeline level)"""
        return self.parse_pipeline()

    def parse_pipeline(self) -> ASTNode:
        """Parse pipeline (->)"""
        left = self.parse_parallel()

        while self.current_token().type == TokenType.ARROW:
            self.advance()
            right = self.parse_parallel()
            left = SequenceNode(left, right)

        return left

    def parse_parallel(self) -> ASTNode:
        """Parse parallel (||)"""
        branches = [self.parse_combination()]

        while self.current_token().type == TokenType.PARALLEL:
            self.advance()
            branches.append(self.parse_combination())

        if len(branches) == 1:
            return branches[0]
        return ParallelNode(branches)

    def parse_combination(self) -> ASTNode:
        """Parse combination (+)"""
        base = self.parse_primary()
        additions = []

        while self.current_token().type == TokenType.PLUS:
            self.advance()
            additions.append(self.parse_primary())

        if not additions:
            return base
        return CombinationNode(base, additions)

    def parse_primary(self) -> ASTNode:
        """Parse primary expression"""
        token = self.current_token()

        if token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        elif token.type == TokenType.COMMAND:
            return self.parse_command()

        elif token.type == TokenType.IDENTIFIER:
            return self.parse_agent_or_skill()

        else:
            raise ParseError(f"Unexpected token: {token}")

    def parse_command(self) -> CommandNode:
        """Parse command invocation"""
        name = self.advance().value
        args = []

        if self.current_token().type == TokenType.LPAREN:
            self.advance()
            while self.current_token().type != TokenType.RPAREN:
                if self.current_token().type == TokenType.STRING:
                    args.append(self.advance().value.strip('"'))
                elif self.current_token().type == TokenType.NUMBER:
                    args.append(float(self.advance().value))
                elif self.current_token().type == TokenType.IDENTIFIER:
                    args.append(self.advance().value)

                if self.current_token().type == TokenType.COMMA:
                    self.advance()

            self.expect(TokenType.RPAREN)

        return CommandNode(name, args)

    def parse_agent_or_skill(self) -> ASTNode:
        """Parse agent reference or skill"""
        name = self.expect(TokenType.IDENTIFIER).value
        skills = []

        if self.current_token().type == TokenType.LBRACKET:
            self.advance()
            while self.current_token().type != TokenType.RBRACKET:
                skills.append(self.expect(TokenType.IDENTIFIER).value)
                if self.current_token().type == TokenType.COMMA:
                    self.advance()
            self.expect(TokenType.RBRACKET)

        return AgentNode(name, skills)
```

### 3.3 DAG Builder

```python
from typing import Set, Dict, List
import networkx as nx

class DAGBuilder:
    """Build execution DAG from typed AST"""

    def build(self, ast: TypedAST) -> nx.DiGraph:
        """
        Build directed acyclic graph from AST.

        Returns:
            NetworkX DiGraph representing execution dependencies

        Raises:
            CyclicDependencyError: If cycle detected
        """
        dag = nx.DiGraph()
        self._visit(ast, dag, parent=None)

        # Check for cycles
        if not nx.is_directed_acyclic_graph(dag):
            cycle = nx.find_cycle(dag)
            raise CyclicDependencyError(f"Cycle detected: {cycle}")

        return dag

    def _visit(
        self,
        node: TypedAST,
        dag: nx.DiGraph,
        parent: Optional[str]
    ) -> str:
        """Visit AST node and add to DAG"""

        if isinstance(node.node, AgentNode):
            node_id = self._add_agent_node(node, dag)
            if parent:
                dag.add_edge(parent, node_id)
            return node_id

        elif isinstance(node.node, SequenceNode):
            left_id = self._visit(node.children[0], dag, parent)
            right_id = self._visit(node.children[1], dag, left_id)
            return right_id

        elif isinstance(node.node, ParallelNode):
            parallel_ids = []
            for child in node.children:
                child_id = self._visit(child, dag, parent)
                parallel_ids.append(child_id)

            # Add merge node
            merge_id = f"merge_{hash(node)}"
            dag.add_node(merge_id, type='merge')
            for pid in parallel_ids:
                dag.add_edge(pid, merge_id)

            return merge_id

        elif isinstance(node.node, CombinationNode):
            return self._visit(node.children[0], dag, parent)

        elif isinstance(node.node, CommandNode):
            node_id = self._add_command_node(node, dag)
            if parent:
                dag.add_edge(parent, node_id)
            return node_id

        else:
            raise ValueError(f"Unknown node type: {type(node.node)}")

    def _add_agent_node(self, node: TypedAST, dag: nx.DiGraph) -> str:
        """Add agent node to DAG"""
        agent_node = node.node
        node_id = f"{agent_node.name}_{hash(node)}"

        dag.add_node(
            node_id,
            type='agent',
            name=agent_node.name,
            skills=agent_node.skills,
            ast_node=node
        )

        return node_id

    def _add_command_node(self, node: TypedAST, dag: nx.DiGraph) -> str:
        """Add command node to DAG"""
        command_node = node.node
        node_id = f"{command_node.name}_{hash(node)}"

        dag.add_node(
            node_id,
            type='command',
            name=command_node.name,
            args=command_node.arguments,
            ast_node=node
        )

        return node_id
```

---

## 4. Data Flow

### 4.1 End-to-End Example

```python
# Example workflow
dsl_source = """
workflow api_design {
  name: "API Design Workflow"
  version: "1.0.0"

  /ctx7("fastapi") -> api-architect + rest-api-design-patterns
}
"""

# 1. Lexical Analysis
lexer = Lexer(dsl_source)
tokens = lexer.tokenize()
# Output: [
#   Token(WORKFLOW, 'workflow', 1, 1),
#   Token(IDENTIFIER, 'api_design', 1, 10),
#   Token(LBRACE, '{', 1, 20),
#   ...
# ]

# 2. Syntax Analysis
parser = RecursiveDescentParser(tokens)
ast = parser.parse()
# Output: WorkflowNode(
#   name='api_design',
#   metadata={'name': 'API Design Workflow', 'version': '1.0.0'},
#   body=SequenceNode(
#     left=CommandNode('/ctx7', ['fastapi']),
#     right=CombinationNode(
#       base=AgentNode('api-architect'),
#       additions=[SkillNode('rest-api-design-patterns')]
#     )
#   )
# )

# 3. Type Checking
registry = AgentRegistry()
typechecker = TypeChecker(registry)
typed_ast = typechecker.check(ast)
# Output: TypedAST(
#   node=WorkflowNode(...),
#   type=WorkflowType(input=None, output=APISpec),
#   children=[...]
# )

# 4. DAG Construction
dag_builder = DAGBuilder()
dag = dag_builder.build(typed_ast)
# Output: DiGraph with nodes:
#   - /ctx7_12345 (command)
#   - api-architect_67890 (agent)
# Edges:
#   - /ctx7_12345 -> api-architect_67890

# 5. Optimization
optimizer = Optimizer()
plan = optimizer.create_execution_plan(dag)
# Output: ExecutionPlan(
#   dag=dag,
#   parallel_groups=[],  # No parallelism in this workflow
#   resource_allocation={'api-architect': Resource(cpu=1, memory=2GB)}
# )

# 6. Execution
executor = Executor()
context = ExecutionContext(working_dir=Path.cwd())
result = await executor.execute(plan, context, ResourceLimits())
# Output: Result(
#   task_id='workflow_api_design',
#   output=APISpecification(...),
#   metadata={'duration': 45.2, 'tasks_executed': 2},
#   errors=[]
# )
```

### 4.2 Parallel Execution Flow

```python
dsl_source = """
(agent1 || agent2 || agent3) -> merger
"""

# After parsing and DAG construction:
dag = nx.DiGraph()
dag.add_edges_from([
    ('agent1_1', 'merge_1'),
    ('agent2_2', 'merge_1'),
    ('agent3_3', 'merge_1'),
    ('merge_1', 'merger_4')
])

# Execution plan identifies parallel group
plan.parallel_groups = [
    ['agent1_1', 'agent2_2', 'agent3_3']
]

# Executor runs them concurrently
async def execute_parallel_group(tasks):
    results = await asyncio.gather(*[
        execute_task(task) for task in tasks
    ])
    return results

# Timeline:
# t=0s:  agent1, agent2, agent3 start
# t=10s: agent1 completes
# t=12s: agent2 completes
# t=15s: agent3 completes → merge triggered
# t=15s: merger starts with merged input
# t=20s: merger completes
# Total: 20s (vs 37s if sequential)
```

---

## 5. Extension Points

### 5.1 Custom Operators

```python
class OperatorRegistry:
    """Registry for custom operators"""

    def register(
        self,
        symbol: str,
        precedence: int,
        semantics: Callable
    ):
        """Register custom operator"""
        self.operators[symbol] = Operator(
            symbol=symbol,
            precedence=precedence,
            semantics=semantics
        )

# Example: retry operator
registry.register(
    symbol='>>',
    precedence=3,
    semantics=lambda task: retry_wrapper(task, max_attempts=3)
)

# Usage in DSL:
# risky_task >> safe_fallback
```

### 5.2 Custom Agent Types

```python
class CustomAgentType:
    """Base class for custom agent types"""

    def execute(
        self,
        input: Any,
        context: ExecutionContext
    ) -> Result:
        """Execute agent logic"""
        raise NotImplementedError

# Example: LLM-powered agent
class LLMAgent(CustomAgentType):
    def __init__(self, model: str, prompt: str):
        self.model = model
        self.prompt = prompt

    async def execute(self, input, context):
        response = await anthropic_client.messages.create(
            model=self.model,
            messages=[
                {"role": "user", "content": f"{self.prompt}\n\nInput: {input}"}
            ]
        )
        return Result(output=response.content)

# Register with runtime
registry.register_agent_class('llm-agent', LLMAgent)
```

### 5.3 Middleware

```python
class Middleware:
    """Middleware for execution pipeline"""

    async def before_execute(
        self,
        task: Task,
        context: ExecutionContext
    ) -> Tuple[Task, ExecutionContext]:
        """Called before task execution"""
        return task, context

    async def after_execute(
        self,
        result: Result,
        context: ExecutionContext
    ) -> Result:
        """Called after task execution"""
        return result

# Example: logging middleware
class LoggingMiddleware(Middleware):
    async def before_execute(self, task, context):
        logger.info(f"Starting task: {task.id}")
        return task, context

    async def after_execute(self, result, context):
        logger.info(f"Completed task: {result.task_id} in {result.duration}s")
        return result

# Register
executor.add_middleware(LoggingMiddleware())
```

---

**Document Status**: API Blueprint Complete
**Implementation**: Ready for prototyping
**Version**: 1.0.0
