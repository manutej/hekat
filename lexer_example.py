"""Example usage of HEKAT DSL Lexer."""

from hekat_lexer import Lexer, TokenType


def example_simple_query():
    """Example: Simple agent invocation."""
    print("Example 1: Simple Query")
    print("-" * 40)

    dsl = 'api-architect : "design REST API"'
    print(f"Input: {dsl}\n")

    lexer = Lexer(dsl)
    tokens = lexer.tokenize()

    for token in tokens:
        print(f"{token.type.name:15} = {token.value}")
    print()


def example_sequential():
    """Example: Sequential agent pipeline."""
    print("Example 2: Sequential Pipeline")
    print("-" * 40)

    dsl = 'research -> design -> implement : "build feature"'
    print(f"Input: {dsl}\n")

    lexer = Lexer(dsl)
    tokens = lexer.tokenize()

    for token in tokens:
        print(f"{token.type.name:15} = {token.value}")
    print()


def example_parallel():
    """Example: Parallel agent execution."""
    print("Example 3: Parallel Execution")
    print("-" * 40)

    dsl = '(frontend || backend || devops) : "design system"'
    print(f"Input: {dsl}\n")

    lexer = Lexer(dsl)
    tokens = lexer.tokenize()

    for token in tokens:
        print(f"{token.type.name:15} = {token.value}")
    print()


def example_mixed():
    """Example: Mixed sequential and parallel."""
    print("Example 4: Mixed Sequential + Parallel")
    print("-" * 40)

    dsl = 'research -> (design || implement) + skill : "build app"'
    print(f"Input: {dsl}\n")

    lexer = Lexer(dsl)
    tokens = lexer.tokenize()

    for token in tokens:
        print(f"{token.type.name:15} = {token.value}")
    print()


def example_ensemble():
    """Example: Ensemble voting pattern."""
    print("Example 5: Ensemble Voting")
    print("-" * 40)

    dsl = 'sample^3 ; merge ; synthesize : "research topic"'
    print(f"Input: {dsl}\n")

    lexer = Lexer(dsl)
    tokens = lexer.tokenize()

    for token in tokens:
        print(f"{token.type.name:15} = {token.value}")
    print()


def example_fallback():
    """Example: Fallback chain."""
    print("Example 6: Fallback Chain")
    print("-" * 40)

    dsl = 'primary ? secondary ? tertiary : "complex task"'
    print(f"Input: {dsl}\n")

    lexer = Lexer(dsl)
    tokens = lexer.tokenize()

    for token in tokens:
        print(f"{token.type.name:15} = {token.value}")
    print()


def example_command():
    """Example: Command enhancement."""
    print("Example 7: Command Enhancement")
    print("-" * 40)

    dsl = '@ctx7(api-architect) : "design API"'
    print(f"Input: {dsl}\n")

    lexer = Lexer(dsl)
    tokens = lexer.tokenize()

    for token in tokens:
        print(f"{token.type.name:15} = {token.value}")
    print()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("HEKAT DSL Lexer - Example Usage")
    print("="*60 + "\n")

    example_simple_query()
    example_sequential()
    example_parallel()
    example_mixed()
    example_ensemble()
    example_fallback()
    example_command()

    print("="*60)
    print("All examples completed successfully")
    print("="*60 + "\n")
