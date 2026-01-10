"""
regex2dfa - Convert regular expressions to minimized DFAs in AT&T FST format.

Pure Python implementation with zero dependencies.
Results are cached in memory for fast repeated lookups.
"""

from .core import regex2dfa, Regex2DFA, clear_cache, cache_info
from .parser import parse_regex, RegexError
from .thompson import build_nfa
from .subset import nfa_to_dfa
from .hopcroft import minimize_dfa
from .formatter import format_att

__version__ = "0.2.1"
__all__ = [
    "regex2dfa",
    "Regex2DFA",
    "RegexError",
    "clear_cache",
    "cache_info",
    "parse_regex",
    "build_nfa",
    "nfa_to_dfa",
    "minimize_dfa",
    "format_att",
]
