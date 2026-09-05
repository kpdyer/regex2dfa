"""Cached conversion and lazy access to the regex-to-DFA pipeline."""

from functools import cached_property, lru_cache

from .parser import parse_regex, Token
from .thompson import build_nfa
from .subset import nfa_to_dfa
from .hopcroft import minimize_dfa
from .formatter import format_att
from .nfa import NFA
from .dfa import DFA


@lru_cache(maxsize=1024)
def regex2dfa(regex: str) -> str:
    """Convert a regex to AT&T FST text, caching up to 1,024 results.

    Example:
        >>> regex2dfa("a")
        '0\\t1\\t97\\t97\\n1'
    """
    return Regex2DFA(regex).to_att()


def clear_cache() -> None:
    """Clear the regex2dfa result cache and its statistics."""
    regex2dfa.cache_clear()


def cache_info():
    """Return cache statistics: hits, misses, maxsize and currsize."""
    return regex2dfa.cache_info()


class Regex2DFA:
    """Lazily build and retain each conversion stage for a regex."""

    def __init__(self, regex: str):
        self.regex = regex

    @cached_property
    def postfix(self) -> list[Token]:
        """Postfix tokens, including an empty list for an empty pattern."""
        return parse_regex(self.regex)

    @cached_property
    def nfa(self) -> NFA:
        """NFA built with Thompson's construction."""
        return build_nfa(self.postfix)

    @cached_property
    def dfa(self) -> DFA:
        """DFA before minimization."""
        return nfa_to_dfa(self.nfa)

    @cached_property
    def minimized_dfa(self) -> DFA:
        """DFA minimized with Hopcroft's algorithm."""
        return minimize_dfa(self.dfa)

    def to_att(self) -> str:
        """Return the minimized DFA as AT&T FST text."""
        return format_att(self.minimized_dfa)

    def __str__(self) -> str:
        return self.to_att()
