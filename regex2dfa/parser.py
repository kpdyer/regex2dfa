"""
Regex parser - tokenizes and converts to postfix notation.

Uses the shunting-yard algorithm to handle operator precedence.
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Set


class RegexError(Exception):
    """Exception raised for invalid regex syntax."""
    pass


class TokenType(Enum):
    LITERAL = auto()      # Single character or character class
    STAR = auto()         # *
    PLUS = auto()         # +
    QUESTION = auto()     # ?
    ALTERNATION = auto()  # |
    CONCAT = auto()       # Implicit concatenation
    LPAREN = auto()       # (
    RPAREN = auto()       # )


@dataclass
class Token:
    type: TokenType
    chars: Set[int] = field(default_factory=set)  # For LITERAL: characters that match


class RegexParser:
    """Parses a regex string into postfix tokens."""
    
    def __init__(self, regex: str):
        self.regex = regex
        self.pos = 0
    
    def peek(self) -> str:
        return self.regex[self.pos] if self.pos < len(self.regex) else '\0'
    
    def advance(self) -> str:
        if self.pos < len(self.regex):
            c = self.regex[self.pos]
            self.pos += 1
            return c
        return '\0'
    
    def is_at_end(self) -> bool:
        return self.pos >= len(self.regex)
    
    def parse(self) -> List[Token]:
        """Parse regex and return postfix token list."""
        infix = self._tokenize()
        infix = self._insert_concat_operators(infix)
        return self._to_postfix(infix)
    
    def _parse_char_class(self) -> Set[int]:
        """Parse a character class [...]."""
        start_pos = self.pos - 1  # Position of '['
        chars: Set[int] = set()
        negated = False
        
        if self.peek() == '^':
            negated = True
            self.advance()
        
        while not self.is_at_end() and self.peek() != ']':
            c = ord(self.advance())
            
            # Check for range a-z
            if self.peek() == '-' and self.pos + 1 < len(self.regex) and self.regex[self.pos + 1] != ']':
                self.advance()  # consume '-'
                end = ord(self.advance())
                if end < c:
                    raise RegexError(f"Invalid character range [{chr(c)}-{chr(end)}]: start > end")
                for i in range(c, end + 1):
                    chars.add(i)
            else:
                chars.add(c)
        
        if self.is_at_end():
            raise RegexError(f"Unclosed character class at position {start_pos}")
        
        self.advance()  # consume ']'
        
        if negated:
            all_chars = set(range(256))
            chars = all_chars - chars
        
        return chars
    
    def _parse_escape(self) -> Token:
        """Parse an escape sequence."""
        token = Token(TokenType.LITERAL)
        c = self.advance()
        
        if c == 'n':
            token.chars.add(ord('\n'))
        elif c == 'r':
            token.chars.add(ord('\r'))
        elif c == 't':
            token.chars.add(ord('\t'))
        elif c == '0':
            token.chars.add(0)
        elif c == 'x':
            # Hex escape \xNN
            hex_str = ''
            if not self.is_at_end():
                hex_str += self.advance()
            if not self.is_at_end():
                hex_str += self.advance()
            token.chars.add(int(hex_str, 16) if hex_str else 0)
        elif c == 'C':
            # Any byte
            token.chars = set(range(256))
        elif c == 'd':
            # Digits
            token.chars = set(range(ord('0'), ord('9') + 1))
        elif c == 'w':
            # Word characters
            token.chars = set(range(ord('a'), ord('z') + 1))
            token.chars |= set(range(ord('A'), ord('Z') + 1))
            token.chars |= set(range(ord('0'), ord('9') + 1))
            token.chars.add(ord('_'))
        elif c == 's':
            # Whitespace
            token.chars = {ord(' '), ord('\t'), ord('\n'), ord('\r')}
        else:
            # Escaped literal
            token.chars.add(ord(c))
        
        return token
    
    def _tokenize(self) -> List[Token]:
        """Convert regex string to token list."""
        tokens: List[Token] = []
        paren_depth = 0
        paren_positions: List[int] = []
        
        while not self.is_at_end():
            pos = self.pos
            c = self.advance()
            token = Token(TokenType.LITERAL)
            
            if c == '^' or c == '$':
                # Skip anchors (implicit in our matching)
                continue
            elif c == '(':
                paren_depth += 1
                paren_positions.append(pos)
                token = Token(TokenType.LPAREN)
            elif c == ')':
                if paren_depth == 0:
                    raise RegexError(f"Unmatched ')' at position {pos}")
                paren_depth -= 1
                paren_positions.pop()
                token = Token(TokenType.RPAREN)
            elif c == '*':
                self._validate_quantifier(tokens, '*', pos)
                token = Token(TokenType.STAR)
            elif c == '+':
                self._validate_quantifier(tokens, '+', pos)
                token = Token(TokenType.PLUS)
            elif c == '?':
                self._validate_quantifier(tokens, '?', pos)
                token = Token(TokenType.QUESTION)
            elif c == '|':
                self._validate_alternation(tokens, pos)
                token = Token(TokenType.ALTERNATION)
            elif c == '.':
                # Any character (any byte 0-255)
                token = Token(TokenType.LITERAL, set(range(256)))
            elif c == '[':
                token = Token(TokenType.LITERAL, self._parse_char_class())
            elif c == '\\':
                token = self._parse_escape()
            else:
                token = Token(TokenType.LITERAL, {ord(c)})
            
            tokens.append(token)
        
        if paren_depth > 0:
            raise RegexError(f"Unclosed '(' at position {paren_positions[-1]}")
        
        # Check for trailing alternation
        if tokens and tokens[-1].type == TokenType.ALTERNATION:
            raise RegexError("Empty alternation at end of pattern")
        
        return tokens
    
    def _validate_quantifier(self, tokens: List[Token], quantifier: str, pos: int):
        """Validate that a quantifier has an operand."""
        if not tokens:
            raise RegexError(f"Quantifier '{quantifier}' at position {pos} has nothing to repeat")
        
        last = tokens[-1]
        if last.type in {TokenType.LPAREN, TokenType.ALTERNATION}:
            raise RegexError(f"Quantifier '{quantifier}' at position {pos} has nothing to repeat")
        if last.type in {TokenType.STAR, TokenType.PLUS, TokenType.QUESTION}:
            raise RegexError(f"Multiple quantifiers at position {pos}")
    
    def _validate_alternation(self, tokens: List[Token], pos: int):
        """Validate alternation has left operand."""
        if not tokens:
            raise RegexError(f"Empty alternation at position {pos}")
        
        last = tokens[-1]
        if last.type in {TokenType.LPAREN, TokenType.ALTERNATION}:
            raise RegexError(f"Empty alternation at position {pos}")
    
    def _is_operand(self, t: Token) -> bool:
        return t.type == TokenType.LITERAL
    
    def _need_concat(self, left: Token, right: Token) -> bool:
        """Check if we need to insert a concat operator between two tokens."""
        left_ok = (self._is_operand(left) or 
                   left.type in {TokenType.RPAREN, TokenType.STAR, 
                                 TokenType.PLUS, TokenType.QUESTION})
        right_ok = self._is_operand(right) or right.type == TokenType.LPAREN
        return left_ok and right_ok
    
    def _insert_concat_operators(self, tokens: List[Token]) -> List[Token]:
        """Insert explicit concatenation operators."""
        result: List[Token] = []
        for i, tok in enumerate(tokens):
            result.append(tok)
            if i + 1 < len(tokens) and self._need_concat(tok, tokens[i + 1]):
                result.append(Token(TokenType.CONCAT))
        return result
    
    def _precedence(self, token_type: TokenType) -> int:
        """Return operator precedence."""
        if token_type == TokenType.ALTERNATION:
            return 1
        elif token_type == TokenType.CONCAT:
            return 2
        elif token_type in {TokenType.STAR, TokenType.PLUS, TokenType.QUESTION}:
            return 3
        return 0
    
    def _to_postfix(self, infix: List[Token]) -> List[Token]:
        """Convert infix tokens to postfix using shunting-yard."""
        output: List[Token] = []
        ops: List[Token] = []
        
        for token in infix:
            if self._is_operand(token):
                output.append(token)
            elif token.type == TokenType.LPAREN:
                ops.append(token)
            elif token.type == TokenType.RPAREN:
                while ops and ops[-1].type != TokenType.LPAREN:
                    output.append(ops.pop())
                if ops:
                    ops.pop()  # Remove LPAREN
            else:
                # Operator
                while (ops and 
                       ops[-1].type != TokenType.LPAREN and
                       self._precedence(ops[-1].type) >= self._precedence(token.type)):
                    output.append(ops.pop())
                ops.append(token)
        
        while ops:
            output.append(ops.pop())
        
        return output


def parse_regex(regex: str) -> List[Token]:
    """Parse a regex string into postfix tokens."""
    parser = RegexParser(regex)
    return parser.parse()
