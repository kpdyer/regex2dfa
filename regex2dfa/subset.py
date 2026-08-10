"""
Subset construction - converts NFA to DFA using the powerset method.
"""

from collections import deque
from typing import Dict, FrozenSet

from .nfa import NFA, EPSILON
from .dfa import DFA


def nfa_to_dfa(nfa: NFA) -> DFA:
    """
    Convert an NFA to a DFA using subset construction.

    Each DFA state represents a set of NFA states. We use BFS to explore all
    reachable DFA states.

    For every DFA state we make a single pass over the transitions of its NFA
    states to build the per-character move sets, rather than re-scanning the
    whole alphabet. Characters whose move set is identical (common for ``.`` and
    wide character classes, where hundreds of bytes lead to the same target)
    share a single epsilon-closure computation.
    """
    dfa = DFA()
    nfa_states = nfa.states
    accept = nfa.accept
    epsilon_closure = nfa.epsilon_closure

    # Map from frozen set of NFA states to DFA state id.
    state_map: Dict[FrozenSet[int], int] = {}

    # Start with epsilon closure of NFA start state.
    start_set = frozenset(epsilon_closure({nfa.start}))
    start_id = dfa.new_state(accept in start_set)
    dfa.start = start_id
    state_map[start_set] = start_id

    # BFS to explore all reachable DFA states.
    worklist = deque([start_set])

    while worklist:
        current_set = worklist.popleft()
        current_id = state_map[current_set]
        current_transitions = dfa.states[current_id].transitions

        # Single pass over the current set's transitions: char -> NFA targets.
        moves: Dict[int, set] = {}
        for state in current_set:
            nfa_state = nfa_states.get(state)
            if nfa_state is None:
                continue
            for char, targets in nfa_state.transitions.items():
                if char == EPSILON:
                    continue
                bucket = moves.get(char)
                if bucket is None:
                    moves[char] = set(targets)
                else:
                    bucket |= targets

        # Group characters by identical move set so a closure is computed once
        # per distinct target set instead of once per character.
        move_cache: Dict[FrozenSet[int], int] = {}
        for char, move_set in moves.items():
            move_key = frozenset(move_set)
            next_id = move_cache.get(move_key, -1)
            if next_id == -1:
                next_set = frozenset(epsilon_closure(move_set))
                next_id = state_map.get(next_set, -1)
                if next_id == -1:
                    next_id = dfa.new_state(accept in next_set)
                    state_map[next_set] = next_id
                    worklist.append(next_set)
                move_cache[move_key] = next_id
            current_transitions[char] = next_id

    return dfa
