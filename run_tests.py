"""Run parser tests without pytest."""

import sys
from hekat_parser import parse, ParseError, SimpleNode, SequentialNode, ParallelNode, FallbackNode, EnsembleNode, CommandedNode, SkilledNode

tests_passed = 0
tests_failed = 0

def test(name, func):
    """Run a single test."""
    global tests_passed, tests_failed
    try:
        func()
        print(f"✓ {name}")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ {name}: {e}")
        tests_failed += 1

# Pattern 1: Simple
def test_simple():
    result = parse('api-architect : "design API"')
    assert isinstance(result.expression, SimpleNode)
    assert result.expression.name == "api-architect"

test("Simple agent", test_simple)

# Pattern 2: Sequential
def test_seq2():
    result = parse('deep-researcher -> api-architect : "build"')
    assert isinstance(result.expression, SequentialNode)
    assert len(result.expression.steps) == 2

test("Sequential two agents", test_seq2)

def test_seq3():
    result = parse('A -> B -> C : "task"')
    assert isinstance(result.expression, SequentialNode)
    assert len(result.expression.steps) == 3

test("Sequential three agents", test_seq3)

# Pattern 3: Parallel
def test_par2():
    result = parse('(A || B) : "task"')
    assert isinstance(result.expression, ParallelNode)
    assert len(result.expression.branches) == 2

test("Parallel two agents", test_par2)

def test_par3():
    result = parse('(A || B || C) : "task"')
    assert isinstance(result.expression, ParallelNode)
    assert len(result.expression.branches) == 3

test("Parallel three agents", test_par3)

# Pattern 4: Mixed
def test_mixed1():
    result = parse('A -> (B || C) -> D : "task"')
    assert isinstance(result.expression, SequentialNode)
    assert isinstance(result.expression.steps[1], ParallelNode)

test("Mixed sequential-parallel", test_mixed1)

def test_mixed2():
    result = parse('(A -> B || C -> D) : "task"')
    assert isinstance(result.expression, ParallelNode)
    assert isinstance(result.expression.branches[0], SequentialNode)

test("Mixed parallel-sequential", test_mixed2)

# Pattern 5: Fallback
def test_fall2():
    result = parse('A ? B : "task"')
    assert isinstance(result.expression, FallbackNode)
    assert len(result.expression.alternatives) == 2

test("Fallback two alternatives", test_fall2)

def test_fall3():
    result = parse('A ? B ? C : "task"')
    assert isinstance(result.expression, FallbackNode)
    assert len(result.expression.alternatives) == 3

test("Fallback three alternatives", test_fall3)

# Pattern 6: Ensemble
def test_ensemble():
    result = parse('sample^3 ; merge ; synthesize : "research"')
    assert isinstance(result.expression, EnsembleNode)
    assert result.expression.count == 3

test("Ensemble basic", test_ensemble)

# Pattern 7: Commanded
def test_commanded():
    result = parse('@ctx7(researcher) : "analyze"')
    assert isinstance(result.expression, CommandedNode)
    assert result.expression.command == "ctx7"

test("Commanded single agent", test_commanded)

# Pattern 8: Skilled
def test_skilled1():
    result = parse('api-architect + fastapi : "design"')
    assert isinstance(result.expression, SkilledNode)
    assert result.expression.skills == ["fastapi"]

test("Skilled one skill", test_skilled1)

def test_skilled2():
    result = parse('agent + skill1 + skill2 : "task"')
    assert isinstance(result.expression, SkilledNode)
    assert len(result.expression.skills) == 2

test("Skilled multiple skills", test_skilled2)

# Complex combinations
def test_complex1():
    result = parse('A -> (B || C) ? D : "task"')
    assert isinstance(result.expression, FallbackNode)
    assert isinstance(result.expression.alternatives[0], SequentialNode)

test("Complex fallback-sequential-parallel", test_complex1)

def test_complex2():
    result = parse('(A + skill1 || B + skill2) : "task"')
    assert isinstance(result.expression, ParallelNode)
    assert isinstance(result.expression.branches[0], SkilledNode)

test("Complex parallel with skilled", test_complex2)

def test_complex3():
    result = parse('agent + skill -> @cmd(other) : "task"')
    assert isinstance(result.expression, SequentialNode)
    assert isinstance(result.expression.steps[0], SkilledNode)
    assert isinstance(result.expression.steps[1], CommandedNode)

test("Complex sequential skilled-commanded", test_complex3)

# Nesting
def test_nested1():
    result = parse('(A || B) ? (C || D) : "task"')
    assert isinstance(result.expression, FallbackNode)
    assert isinstance(result.expression.alternatives[0], ParallelNode)

test("Nested parallel in fallback", test_nested1)

def test_nested2():
    result = parse('(A -> B -> C || D -> E) : "task"')
    assert isinstance(result.expression, ParallelNode)
    assert isinstance(result.expression.branches[0], SequentialNode)
    assert len(result.expression.branches[0].steps) == 3

test("Nested sequential in parallel", test_nested2)

# Error cases
def test_error(name, query, expected_msg):
    """Test error case."""
    global tests_passed, tests_failed
    try:
        parse(query)
        print(f"✗ {name}: Expected ParseError but succeeded")
        tests_failed += 1
    except ParseError as e:
        if expected_msg in str(e):
            print(f"✓ {name}")
            tests_passed += 1
        else:
            print(f"✗ {name}: Wrong error message: {e}")
            tests_failed += 1
    except Exception as e:
        print(f"✗ {name}: Unexpected error: {e}")
        tests_failed += 1

test_error("Error missing colon", "agent", "Expected COLON")
test_error("Error missing prompt", "agent :", "Expected STRING")
test_error("Error unclosed paren", "(A || B", "Expected RPAREN")
test_error("Error single parallel branch", "(A) : \"task\"", "at least 2 branches")
test_error("Error ensemble invalid count", "sample^0 ; merge ; synth : \"task\"", "between 1 and 10")
test_error("Error commanded empty", "@ctx7() : \"task\"", "at least one agent")

# Precedence tests
def test_prec1():
    result = parse('A -> B ? C -> D : "task"')
    assert isinstance(result.expression, FallbackNode)
    assert isinstance(result.expression.alternatives[0], SequentialNode)

test("Precedence fallback<sequential", test_prec1)

def test_prec2():
    result = parse('A -> (B || C) -> D : "task"')
    assert isinstance(result.expression, SequentialNode)
    assert isinstance(result.expression.steps[1], ParallelNode)

test("Precedence sequential<parallel", test_prec2)

def test_prec3():
    result = parse('A + skill -> B : "task"')
    assert isinstance(result.expression, SequentialNode)
    assert isinstance(result.expression.steps[0], SkilledNode)

test("Precedence skilled highest", test_prec3)

# Summary
print(f"\n{'='*60}")
print(f"Tests passed: {tests_passed}")
print(f"Tests failed: {tests_failed}")
print(f"Total tests: {tests_passed + tests_failed}")
print(f"Success rate: {tests_passed/(tests_passed+tests_failed)*100:.1f}%")
print(f"{'='*60}")

sys.exit(0 if tests_failed == 0 else 1)
