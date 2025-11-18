#!/usr/bin/env python3
"""
HEKAT DSL Compiler Demo

Demonstrates all 8 query patterns and compiler features
"""

from hekat_compiler import HEKATCompiler, CompileError


def demo():
    compiler = HEKATCompiler()

    print("=" * 70)
    print("HEKAT DSL UNIFIED COMPILER - DEMONSTRATION")
    print("=" * 70)
    print()

    queries = [
        ("Simple", 'practical-programmer : "implement authentication"'),
        ("Skilled", 'practical-programmer + fastapi + postgresql : "build REST API"'),
        ("Sequential", 'deep-researcher -> api-architect -> practical-programmer : "design and implement API"'),
        ("Parallel", '(practical-programmer || test-engineer || docs-generator) : "complete documentation"'),
        ("Mixed", 'deep-researcher -> (api-architect || debug-detective) -> practical-programmer : "design database system"'),
        ("Fallback", 'practical-programmer ? code-trimmer ? code-craftsman : "refactor codebase"'),
        ("Ensemble", 'deep-researcher^3; merge; synthesize : "comprehensive research on topic"'),
        ("Commanded", '@ctx7(deep-researcher) : "research React hooks documentation"'),
    ]

    for pattern_name, query in queries:
        print(f"{'─' * 70}")
        print(f"Pattern: {pattern_name}")
        print(f"Query: {query}")
        print()

        try:
            plan = compiler.compile(query)

            print(f"  Pattern Type: {plan.pattern_type}")
            print(f"  Complexity: {plan.complexity_level}")
            print(f"  Total Tokens: {plan.total_tokens}")
            print(f"  Phases: {len(plan.phases)}")
            print()

            for phase in plan.phases:
                parallel_indicator = " [PARALLEL]" if phase.can_parallelize else ""
                agents_list = ", ".join(phase.agents)
                print(f"    Phase {phase.num}{parallel_indicator}: {agents_list} ({phase.token_budget} tokens)")

            print()
            print(f"  Metadata:")
            print(f"    Total Agents: {plan.metadata['total_agents']}")
            print(f"    Execution Depth: {plan.metadata['execution_depth']}")
            print(f"    Has Parallelism: {plan.metadata['has_parallelism']}")
            print(f"    Has Fallback: {plan.metadata['has_fallback']}")

        except CompileError as e:
            print(f"  ❌ Compilation Error: {e}")

        print()

    print("=" * 70)
    print("COMPILER DEMONSTRATION COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    demo()
