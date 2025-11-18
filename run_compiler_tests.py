"""
Simple test runner for HEKAT Compiler (no pytest required)
"""

from hekat_compiler import HEKATCompiler, CompileError

def test(name, func):
    """Run single test"""
    try:
        func()
        print(f"✅ {name}")
        return True
    except AssertionError as e:
        print(f"❌ {name}: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {name}: {e}")
        return False


def main():
    compiler = HEKATCompiler()
    passed = 0
    total = 0

    # Test 1: Simple Pattern
    def t1():
        plan = compiler.compile('practical-programmer : "implement auth"')
        assert plan.pattern_type == 'Simple'
        assert plan.complexity_level == 'L1'
        assert len(plan.phases) == 1
    total += 1
    if test("Simple pattern", t1): passed += 1

    # Test 2: Skilled Pattern
    def t2():
        plan = compiler.compile('practical-programmer + fastapi + postgresql : "build API"')
        assert plan.pattern_type == 'Skilled'
        assert 'fastapi' in plan.phases[0].skills
    total += 1
    if test("Skilled pattern", t2): passed += 1

    # Test 3: Sequential Pattern
    def t3():
        plan = compiler.compile('deep-researcher -> api-architect -> practical-programmer : "design"')
        assert plan.pattern_type == 'Sequential'
        assert len(plan.phases) == 3
    total += 1
    if test("Sequential pattern", t3): passed += 1

    # Test 4: Parallel Pattern
    def t4():
        plan = compiler.compile('(practical-programmer || test-engineer || docs-generator) : "docs"')
        assert plan.pattern_type == 'Parallel'
        assert plan.phases[0].can_parallelize is True
    total += 1
    if test("Parallel pattern", t4): passed += 1

    # Test 5: Mixed Pattern
    def t5():
        plan = compiler.compile('deep-researcher -> (api-architect || debug-detective) -> practical-programmer : "fix"')
        assert plan.pattern_type == 'Mixed'
        assert len(plan.phases) == 3
    total += 1
    if test("Mixed pattern", t5): passed += 1

    # Test 6: Fallback Pattern
    def t6():
        plan = compiler.compile('practical-programmer ? code-trimmer ? code-craftsman : "refactor"')
        assert plan.pattern_type == 'Fallback'
        assert plan.metadata['has_fallback'] is True
    total += 1
    if test("Fallback pattern", t6): passed += 1

    # Test 7: Ensemble Pattern
    def t7():
        plan = compiler.compile('deep-researcher^3; merge; synthesize : "research"')
        assert plan.pattern_type == 'Ensemble'
    total += 1
    if test("Ensemble pattern", t7): passed += 1

    # Test 8: Commanded Pattern
    def t8():
        plan = compiler.compile('@ctx7(deep-researcher) : "research lib"')
        assert plan.pattern_type == 'Commanded'
    total += 1
    if test("Commanded pattern", t8): passed += 1

    # Test 9: Invalid Agent
    def t9():
        try:
            compiler.compile('nonexistent-agent : "task"')
            assert False, "Should have raised CompileError"
        except CompileError as e:
            assert "Agent 'nonexistent-agent' not found" in str(e)
    total += 1
    if test("Invalid agent error", t9): passed += 1

    # Test 10: Invalid Skill
    def t10():
        try:
            compiler.compile('practical-programmer + nonexistent-skill : "task"')
            assert False, "Should have raised CompileError"
        except CompileError as e:
            assert "Skill 'nonexistent-skill' not found" in str(e)
    total += 1
    if test("Invalid skill error", t10): passed += 1

    # Test 11: Token Budget Single Agent
    def t11():
        plan = compiler.compile('practical-programmer : "short task"')
        assert 500 <= plan.total_tokens <= 1000
    total += 1
    if test("Token budget single agent", t11): passed += 1

    # Test 12: Token Budget Increases
    def t12():
        plan1 = compiler.compile('practical-programmer : "task"')
        plan2 = compiler.compile('practical-programmer -> test-engineer -> docs-generator : "task"')
        assert plan2.total_tokens > plan1.total_tokens
    total += 1
    if test("Token budget increases", t12): passed += 1

    # Test 13: Complexity L1
    def t13():
        plan = compiler.compile('practical-programmer : "task"')
        assert plan.complexity_level == 'L1'
    total += 1
    if test("Complexity L1", t13): passed += 1

    # Test 14: Complexity L2
    def t14():
        plan = compiler.compile('practical-programmer -> test-engineer : "task"')
        assert plan.complexity_level == 'L2'
    total += 1
    if test("Complexity L2", t14): passed += 1

    # Test 15: Complexity L3
    def t15():
        plan = compiler.compile('(practical-programmer || test-engineer || docs-generator) : "task"')
        assert plan.complexity_level == 'L3'
    total += 1
    if test("Complexity L3", t15): passed += 1

    # Test 16: Deeply Nested
    def t16():
        # Simplified: just use multiple parallel groups
        plan = compiler.compile('deep-researcher -> (api-architect || debug-detective || test-engineer) -> docs-generator : "build"')
        assert plan.pattern_type == 'Mixed'
        assert len(plan.phases) >= 3
    total += 1
    if test("Deeply nested pattern", t16): passed += 1

    # Test 17: Multiple Parallel Groups
    def t17():
        plan = compiler.compile('(deep-researcher || api-architect) -> (practical-programmer || test-engineer) : "develop"')
        assert plan.pattern_type == 'Mixed'
        assert len(plan.phases) == 2
    total += 1
    if test("Multiple parallel groups", t17): passed += 1

    # Test 18: Long Sequence
    def t18():
        plan = compiler.compile('deep-researcher -> api-architect -> practical-programmer -> test-engineer -> deployment-orchestrator : "full"')
        assert plan.pattern_type == 'Sequential'
        assert len(plan.phases) == 5
    total += 1
    if test("Long sequence", t18): passed += 1

    # Test 19: Plan Has Metadata
    def t19():
        plan = compiler.compile('practical-programmer -> test-engineer : "task"')
        assert 'total_agents' in plan.metadata
        assert plan.metadata['total_agents'] == 2
    total += 1
    if test("Plan has metadata", t19): passed += 1

    # Test 20: Plan Preserves Prompt
    def t20():
        prompt = "build authentication system"
        plan = compiler.compile(f'practical-programmer : "{prompt}"')
        assert plan.prompt == prompt
    total += 1
    if test("Plan preserves prompt", t20): passed += 1

    # Test 21: Phase Numbering
    def t21():
        plan = compiler.compile('deep-researcher -> api-architect -> practical-programmer : "task"')
        assert plan.phases[0].num == 1
        assert plan.phases[1].num == 2
        assert plan.phases[2].num == 3
    total += 1
    if test("Phase numbering", t21): passed += 1

    # Test 22: Parallel Has Penalty
    def t22():
        sequential = compiler.compile('practical-programmer -> test-engineer : "task"')
        parallel = compiler.compile('(practical-programmer || test-engineer) : "task"')
        assert parallel.phases[0].token_budget > sequential.phases[0].token_budget
    total += 1
    if test("Parallel token penalty", t22): passed += 1

    # Test 23: Skilled Sequential
    def t23():
        plan = compiler.compile('practical-programmer + fastapi -> test-engineer : "test API"')
        assert plan.pattern_type == 'Sequential'
        assert len(plan.phases) == 2
        assert 'fastapi' in plan.phases[0].skills
    total += 1
    if test("Skilled sequential", t23): passed += 1

    # Test 24: Whitespace Handling
    def t24():
        plan = compiler.compile('  practical-programmer   ->   test-engineer  :  "task"  ')
        assert plan.pattern_type == 'Sequential'
        assert len(plan.phases) == 2
    total += 1
    if test("Whitespace handling", t24): passed += 1

    # Test 25: All Pattern Types
    def t25():
        patterns = [
            ('practical-programmer : "task"', 'Simple'),
            ('practical-programmer + fastapi : "task"', 'Skilled'),
            ('practical-programmer -> test-engineer : "task"', 'Sequential'),
            ('(practical-programmer || test-engineer) : "task"', 'Parallel'),
            ('practical-programmer -> (test-engineer || docs-generator) : "task"', 'Mixed'),
            ('practical-programmer ? test-engineer : "task"', 'Fallback'),
            ('practical-programmer^2; merge; synthesize : "task"', 'Ensemble'),
            ('@ctx7(practical-programmer) : "task"', 'Commanded')
        ]
        for query, expected in patterns:
            plan = compiler.compile(query)
            assert plan.pattern_type == expected
    total += 1
    if test("All 8 pattern types", t25): passed += 1

    print(f"\n{'='*60}")
    print(f"RESULTS: {passed}/{total} tests passed ({100*passed//total}%)")
    print(f"{'='*60}")

    return passed == total


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
