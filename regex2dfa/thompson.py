"""
Thompson's construction - builds an NFA from postfix regex tokens.
"""

from typing import List
from dataclasses import dataclass

from .parser import Token, TokenType
from .nfa import NFA


@dataclass
class NFAFragment:
    """A fragment of an NFA with a start and accept state."""
    start: int
    accept: int


def build_nfa(postfix: List[Token]) -> NFA:
    """
    Build an NFA from postfix tokens using Thompson's construction.
    
    Each regex operator creates a small NFA fragment, and these
    fragments are combined according to the postfix expression.
    """
    nfa = NFA()
    stack: List[NFAFragment] = []
    
    for token in postfix:
        if token.type == TokenType.LITERAL:
            # Create states for literal match
            start = nfa.new_state()
            accept = nfa.new_state()
            
            # Add transitions for each character in the set
            for char in token.chars:
                nfa.add_transition(start, char, accept)
            
            stack.append(NFAFragment(start, accept))
        
        elif token.type == TokenType.CONCAT:
            # Concatenation: connect two fragments
            if len(stack) < 2:
                continue
            frag2 = stack.pop()
            frag1 = stack.pop()
            
            # Connect frag1's accept to frag2's start via epsilon
            nfa.add_epsilon(frag1.accept, frag2.start)
            
            stack.append(NFAFragment(frag1.start, frag2.accept))
        
        elif token.type == TokenType.ALTERNATION:
            # Alternation: create new start/accept with epsilon branches
            if len(stack) < 2:
                continue
            frag2 = stack.pop()
            frag1 = stack.pop()
            
            start = nfa.new_state()
            accept = nfa.new_state()
            
            # Epsilon from new start to both fragment starts
            nfa.add_epsilon(start, frag1.start)
            nfa.add_epsilon(start, frag2.start)
            
            # Epsilon from both fragment accepts to new accept
            nfa.add_epsilon(frag1.accept, accept)
            nfa.add_epsilon(frag2.accept, accept)
            
            stack.append(NFAFragment(start, accept))
        
        elif token.type in {TokenType.STAR, TokenType.PLUS, TokenType.QUESTION}:
            if not stack:
                continue
            frag = stack.pop()
            
            start = nfa.new_state()
            accept = nfa.new_state()
            
            nfa.add_epsilon(start, frag.start)
            nfa.add_epsilon(frag.accept, accept)

            # Star and optional can skip; star and plus can loop.
            if token.type != TokenType.PLUS:
                nfa.add_epsilon(start, accept)
            if token.type != TokenType.QUESTION:
                nfa.add_epsilon(frag.accept, frag.start)
            
            stack.append(NFAFragment(start, accept))
    
    # The final fragment is the complete NFA
    if stack:
        final = stack.pop()
        nfa.start = final.start
        nfa.accept = final.accept
    else:
        # Empty regex: create accepting start state
        start = nfa.new_state()
        nfa.start = start
        nfa.accept = start
    
    return nfa
