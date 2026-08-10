"""
Subset construction - converts NFA to DFA using the powerset method.
"""

from collections import deque
from typing import Dict, FrozenSet, Set

from .nfa import NFA, EPSILON
from .dfa import DFA


def nfa_to_dfa(nfa: NFA) -> DFA:
    """
    Convert an NFA to a DFA using subset construction.

    Each DFA state represents a set of NFA states.
    We use BFS to explore all reachable DFA states.
    """
    dfa = DFA()
    nfa_states = nfa.states
    accept = nfa.accept
    closure = nfa.epsilon_closure

    # Map from frozen set of NFA states to DFA state id
    state_map: Dict[FrozenSet[int], int] = {}

    # Start with epsilon closure of NFA start state
    start_set = frozenset(closure({nfa.start}))

    start_id = dfa.new_state(accept in start_set)
    dfa.start = start_id
    state_map[start_set] = start_id

    # BFS to explore all reachable DFA states
    worklist: deque = deque((start_set,))

    while worklist:
        current_set = worklist.popleft()
        current_id = state_map[current_set]

        # Gather every non-epsilon transition out of the states in this set in a
        # single pass, grouped by character. This visits only characters that
        # actually occur, instead of scanning the whole alphabet per state.
        moves: Dict[int, Set[int]] = {}
        for state in current_set:
            st = nfa_states.get(state)
            if st is None:
                continue
            for char, targets in st.transitions.items():
                if char == EPSILON:
                    continue
                group = moves.get(char)
                if group is None:
                    moves[char] = set(targets)
                else:
                    group |= targets

        for char, move_set in moves.items():
            # Take epsilon closure of the move set to form the next DFA state.
            next_set = frozenset(closure(move_set))

            # Check if this DFA state already exists
            next_id = state_map.get(next_set)
            if next_id is None:
                next_id = dfa.new_state(accept in next_set)
                state_map[next_set] = next_id
                worklist.append(next_set)

            # Add transition
            dfa.add_transition(current_id, char, next_id)

    return dfa
