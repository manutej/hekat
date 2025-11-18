"""HEKAT DSL DAG Builder - Converts AST to execution DAG."""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple
from hekat_parser import (
    ExpressionNode, SimpleNode, SequentialNode, ParallelNode,
    FallbackNode, EnsembleNode, CommandedNode, SkilledNode
)


@dataclass
class DAGNode:
    """Node in the execution DAG."""
    id: int
    expr: ExpressionNode
    dependencies: Set[int] = field(default_factory=set)
    is_fallback: bool = False
    fallback_of: int = None  # ID of node this is a fallback for


@dataclass
class DAG:
    """Directed Acyclic Graph representing execution plan."""
    nodes: Dict[int, DAGNode]
    execution_order: List[int]
    parallel_phases: Dict[int, List[int]]  # phase -> list of node IDs


class DAGBuilder:
    """Converts AST to execution DAG (Directed Acyclic Graph)."""

    def __init__(self):
        """Initialize DAG builder."""
        self.next_id = 0
        self.nodes: Dict[int, DAGNode] = {}

    def build(self, expr: ExpressionNode) -> DAG:
        """Convert expression to DAG.

        Returns: DAG with nodes, edges, parallelism info
        """
        self.next_id = 0
        self.nodes = {}

        # Build DAG nodes from AST
        root_ids = self._build_nodes(expr, set())

        # Detect cycles (should be none in valid DSL)
        cycles = self._detect_cycles()
        if cycles:
            raise ValueError(f"Detected cycles in DAG: {cycles}")

        # Compute topological sort
        execution_order = self._topological_sort()

        # Identify parallel execution phases
        parallel_phases = self._identify_parallelism()

        return DAG(
            nodes=self.nodes,
            execution_order=execution_order,
            parallel_phases=parallel_phases
        )

    def _build_nodes(
        self,
        expr: ExpressionNode,
        dependencies: Set[int]
    ) -> Set[int]:
        """Create DAG nodes from expression.

        Returns: Set of node IDs created (can be multiple for parallel/seq)
        """
        if isinstance(expr, SimpleNode):
            return self._build_simple(expr, dependencies)

        elif isinstance(expr, SkilledNode):
            return self._build_skilled(expr, dependencies)

        elif isinstance(expr, CommandedNode):
            return self._build_commanded(expr, dependencies)

        elif isinstance(expr, EnsembleNode):
            return self._build_ensemble(expr, dependencies)

        elif isinstance(expr, SequentialNode):
            return self._build_sequential(expr, dependencies)

        elif isinstance(expr, ParallelNode):
            return self._build_parallel(expr, dependencies)

        elif isinstance(expr, FallbackNode):
            return self._build_fallback(expr, dependencies)

        return set()

    def _build_simple(
        self,
        expr: SimpleNode,
        dependencies: Set[int]
    ) -> Set[int]:
        """Build single node for SimpleNode."""
        node_id = self.next_id
        self.next_id += 1

        self.nodes[node_id] = DAGNode(
            id=node_id,
            expr=expr,
            dependencies=dependencies.copy()
        )
        return {node_id}

    def _build_skilled(
        self,
        expr: SkilledNode,
        dependencies: Set[int]
    ) -> Set[int]:
        """Build single node for SkilledNode."""
        node_id = self.next_id
        self.next_id += 1

        self.nodes[node_id] = DAGNode(
            id=node_id,
            expr=expr,
            dependencies=dependencies.copy()
        )
        return {node_id}

    def _build_commanded(
        self,
        expr: CommandedNode,
        dependencies: Set[int]
    ) -> Set[int]:
        """Build single node for CommandedNode."""
        node_id = self.next_id
        self.next_id += 1

        self.nodes[node_id] = DAGNode(
            id=node_id,
            expr=expr,
            dependencies=dependencies.copy()
        )
        return {node_id}

    def _build_ensemble(
        self,
        expr: EnsembleNode,
        dependencies: Set[int]
    ) -> Set[int]:
        """Build nodes for EnsembleNode.

        Creates: sample nodes (parallel) -> merge -> synthesize
        """
        # Create parallel sample nodes
        sample_ids = set()
        for i in range(expr.count):
            node_id = self.next_id
            self.next_id += 1
            self.nodes[node_id] = DAGNode(
                id=node_id,
                expr=expr,  # All samples use same base agent
                dependencies=dependencies.copy()
            )
            sample_ids.add(node_id)

        # Merge node depends on all samples
        merge_id = self.next_id
        self.next_id += 1
        self.nodes[merge_id] = DAGNode(
            id=merge_id,
            expr=expr,
            dependencies=sample_ids.copy()
        )

        # Synthesize node depends on merge
        synth_id = self.next_id
        self.next_id += 1
        self.nodes[synth_id] = DAGNode(
            id=synth_id,
            expr=expr,
            dependencies={merge_id}
        )

        return {synth_id}

    def _build_sequential(
        self,
        expr: SequentialNode,
        dependencies: Set[int]
    ) -> Set[int]:
        """Build chain of dependent nodes."""
        current_deps = dependencies
        for step in expr.steps:
            # Each step depends on previous step's output
            current_deps = self._build_nodes(step, current_deps)

        return current_deps

    def _build_parallel(
        self,
        expr: ParallelNode,
        dependencies: Set[int]
    ) -> Set[int]:
        """Build independent parallel branches."""
        branch_outputs = set()

        for branch in expr.branches:
            # All branches have same dependencies (no mutual deps)
            branch_ids = self._build_nodes(branch, dependencies)
            branch_outputs.update(branch_ids)

        return branch_outputs

    def _build_fallback(
        self,
        expr: FallbackNode,
        dependencies: Set[int]
    ) -> Set[int]:
        """Build fallback chain.

        Primary alternative is tried first, others are fallbacks.
        """
        primary_ids = self._build_nodes(expr.alternatives[0], dependencies)

        # Mark subsequent alternatives as fallbacks
        for i, alternative in enumerate(expr.alternatives[1:], start=1):
            fallback_ids = self._build_nodes(alternative, dependencies)
            # Mark as fallback of primary
            for fid in fallback_ids:
                self.nodes[fid].is_fallback = True
                # Link to first node of primary as fallback target
                self.nodes[fid].fallback_of = min(primary_ids)

        # Return primary IDs (fallbacks are alternatives, not in main path)
        return primary_ids

    def _topological_sort(self) -> List[int]:
        """Sort DAG nodes in execution order (Kahn's algorithm)."""
        # Calculate in-degree for each node
        in_degree = {node_id: len(node.dependencies) for node_id, node in self.nodes.items()}

        # Queue of nodes with no dependencies
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            # Sort for deterministic ordering
            queue.sort()
            node_id = queue.pop(0)
            result.append(node_id)

            # Remove this node's edges
            for other_id, other_node in self.nodes.items():
                if node_id in other_node.dependencies:
                    in_degree[other_id] -= 1
                    if in_degree[other_id] == 0:
                        queue.append(other_id)

        if len(result) != len(self.nodes):
            raise ValueError("Topological sort failed: cycle detected")

        return result

    def _detect_cycles(self) -> List[List[int]]:
        """Detect circular dependencies using DFS."""
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node_id: int, path: List[int]) -> None:
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)

            for dep_id in self.nodes[node_id].dependencies:
                if dep_id not in visited:
                    dfs(dep_id, path[:])
                elif dep_id in rec_stack:
                    # Found cycle
                    cycle_start = path.index(dep_id)
                    cycles.append(path[cycle_start:])

            rec_stack.remove(node_id)

        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id, [])

        return cycles

    def _identify_parallelism(self) -> Dict[int, List[int]]:
        """Return dict of {phase: [nodes_that_can_run_in_parallel]}.

        Phase represents execution level:
        - Phase 0: nodes with no dependencies
        - Phase 1: nodes depending only on phase 0
        - etc.
        """
        phases: Dict[int, List[int]] = {}
        node_phase: Dict[int, int] = {}

        # Assign phases based on maximum dependency phase
        for node_id in self.nodes:
            if not self.nodes[node_id].dependencies:
                # No dependencies = phase 0
                node_phase[node_id] = 0
            else:
                # Phase = max(dependency phases) + 1
                max_dep_phase = max(
                    node_phase.get(dep_id, 0)
                    for dep_id in self.nodes[node_id].dependencies
                )
                node_phase[node_id] = max_dep_phase + 1

        # Group nodes by phase
        for node_id, phase in node_phase.items():
            if phase not in phases:
                phases[phase] = []
            phases[phase].append(node_id)

        return phases
