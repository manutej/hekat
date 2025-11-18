"""HEKAT DSL Lexer - Tokenizes DSL strings into token stream."""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    """Token types for HEKAT DSL."""
    # Identifiers
    IDENTIFIER = 'IDENTIFIER'  # agent-name, skill-name

    # Operators
    COLON = 'COLON'           # : (invocation)
    PLUS = 'PLUS'             # + (skill composition)
    ARROW = 'ARROW'           # -> (sequential)
    PIPE = 'PIPE'             # || (parallel)
    QUESTION = 'QUESTION'     # ? (fallback)
    SEMICOLON = 'SEMICOLON'   # ; (context separator)
    CARET = 'CARET'           # ^ (repetition)

    # Grouping
    LPAREN = 'LPAREN'         # (
    RPAREN = 'RPAREN'         # )

    # Literals
    STRING = 'STRING'         # "prompt text" or 'prompt text'
    NUMBER = 'NUMBER'         # 3 (for sample^3)

    # Special
    AT = 'AT'                 # @ (command marker)
    EOF = 'EOF'


@dataclass
class Token:
    """Token with type, value, and position."""
    type: TokenType
    value: any
    position: int


class LexerError(Exception):
    """Lexer error with position context."""
    def __init__(self, message: str, position: int, context: str = ""):
        self.position = position
        self.context = context
        super().__init__(f"{message} at position {position}: {context}")


class Lexer:
    """Tokenizes HEKAT DSL strings."""

    def __init__(self, input_text: str):
        """Initialize lexer with input string."""
        self.input = input_text
        self.position = 0
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        """Tokenize input string and return list of tokens."""
        while self.position < len(self.input):
            self._skip_whitespace()

            if self.position >= len(self.input):
                break

            char = self._current_char()

            # Multi-character operators (check first)
            if self._match_string('->'):
                self.tokens.append(Token(TokenType.ARROW, '->', self.position - 2))
            elif self._match_string('||'):
                self.tokens.append(Token(TokenType.PIPE, '||', self.position - 2))
            # Single-character operators
            elif char == ':':
                self.tokens.append(Token(TokenType.COLON, ':', self.position))
                self._advance()
            elif char == '+':
                self.tokens.append(Token(TokenType.PLUS, '+', self.position))
                self._advance()
            elif char == '?':
                self.tokens.append(Token(TokenType.QUESTION, '?', self.position))
                self._advance()
            elif char == ';':
                self.tokens.append(Token(TokenType.SEMICOLON, ';', self.position))
                self._advance()
            elif char == '^':
                self.tokens.append(Token(TokenType.CARET, '^', self.position))
                self._advance()
            elif char == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', self.position))
                self._advance()
            elif char == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', self.position))
                self._advance()
            elif char == '@':
                self.tokens.append(Token(TokenType.AT, '@', self.position))
                self._advance()
            # String literals
            elif char in ('"', "'"):
                self.tokens.append(self._read_string())
            # Numbers
            elif char.isdigit():
                self.tokens.append(self._read_number())
            # Identifiers (agent-name, skill-name, keywords)
            elif self._is_identifier_start(char):
                self.tokens.append(self._read_identifier())
            else:
                context = self.input[max(0, self.position-10):self.position+10]
                raise LexerError(f"Unexpected character '{char}'", self.position, context)

        self.tokens.append(Token(TokenType.EOF, None, self.position))
        return self.tokens

    def _current_char(self) -> str:
        """Get current character."""
        if self.position < len(self.input):
            return self.input[self.position]
        return ''

    def _peek_char(self, offset: int = 1) -> str:
        """Peek ahead at character."""
        pos = self.position + offset
        if pos < len(self.input):
            return self.input[pos]
        return ''

    def _advance(self) -> None:
        """Move position forward by one."""
        self.position += 1

    def _skip_whitespace(self) -> None:
        """Skip whitespace characters."""
        while self.position < len(self.input) and self.input[self.position].isspace():
            self.position += 1

    def _match_string(self, target: str) -> bool:
        """Match and consume multi-character string."""
        end_pos = self.position + len(target)
        if end_pos <= len(self.input) and self.input[self.position:end_pos] == target:
            self.position = end_pos
            return True
        return False

    def _read_string(self) -> Token:
        """Read quoted string with escape handling."""
        start_pos = self.position
        quote_char = self._current_char()
        self._advance()  # Skip opening quote

        value = []
        while self.position < len(self.input):
            char = self._current_char()

            if char == '\\':
                # Handle escape sequences
                self._advance()
                if self.position < len(self.input):
                    escaped = self._current_char()
                    if escaped == 'n':
                        value.append('\n')
                    elif escaped == 't':
                        value.append('\t')
                    elif escaped == '\\':
                        value.append('\\')
                    elif escaped in ('"', "'"):
                        value.append(escaped)
                    else:
                        value.append(escaped)
                    self._advance()
            elif char == quote_char:
                # Found closing quote
                self._advance()
                return Token(TokenType.STRING, ''.join(value), start_pos)
            else:
                value.append(char)
                self._advance()

        # Unterminated string
        context = self.input[start_pos:start_pos+20]
        raise LexerError(f"Unterminated string starting with {quote_char}", start_pos, context)

    def _read_number(self) -> Token:
        """Read numeric literal."""
        start_pos = self.position
        value = []

        while self.position < len(self.input) and self._current_char().isdigit():
            value.append(self._current_char())
            self._advance()

        return Token(TokenType.NUMBER, int(''.join(value)), start_pos)

    def _read_identifier(self) -> Token:
        """Read identifier (agent-name, skill-name, keyword)."""
        start_pos = self.position
        value = []

        while self.position < len(self.input) and self._is_identifier_char(self._current_char()):
            value.append(self._current_char())
            self._advance()

        return Token(TokenType.IDENTIFIER, ''.join(value), start_pos)

    def _is_identifier_start(self, char: str) -> bool:
        """Check if character can start an identifier."""
        return char.isalpha() or char == '_'

    def _is_identifier_char(self, char: str) -> bool:
        """Check if character can be part of an identifier."""
        return char.isalnum() or char in ('_', '-')
