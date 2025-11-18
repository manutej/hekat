"""
Comprehensive tests for HEKAT Compiler

End-to-end tests: DSL string → ExecutionPlan
Tests all 8 patterns, error handling, token estimates, complexity classification
"""

import pytest
from hekat_compiler import HEKATCompiler, CompileError, ExecutionPlan, Phase


@pytest.fixture
def compiler():
    """Fresh compiler instance"""
    return HEKATCompiler()


# ============================================================================
# PATTERN TESTS (8 patterns)
# ============================================================================

def test_simple_pattern(compiler):
    """Simple: 'agent : \"prompt\"' → L1 plan with 1 phase"""
    plan = compiler.compile('practical-programmer : "implement authentication"')
    assert plan.pattern_type == 'Simple'
    assert plan.complexity_level == 'L1'
    assert len(plan.phases) == 1
    assert plan.phases[0].agents == ['practical-programmer']
    assert plan.phases[0].can_parallelize is False
    assert plan.total_tokens > 0


def test_skilled_pattern(compiler):
    """Skilled: 'agent + skill : \"prompt\"' → L1 plan with skills"""
    plan = compiler.compile('practical-programmer + fastapi + postgresql : "build API"')
    assert plan.pattern_type == 'Skilled'
    assert plan.complexity_level == 'L1'
    assert len(plan.phases) == 1
    assert plan.phases[0].agents == ['practical-programmer']
    assert 'fastapi' in plan.phases[0].skills
    assert 'postgresql' in plan.phases[0].skills


def test_sequential_pattern(compiler):
    """Sequential: 'A → B → C : \"prompt\"' → L3 plan with 3 phases"""
    plan = compiler.compile(
        'deep-researcher → api-architect → practical-programmer : "design API"'
    )
    assert plan.pattern_type == 'Sequential'
    assert plan.complexity_level in ['L2', 'L3']
    assert len(plan.phases) == 3
    assert plan.phases[0].agents == ['deep-researcher']
    assert plan.phases[1].agents == ['api-architect']
    assert plan.phases[2].agents == ['practical-programmer']
    assert all(not p.can_parallelize for p in plan.phases)


def test_parallel_pattern(compiler):
    """Parallel: '(A || B || C) : \"prompt\"' → L3 plan with 1 parallel phase"""
    plan = compiler.compile(
        '(practical-programmer || test-engineer || docs-generator) : "documentation"'
    )
    assert plan.pattern_type == 'Parallel'
    assert plan.complexity_level == 'L3'
    assert len(plan.phases) == 1
    assert plan.phases[0].can_parallelize is True
    assert len(plan.phases[0].agents) == 3
    assert set(plan.phases[0].agents) == {
        'practical-programmer', 'test-engineer', 'docs-generator'
    }


def test_mixed_pattern(compiler):
    """Mixed: 'A → (B || C) → D : \"prompt\"' → L4 plan with 3 phases"""
    plan = compiler.compile(
        'deep-researcher → (api-architect || debug-detective) → practical-programmer : "fix bug"'
    )
    assert plan.pattern_type == 'Mixed'
    assert plan.complexity_level in ['L3', 'L4']
    assert len(plan.phases) == 3
    assert plan.phases[0].can_parallelize is False
    assert plan.phases[1].can_parallelize is True
    assert plan.phases[2].can_parallelize is False


def test_fallback_pattern(compiler):
    """Fallback: 'A ? B ? C : \"prompt\"' → L6 plan with fallback"""
    plan = compiler.compile(
        'practical-programmer ? code-trimmer ? code-craftsman : "refactor code"'
    )
    assert plan.pattern_type == 'Fallback'
    assert plan.complexity_level in ['L4', 'L5', 'L6']
    assert plan.metadata['has_fallback'] is True


def test_ensemble_pattern(compiler):
    """Ensemble: 'sample^N ; merge ; synthesize : \"prompt\"' → L5 plan"""
    plan = compiler.compile(
        'sample^3 ; merge ; synthesize deep-researcher : "research topic"'
    )
    assert plan.pattern_type == 'Ensemble'
    assert plan.complexity_level in ['L4', 'L5']
    # Should create multiple phases for sampling
    assert len(plan.phases) >= 1


def test_commanded_pattern(compiler):
    """Commanded: '@ctx7(agent) : \"prompt\"' → L1 plan with command"""
    plan = compiler.compile('@ctx7(deep-researcher) : "research library"')
    assert plan.pattern_type == 'Commanded'
    assert plan.complexity_level == 'L1'
    assert len(plan.phases) == 1


# ============================================================================
# COMPLEX COMBINATIONS
# ============================================================================

def test_deeply_nested_mixed_pattern(compiler):
    """Complex: 'A → (B || (C → D)) → E : \"prompt\"'"""
    plan = compiler.compile(
        'deep-researcher → (api-architect || (practical-programmer → test-engineer)) → docs-generator : "build feature"'
    )
    assert plan.pattern_type == 'Mixed'
    assert plan.complexity_level in ['L4', 'L5', 'L6']
    assert len(plan.phases) >= 3


def test_multiple_parallel_groups(compiler):
    """'(A || B) → (C || D) : \"prompt\"' → 2 parallel phases"""
    plan = compiler.compile(
        '(deep-researcher || api-architect) → (practical-programmer || test-engineer) : "develop feature"'
    )
    assert plan.pattern_type == 'Mixed'
    assert len(plan.phases) == 2
    assert plan.phases[0].can_parallelize is True
    assert plan.phases[1].can_parallelize is True


def test_long_sequence(compiler):
    """'A → B → C → D → E : \"prompt\"' → L5 plan, 5 phases"""
    plan = compiler.compile(
        'deep-researcher → api-architect → practical-programmer → test-engineer → deployment-orchestrator : "full workflow"'
    )
    assert plan.pattern_type == 'Sequential'
    assert plan.complexity_level in ['L4', 'L5']
    assert len(plan.phases) == 5


def test_skilled_sequential(compiler):
    """'agent + skill → agent : \"prompt\"'"""
    plan = compiler.compile(
        'practical-programmer + fastapi → test-engineer : "test API"'
    )
    assert plan.pattern_type == 'Sequential'
    assert len(plan.phases) == 2
    assert 'fastapi' in plan.phases[0].skills


# ============================================================================
# ERROR HANDLING
# ============================================================================

def test_invalid_agent_name(compiler):
    """'nonexistent-agent : \"prompt\"' → CompileError"""
    with pytest.raises(CompileError) as exc:
        compiler.compile('nonexistent-agent : "do something"')
    assert "Agent 'nonexistent-agent' not found" in str(exc.value)


def test_invalid_skill_name(compiler):
    """'agent + nonexistent-skill : \"prompt\"' → CompileError"""
    with pytest.raises(CompileError) as exc:
        compiler.compile('practical-programmer + nonexistent-skill : "task"')
    assert "Skill 'nonexistent-skill' not found" in str(exc.value)


def test_syntax_error_missing_colon(compiler):
    """'agent \"prompt\"' (no colon) → CompileError"""
    with pytest.raises(CompileError) as exc:
        compiler.compile('practical-programmer "implement feature"')
    assert "Parser error" in str(exc.value)


def test_syntax_error_unmatched_paren(compiler):
    """'(A || B : \"prompt\"' (missing closing paren) → CompileError"""
    with pytest.raises(CompileError) as exc:
        compiler.compile('(practical-programmer || test-engineer : "task"')
    assert "Parser error" in str(exc.value) or "unmatched" in str(exc.value).lower()


def test_empty_query(compiler):
    """'' (empty string) → CompileError"""
    with pytest.raises(CompileError):
        compiler.compile('')


# ============================================================================
# TOKEN BUDGET ESTIMATES
# ============================================================================

def test_token_budget_single_agent(compiler):
    """Single agent → ~600-800 tokens"""
    plan = compiler.compile('practical-programmer : "short task"')
    assert 500 <= plan.total_tokens <= 1000


def test_token_budget_increases_with_agents(compiler):
    """More agents → higher token budget"""
    plan1 = compiler.compile('practical-programmer : "task"')
    plan2 = compiler.compile(
        'practical-programmer → test-engineer → docs-generator : "task"'
    )
    assert plan2.total_tokens > plan1.total_tokens


def test_token_budget_increases_with_prompt_length(compiler):
    """Longer prompt → higher token budget"""
    short_prompt = 'practical-programmer : "task"'
    long_prompt = 'practical-programmer : "' + ('x' * 500) + '"'

    plan1 = compiler.compile(short_prompt)
    plan2 = compiler.compile(long_prompt)

    assert plan2.total_tokens > plan1.total_tokens


def test_parallel_has_penalty(compiler):
    """Parallel execution → token penalty"""
    sequential = compiler.compile('practical-programmer → test-engineer : "task"')
    parallel = compiler.compile('(practical-programmer || test-engineer) : "task"')

    # Parallel should have higher budget per phase
    assert parallel.phases[0].token_budget > sequential.phases[0].token_budget


# ============================================================================
# PATTERN TYPE DETECTION
# ============================================================================

def test_pattern_detection_all_types(compiler):
    """Verify all 8 pattern types detected correctly"""
    patterns = [
        ('practical-programmer : "task"', 'Simple'),
        ('practical-programmer + fastapi : "task"', 'Skilled'),
        ('practical-programmer → test-engineer : "task"', 'Sequential'),
        ('(practical-programmer || test-engineer) : "task"', 'Parallel'),
        ('practical-programmer → (test-engineer || docs-generator) : "task"', 'Mixed'),
        ('practical-programmer ? test-engineer : "task"', 'Fallback'),
        ('sample^2 ; merge ; synthesize practical-programmer : "task"', 'Ensemble'),
        ('@ctx7(practical-programmer) : "task"', 'Commanded')
    ]

    for query, expected_type in patterns:
        plan = compiler.compile(query)
        assert plan.pattern_type == expected_type, f"Failed for: {query}"


# ============================================================================
# COMPLEXITY CLASSIFICATION
# ============================================================================

def test_complexity_l1(compiler):
    """Single agent → L1"""
    plan = compiler.compile('practical-programmer : "task"')
    assert plan.complexity_level == 'L1'


def test_complexity_l2(compiler):
    """Two agents, simple sequence → L2"""
    plan = compiler.compile('practical-programmer → test-engineer : "task"')
    assert plan.complexity_level == 'L2'


def test_complexity_l3(compiler):
    """3 agents or simple parallel → L3"""
    plan = compiler.compile('(practical-programmer || test-engineer || docs-generator) : "task"')
    assert plan.complexity_level == 'L3'


def test_complexity_increases_with_agents(compiler):
    """More agents → higher complexity"""
    plan1 = compiler.compile('practical-programmer : "task"')
    plan5 = compiler.compile(
        'deep-researcher → api-architect → practical-programmer → test-engineer → docs-generator : "task"'
    )

    complexity_order = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7']
    assert complexity_order.index(plan5.complexity_level) > complexity_order.index(plan1.complexity_level)


# ============================================================================
# METADATA & PLAN STRUCTURE
# ============================================================================

def test_plan_has_metadata(compiler):
    """ExecutionPlan includes metadata"""
    plan = compiler.compile('practical-programmer → test-engineer : "task"')
    assert 'total_agents' in plan.metadata
    assert 'execution_depth' in plan.metadata
    assert 'has_parallelism' in plan.metadata
    assert plan.metadata['total_agents'] == 2
    assert plan.metadata['execution_depth'] == 2
    assert plan.metadata['has_parallelism'] is False


def test_plan_has_prompt(compiler):
    """ExecutionPlan preserves original prompt"""
    prompt = "build authentication system"
    plan = compiler.compile(f'practical-programmer : "{prompt}"')
    assert plan.prompt == prompt


def test_phase_numbering(compiler):
    """Phases numbered sequentially from 1"""
    plan = compiler.compile('deep-researcher → api-architect → practical-programmer : "task"')
    assert plan.phases[0].num == 1
    assert plan.phases[1].num == 2
    assert plan.phases[2].num == 3


# ============================================================================
# EDGE CASES
# ============================================================================

def test_single_agent_in_parens(compiler):
    """'(agent) : \"prompt\"' → treated as simple"""
    plan = compiler.compile('(practical-programmer) : "task"')
    # Should still work, treated as single agent
    assert len(plan.phases) == 1
    assert plan.phases[0].agents == ['practical-programmer']


def test_whitespace_handling(compiler):
    """Extra whitespace shouldn't break compilation"""
    plan = compiler.compile('  practical-programmer   →   test-engineer  :  "task"  ')
    assert plan.pattern_type == 'Sequential'
    assert len(plan.phases) == 2
