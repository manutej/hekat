"""Comprehensive tests for Hekat DSL Lexer.

Tests cover:
- Token types (operators, literals, keywords)
- Whitespace and comment handling
- Line and column tracking
- Error cases
- All 6 complexity levels
"""

import pytest
from hekat.compiler.lexer import Lexer, Token, TokenType, LexerError


class TestBasicTokenization:
    """Test basic tokenization of simple expressions."""

    def test_single_identifier(self):
        """Test parsing single identifier."""
        lexer = Lexer("agent")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "agent"
        assert tokens[0].line == 1
        assert tokens[0].column == 1

    def test_identifier_with_hyphen(self):
        """Test identifier with hyphens."""
        lexer = Lexer("api-architect")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "api-architect"

    def test_identifier_with_underscore(self):
        """Test identifier with underscores."""
        lexer = Lexer("deep_researcher")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "deep_researcher"

    def test_identifier_with_numbers(self):
        """Test identifier with numbers."""
        lexer = Lexer("agent123")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "agent123"


class TestOperators:
    """Test all DSL operators."""

    def test_sequential_operator(self):
        """Test -> operator."""
        lexer = Lexer("a -> b")
        tokens = lexer.tokenize()
        assert len(tokens) == 3
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[1].type == TokenType.SEQUENTIAL
        assert tokens[1].value == "->"
        assert tokens[2].type == TokenType.IDENTIFIER

    def test_parallel_operator(self):
        """Test || operator."""
        lexer = Lexer("a || b")
        tokens = lexer.tokenize()
        assert len(tokens) == 3
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[1].type == TokenType.PARALLEL
        assert tokens[1].value == "||"
        assert tokens[2].type == TokenType.IDENTIFIER

    def test_combination_operator(self):
        """Test + operator."""
        lexer = Lexer("a + b")
        tokens = lexer.tokenize()
        assert len(tokens) == 3
        assert tokens[1].type == TokenType.COMBINATION
        assert tokens[1].value == "+"

    def test_specification_operator(self):
        """Test : operator."""
        lexer = Lexer('a : "task"')
        tokens = lexer.tokenize()
        assert len(tokens) == 3
        assert tokens[1].type == TokenType.SPECIFICATION
        assert tokens[1].value == ":"

    def test_question_operator(self):
        """Test ? operator for conditionals."""
        lexer = Lexer("a ? b")
        tokens = lexer.tokenize()
        assert tokens[1].type == TokenType.QUESTION

    def test_star_operator(self):
        """Test * operator for iteration."""
        lexer = Lexer("a * 3")
        tokens = lexer.tokenize()
        assert tokens[1].type == TokenType.STAR

    def test_retry_operator(self):
        """Test ⟲ operator for retry."""
        lexer = Lexer("a ⟲ b")
        tokens = lexer.tokenize()
        assert tokens[1].type == TokenType.RETRY


class TestAgentLiterals:
    """Test agent literal tokenization."""

    def test_agent_literal_simple(self):
        """Test simple agent literal."""
        lexer = Lexer("/ctx7")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.AGENT_LITERAL
        assert tokens[0].value == "/ctx7"

    def test_agent_literal_with_hyphen(self):
        """Test agent literal with hyphen."""
        lexer = Lexer("/deep-researcher")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.AGENT_LITERAL
        assert tokens[0].value == "/deep-researcher"

    def test_agent_literal_with_underscore(self):
        """Test agent literal with underscore."""
        lexer = Lexer("/meta_skill_builder")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.AGENT_LITERAL
        assert tokens[0].value == "/meta_skill_builder"

    def test_multiple_agent_literals(self):
        """Test expression with multiple agent literals."""
        lexer = Lexer("/deep || /ctx7")
        tokens = lexer.tokenize()
        assert len(tokens) == 3
        assert tokens[0].type == TokenType.AGENT_LITERAL
        assert tokens[0].value == "/deep"
        assert tokens[1].type == TokenType.PARALLEL
        assert tokens[2].type == TokenType.AGENT_LITERAL
        assert tokens[2].value == "/ctx7"

    def test_agent_literal_invalid_start(self):
        """Test agent literal must start with letter."""
        lexer = Lexer("/123")
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        assert "must start with letter" in str(exc_info.value)


class TestStringLiterals:
    """Test string literal tokenization."""

    def test_string_double_quotes(self):
        """Test string with double quotes."""
        lexer = Lexer('"hello world"')
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello world"

    def test_string_single_quotes(self):
        """Test string with single quotes."""
        lexer = Lexer("'hello world'")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello world"

    def test_string_escape_sequences(self):
        """Test escape sequences in strings."""
        lexer = Lexer(r'"hello\nworld\ttab"')
        tokens = lexer.tokenize()
        assert tokens[0].value == "hello\nworld\ttab"

    def test_string_escaped_quotes(self):
        """Test escaped quotes in strings."""
        lexer = Lexer(r'"say \"hello\""')
        tokens = lexer.tokenize()
        assert tokens[0].value == 'say "hello"'

    def test_string_empty(self):
        """Test empty string."""
        lexer = Lexer('""')
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].value == ""

    def test_string_unterminated(self):
        """Test unterminated string raises error."""
        lexer = Lexer('"hello')
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        assert "Unterminated string" in str(exc_info.value)

    def test_string_with_newline(self):
        """Test string cannot contain unescaped newline."""
        lexer = Lexer('"hello\nworld"')
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        assert "Unterminated string (newline)" in str(exc_info.value)


class TestNumberLiterals:
    """Test number literal tokenization."""

    def test_integer(self):
        """Test integer number."""
        lexer = Lexer("123")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "123"

    def test_float(self):
        """Test floating point number."""
        lexer = Lexer("123.456")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "123.456"

    def test_float_leading_zero(self):
        """Test float with leading zero."""
        lexer = Lexer("0.5")
        tokens = lexer.tokenize()
        assert tokens[0].value == "0.5"

    def test_number_in_expression(self):
        """Test number in arithmetic expression."""
        lexer = Lexer("a * 3")
        tokens = lexer.tokenize()
        assert len(tokens) == 3
        assert tokens[2].type == TokenType.NUMBER
        assert tokens[2].value == "3"


class TestKeywords:
    """Test keyword tokenization."""

    def test_workflow_keyword(self):
        """Test 'workflow' keyword."""
        lexer = Lexer("workflow")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.WORKFLOW

    def test_if_keyword(self):
        """Test 'if' keyword."""
        lexer = Lexer("if")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IF

    def test_else_keyword(self):
        """Test 'else' keyword."""
        lexer = Lexer("else")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.ELSE

    def test_keyword_vs_identifier(self):
        """Test keywords are distinct from identifiers."""
        lexer = Lexer("workflow_name")
        tokens = lexer.tokenize()
        # Should be identifier, not keyword
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "workflow_name"


class TestGrouping:
    """Test grouping characters."""

    def test_parentheses(self):
        """Test ( and ) tokens."""
        lexer = Lexer("(a || b)")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.LPAREN
        assert tokens[4].type == TokenType.RPAREN

    def test_braces(self):
        """Test { and } tokens."""
        lexer = Lexer("{a}")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.LBRACE
        assert tokens[2].type == TokenType.RBRACE

    def test_brackets(self):
        """Test [ and ] tokens."""
        lexer = Lexer("[a, b]")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.LBRACKET
        assert tokens[4].type == TokenType.RBRACKET


class TestWhitespaceAndComments:
    """Test whitespace and comment handling."""

    def test_whitespace_ignored(self):
        """Test whitespace between tokens is ignored."""
        lexer = Lexer("a    ->    b")
        tokens = lexer.tokenize()
        assert len(tokens) == 3

    def test_newlines_ignored(self):
        """Test newlines are ignored."""
        lexer = Lexer("a\n->\nb")
        tokens = lexer.tokenize()
        assert len(tokens) == 3

    def test_tabs_ignored(self):
        """Test tabs are ignored."""
        lexer = Lexer("a\t->\tb")
        tokens = lexer.tokenize()
        assert len(tokens) == 3

    def test_comment_single_line(self):
        """Test single-line comment."""
        lexer = Lexer("a # this is a comment\nb")
        tokens = lexer.tokenize()
        assert len(tokens) == 2
        assert tokens[0].value == "a"
        assert tokens[1].value == "b"

    def test_comment_at_start(self):
        """Test comment at start of line."""
        lexer = Lexer("# comment\na -> b")
        tokens = lexer.tokenize()
        assert len(tokens) == 3

    def test_comment_at_end(self):
        """Test comment at end of source."""
        lexer = Lexer("a -> b # final comment")
        tokens = lexer.tokenize()
        assert len(tokens) == 3


class TestLocationTracking:
    """Test line and column tracking."""

    def test_single_line_columns(self):
        """Test column tracking on single line."""
        lexer = Lexer("a -> b")
        tokens = lexer.tokenize()
        assert tokens[0].column == 1  # 'a' at column 1
        assert tokens[1].column == 3  # '->' at column 3
        assert tokens[2].column == 6  # 'b' at column 6

    def test_multiline_tracking(self):
        """Test line and column tracking across lines."""
        lexer = Lexer("a\n->\nb")
        tokens = lexer.tokenize()
        assert tokens[0].line == 1
        assert tokens[1].line == 2
        assert tokens[2].line == 3

    def test_error_location(self):
        """Test error includes correct location."""
        lexer = Lexer("a\n@")  # @ is invalid
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        assert exc_info.value.line == 2
        assert exc_info.value.column == 1


class TestComplexExpressions:
    """Test tokenization of complex real-world expressions."""

    def test_level_1_basic(self):
        """Test Level 1: Basic invocation."""
        source = 'api-architect : "design REST API"'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        assert len(tokens) == 3
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[1].type == TokenType.SPECIFICATION
        assert tokens[2].type == TokenType.STRING

    def test_level_2_sequential(self):
        """Test Level 2: Sequential composition."""
        source = "research -> design -> implement"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        assert len(tokens) == 5
        assert all(tokens[i].type == TokenType.SEQUENTIAL for i in [1, 3])

    def test_level_2_parallel(self):
        """Test Level 2: Parallel composition."""
        source = "frontend || backend"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        assert len(tokens) == 3
        assert tokens[1].type == TokenType.PARALLEL

    def test_level_2_combination(self):
        """Test Level 2: Combination."""
        source = "agent + skill1 + skill2"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        assert len(tokens) == 5
        assert tokens[1].type == TokenType.COMBINATION
        assert tokens[3].type == TokenType.COMBINATION

    def test_level_3_complex(self):
        """Test Level 3: Complex parallel streams."""
        source = '(/deep + /ctx7 || /orch /wflw) : "DSL design"'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        # Should successfully tokenize complex expression
        assert len(tokens) > 5
        assert any(t.type == TokenType.AGENT_LITERAL for t in tokens)
        assert any(t.type == TokenType.PARALLEL for t in tokens)
        assert any(t.type == TokenType.SPECIFICATION for t in tokens)

    def test_level_3_with_grouping(self):
        """Test Level 3: Grouping with parentheses."""
        source = "(a || b) -> (c + d)"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.LPAREN
        assert tokens[4].type == TokenType.RPAREN
        assert tokens[5].type == TokenType.SEQUENTIAL

    def test_all_operators_together(self):
        """Test expression with all operators."""
        source = "(a + b) -> (c || d) : 'task'"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        # Should have all operator types
        operator_types = {t.type for t in tokens}
        assert TokenType.COMBINATION in operator_types
        assert TokenType.SEQUENTIAL in operator_types
        assert TokenType.PARALLEL in operator_types
        assert TokenType.SPECIFICATION in operator_types


class TestErrorCases:
    """Test error handling."""

    def test_unexpected_character(self):
        """Test unexpected character raises error."""
        lexer = Lexer("a @ b")
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        assert "Unexpected character" in str(exc_info.value)

    def test_unterminated_string_eof(self):
        """Test unterminated string at EOF."""
        lexer = Lexer('"unterminated')
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        assert "Unterminated string (EOF)" in str(exc_info.value)

    def test_error_message_format(self):
        """Test error messages have proper format."""
        lexer = Lexer("@")
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        # Should include line and column
        assert "1:1" in str(exc_info.value)


class TestEdgeCases:
    """Test edge cases and corner scenarios."""

    def test_empty_source(self):
        """Test empty source code."""
        lexer = Lexer("")
        tokens = lexer.tokenize()
        assert len(tokens) == 0

    def test_only_whitespace(self):
        """Test source with only whitespace."""
        lexer = Lexer("   \n\t  \n  ")
        tokens = lexer.tokenize()
        assert len(tokens) == 0

    def test_only_comments(self):
        """Test source with only comments."""
        lexer = Lexer("# comment 1\n# comment 2")
        tokens = lexer.tokenize()
        assert len(tokens) == 0

    def test_unicode_retry_operator(self):
        """Test Unicode retry operator ⟲."""
        lexer = Lexer("a ⟲ b")
        tokens = lexer.tokenize()
        assert tokens[1].type == TokenType.RETRY

    def test_very_long_identifier(self):
        """Test very long identifier."""
        long_name = "a" * 100
        lexer = Lexer(long_name)
        tokens = lexer.tokenize()
        assert tokens[0].value == long_name

    def test_dot_after_number_identifier(self):
        """Test dot after number creates separate tokens."""
        lexer = Lexer("123.abc")
        tokens = lexer.tokenize()
        # Should be: number, dot, identifier
        assert len(tokens) == 3
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[1].type == TokenType.DOT
        assert tokens[2].type == TokenType.IDENTIFIER


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
