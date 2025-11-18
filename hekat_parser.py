"""HEKAT DSL Parser - Recursive Descent Parser for All 8 Query Patterns."""

from dataclasses import dataclass
from typing import List
from hekat_lexer import Token, TokenType, Lexer


# AST Node Classes
@dataclass
class ExpressionNode:
    """Base class for expression nodes."""
    pass


@dataclass
class SimpleNode(ExpressionNode):
    """Simple agent invocation: agent"""
    name: str


@dataclass
class SequentialNode(ExpressionNode):
    """Sequential composition: A → B → C"""
    steps: List[ExpressionNode]


@dataclass
class ParallelNode(ExpressionNode):
    """Parallel composition: (A || B || C)"""
    branches: List[ExpressionNode]


@dataclass
class FallbackNode(ExpressionNode):
    """Fallback chain: A ? B ? C"""
    alternatives: List[ExpressionNode]


@dataclass
class EnsembleNode(ExpressionNode):
    """Ensemble pattern: sample^3 ; merge ; synthesize"""
    base: str
    count: int
    merge_step: str
    synth_step: str


@dataclass
class CommandedNode(ExpressionNode):
    """Commanded pattern: @ctx7(agent)"""
    command: str
    agents: List[str]


@dataclass
class SkilledNode(ExpressionNode):
    """Skilled pattern: agent + skill1 + skill2"""
    agent: str
    skills: List[str]


@dataclass
class QueryNode:
    """Complete query: expression : "prompt" """
    expression: ExpressionNode
    prompt: str


class ParseError(Exception):
    """Parser error with position context."""
    def __init__(self, message: str, token: Token):
        self.token = token
        super().__init__(f"{message} at position {token.position} (got {token.type.value})")


class Parser:
    """Recursive descent parser for HEKAT DSL."""

    def __init__(self, tokens: List[Token]):
        """Initialize parser with token stream."""
        self.tokens = tokens
        self.position = 0

    def parse(self) -> QueryNode:
        """Parse complete query: <expression> : <string>"""
        expression = self._expression()
        self._expect(TokenType.COLON)
        prompt_token = self._expect(TokenType.STRING)
        self._expect(TokenType.EOF)
        return QueryNode(expression=expression, prompt=prompt_token.value)

    def _expression(self) -> ExpressionNode:
        """Parse expression: <fallback>"""
        return self._fallback()

    def _fallback(self) -> ExpressionNode:
        """Parse fallback: <sequential> (QUESTION <sequential>)*"""
        alternatives = [self._sequential()]

        while self._current().type == TokenType.QUESTION:
            self._advance()
            alternatives.append(self._sequential())

        if len(alternatives) == 1:
            return alternatives[0]
        return FallbackNode(alternatives=alternatives)

    def _sequential(self) -> ExpressionNode:
        """Parse sequential: <parallel_or_atom> (ARROW <parallel_or_atom>)*"""
        steps = [self._parallel_or_atom()]

        while self._current().type == TokenType.ARROW:
            self._advance()
            steps.append(self._parallel_or_atom())

        if len(steps) == 1:
            return steps[0]
        return SequentialNode(steps=steps)

    def _parallel_or_atom(self) -> ExpressionNode:
        """Parse parallel or atom."""
        if self._current().type == TokenType.LPAREN:
            return self._parallel()
        return self._atom()

    def _parallel(self) -> ParallelNode:
        """Parse parallel: LPAREN <sequential> (PIPE <sequential>)+ RPAREN"""
        self._expect(TokenType.LPAREN)

        branches = [self._sequential()]

        if self._current().type != TokenType.PIPE:
            raise ParseError(
                "Parallel expression requires at least 2 branches separated by ||",
                self._current()
            )

        while self._current().type == TokenType.PIPE:
            self._advance()
            branches.append(self._sequential())

        self._expect(TokenType.RPAREN)
        return ParallelNode(branches=branches)

    def _atom(self) -> ExpressionNode:
        """Parse atom: <ensemble> | <commanded> | <skilled> | <simple>"""
        current = self._current()

        # Commanded: @command(...)
        if current.type == TokenType.AT:
            return self._commanded()

        # Need lookahead for ensemble and skilled
        if current.type == TokenType.IDENTIFIER:
            next_token = self._peek()

            # Ensemble: identifier^number;...
            if next_token and next_token.type == TokenType.CARET:
                return self._ensemble()

            # Skilled: agent+skill+...
            if next_token and next_token.type == TokenType.PLUS:
                return self._skilled()

        # Simple: agent or identifier
        return self._simple()

    def _ensemble(self) -> EnsembleNode:
        """Parse ensemble: IDENTIFIER CARET NUMBER SEMICOLON IDENTIFIER SEMICOLON IDENTIFIER"""
        base_token = self._expect(TokenType.IDENTIFIER)
        self._expect(TokenType.CARET)
        count_token = self._expect(TokenType.NUMBER)

        if count_token.value < 1 or count_token.value > 10:
            raise ParseError(
                f"Ensemble count must be between 1 and 10 (got {count_token.value})",
                count_token
            )

        self._expect(TokenType.SEMICOLON)
        merge_token = self._expect(TokenType.IDENTIFIER)
        self._expect(TokenType.SEMICOLON)
        synth_token = self._expect(TokenType.IDENTIFIER)

        return EnsembleNode(
            base=base_token.value,
            count=count_token.value,
            merge_step=merge_token.value,
            synth_step=synth_token.value
        )

    def _commanded(self) -> CommandedNode:
        """Parse commanded: AT IDENTIFIER LPAREN <agent_list> RPAREN"""
        self._expect(TokenType.AT)
        command_token = self._expect(TokenType.IDENTIFIER)
        self._expect(TokenType.LPAREN)

        agents = self._agent_list()

        if not agents:
            raise ParseError(
                "Commanded pattern requires at least one agent",
                self._current()
            )

        self._expect(TokenType.RPAREN)
        return CommandedNode(command=command_token.value, agents=agents)

    def _agent_list(self) -> List[str]:
        """Parse agent list: IDENTIFIER (COMMA IDENTIFIER)*"""
        # Handle empty list
        if self._current().type == TokenType.RPAREN:
            return []

        agents = [self._expect(TokenType.IDENTIFIER).value]

        # Parse additional agents separated by commas
        # Note: Lexer doesn't have COMMA token - using current grammar
        # For now, assume single agent (can extend if comma is added to lexer)

        return agents

    def _skilled(self) -> SkilledNode:
        """Parse skilled: IDENTIFIER (PLUS IDENTIFIER)+"""
        agent_token = self._expect(TokenType.IDENTIFIER)

        skills = []
        while self._current().type == TokenType.PLUS:
            self._advance()
            skill_token = self._expect(TokenType.IDENTIFIER)
            skills.append(skill_token.value)

        if not skills:
            raise ParseError(
                "Skilled pattern requires at least one skill",
                self._current()
            )

        return SkilledNode(agent=agent_token.value, skills=skills)

    def _simple(self) -> SimpleNode:
        """Parse simple: IDENTIFIER"""
        token = self._expect(TokenType.IDENTIFIER)
        return SimpleNode(name=token.value)

    def _current(self) -> Token:
        """Get current token."""
        return self.tokens[self.position]

    def _peek(self, offset: int = 1) -> Token:
        """Peek ahead at token."""
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def _advance(self) -> None:
        """Move to next token."""
        if self.position < len(self.tokens) - 1:
            self.position += 1

    def _expect(self, token_type: TokenType) -> Token:
        """Consume and return token of expected type, or raise error."""
        token = self._current()
        if token.type != token_type:
            raise ParseError(f"Expected {token_type.value}", token)
        self._advance()
        return token


def parse(input_text: str) -> QueryNode:
    """Convenience function: tokenize and parse input string."""
    lexer = Lexer(input_text)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()
