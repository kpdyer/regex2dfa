"""Tests for Python API (caching, OOP interface)."""

import pytest
from regex2dfa import regex2dfa, Regex2DFA, clear_cache, cache_info


class TestCaching:
    """Tests for result caching."""
    
    def test_cache_hit(self):
        """Second call hits cache."""
        clear_cache()
        
        regex2dfa("(x|y)+")
        info1 = cache_info()
        assert info1.misses == 1
        assert info1.hits == 0
        
        regex2dfa("(x|y)+")
        info2 = cache_info()
        assert info2.hits == 1
    
    def test_cache_same_result(self):
        """Cached result matches original."""
        clear_cache()
        
        result1 = regex2dfa("a+")
        result2 = regex2dfa("a+")
        
        assert result1 == result2
    
    def test_clear_cache(self):
        """clear_cache() works."""
        clear_cache()
        
        regex2dfa("test")
        assert cache_info().currsize >= 1
        
        clear_cache()
        assert cache_info().currsize == 0


class TestOOPInterface:
    """Tests for Regex2DFA class."""
    
    def test_to_att(self):
        """to_att() returns expected output."""
        converter = Regex2DFA("a")
        assert converter.to_att() == "0\t1\t97\t97\n1"
    
    def test_str(self):
        """__str__ returns to_att()."""
        converter = Regex2DFA("a|b")
        assert str(converter) == converter.to_att()
    
    def test_nfa_states(self):
        """NFA has expected number of states."""
        converter = Regex2DFA("a")
        assert len(converter.nfa.states) == 2
    
    def test_empty(self):
        """Empty regex."""
        converter = Regex2DFA("")
        assert converter.to_att() == "0"
