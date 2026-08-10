"""
Hopcroft's algorithm for DFA minimization.

Uses partition refinement to find the minimal DFA.

The input DFAs are *partial*: a state may have no transition on a given symbol,
which semantically means "reject" (a transition to an implicit dead state).
Hopcroft's algorithm is only correct on a *complete* DFA, so minimization runs
against a completed view in which every (state, symbol) pair has a target -- real
transitions where they exist, and a virtual dead state everywhere else. The dead
state (and any real trap states equivalent to it) is dropped when the minimized
DFA is rebuilt, restoring the partial representation.
"""

from typing import Set, Dict, List, Tuple
from collections import deque

from .dfa import DFA

# Virtual dead/sink state used only during minimization. It is never a real
# state id (those are >= 0) and never appears in the rebuilt DFA.
_DEAD = -1


def minimize_dfa(dfa: DFA) -> DFA:
    """
    Minimize a DFA using Hopcroft's algorithm.

    The algorithm works by partition refinement:
    1. Complete the transition function with a virtual dead state so the
       algorithm's correctness assumptions hold for partial DFAs.
    2. Start with two partitions: accepting and non-accepting states.
    3. Repeatedly refine partitions by splitting states that behave differently.
    4. Rebuild the DFA from the final partition, dropping the dead block.
    """
    if not dfa.states:
        return dfa

    # Get the alphabet
    alphabet = dfa.get_alphabet()
    if not alphabet:
        # No transitions anywhere; nothing to merge beyond the trivial case.
        return _renumber_states(dfa)

    # Initial partition: accepting vs non-accepting states. The virtual dead
    # state is non-accepting; keeping it in the partition is what makes the
    # refinement distinguish states that differ only by a missing transition.
    accepting = frozenset(set(dfa.accept_states) & set(dfa.states))
    non_accepting = frozenset((set(dfa.states) - set(dfa.accept_states)) | {_DEAD})

    # P is the current partition (set of blocks)
    P: Set[frozenset] = set()
    if accepting:
        P.add(accepting)
    P.add(non_accepting)  # always non-empty (contains the dead state)

    if len(P) <= 1:
        # No accepting states at all (empty language); nothing to refine.
        return _renumber_states(dfa)

    # W is the worklist of blocks to process
    W: deque = deque()

    # Start with the smaller of accepting/non-accepting
    if len(accepting) <= len(non_accepting):
        W.append(accepting)
    else:
        W.append(non_accepting)

    # Build reverse transition map over the *completed* transition function:
    # (target, char) -> set of source states, with missing transitions and the
    # dead state routed to _DEAD.
    reverse: Dict[Tuple[int, int], Set[int]] = {}
    for state_id, state in dfa.states.items():
        transitions = state.transitions
        for char in alphabet:
            key = (transitions.get(char, _DEAD), char)
            if key not in reverse:
                reverse[key] = set()
            reverse[key].add(state_id)
    for char in alphabet:
        key = (_DEAD, char)
        if key not in reverse:
            reverse[key] = set()
        reverse[key].add(_DEAD)

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
    """Build a new DFA from the partition, dropping the dead block."""
    new_dfa = DFA()

    # Identify the block containing the virtual dead state (and any real trap
    # states equivalent to it). It must not appear in the output.
    dead_block = None
    state_to_block: Dict[int, frozenset] = {}
    for block in partition:
        if _DEAD in block:
            dead_block = block
        for state in block:
            state_to_block[state] = block

    # Map each surviving block to a new state id
    block_to_id: Dict[frozenset, int] = {}

    # Find the start block and create it first
    start_block = state_to_block.get(old_dfa.start)
    if start_block is not None and start_block is not dead_block:
        is_accept = any(s in old_dfa.accept_states for s in start_block)
        start_id = new_dfa.new_state(is_accept)
        new_dfa.start = start_id
        block_to_id[start_block] = start_id

    # Create remaining states
    for block in partition:
        if block is dead_block or block in block_to_id:
            continue
        is_accept = any(s in old_dfa.accept_states for s in block)
        block_to_id[block] = new_dfa.new_state(is_accept)

    # Add transitions (use a real representative state from each block)
    for block in partition:
        if block is dead_block:
            continue
        new_state_id = block_to_id[block]
        rep = next((s for s in block if s in old_dfa.states), None)
        if rep is None:
            continue
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

        # Enqueue neighbors in ascending input-character order. Ordering by the
        # transition label (rather than by target id) makes the numbering a
        # canonical function of the automaton's structure, so it is independent
        # of the order states happened to be created during construction.
        if old_id in dfa.states:
            transitions = dfa.states[old_id].transitions
            for char in sorted(transitions):
                target = transitions[char]
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
