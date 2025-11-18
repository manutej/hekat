"""Standalone test runner for HEKAT DSL Lexer (no pytest required)."""

from hekat_lexer import Lexer, Token, TokenType, LexerError


def test_token_types():
    """Test individual token type recognition."""
    print("Testing token types...")

    tests = [
        ("api-architect", TokenType.IDENTIFIER, "api-architect"),
        (":", TokenType.COLON, ":"),
        ("+", TokenType.PLUS, "+"),
        ("->", TokenType.ARROW, "->"),
        ("||", TokenType.PIPE, "||"),
        ("?", TokenType.QUESTION, "?"),
        (";", TokenType.SEMICOLON, ";"),
        ("^", TokenType.CARET, "^"),
        ("(", TokenType.LPAREN, "("),
        (")", TokenType.RPAREN, ")"),
        ("@", TokenType.AT, "@"),
        ('"design API"', TokenType.STRING, "design API"),
        ("'build feature'", TokenType.STRING, "build feature"),
        ("42", TokenType.NUMBER, 42),
    ]

    for input_str, expected_type, expected_value in tests:
        lexer = Lexer(input_str)
        tokens = lexer.tokenize()
        assert tokens[0].type == expected_type, f"Failed: {input_str}"
        assert tokens[0].value == expected_value, f"Failed value: {input_str}"

    print("✓ All token type tests passed")


def test_multi_token_sequences():
    """Test parsing multi-token sequences."""
    print("Testing multi-token sequences...")

    # Simple query
    lexer = Lexer('api-architect : "design API"')
    tokens = lexer.tokenize()
    assert len(tokens) == 4
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[1].type == TokenType.COLON
    assert tokens[2].type == TokenType.STRING
    assert tokens[3].type == TokenType.EOF

    # Sequential
    lexer = Lexer("research -> design -> implement")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[1].type == TokenType.ARROW
    assert tokens[2].type == TokenType.IDENTIFIER
    assert tokens[3].type == TokenType.ARROW

    # Parallel
    lexer = Lexer("(frontend || backend || devops)")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.LPAREN
    assert tokens[2].type == TokenType.PIPE
    assert tokens[6].type == TokenType.RPAREN

    # Skills
    lexer = Lexer("programmer + pytest + tdd")
    tokens = lexer.tokenize()
    assert tokens[1].type == TokenType.PLUS
    assert tokens[3].type == TokenType.PLUS

    # Ensemble
    lexer = Lexer("sample^3 ; merge ; synthesize")
    tokens = lexer.tokenize()
    assert tokens[1].type == TokenType.CARET
    assert tokens[2].type == TokenType.NUMBER
    assert tokens[2].value == 3

    # Fallback
    lexer = Lexer("primary ? secondary ? tertiary")
    tokens = lexer.tokenize()
    assert tokens[1].type == TokenType.QUESTION
    assert tokens[3].type == TokenType.QUESTION

    # Command
    lexer = Lexer("@ctx7")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.AT
    assert tokens[1].value == "ctx7"

    print("✓ All multi-token sequence tests passed")


def test_edge_cases():
    """Test edge cases."""
    print("Testing edge cases...")

    # Nested parentheses
    lexer = Lexer("(a -> (b || c))")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.LPAREN
    assert tokens[3].type == TokenType.LPAREN
    assert tokens[7].type == TokenType.RPAREN
    assert tokens[8].type == TokenType.RPAREN

    # Escaped quotes
    lexer = Lexer(r'"text with \"quotes\" inside"')
    tokens = lexer.tokenize()
    assert tokens[0].value == 'text with "quotes" inside'

    # Whitespace handling
    lexer = Lexer("  agent  ->  another  ")
    tokens = lexer.tokenize()
    assert len(tokens) == 4
    assert tokens[0].value == "agent"
    assert tokens[2].value == "another"

    # Complex query
    lexer = Lexer('research -> (design || implement) + skill : "build feature"')
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[1].type == TokenType.ARROW
    assert tokens[2].type == TokenType.LPAREN
    assert tokens[4].type == TokenType.PIPE
    assert tokens[6].type == TokenType.RPAREN
    assert tokens[7].type == TokenType.PLUS
    assert tokens[9].type == TokenType.COLON
    assert tokens[10].type == TokenType.STRING

    # Empty string
    lexer = Lexer('""')
    tokens = lexer.tokenize()
    assert tokens[0].value == ""

    # Number in identifier
    lexer = Lexer("agent2")
    tokens = lexer.tokenize()
    assert tokens[0].value == "agent2"

    # Escape sequences
    lexer = Lexer(r'"line1\nline2\ttabbed"')
    tokens = lexer.tokenize()
    assert tokens[0].value == "line1\nline2\ttabbed"

    print("✓ All edge case tests passed")


def test_error_handling():
    """Test error conditions."""
    print("Testing error handling...")

    # Unterminated string
    try:
        lexer = Lexer('"unterminated string')
        lexer.tokenize()
        assert False, "Should have raised LexerError"
    except LexerError as e:
        assert "Unterminated string" in str(e)

    # Invalid character
    try:
        lexer = Lexer("agent $ invalid")
        lexer.tokenize()
        assert False, "Should have raised LexerError"
    except LexerError as e:
        assert "Unexpected character" in str(e)
        assert e.position == 6

    print("✓ All error handling tests passed")


def test_eof_handling():
    """Test EOF token generation."""
    print("Testing EOF handling...")

    # EOF always present
    lexer = Lexer("agent")
    tokens = lexer.tokenize()
    assert tokens[-1].type == TokenType.EOF

    # EOF only for empty input
    lexer = Lexer("")
    tokens = lexer.tokenize()
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF

    print("✓ All EOF tests passed")


def run_all_tests():
    """Run all test suites."""
    print("\n" + "="*60)
    print("HEKAT DSL Lexer Test Suite")
    print("="*60 + "\n")

    test_token_types()
    test_multi_token_sequences()
    test_edge_cases()
    test_error_handling()
    test_eof_handling()

    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
