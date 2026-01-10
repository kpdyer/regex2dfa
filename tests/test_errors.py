"""Tests for error handling of invalid regex patterns."""

import pytest
from regex2dfa import regex2dfa, RegexError


class TestUnclosedDelimiters:
    """Tests for unclosed parentheses and brackets."""
    
    def test_unclosed_paren(self):
        with pytest.raises(RegexError, match="Unclosed '\\('"):
            regex2dfa("(a")
    
    def test_unclosed_paren_nested(self):
        with pytest.raises(RegexError, match="Unclosed '\\('"):
            regex2dfa("((a)")
    
    def test_unmatched_close_paren(self):
        with pytest.raises(RegexError, match="Unmatched '\\)'"):
            regex2dfa("a)")
    
    def test_unclosed_bracket(self):
        with pytest.raises(RegexError, match="Unclosed character class"):
            regex2dfa("[abc")
    
    def test_unclosed_bracket_with_escape(self):
        with pytest.raises(RegexError, match="Unclosed character class"):
            regex2dfa("[a-z")


class TestDanglingQuantifiers:
    """Tests for quantifiers with nothing to repeat."""
    
    def test_star_at_start(self):
        with pytest.raises(RegexError, match="nothing to repeat"):
            regex2dfa("*")
    
    def test_plus_at_start(self):
        with pytest.raises(RegexError, match="nothing to repeat"):
            regex2dfa("+")
    
    def test_question_at_start(self):
        with pytest.raises(RegexError, match="nothing to repeat"):
            regex2dfa("?")
    
    def test_star_after_paren(self):
        with pytest.raises(RegexError, match="nothing to repeat"):
            regex2dfa("(*)")
    
    def test_star_after_alternation(self):
        with pytest.raises(RegexError, match="nothing to repeat"):
            regex2dfa("a|*")
    
    def test_multiple_quantifiers(self):
        with pytest.raises(RegexError, match="Multiple quantifiers"):
            regex2dfa("a**")
    
    def test_multiple_quantifiers_mixed(self):
        with pytest.raises(RegexError, match="Multiple quantifiers"):
            regex2dfa("a+?")


class TestEmptyAlternation:
    """Tests for empty alternation operands."""
    
    def test_trailing_alternation(self):
        with pytest.raises(RegexError, match="Empty alternation"):
            regex2dfa("a|")
    
    def test_leading_alternation(self):
        with pytest.raises(RegexError, match="Empty alternation"):
            regex2dfa("|a")
    
    def test_double_alternation(self):
        with pytest.raises(RegexError, match="Empty alternation"):
            regex2dfa("a||b")
    
    def test_alternation_after_paren(self):
        with pytest.raises(RegexError, match="Empty alternation"):
            regex2dfa("(|a)")


class TestInvalidCharacterRanges:
    """Tests for invalid character class ranges."""
    
    def test_inverted_range(self):
        with pytest.raises(RegexError, match="Invalid character range"):
            regex2dfa("[z-a]")
    
    def test_inverted_digit_range(self):
        with pytest.raises(RegexError, match="Invalid character range"):
            regex2dfa("[9-0]")
