"""Tests for HEKAT Parser Phase 2A - Sequential & Parallel Patterns."""

import pytest
from hekat_parser import (
    Parser, QueryNode, SimpleNode, SequentialNode, ParallelNode,
    ParseError, parse
)
from hekat_lexer import Lexer, TokenType


class TestSimplePattern:
    """Test Type 1: Simple agent invocation."""

    def test_simple_agent(self):
        """agent : \"prompt\" """
        result = parse('agent : "prompt"')
        assert isinstance(result, QueryNode)
        assert isinstance(result.expression, SimpleNode)
        assert result.expression.agent == 'agent'
        assert result.prompt == 'prompt'

    def test_simple_hyphenated_agent(self):
        """api-architect : \"design API\" """
        result = parse('api-architect : "design API"')
        assert result.expression.agent == 'api-architect'
        assert result.prompt == 'design API'


class TestSequentialPattern:
    """Test Type 2: Sequential composition."""

    def test_sequential_two_agents(self):
        """A → B : \"prompt\" """
        result = parse('A -> B : "prompt"')
        assert isinstance(result.expression, SequentialNode)
        assert len(result.expression.expressions) == 2
        assert result.expression.expressions[0].agent == 'A'
        assert result.expression.expressions[1].agent == 'B'
        assert result.prompt == 'prompt'

    def test_sequential_three_agents(self):
        """X → Y → Z : \"task\" """
        result = parse('X -> Y -> Z : "task"')
        assert isinstance(result.expression, SequentialNode)
        assert len(result.expression.expressions) == 3
        assert result.expression.expressions[0].agent == 'X'
        assert result.expression.expressions[1].agent == 'Y'
        assert result.expression.expressions[2].agent == 'Z'
        assert result.prompt == 'task'

    def test_sequential_left_associative(self):
        """A → B → C parses as left-associative chain."""
        result = parse('A -> B -> C : "test"')
        assert isinstance(result.expression, SequentialNode)
        # All expressions in flat list (left-associative)
        assert len(result.expression.expressions) == 3


class TestParallelPattern:
    """Test Type 3: Parallel composition."""

    def test_parallel_two_agents(self):
        """(A || B) : \"task\" """
        result = parse('(A || B) : "task"')
        assert isinstance(result.expression, ParallelNode)
        assert len(result.expression.expressions) == 2
        assert result.expression.expressions[0].agent == 'A'
        assert result.expression.expressions[1].agent == 'B'
        assert result.prompt == 'task'

    def test_parallel_three_agents(self):
        """(A || B || C) : \"prompt\" """
        result = parse('(A || B || C) : "prompt"')
        assert isinstance(result.expression, ParallelNode)
        assert len(result.expression.expressions) == 3
        assert result.expression.expressions[0].agent == 'A'
        assert result.expression.expressions[1].agent == 'B'
        assert result.expression.expressions[2].agent == 'C'

    def test_parallel_with_hyphens(self):
        """(api-architect || deep-researcher || test-engineer) : \"evaluate\" """
        result = parse('(api-architect || deep-researcher || test-engineer) : "evaluate"')
        assert isinstance(result.expression, ParallelNode)
        assert len(result.expression.expressions) == 3
        assert result.expression.expressions[0].agent == 'api-architect'
        assert result.expression.expressions[1].agent == 'deep-researcher'
        assert result.expression.expressions[2].agent == 'test-engineer'


class TestErrorHandling:
    """Test error cases."""

    def test_missing_colon(self):
        """agent \"prompt\" - missing colon raises error."""
        with pytest.raises(ParseError) as exc:
            parse('agent "prompt"')
        assert "Expected COLON" in str(exc.value)

    def test_unmatched_lparen(self):
        """(A || B : \"task\" - missing closing paren."""
        with pytest.raises(ParseError) as exc:
            parse('(A || B : "task"')
        assert "Expected RPAREN" in str(exc.value)

    def test_unmatched_rparen(self):
        """A || B) : \"task\" - unexpected closing paren."""
        with pytest.raises(ParseError) as exc:
            parse('A || B) : "task"')
        assert "Expected COLON" in str(exc.value)

    def test_empty_parallel(self):
        """(A) : \"task\" - single expression in parens requires ||."""
        with pytest.raises(ParseError) as exc:
            parse('(A) : "task"')
        assert "at least 2 expressions" in str(exc.value)

    def test_single_pipe(self):
        """(A | B) : \"task\" - single pipe instead of double."""
        from hekat_lexer import LexerError
        with pytest.raises(LexerError) as exc:
            parse('(A | B) : "task"')
        assert "Unexpected character '|'" in str(exc.value)

    def test_missing_prompt(self):
        """agent : - missing prompt string."""
        with pytest.raises(ParseError) as exc:
            parse('agent :')
        assert "Expected STRING" in str(exc.value)


class TestIntegrationWithLexer:
    """Test end-to-end: string → tokens → AST."""

    def test_sequential_integration(self):
        """End-to-end: \"agent → agent : \\\"prompt\\\"\" """
        input_text = 'researcher -> architect : "build API"'

        # Lexer phase
        lexer = Lexer(input_text)
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == 'researcher'
        assert tokens[1].type == TokenType.ARROW
        assert tokens[2].type == TokenType.IDENTIFIER
        assert tokens[2].value == 'architect'
        assert tokens[3].type == TokenType.COLON
        assert tokens[4].type == TokenType.STRING
        assert tokens[4].value == 'build API'

        # Parser phase
        parser = Parser(tokens)
        result = parser.parse()
        assert isinstance(result.expression, SequentialNode)
        assert len(result.expression.expressions) == 2
        assert result.prompt == 'build API'

    def test_parallel_integration(self):
        """End-to-end: parallel with real agent names."""
        input_text = '(api-architect || test-engineer) : "evaluate framework"'

        result = parse(input_text)
        assert isinstance(result.expression, ParallelNode)
        assert len(result.expression.expressions) == 2
        assert result.expression.expressions[0].agent == 'api-architect'
        assert result.expression.expressions[1].agent == 'test-engineer'
        assert result.prompt == 'evaluate framework'


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_whitespace_tolerance(self):
        """Parser handles extra whitespace."""
        result = parse('  A   ->   B   :   "task"  ')
        assert isinstance(result.expression, SequentialNode)
        assert result.prompt == 'task'

    def test_single_char_agents(self):
        """Single character agent names."""
        result = parse('A -> B -> C : "test"')
        assert len(result.expression.expressions) == 3

    def test_long_agent_names(self):
        """Long hyphenated agent names."""
        result = parse('very-long-agent-name -> another-agent : "task"')
        assert result.expression.expressions[0].agent == 'very-long-agent-name'
        assert result.expression.expressions[1].agent == 'another-agent'
