"""
HEKAT DSL Unified Compiler

Complete compilation pipeline: DSL string → ExecutionPlan
Chains: Lexer → Parser → TypeChecker → DAGBuilder → Plan Generator
"""

from dataclasses import dataclass, field
from typing import List, Optional
from hekat_lexer import Lexer, LexerError
from hekat_parser import Parser, ParseError, QueryNode
from hekat_type_checker import TypeChecker
from hekat_dag_builder import DAGBuilder, DAG


class CompileError(Exception):
    """Compilation failed with helpful error message"""
    pass


@dataclass
class Phase:
    """Single execution phase in Task Relay plan"""
    num: int
    agents: List[str]
    token_budget: int
    can_parallelize: bool
    skills: List[str] = field(default_factory=list)


@dataclass
class ExecutionPlan:
    """Complete execution plan for HEKAT query"""
    pattern_type: str  # Simple, Sequential, Parallel, Mixed, etc.
    complexity_level: str  # L1-L7
    phases: List[Phase]
    total_tokens: int
    prompt: str
    metadata: dict = field(default_factory=dict)


class HEKATCompiler:
    """Complete HEKAT DSL compiler: string → execution plan"""

    def compile(self, dsl_string: str) -> ExecutionPlan:
        """Main entry point.

        Pipeline:
        1. Lex (string → tokens)
        2. Parse (tokens → AST)
        3. Type check (validate agents/skills)
        4. Build DAG (AST → execution graph)
        5. Generate plan (DAG → Task Relay phases with budgets)

        Returns: ExecutionPlan with phases, budgets, token estimates
        Raises: CompileError with helpful message
        """
        try:
            # Phase 1: Lex
            lexer = Lexer(dsl_string)
            tokens = lexer.tokenize()

            # Phase 2: Parse
            parser = Parser(tokens)
            ast = parser.parse()

            # Phase 3: Type Check
            checker = TypeChecker()
            validation = checker.validate(ast)
            if not validation['valid']:
                errors = ', '.join(validation['errors'])
                raise CompileError(f"Validation failed: {errors}")

            # Phase 4: Build DAG
            dag_builder = DAGBuilder()
            dag = dag_builder.build(ast.expression)

            # Phase 5: Generate Execution Plan
            plan = self._generate_execution_plan(dag, ast)

            return plan

        except LexerError as e:
            raise CompileError(f"Lexer error: {e}")
        except ParseError as e:
            raise CompileError(f"Parser error: {e}")
        except Exception as e:
            raise CompileError(f"Compilation failed: {e}")

    def _generate_execution_plan(self, dag: DAG, ast: QueryNode) -> ExecutionPlan:
        """Convert DAG to Task Relay execution plan"""
        phases = []
        total_tokens = 0

        # Extract skills if present
        skills = self._extract_skills(ast)

        # Convert parallel_phases dict to list of phases
        for idx, phase_num in enumerate(sorted(dag.parallel_phases.keys()), 1):
            node_ids = dag.parallel_phases[phase_num]
            phase_nodes = [dag.nodes[nid] for nid in node_ids]
            agents = [self._extract_agent_name(node.expr) for node in phase_nodes]
            token_budget = self._estimate_tokens(phase_nodes, ast.prompt)
            total_tokens += token_budget

            phases.append(Phase(
                num=idx,  # Use 1-based enumeration
                agents=agents,
                token_budget=token_budget,
                can_parallelize=(len(agents) > 1),
                skills=skills
            ))

        pattern_type = self._detect_pattern(ast)

        # Compute DAG metrics
        total_agents = len(dag.nodes)
        execution_depth = len(dag.parallel_phases)
        has_parallelism = any(len(nodes) > 1 for nodes in dag.parallel_phases.values())
        has_fallback = self._has_fallback(ast)

        complexity = self._classify_complexity_from_metrics(
            total_agents, execution_depth, has_parallelism, has_fallback
        )

        return ExecutionPlan(
            pattern_type=pattern_type,
            complexity_level=complexity,
            phases=phases,
            total_tokens=total_tokens,
            prompt=ast.prompt,
            metadata={
                'total_agents': total_agents,
                'execution_depth': execution_depth,
                'has_parallelism': has_parallelism,
                'has_fallback': has_fallback
            }
        )

    def _extract_agent_name(self, expr) -> str:
        """Extract agent name from expression node"""
        from hekat_parser import (SimpleNode, SkilledNode, CommandedNode, EnsembleNode)

        if isinstance(expr, SimpleNode):
            return expr.name
        elif isinstance(expr, SkilledNode):
            return expr.agent
        elif isinstance(expr, CommandedNode):
            # Return the command + first agent
            return f"{expr.command}({expr.agents[0] if expr.agents else 'unknown'})"
        elif isinstance(expr, EnsembleNode):
            return expr.base

        return "unknown"

    def _extract_skills(self, ast: QueryNode) -> List[str]:
        """Extract skill names from AST"""
        from hekat_parser import (SimpleNode, SequentialNode, ParallelNode,
                                   FallbackNode, EnsembleNode, CommandedNode, SkilledNode)
        skills = []

        def extract_from_expr(expr):
            if isinstance(expr, SkilledNode):
                skills.extend(expr.skills)
            elif isinstance(expr, SequentialNode):
                for step in expr.steps:
                    extract_from_expr(step)
            elif isinstance(expr, ParallelNode):
                for branch in expr.branches:
                    extract_from_expr(branch)
            elif isinstance(expr, FallbackNode):
                for alt in expr.alternatives:
                    extract_from_expr(alt)

        extract_from_expr(ast.expression)
        return skills

    def _estimate_tokens(self, nodes, prompt: str) -> int:
        """Estimate token budget based on agent count and prompt length"""
        # Base: 500 tokens
        # Per agent: 100 tokens
        # Prompt: ~0.75 tokens per char (rough heuristic)
        # Parallel penalty: +200 if multiple agents
        base = 500
        per_agent = 100 * len(nodes)
        prompt_tokens = int(len(prompt) * 0.75)
        parallel_penalty = 200 if len(nodes) > 1 else 0

        return base + per_agent + prompt_tokens + parallel_penalty

    def _detect_pattern(self, ast: QueryNode) -> str:
        """Detect pattern type from AST"""
        from hekat_parser import (SimpleNode, SequentialNode, ParallelNode,
                                   FallbackNode, EnsembleNode, CommandedNode, SkilledNode)

        expr = ast.expression

        if isinstance(expr, SkilledNode):
            return 'Skilled'
        elif isinstance(expr, SimpleNode):
            return 'Simple'
        elif isinstance(expr, SequentialNode):
            # Check if mixed (contains parallel children)
            has_parallel = any(isinstance(step, ParallelNode) for step in expr.steps)
            return 'Mixed' if has_parallel else 'Sequential'
        elif isinstance(expr, ParallelNode):
            return 'Parallel'
        elif isinstance(expr, FallbackNode):
            return 'Fallback'
        elif isinstance(expr, EnsembleNode):
            return 'Ensemble'
        elif isinstance(expr, CommandedNode):
            return 'Commanded'

        return 'Unknown'

    def _has_fallback(self, ast: QueryNode) -> bool:
        """Check if AST contains fallback pattern"""
        from hekat_parser import FallbackNode, SequentialNode, ParallelNode

        def check_expr(expr):
            if isinstance(expr, FallbackNode):
                return True
            elif isinstance(expr, SequentialNode):
                return any(check_expr(step) for step in expr.steps)
            elif isinstance(expr, ParallelNode):
                return any(check_expr(branch) for branch in expr.branches)
            return False

        return check_expr(ast.expression)

    def _classify_complexity_from_metrics(self, agent_count: int, depth: int,
                                         has_parallel: bool, has_fallback: bool) -> str:
        """L1-L7 complexity classification"""
        # L1: Single agent, no complexity
        if agent_count == 1 and depth == 1:
            return 'L1'

        # L2: 2 agents, simple sequence
        if agent_count == 2 and depth == 2 and not has_parallel:
            return 'L2'

        # L3: 3 agents or simple parallelism
        if agent_count <= 3 and (has_parallel or depth <= 2):
            return 'L3'

        # L4: 4-5 agents with some structure
        if agent_count <= 5 and depth <= 3:
            return 'L4'

        # L5: 5-7 agents with parallelism
        if agent_count <= 7 and has_parallel:
            return 'L5'

        # L6: 7-10 agents or fallback patterns
        if agent_count <= 10 or has_fallback:
            return 'L6'

        # L7: 10+ agents or deep nesting
        return 'L7'
