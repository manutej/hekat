"""Demo: End-to-end parsing for all 8 HEKAT patterns."""

from hekat_parser import parse

print("="*70)
print("HEKAT DSL Parser - All 8 Patterns Demo")
print("="*70)

patterns = [
    ("Simple", 'api-architect : "design REST API"'),
    ("Sequential", 'deep-researcher -> api-architect -> practical-programmer : "build feature"'),
    ("Parallel", '(api-architect || deep-researcher || test-engineer) : "evaluate tech"'),
    ("Mixed", 'deep-researcher -> (api-architect || db-expert) -> practical-programmer : "design system"'),
    ("Fallback", 'deployment-orchestrator ? devops-github-expert ? practical-programmer : "deploy app"'),
    ("Ensemble", 'sample^3 ; merge ; synthesize : "research quantum computing"'),
    ("Commanded", '@ctx7(deep-researcher) : "analyze React hooks"'),
    ("Skilled", 'api-architect + fastapi + postgresql : "design user service API"'),
]

for name, query in patterns:
    print(f"\n{'─'*70}")
    print(f"Pattern {patterns.index((name, query)) + 1}: {name}")
    print(f"{'─'*70}")
    print(f"Query: {query}")
    print()

    result = parse(query)
    print(f"AST Root: {type(result).__name__}")
    print(f"Expression: {type(result.expression).__name__}")
    print(f"Prompt: {result.prompt}")

    # Show structure details
    expr = result.expression
    if hasattr(expr, 'steps'):
        print(f"Steps: {len(expr.steps)}")
    if hasattr(expr, 'branches'):
        print(f"Branches: {len(expr.branches)}")
    if hasattr(expr, 'alternatives'):
        print(f"Alternatives: {len(expr.alternatives)}")
    if hasattr(expr, 'skills'):
        print(f"Skills: {expr.skills}")
    if hasattr(expr, 'command'):
        print(f"Command: {expr.command}")
    if hasattr(expr, 'count'):
        print(f"Samples: {expr.count}")

print(f"\n{'='*70}")
print("All 8 patterns parsed successfully!")
print(f"{'='*70}")
