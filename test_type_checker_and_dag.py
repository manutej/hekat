"""Tests for HEKAT Type Checker and DAG Builder."""

import pytest
from hekat_lexer import Lexer
from hekat_parser import Parser, QueryNode, SimpleNode, SequentialNode, ParallelNode, SkilledNode, EnsembleNode
from hekat_type_checker import TypeChecker
from hekat_dag_builder import DAGBuilder, DAG


# Helper function
def parse(dsl: str) -> QueryNode:
    """Parse DSL string to QueryNode."""
    lexer = Lexer(dsl)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


# ============================================================================
# TYPE CHECKER TESTS
# ============================================================================

def test_type_checker_valid_agent():
    """Valid agent name should pass validation."""
    query = parse('deep-researcher : "research topic"')
    checker = TypeChecker()
    result = checker.validate(query)
    assert result['valid'] is True
    assert len(result['errors']) == 0


def test_type_checker_invalid_agent():
    """Invalid agent name should fail validation."""
    query = parse('nonexistent-agent : "do something"')
    checker = TypeChecker()
    result = checker.validate(query)
    assert result['valid'] is False
    assert "Agent 'nonexistent-agent' not found" in result['errors']


def test_type_checker_valid_skilled():
    """Valid SkilledNode with existing agent and skills."""
    query = parse('practical-programmer + fastapi + postgresql : "build API"')
    checker = TypeChecker()
    result = checker.validate(query)
    assert result['valid'] is True
    assert len(result['errors']) == 0


def test_type_checker_invalid_skill():
    """Invalid skill in SkilledNode should fail."""
    query = parse('practical-programmer + nonexistent-skill : "build"')
    checker = TypeChecker()
    result = checker.validate(query)
    assert result['valid'] is False
    assert "Skill 'nonexistent-skill' not found" in result['errors']


def test_type_checker_invalid_agent_in_skilled():
    """Invalid agent in SkilledNode should fail."""
    query = parse('fake-agent + fastapi : "build"')
    checker = TypeChecker()
    result = checker.validate(query)
    assert result['valid'] is False
    assert "Agent 'fake-agent' not found" in result['errors']


def test_type_checker_valid_sequential():
    """Valid sequential composition."""
    query = parse('deep-researcher -> practical-programmer -> test-engineer : "build feature"')
    checker = TypeChecker()
    result = checker.validate(query)
    assert result['valid'] is True


def test_type_checker_invalid_agent_in_sequential():
    """Invalid agent in sequential chain should fail."""
    query = parse('deep-researcher -> fake-agent -> test-engineer : "build"')
    checker = TypeChecker()
    result = checker.validate(query)
    assert result['valid'] is False
    assert "Agent 'fake-agent' not found" in result['errors']


def test_type_checker_valid_parallel():
    """Valid parallel composition."""
    query = parse('(deep-researcher || api-architect || practical-programmer) : "parallel work"')
    checker = TypeChecker()
    result = checker.validate(query)
    assert result['valid'] is True


def test_type_checker_invalid_agent_in_parallel():
    """Invalid agent in parallel branch should fail."""
    query = parse('(deep-researcher || fake-agent) : "parallel"')
    checker = TypeChecker()
    result = checker.validate(query)
    assert result['valid'] is False
    assert "Agent 'fake-agent' not found" in result['errors']


def test_type_checker_valid_fallback():
    """Valid fallback chain."""
    query = parse('practical-programmer ? debug-detective ? deep-researcher : "fix bug"')
    checker = TypeChecker()
    result = checker.validate(query)
    assert result['valid'] is True


def test_type_checker_ensemble_valid():
    """Valid ensemble pattern."""
    query = parse('deep-researcher^3;merge;synthesize : "research"')
    checker = TypeChecker()
    result = checker.validate(query)
    assert result['valid'] is True


def test_type_checker_ensemble_invalid_agent():
    """Ensemble with invalid base agent should fail."""
    query = parse('fake-agent^3;merge;synthesize : "research"')
    checker = TypeChecker()
    result = checker.validate(query)
    assert result['valid'] is False
    assert "Ensemble base agent 'fake-agent' not found" in result['errors']


def test_type_checker_commanded_valid():
    """Valid commanded pattern (command may be external)."""
    query = parse('@ctx7(deep-researcher) : "get docs"')
    checker = TypeChecker()
    result = checker.validate(query)
    # Valid because agent exists, warning about command is OK
    assert result['valid'] is True


def test_type_checker_commanded_invalid_agent():
    """Commanded with invalid agent should fail."""
    query = parse('@ctx7(fake-agent) : "get docs"')
    checker = TypeChecker()
    result = checker.validate(query)
    assert result['valid'] is False
    assert "Agent 'fake-agent' not found in commanded pattern" in result['errors']


def test_type_checker_empty_prompt():
    """Empty prompt should fail validation."""
    query = parse('deep-researcher : ""')
    checker = TypeChecker()
    result = checker.validate(query)
    assert result['valid'] is False
    assert "Query prompt cannot be empty" in result['errors']


def test_type_checker_complex_nested():
    """Complex nested composition should validate correctly."""
    query = parse(
        'deep-researcher -> (practical-programmer || test-engineer) -> deployment-orchestrator : "full flow"'
    )
    checker = TypeChecker()
    result = checker.validate(query)
    assert result['valid'] is True


# ============================================================================
# DAG BUILDER TESTS
# ============================================================================

def test_dag_simple_node():
    """SimpleNode creates single DAG node."""
    query = parse('deep-researcher : "research"')
    builder = DAGBuilder()
    dag = builder.build(query.expression)

    assert len(dag.nodes) == 1
    assert len(dag.execution_order) == 1
    node = dag.nodes[0]
    assert isinstance(node.expr, SimpleNode)
    assert len(node.dependencies) == 0


def test_dag_sequential_chain():
    """SequentialNode creates chain with dependencies."""
    query = parse('deep-researcher -> practical-programmer -> test-engineer : "sequential"')
    builder = DAGBuilder()
    dag = builder.build(query.expression)

    assert len(dag.nodes) == 3
    # Node 0 (deep-researcher) has no deps
    assert len(dag.nodes[0].dependencies) == 0
    # Node 1 (practical-programmer) depends on node 0
    assert dag.nodes[1].dependencies == {0}
    # Node 2 (test-engineer) depends on node 1
    assert dag.nodes[2].dependencies == {1}


def test_dag_parallel_branches():
    """ParallelNode creates independent branches."""
    query = parse('(deep-researcher || api-architect || practical-programmer) : "parallel"')
    builder = DAGBuilder()
    dag = builder.build(query.expression)

    assert len(dag.nodes) == 3
    # All nodes have no dependencies (parallel)
    for node in dag.nodes.values():
        assert len(node.dependencies) == 0


def test_dag_mixed_sequential_parallel():
    """Mixed sequential and parallel creates correct structure."""
    query = parse('deep-researcher -> (practical-programmer || test-engineer) : "mixed"')
    builder = DAGBuilder()
    dag = builder.build(query.expression)

    assert len(dag.nodes) == 3
    # Node 0 (deep-researcher) has no deps
    assert len(dag.nodes[0].dependencies) == 0
    # Nodes 1 and 2 (parallel branches) both depend on node 0
    assert dag.nodes[1].dependencies == {0}
    assert dag.nodes[2].dependencies == {0}


def test_dag_fallback_structure():
    """FallbackNode creates primary path with fallback alternatives."""
    query = parse('practical-programmer ? debug-detective ? deep-researcher : "fallback"')
    builder = DAGBuilder()
    dag = builder.build(query.expression)

    assert len(dag.nodes) == 3
    # Primary node (0) has no deps
    assert len(dag.nodes[0].dependencies) == 0
    assert dag.nodes[0].is_fallback is False
    # Fallback nodes are marked
    assert dag.nodes[1].is_fallback is True
    assert dag.nodes[2].is_fallback is True


def test_dag_ensemble_structure():
    """EnsembleNode creates sample->merge->synth structure."""
    query = parse('deep-researcher^3;merge;synthesize : "ensemble"')
    builder = DAGBuilder()
    dag = builder.build(query.expression)

    # 3 sample nodes + 1 merge + 1 synth = 5 nodes
    assert len(dag.nodes) == 5

    # First 3 nodes are samples (no dependencies)
    for i in range(3):
        assert len(dag.nodes[i].dependencies) == 0

    # Merge node (3) depends on all 3 samples
    assert dag.nodes[3].dependencies == {0, 1, 2}

    # Synth node (4) depends on merge
    assert dag.nodes[4].dependencies == {3}


def test_dag_topological_sort_simple():
    """Topological sort returns correct execution order."""
    query = parse('deep-researcher -> practical-programmer : "seq"')
    builder = DAGBuilder()
    dag = builder.build(query.expression)

    assert dag.execution_order == [0, 1]


def test_dag_topological_sort_complex():
    """Topological sort handles complex dependencies."""
    query = parse('deep-researcher -> (practical-programmer || test-engineer) -> deployment-orchestrator : "complex"')
    builder = DAGBuilder()
    dag = builder.build(query.expression)

    # Node 0 first, then 1 and 2 (parallel), then 3
    assert dag.execution_order[0] == 0
    assert set(dag.execution_order[1:3]) == {1, 2}
    assert dag.execution_order[3] == 3


def test_dag_parallel_phases_simple():
    """Parallel phases correctly identify independent nodes."""
    query = parse('(deep-researcher || api-architect) : "parallel"')
    builder = DAGBuilder()
    dag = builder.build(query.expression)

    # Both nodes in phase 0 (no dependencies)
    assert 0 in dag.parallel_phases
    assert set(dag.parallel_phases[0]) == {0, 1}


def test_dag_parallel_phases_sequential():
    """Sequential nodes go in different phases."""
    query = parse('deep-researcher -> practical-programmer : "seq"')
    builder = DAGBuilder()
    dag = builder.build(query.expression)

    # Node 0 in phase 0, node 1 in phase 1
    assert dag.parallel_phases[0] == [0]
    assert dag.parallel_phases[1] == [1]


def test_dag_parallel_phases_mixed():
    """Mixed pattern creates correct phases."""
    query = parse('deep-researcher -> (practical-programmer || test-engineer) : "mixed"')
    builder = DAGBuilder()
    dag = builder.build(query.expression)

    # Phase 0: node 0
    assert dag.parallel_phases[0] == [0]
    # Phase 1: nodes 1 and 2 (parallel after node 0)
    assert set(dag.parallel_phases[1]) == {1, 2}


def test_dag_no_cycles():
    """Valid DSL should never have cycles."""
    query = parse('deep-researcher -> practical-programmer -> test-engineer : "no cycles"')
    builder = DAGBuilder()
    dag = builder.build(query.expression)

    # No exception means no cycles detected
    assert len(dag.nodes) == 3


def test_dag_skilled_node():
    """SkilledNode creates single node with skills."""
    query = parse('practical-programmer + fastapi + postgresql : "skilled"')
    builder = DAGBuilder()
    dag = builder.build(query.expression)

    assert len(dag.nodes) == 1
    node = dag.nodes[0]
    assert isinstance(node.expr, SkilledNode)
    assert node.expr.agent == 'practical-programmer'
    assert set(node.expr.skills) == {'fastapi', 'postgresql'}


def test_dag_commanded_node():
    """CommandedNode creates single node."""
    query = parse('@ctx7(deep-researcher) : "commanded"')
    builder = DAGBuilder()
    dag = builder.build(query.expression)

    assert len(dag.nodes) == 1


def test_dag_complex_nested_pattern():
    """Complex nested pattern creates correct DAG structure."""
    # A -> (B || C) -> D ? E
    query = parse('deep-researcher -> (practical-programmer || test-engineer) -> deployment-orchestrator ? debug-detective : "complex"')
    builder = DAGBuilder()
    dag = builder.build(query.expression)

    # 5 nodes total (1 + 2 parallel + 1 + 1 fallback)
    assert len(dag.nodes) == 5

    # Verify dependency structure
    assert len(dag.nodes[0].dependencies) == 0  # deep-researcher
    assert dag.nodes[1].dependencies == {0}  # practical-programmer depends on 0
    assert dag.nodes[2].dependencies == {0}  # test-engineer depends on 0
    # deployment-orchestrator depends on both parallel branches
    assert dag.nodes[3].dependencies == {1, 2}
    # fallback has no deps (alternative path)
    assert len(dag.nodes[4].dependencies) == 0
    assert dag.nodes[4].is_fallback is True
