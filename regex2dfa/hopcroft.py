"""
Hopcroft's algorithm for DFA minimization.

Uses partition refinement to find the minimal DFA.
"""

from typing import Set, Dict, List, Tuple
from collections import deque

from .dfa import DFA, DFAState


def minimize_dfa(dfa: DFA) -> DFA:
    """
    Minimize a DFA using Hopcroft's algorithm.
    
    The algorithm works by partition refinement:
    1. Start with two partitions: accepting and non-accepting states
    2. Repeatedly refine partitions by splitting states that behave differently
    3. When no more splits are possible, each partition becomes one state
    """
    if not dfa.states:
        return dfa
    
    # Get the alphabet
    alphabet = dfa.get_alphabet()
    
    # Initial partition: accepting vs non-accepting states
    accepting = frozenset(dfa.accept_states)
    non_accepting = frozenset(set(dfa.states.keys()) - dfa.accept_states)
    
    # P is the current partition (set of blocks)
    P: Set[frozenset] = set()
    if accepting:
        P.add(accepting)
    if non_accepting:
        P.add(non_accepting)
    
    if len(P) <= 1:
        # Already minimal (all states same type)
        return _renumber_states(dfa)
    
    # W is the worklist of blocks to process
    W: deque = deque()
    
    # Start with the smaller of accepting/non-accepting
    if accepting and non_accepting:
        if len(accepting) <= len(non_accepting):
            W.append(accepting)
        else:
            W.append(non_accepting)
    elif accepting:
        W.append(accepting)
    elif non_accepting:
        W.append(non_accepting)
    
    # Build reverse transition map: (target, char) -> set of source states
    reverse: Dict[Tuple[int, int], Set[int]] = {}
    for state_id, state in dfa.states.items():
        for char, target in state.transitions.items():
            key = (target, char)
            if key not in reverse:
                reverse[key] = set()
            reverse[key].add(state_id)
    
    # Refine partitions
    while W:
        A = W.popleft()
        
        for char in alphabet:
            # X = states that transition to A on char
            X: Set[int] = set()
            for state in A:
                key = (state, char)
                if key in reverse:
                    X |= reverse[key]
            
            if not X:
                continue
            
            # Check each block in P
            new_P: Set[frozenset] = set()
            for Y in P:
                # Split Y into states in X and states not in X
                intersection = Y & X
                difference = Y - X
                
                if intersection and difference:
                    # Y needs to be split
                    new_P.add(frozenset(intersection))
                    new_P.add(frozenset(difference))
                    
                    # Update worklist
                    if Y in W:
                        W.remove(Y)
                        W.append(frozenset(intersection))
                        W.append(frozenset(difference))
                    else:
                        if len(intersection) <= len(difference):
                            W.append(frozenset(intersection))
                        else:
                            W.append(frozenset(difference))
                else:
                    new_P.add(Y)
            
            P = new_P
    
    # Build the minimized DFA
    return _build_minimized_dfa(dfa, P)


def _build_minimized_dfa(old_dfa: DFA, partition: Set[frozenset]) -> DFA:
    """Build a new DFA from the partition."""
    new_dfa = DFA()
    
    # Map old state to its partition (block)
    state_to_block: Dict[int, frozenset] = {}
    for block in partition:
        for state in block:
            state_to_block[state] = block
    
    # Map each block to a new state id
    block_to_id: Dict[frozenset, int] = {}
    
    # Find the start block and create it first
    start_block = state_to_block.get(old_dfa.start)
    if start_block is not None:
        is_accept = any(s in old_dfa.accept_states for s in start_block)
        start_id = new_dfa.new_state(is_accept)
        new_dfa.start = start_id
        block_to_id[start_block] = start_id
    
    # Create remaining states
    for block in partition:
        if block not in block_to_id:
            is_accept = any(s in old_dfa.accept_states for s in block)
            block_to_id[block] = new_dfa.new_state(is_accept)
    
    # Add transitions (use any representative state from each block)
    for block in partition:
        rep = next(iter(block))  # Representative state
        new_state_id = block_to_id[block]
        
        if rep in old_dfa.states:
            for char, target in old_dfa.states[rep].transitions.items():
                target_block = state_to_block.get(target)
                if target_block is not None and target_block in block_to_id:
                    new_dfa.add_transition(new_state_id, char, block_to_id[target_block])
    
    return _renumber_states(new_dfa)


def _renumber_states(dfa: DFA) -> DFA:
    """
    Renumber states so that start = 0 and states are numbered in BFS order.
    """
    if not dfa.states:
        return dfa
    
    new_dfa = DFA()
    old_to_new: Dict[int, int] = {}
    
    # BFS from start state
    visited = set()
    queue = deque([dfa.start])
    
    while queue:
        old_id = queue.popleft()
        if old_id in visited:
            continue
        visited.add(old_id)
        
        # Assign new ID
        is_accept = old_id in dfa.accept_states
        new_id = new_dfa.new_state(is_accept)
        old_to_new[old_id] = new_id
        
        if old_id == dfa.start:
            new_dfa.start = new_id
        
        # Add neighbors to queue (sorted for deterministic order)
        if old_id in dfa.states:
            targets = sorted(set(dfa.states[old_id].transitions.values()))
            for target in targets:
                if target not in visited:
                    queue.append(target)
    
    # Add transitions with new IDs
    for old_id in visited:
        if old_id in dfa.states:
            new_id = old_to_new[old_id]
            for char, target in dfa.states[old_id].transitions.items():
                if target in old_to_new:
                    new_dfa.add_transition(new_id, char, old_to_new[target])
    
    return new_dfa
