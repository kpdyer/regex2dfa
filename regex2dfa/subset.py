"""
Subset construction - converts NFA to DFA using the powerset method.
"""

from typing import Set, Dict, FrozenSet

from .nfa import NFA, EPSILON
from .dfa import DFA


def nfa_to_dfa(nfa: NFA) -> DFA:
    """
    Convert an NFA to a DFA using subset construction.
    
    Each DFA state represents a set of NFA states.
    We use BFS to explore all reachable DFA states.
    """
    dfa = DFA()
    
    # Map from frozen set of NFA states to DFA state id
    state_map: Dict[FrozenSet[int], int] = {}
    
    # Get all characters used in the NFA (excluding epsilon)
    alphabet: Set[int] = set()
    for state in nfa.states.values():
        for char in state.transitions.keys():
            if char != EPSILON:
                alphabet.add(char)
    
    # Start with epsilon closure of NFA start state
    start_set = frozenset(nfa.epsilon_closure({nfa.start}))
    is_accept = nfa.accept in start_set
    
    start_id = dfa.new_state(is_accept)
    dfa.start = start_id
    state_map[start_set] = start_id
    
    # BFS to explore all reachable DFA states
    worklist = [start_set]
    
    while worklist:
        current_set = worklist.pop(0)
        current_id = state_map[current_set]
        
        # For each character in the alphabet
        for char in alphabet:
            # Compute the set of NFA states reachable on this character
            move_set = nfa.move(current_set, char)
            if not move_set:
                continue
            
            # Take epsilon closure
            next_set = frozenset(nfa.epsilon_closure(move_set))
            
            # Check if this DFA state already exists
            if next_set not in state_map:
                is_accept = nfa.accept in next_set
                next_id = dfa.new_state(is_accept)
                state_map[next_set] = next_id
                worklist.append(next_set)
            else:
                next_id = state_map[next_set]
            
            # Add transition
            dfa.add_transition(current_id, char, next_id)
    
    return dfa
