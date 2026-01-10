"""
Core API - ties all components together.

Results are cached in memory for repeated calls with the same regex.
"""

from functools import lru_cache
from typing import Optional

from .parser import parse_regex
from .thompson import build_nfa
from .subset import nfa_to_dfa
from .hopcroft import minimize_dfa
from .formatter import format_att


# Default cache size (number of regex patterns to cache)
_DEFAULT_CACHE_SIZE = 1024


@lru_cache(maxsize=_DEFAULT_CACHE_SIZE)
def regex2dfa(regex: str) -> str:
    """
    Convert a regex to a minimized DFA in AT&T FST format.
    
    Results are cached in memory - repeated calls with the same regex
    will return instantly from the cache.
    
    Args:
        regex: The regular expression to convert.
        
    Returns:
        The DFA in AT&T FST format (tab-separated transitions, then final states).
    
    Example:
        >>> regex2dfa("(a|b)+")
        '0\\t1\\t97\\t97\\n0\\t1\\t98\\t98\\n1\\t1\\t97\\t97\\n1\\t1\\t98\\t98\\n1'
    """
    # Handle empty regex
    if not regex:
        return "0"
    
    # Strip anchors if present (they're implicit)
    pattern = regex
    if pattern.startswith('^'):
        pattern = pattern[1:]
    if pattern.endswith('$'):
        pattern = pattern[:-1]
    
    # Handle empty pattern after stripping anchors
    if not pattern:
        return "0"
    
    # Pipeline: Parse → NFA → DFA → Minimize → Format
    postfix = parse_regex(pattern)
    
    if not postfix:
        return "0"
    
    nfa = build_nfa(postfix)
    dfa = nfa_to_dfa(nfa)
    min_dfa = minimize_dfa(dfa)
    
    return format_att(min_dfa)


def clear_cache() -> None:
    """Clear the regex2dfa result cache."""
    regex2dfa.cache_clear()


def cache_info():
    """
    Get cache statistics.
    
    Returns:
        Named tuple with hits, misses, maxsize, currsize.
    
    Example:
        >>> from regex2dfa import regex2dfa, cache_info
        >>> regex2dfa("a+")
        >>> regex2dfa("a+")  # cache hit
        >>> cache_info()
        CacheInfo(hits=1, misses=1, maxsize=1024, currsize=1)
    """
    return regex2dfa.cache_info()


class Regex2DFA:
    """
    Object-oriented interface to the regex2dfa converter.
    
    Allows access to intermediate representations (NFA, DFA).
    """
    
    def __init__(self, regex: str):
        self.regex = regex
        self._pattern = regex
        self._postfix = None
        self._nfa = None
        self._dfa = None
        self._min_dfa = None
        
        # Strip anchors
        if self._pattern.startswith('^'):
            self._pattern = self._pattern[1:]
        if self._pattern.endswith('$'):
            self._pattern = self._pattern[:-1]
    
    @property
    def postfix(self):
        """Get the postfix token representation."""
        if self._postfix is None and self._pattern:
            self._postfix = parse_regex(self._pattern)
        return self._postfix
    
    @property
    def nfa(self):
        """Get the NFA."""
        if self._nfa is None and self.postfix:
            self._nfa = build_nfa(self.postfix)
        return self._nfa
    
    @property
    def dfa(self):
        """Get the (non-minimized) DFA."""
        if self._dfa is None and self.nfa:
            self._dfa = nfa_to_dfa(self.nfa)
        return self._dfa
    
    @property
    def minimized_dfa(self):
        """Get the minimized DFA."""
        if self._min_dfa is None and self.dfa:
            self._min_dfa = minimize_dfa(self.dfa)
        return self._min_dfa
    
    def to_att(self) -> str:
        """Get the AT&T FST format output."""
        if not self._pattern:
            return "0"
        if self.minimized_dfa is None:
            return "0"
        return format_att(self.minimized_dfa)
    
    def __str__(self) -> str:
        return self.to_att()
