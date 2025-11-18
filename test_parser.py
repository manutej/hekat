"""Comprehensive tests for HEKAT DSL Parser - All 8 Patterns."""

import pytest
from hekat_parser import (
    parse, Parser, ParseError,
    QueryNode, SimpleNode, SequentialNode, ParallelNode,
    FallbackNode, EnsembleNode, CommandedNode, SkilledNode
)
from hekat_lexer import Lexer


# Pattern 1: Simple
def test_simple_agent():
    """Test simple agent invocation."""
    result = parse('api-architect : "design API"')
    assert isinstance(result, QueryNode)
    assert isinstance(result.expression, SimpleNode)
    assert result.expression.name == "api-architect"
    assert result.prompt == "design API"


# Pattern 2: Sequential
def test_sequential_two_agents():
    """Test sequential with 2 agents."""
    result = parse('deep-researcher -> api-architect : "build feature"')
    assert isinstance(result.expression, SequentialNode)
    assert len(result.expression.steps) == 2
    assert result.expression.steps[0].name == "deep-researcher"
    assert result.expression.steps[1].name == "api-architect"


def test_sequential_three_agents():
    """Test sequential with 3 agents."""
    result = parse('A -> B -> C : "task"')
    assert isinstance(result.expression, SequentialNode)
    assert len(result.expression.steps) == 3
    assert [s.name for s in result.expression.steps] == ["A", "B", "C"]


# Pattern 3: Parallel
def test_parallel_two_agents():
    """Test parallel with 2 agents."""
    result = parse('(api-architect || deep-researcher) : "evaluate"')
    assert isinstance(result.expression, ParallelNode)
    assert len(result.expression.branches) == 2
    assert result.expression.branches[0].name == "api-architect"
    assert result.expression.branches[1].name == "deep-researcher"


def test_parallel_three_agents():
    """Test parallel with 3 agents."""
    result = parse('(A || B || C) : "task"')
    assert isinstance(result.expression, ParallelNode)
    assert len(result.expression.branches) == 3


def test_parallel_single_branch_error():
    """Test parallel with single branch raises error."""
    with pytest.raises(ParseError) as exc:
        parse('(A) : "task"')
    assert "at least 2 branches" in str(exc.value)


# Pattern 4: Mixed
def test_mixed_sequential_parallel():
    """Test sequential with parallel in middle."""
    result = parse('A -> (B || C) -> D : "task"')
    assert isinstance(result.expression, SequentialNode)
    assert len(result.expression.steps) == 3
    assert isinstance(result.expression.steps[1], ParallelNode)
    assert len(result.expression.steps[1].branches) == 2


def test_mixed_parallel_sequential():
    """Test parallel with sequential branches."""
    result = parse('(A -> B || C -> D) : "task"')
    assert isinstance(result.expression, ParallelNode)
    assert len(result.expression.branches) == 2
    assert isinstance(result.expression.branches[0], SequentialNode)
    assert isinstance(result.expression.branches[1], SequentialNode)


# Pattern 5: Fallback
def test_fallback_two_alternatives():
    """Test fallback with 2 alternatives."""
    result = parse('deploy-orchestrator ? devops-expert : "deploy"')
    assert isinstance(result.expression, FallbackNode)
    assert len(result.expression.alternatives) == 2
    assert result.expression.alternatives[0].name == "deploy-orchestrator"
    assert result.expression.alternatives[1].name == "devops-expert"


def test_fallback_three_alternatives():
    """Test fallback with 3 alternatives."""
    result = parse('A ? B ? C : "task"')
    assert isinstance(result.expression, FallbackNode)
    assert len(result.expression.alternatives) == 3


def test_fallback_with_sequential():
    """Test fallback with sequential branches."""
    result = parse('A -> B ? C -> D : "task"')
    assert isinstance(result.expression, FallbackNode)
    assert len(result.expression.alternatives) == 2
    assert isinstance(result.expression.alternatives[0], SequentialNode)
    assert isinstance(result.expression.alternatives[1], SequentialNode)


# Pattern 6: Ensemble
def test_ensemble_basic():
    """Test ensemble pattern."""
    result = parse('sample^3 ; merge ; synthesize : "research"')
    assert isinstance(result.expression, EnsembleNode)
    assert result.expression.base == "sample"
    assert result.expression.count == 3
    assert result.expression.merge_step == "merge"
    assert result.expression.synth_step == "synthesize"


def test_ensemble_invalid_count():
    """Test ensemble with invalid count."""
    with pytest.raises(ParseError) as exc:
        parse('sample^0 ; merge ; synthesize : "task"')
    assert "between 1 and 10" in str(exc.value)

    with pytest.raises(ParseError) as exc:
        parse('sample^15 ; merge ; synthesize : "task"')
    assert "between 1 and 10" in str(exc.value)


# Pattern 7: Commanded
def test_commanded_single_agent():
    """Test commanded pattern with single agent."""
    result = parse('@ctx7(deep-researcher) : "analyze"')
    assert isinstance(result.expression, CommandedNode)
    assert result.expression.command == "ctx7"
    assert result.expression.agents == ["deep-researcher"]


def test_commanded_empty_agents_error():
    """Test commanded with empty agents raises error."""
    with pytest.raises(ParseError) as exc:
        parse('@ctx7() : "task"')
    assert "at least one agent" in str(exc.value)


# Pattern 8: Skilled
def test_skilled_one_skill():
    """Test skilled pattern with one skill."""
    result = parse('api-architect + fastapi : "design API"')
    assert isinstance(result.expression, SkilledNode)
    assert result.expression.agent == "api-architect"
    assert result.expression.skills == ["fastapi"]


def test_skilled_multiple_skills():
    """Test skilled pattern with multiple skills."""
    result = parse('api-architect + fastapi + postgresql + jwt : "design"')
    assert isinstance(result.expression, SkilledNode)
    assert result.expression.agent == "api-architect"
    assert result.expression.skills == ["fastapi", "postgresql", "jwt"]


# Complex Combinations
def test_complex_fallback_sequential_parallel():
    """Test fallback with sequential containing parallel."""
    result = parse('A -> (B || C) ? D : "task"')
    assert isinstance(result.expression, FallbackNode)
    assert len(result.expression.alternatives) == 2
    assert isinstance(result.expression.alternatives[0], SequentialNode)


def test_complex_parallel_with_skilled():
    """Test parallel with skilled branches."""
    result = parse('(api-architect + fastapi || db-expert + postgresql) : "design"')
    assert isinstance(result.expression, ParallelNode)
    assert isinstance(result.expression.branches[0], SkilledNode)
    assert isinstance(result.expression.branches[1], SkilledNode)


def test_complex_sequential_skilled_commanded():
    """Test sequential with skilled and commanded."""
    result = parse('api-architect + fastapi -> @ctx7(researcher) : "task"')
    assert isinstance(result.expression, SequentialNode)
    assert isinstance(result.expression.steps[0], SkilledNode)
    assert isinstance(result.expression.steps[1], CommandedNode)


# Nesting Tests
def test_nested_parallel_in_fallback():
    """Test nested parallel inside fallback."""
    result = parse('(A || B) ? (C || D) : "task"')
    assert isinstance(result.expression, FallbackNode)
    assert isinstance(result.expression.alternatives[0], ParallelNode)
    assert isinstance(result.expression.alternatives[1], ParallelNode)


def test_nested_sequential_in_parallel():
    """Test nested sequential inside parallel."""
    result = parse('(A -> B -> C || D -> E) : "task"')
    assert isinstance(result.expression, ParallelNode)
    assert isinstance(result.expression.branches[0], SequentialNode)
    assert len(result.expression.branches[0].steps) == 3


# Error Cases
def test_error_missing_colon():
    """Test error when colon is missing."""
    with pytest.raises(ParseError) as exc:
        parse('api-architect')
    assert "Expected COLON" in str(exc.value)


def test_error_missing_prompt():
    """Test error when prompt string is missing."""
    with pytest.raises(ParseError) as exc:
        parse('api-architect :')
    assert "Expected STRING" in str(exc.value)


def test_error_unclosed_parenthesis():
    """Test error for unclosed parenthesis."""
    with pytest.raises(ParseError) as exc:
        parse('(A || B : "task"')
    assert "Expected RPAREN" in str(exc.value)


def test_error_missing_ensemble_semicolon():
    """Test error when ensemble semicolon is missing."""
    with pytest.raises(ParseError) as exc:
        parse('sample^3 merge : "task"')
    assert "Expected SEMICOLON" in str(exc.value)


# Operator Precedence Tests
def test_precedence_fallback_lower_than_sequential():
    """Test fallback has lower precedence than sequential."""
    result = parse('A -> B ? C -> D : "task"')
    # Should parse as (A -> B) ? (C -> D)
    assert isinstance(result.expression, FallbackNode)
    assert isinstance(result.expression.alternatives[0], SequentialNode)
    assert isinstance(result.expression.alternatives[1], SequentialNode)


def test_precedence_sequential_lower_than_parallel():
    """Test sequential has lower precedence than parallel."""
    result = parse('A -> (B || C) -> D : "task"')
    # Should parse as A -> (B || C) -> D
    assert isinstance(result.expression, SequentialNode)
    assert isinstance(result.expression.steps[1], ParallelNode)


def test_precedence_skilled_highest():
    """Test skilled has highest precedence."""
    result = parse('A + skill1 -> B : "task"')
    # Should parse as (A + skill1) -> B
    assert isinstance(result.expression, SequentialNode)
    assert isinstance(result.expression.steps[0], SkilledNode)


# Edge Cases
def test_agent_with_hyphens():
    """Test agents with hyphens in names."""
    result = parse('deep-researcher : "task"')
    assert result.expression.name == "deep-researcher"


def test_prompt_with_special_chars():
    """Test prompt with special characters."""
    result = parse('agent : "design API with @mentions and #tags"')
    assert result.prompt == "design API with @mentions and #tags"


def test_empty_parallel_not_allowed():
    """Test that empty parallel is not allowed."""
    with pytest.raises(ParseError):
        parse('() : "task"')
