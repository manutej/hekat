"""Hekat DSL Lexer - Tokenization of DSL source code.

Converts source code strings into streams of tokens for parsing.

Example:
    >>> from hekat.compiler.lexer import Lexer
    >>> source = 'api-architect : "design REST API"'
    >>> lexer = Lexer(source)
    >>> tokens = lexer.tokenize()
    >>> assert len(tokens) == 4
    >>> assert tokens[0].type == TokenType.IDENTIFIER
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class TokenType(Enum):
    """Token types for Hekat DSL."""

    # Operators
    SEQUENTIAL = "->"
    PARALLEL = "||"
    COMBINATION = "+"
    SPECIFICATION = ":"
    QUESTION = "?"
    STAR = "*"
    RETRY = "⟲"

    # Grouping
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"

    # Literals
    IDENTIFIER = "identifier"
    AGENT_LITERAL = "/agent"
    STRING = "string"
    NUMBER = "number"

    # Keywords
    WORKFLOW = "workflow"
    IF = "if"
    ELSE = "else"
    THEN = "then"
    WHILE = "while"
    FOR = "for"
    IN = "in"
    RETURN = "return"

    # Special
    COMMA = ","
    DOT = "."
    EQUALS = "="
    EOF = "EOF"


@dataclass
class Token:
    """Represents a lexical token with location information."""

    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


class LexerError(Exception):
    """Exception raised for lexical errors."""

    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer error at {line}:{column}: {message}")


class Lexer:
    """Lexical analyzer for Hekat DSL.

    Converts source code into a stream of tokens.

    Attributes:
        source: The source code string
        pos: Current position in source
        line: Current line number (1-indexed)
        column: Current column number (1-indexed)

    Example:
        >>> lexer = Lexer("a -> b")
        >>> tokens = lexer.tokenize()
        >>> assert tokens[0].type == TokenType.IDENTIFIER
        >>> assert tokens[1].type == TokenType.SEQUENTIAL
    """

    KEYWORDS = {
        "workflow": TokenType.WORKFLOW,
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "then": TokenType.THEN,
        "while": TokenType.WHILE,
        "for": TokenType.FOR,
        "in": TokenType.IN,
        "return": TokenType.RETURN,
    }

    def __init__(self, source: str):
        """Initialize the lexer with source code.

        Args:
            source: The DSL source code to tokenize
        """
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1

    def is_eof(self) -> bool:
        """Check if at end of source."""
        return self.pos >= len(self.source)

    def peek(self, offset: int = 0) -> Optional[str]:
        """Look ahead in source without consuming.

        Args:
            offset: How many characters ahead to look (default: 0)

        Returns:
            The character at pos+offset, or None if past end
        """
        pos = self.pos + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]

    def advance(self) -> str:
        """Consume and return next character, updating position."""
        if self.is_eof():
            raise LexerError("Unexpected end of input", self.line, self.column)

        char = self.source[self.pos]
        self.pos += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def skip_whitespace(self) -> None:
        """Skip whitespace characters (spaces, tabs, newlines)."""
        while not self.is_eof() and self.peek() in " \t\n\r":
            self.advance()

    def skip_comment(self) -> None:
        """Skip single-line comments starting with #."""
        if self.peek() == "#":
            while not self.is_eof() and self.peek() != "\n":
                self.advance()
            if not self.is_eof():
                self.advance()  # Skip the newline

    def skip_whitespace_and_comments(self) -> None:
        """Skip all whitespace and comments."""
        while not self.is_eof():
            if self.peek() in " \t\n\r":
                self.skip_whitespace()
            elif self.peek() == "#":
                self.skip_comment()
            else:
                break

    def identifier_or_keyword(self) -> Token:
        """Parse identifier or keyword.

        Identifiers: letter (letter | digit | '-' | '_')*
        Keywords: workflow, if, else, etc.

        Returns:
            Token with type IDENTIFIER or keyword type
        """
        start_line = self.line
        start_column = self.column
        value = ""

        # First character must be letter or underscore
        if self.peek() and (self.peek().isalpha() or self.peek() == "_"):
            value += self.advance()
        else:
            raise LexerError(
                f"Invalid identifier start: {self.peek()!r}",
                self.line,
                self.column
            )

        # Subsequent characters: letter, digit, hyphen, underscore
        while not self.is_eof():
            char = self.peek()
            if char and (char.isalnum() or char in "-_"):
                value += self.advance()
            else:
                break

        # Check if keyword
        token_type = self.KEYWORDS.get(value, TokenType.IDENTIFIER)

        return Token(token_type, value, start_line, start_column)

    def agent_literal(self) -> Token:
        """Parse agent literal starting with /.

        Format: /identifier

        Returns:
            Token with type AGENT_LITERAL
        """
        start_line = self.line
        start_column = self.column

        # Consume the /
        value = self.advance()

        # Must be followed by identifier characters
        if not self.peek() or not (self.peek().isalpha() or self.peek() == "_"):
            raise LexerError(
                "Agent literal must start with letter after /",
                self.line,
                self.column
            )

        while not self.is_eof():
            char = self.peek()
            if char and (char.isalnum() or char in "-_"):
                value += self.advance()
            else:
                break

        return Token(TokenType.AGENT_LITERAL, value, start_line, start_column)

    def string_literal(self) -> Token:
        """Parse string literal enclosed in quotes.

        Supports both " and ' quotes.
        Handles escape sequences: \\n, \\t, \\", \\'

        Returns:
            Token with type STRING
        """
        start_line = self.line
        start_column = self.column

        # Get opening quote
        quote = self.advance()
        assert quote in "\"'", f"Expected quote, got {quote!r}"

        value = ""

        while not self.is_eof():
            char = self.peek()

            if char == quote:
                # Closing quote
                self.advance()
                break
            elif char == "\\":
                # Escape sequence
                self.advance()
                if self.is_eof():
                    raise LexerError("Unterminated string", self.line, self.column)

                escape_char = self.advance()
                if escape_char == "n":
                    value += "\n"
                elif escape_char == "t":
                    value += "\t"
                elif escape_char == "r":
                    value += "\r"
                elif escape_char == "\\":
                    value += "\\"
                elif escape_char in "\"'":
                    value += escape_char
                else:
                    value += escape_char  # Unknown escape, keep as-is
            elif char == "\n":
                raise LexerError("Unterminated string (newline)", self.line, self.column)
            else:
                value += self.advance()
        else:
            raise LexerError("Unterminated string (EOF)", start_line, start_column)

        return Token(TokenType.STRING, value, start_line, start_column)

    def number_literal(self) -> Token:
        """Parse number literal (integer or float).

        Format: digit+ ('.' digit+)?

        Returns:
            Token with type NUMBER
        """
        start_line = self.line
        start_column = self.column
        value = ""

        # Integer part
        while not self.is_eof() and self.peek() and self.peek().isdigit():
            value += self.advance()

        # Fractional part
        if not self.is_eof() and self.peek() == ".":
            # Look ahead to ensure it's followed by digit
            if self.peek(1) and self.peek(1).isdigit():
                value += self.advance()  # .
                while not self.is_eof() and self.peek() and self.peek().isdigit():
                    value += self.advance()

        return Token(TokenType.NUMBER, value, start_line, start_column)

    def operator(self) -> Token:
        """Parse operator token.

        Handles both single-char and multi-char operators.

        Returns:
            Token with appropriate operator type
        """
        start_line = self.line
        start_column = self.column
        char = self.peek()

        # Multi-character operators
        if char == "-" and self.peek(1) == ">":
            value = self.advance() + self.advance()
            return Token(TokenType.SEQUENTIAL, value, start_line, start_column)

        if char == "|" and self.peek(1) == "|":
            value = self.advance() + self.advance()
            return Token(TokenType.PARALLEL, value, start_line, start_column)

        # Single-character operators
        if char == "+":
            return Token(TokenType.COMBINATION, self.advance(), start_line, start_column)
        if char == ":":
            return Token(TokenType.SPECIFICATION, self.advance(), start_line, start_column)
        if char == "?":
            return Token(TokenType.QUESTION, self.advance(), start_line, start_column)
        if char == "*":
            return Token(TokenType.STAR, self.advance(), start_line, start_column)
        if char == "⟲":
            return Token(TokenType.RETRY, self.advance(), start_line, start_column)
        if char == "(":
            return Token(TokenType.LPAREN, self.advance(), start_line, start_column)
        if char == ")":
            return Token(TokenType.RPAREN, self.advance(), start_line, start_column)
        if char == "{":
            return Token(TokenType.LBRACE, self.advance(), start_line, start_column)
        if char == "}":
            return Token(TokenType.RBRACE, self.advance(), start_line, start_column)
        if char == "[":
            return Token(TokenType.LBRACKET, self.advance(), start_line, start_column)
        if char == "]":
            return Token(TokenType.RBRACKET, self.advance(), start_line, start_column)
        if char == ",":
            return Token(TokenType.COMMA, self.advance(), start_line, start_column)
        if char == ".":
            return Token(TokenType.DOT, self.advance(), start_line, start_column)
        if char == "=":
            return Token(TokenType.EQUALS, self.advance(), start_line, start_column)

        raise LexerError(f"Unexpected character: {char!r}", self.line, self.column)

    def next_token(self) -> Token:
        """Get next token from source.

        Returns:
            The next token, or EOF token if at end
        """
        self.skip_whitespace_and_comments()

        if self.is_eof():
            return Token(TokenType.EOF, "", self.line, self.column)

        char = self.peek()

        # Agent literal
        if char == "/":
            return self.agent_literal()

        # String literal
        if char in "\"'":
            return self.string_literal()

        # Number literal
        if char and char.isdigit():
            return self.number_literal()

        # Identifier or keyword
        if char and (char.isalpha() or char == "_"):
            return self.identifier_or_keyword()

        # Operator or grouping
        return self.operator()

    def tokenize(self) -> List[Token]:
        """Tokenize entire source code.

        Returns:
            List of all tokens (excluding EOF)
        """
        tokens: List[Token] = []

        while not self.is_eof():
            token = self.next_token()
            if token.type == TokenType.EOF:
                break
            tokens.append(token)

        return tokens
