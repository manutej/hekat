"""Comprehensive test suite for HEKAT DSL Lexer."""

import pytest
from hekat_lexer import Lexer, Token, TokenType, LexerError


class TestTokenTypes:
    """Test individual token type recognition."""

    def test_identifier(self):
        lexer = Lexer("api-architect")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "api-architect"

    def test_colon(self):
        lexer = Lexer(":")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.COLON

    def test_plus(self):
        lexer = Lexer("+")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.PLUS

    def test_arrow(self):
        lexer = Lexer("->")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.ARROW
        assert tokens[0].value == "->"

    def test_pipe(self):
        lexer = Lexer("||")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.PIPE
        assert tokens[0].value == "||"

    def test_question(self):
        lexer = Lexer("?")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.QUESTION

    def test_semicolon(self):
        lexer = Lexer(";")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.SEMICOLON

    def test_caret(self):
        lexer = Lexer("^")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.CARET

    def test_lparen(self):
        lexer = Lexer("(")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.LPAREN

    def test_rparen(self):
        lexer = Lexer(")")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.RPAREN

    def test_at(self):
        lexer = Lexer("@")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.AT

    def test_string_double_quotes(self):
        lexer = Lexer('"design API"')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "design API"

    def test_string_single_quotes(self):
        lexer = Lexer("'build feature'")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "build feature"

    def test_number(self):
        lexer = Lexer("42")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 42


class TestMultiTokenSequences:
    """Test parsing multi-token sequences."""

    def test_simple_query(self):
        lexer = Lexer('api-architect : "design API"')
        tokens = lexer.tokenize()
        assert len(tokens) == 4  # IDENTIFIER, COLON, STRING, EOF
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "api-architect"
        assert tokens[1].type == TokenType.COLON
        assert tokens[2].type == TokenType.STRING
        assert tokens[2].value == "design API"
        assert tokens[3].type == TokenType.EOF

    def test_sequential_agents(self):
        lexer = Lexer("research -> design -> implement")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "research"
        assert tokens[1].type == TokenType.ARROW
        assert tokens[2].type == TokenType.IDENTIFIER
        assert tokens[2].value == "design"
        assert tokens[3].type == TokenType.ARROW
        assert tokens[4].type == TokenType.IDENTIFIER
        assert tokens[4].value == "implement"

    def test_parallel_agents(self):
        lexer = Lexer("(frontend || backend || devops)")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.LPAREN
        assert tokens[1].type == TokenType.IDENTIFIER
        assert tokens[2].type == TokenType.PIPE
        assert tokens[3].type == TokenType.IDENTIFIER
        assert tokens[4].type == TokenType.PIPE
        assert tokens[5].type == TokenType.IDENTIFIER
        assert tokens[6].type == TokenType.RPAREN

    def test_agent_with_skills(self):
        lexer = Lexer("programmer + pytest + tdd")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[1].type == TokenType.PLUS
        assert tokens[2].type == TokenType.IDENTIFIER
        assert tokens[3].type == TokenType.PLUS
        assert tokens[4].type == TokenType.IDENTIFIER

    def test_ensemble_pattern(self):
        lexer = Lexer("sample^3 ; merge ; synthesize")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER  # sample
        assert tokens[1].type == TokenType.CARET
        assert tokens[2].type == TokenType.NUMBER
        assert tokens[2].value == 3
        assert tokens[3].type == TokenType.SEMICOLON
        assert tokens[4].type == TokenType.IDENTIFIER  # merge

    def test_fallback_chain(self):
        lexer = Lexer("primary ? secondary ? tertiary")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[1].type == TokenType.QUESTION
        assert tokens[2].type == TokenType.IDENTIFIER
        assert tokens[3].type == TokenType.QUESTION
        assert tokens[4].type == TokenType.IDENTIFIER

    def test_command_pattern(self):
        lexer = Lexer("@ctx7")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.AT
        assert tokens[1].type == TokenType.IDENTIFIER
        assert tokens[1].value == "ctx7"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_nested_parentheses(self):
        lexer = Lexer("(a -> (b || c))")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.LPAREN
        assert tokens[4].type == TokenType.LPAREN
        assert tokens[8].type == TokenType.RPAREN
        assert tokens[9].type == TokenType.RPAREN

    def test_escaped_quotes_in_string(self):
        lexer = Lexer(r'"text with \"quotes\" inside"')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == 'text with "quotes" inside'

    def test_escaped_backslash(self):
        lexer = Lexer(r'"path\\to\\file"')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == r"path\to\file"

    def test_whitespace_handling(self):
        lexer = Lexer("  agent  ->  another  ")
        tokens = lexer.tokenize()
        assert len(tokens) == 4  # IDENTIFIER, ARROW, IDENTIFIER, EOF
        assert tokens[0].value == "agent"
        assert tokens[2].value == "another"

    def test_multiline_input(self):
        lexer = Lexer("research ->\ndesign ->\nimple ment")
        tokens = lexer.tokenize()
        assert tokens[0].value == "research"
        assert tokens[2].value == "design"
        assert tokens[4].value == "implement"

    def test_complex_query(self):
        lexer = Lexer('research -> (design || implement) + skill : "build feature"')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER  # research
        assert tokens[1].type == TokenType.ARROW
        assert tokens[2].type == TokenType.LPAREN
        assert tokens[3].type == TokenType.IDENTIFIER  # design
        assert tokens[4].type == TokenType.PIPE
        assert tokens[5].type == TokenType.IDENTIFIER  # implement
        assert tokens[6].type == TokenType.RPAREN
        assert tokens[7].type == TokenType.PLUS
        assert tokens[8].type == TokenType.IDENTIFIER  # skill
        assert tokens[9].type == TokenType.COLON
        assert tokens[10].type == TokenType.STRING

    def test_empty_string(self):
        lexer = Lexer('""')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == ""

    def test_number_in_identifier(self):
        lexer = Lexer("agent2")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "agent2"


class TestErrorHandling:
    """Test error conditions."""

    def test_unterminated_string(self):
        with pytest.raises(LexerError) as exc_info:
            lexer = Lexer('"unterminated string')
            lexer.tokenize()
        assert "Unterminated string" in str(exc_info.value)

    def test_invalid_character(self):
        with pytest.raises(LexerError) as exc_info:
            lexer = Lexer("agent $ invalid")
            lexer.tokenize()
        assert "Unexpected character" in str(exc_info.value)

    def test_error_position_tracking(self):
        try:
            lexer = Lexer("valid $ invalid")
            lexer.tokenize()
        except LexerError as e:
            assert e.position == 6  # Position of '$'

    def test_escape_sequences_in_string(self):
        lexer = Lexer(r'"line1\nline2\ttabbed"')
        tokens = lexer.tokenize()
        assert tokens[0].value == "line1\nline2\ttabbed"


class TestEOFHandling:
    """Test EOF token generation."""

    def test_eof_always_present(self):
        lexer = Lexer("agent")
        tokens = lexer.tokenize()
        assert tokens[-1].type == TokenType.EOF

    def test_eof_only_for_empty_input(self):
        lexer = Lexer("")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
