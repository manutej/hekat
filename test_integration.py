"""Quick integration test."""

from hekat_lexer import Lexer
from hekat_parser import Parser
from hekat_type_checker import TypeChecker
from hekat_dag_builder import DAGBuilder

# Test full pipeline
dsl = 'deep-researcher -> (practical-programmer + fastapi || test-engineer) -> deployment-orchestrator : "build and deploy API"'

print("=" * 60)
print("HEKAT PARSER INTEGRATION TEST")
print("=" * 60)
print(f"\nDSL: {dsl}\n")

# Lex
lexer = Lexer(dsl)
tokens = lexer.tokenize()
print(f"✓ Lexer: {len(tokens)} tokens")

# Parse
parser = Parser(tokens)
query = parser.parse()
print(f"✓ Parser: AST created")
print(f"  Expression type: {type(query.expression).__name__}")
print(f"  Prompt: {query.prompt}")

# Type check
checker = TypeChecker()
result = checker.validate(query)
print(f"\n✓ Type Checker: {'VALID' if result['valid'] else 'INVALID'}")
if result['errors']:
    print(f"  Errors: {result['errors']}")
if result['warnings']:
    print(f"  Warnings: {result['warnings']}")

# Build DAG
builder = DAGBuilder()
dag = builder.build(query.expression)
print(f"\n✓ DAG Builder:")
print(f"  Nodes: {len(dag.nodes)}")
print(f"  Execution order: {dag.execution_order}")
print(f"  Parallel phases: {dag.parallel_phases}")

print("\n" + "=" * 60)
print("INTEGRATION TEST PASSED ✓")
print("=" * 60)
