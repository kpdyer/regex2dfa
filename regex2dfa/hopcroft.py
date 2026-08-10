"""
Hopcroft's algorithm for DFA minimization.

Uses partition refinement to find the minimal DFA.

The input DFAs are *partial*: a state may have no transition on a given symbol,
which semantically means "reject" (a transition to an implicit dead state).
Hopcroft's algorithm is only correct on a *complete* DFA, so minimization is run
against a completed view in which every (state, symbol) pair has a target -- real
transitions where they exist, and a virtual dead state everywhere else. The dead
state (and any real trap states that turn out to be equivalent to it) is dropped
when the minimized DFA is rebuilt, restoring the partial representation.
"""

from typing import Dict, List, Set, Tuple
from collections import defaultdict, deque

from .dfa import DFA

# Virtual dead/sink state used only during minimization. It is never a real
# state id (those are >= 0) and never appears in the rebuilt DFA.
_DEAD = -1


def minimize_dfa(dfa: DFA) -> DFA:
    """
    Minimize a DFA using Hopcroft's algorithm (partition refinement).

    1. Complete the transition function with a virtual dead state so the
       algorithm's correctness assumptions hold for partial DFAs.
    2. Start with two partitions: accepting and non-accepting states.
    3. Repeatedly refine partitions by splitting states that behave differently.
    4. Rebuild the DFA from the final partition, dropping the dead block.
    """
    if not dfa.states:
        return dfa

    alphabet = dfa.get_alphabet()
    if not alphabet:
        # No transitions anywhere; nothing to merge beyond the trivial case.
        return _renumber_states(dfa)

    states = dfa.states
    accept_states = dfa.accept_states

    # Initial partition: accepting vs non-accepting. The dead state is
    # non-accepting.
    accepting: Set[int] = set(accept_states) & set(states)
    non_accepting: Set[int] = (set(states) - accepting) | {_DEAD}

    partition: List[Set[int]] = []
    if accepting:
        partition.append(accepting)
    partition.append(non_accepting)

    if len(partition) == 1:
        # Every real state is non-accepting (empty language); minimal already.
        return _renumber_states(dfa)

    block_of: Dict[int, int] = {}
    for idx, block in enumerate(partition):
        for state in block:
            block_of[state] = idx

    # Predecessor map over the *completed* transition function:
    # preds[(target, char)] = set of states whose char-transition lands on target
    # (with missing transitions and the dead state routed to _DEAD).
    preds: Dict[Tuple[int, int], Set[int]] = defaultdict(set)
    for state_id, state in states.items():
        transitions = state.transitions
        for char in alphabet:
            target = transitions.get(char, _DEAD)
            preds[(target, char)].add(state_id)
    for char in alphabet:
        preds[(_DEAD, char)].add(_DEAD)

    # Worklist of (block_index, char); in_worklist mirrors it for O(1) lookups.
    smaller = 0 if len(partition[0]) <= len(partition[1]) else 1
    worklist: deque = deque()
    in_worklist: Set[Tuple[int, int]] = set()
    for char in alphabet:
        item = (smaller, char)
        worklist.append(item)
        in_worklist.add(item)

    while worklist:
        a_idx, char = worklist.popleft()
        in_worklist.discard((a_idx, char))

        # X = states that transition into block A on `char`.
        block_a = partition[a_idx]
        X: Set[int] = set()
        for state in block_a:
            p = preds.get((state, char))
            if p:
                X |= p
        if not X:
            continue

        # Only blocks that actually contain a predecessor can need splitting.
        touched: Dict[int, Set[int]] = defaultdict(set)
        for state in X:
            touched[block_of[state]].add(state)

        for y_idx, intersection in touched.items():
            block_y = partition[y_idx]
            if len(intersection) == len(block_y):
                continue  # X fully contains Y; no split.

            difference = block_y - intersection
            partition[y_idx] = intersection
            new_idx = len(partition)
            partition.append(difference)
            for state in difference:
                block_of[state] = new_idx

            # Classic Hopcroft worklist update.
            for c in alphabet:
                if (y_idx, c) in in_worklist:
                    new_item = (new_idx, c)
                    worklist.append(new_item)
                    in_worklist.add(new_item)
                else:
                    if len(intersection) <= len(difference):
                        item = (y_idx, c)
                    else:
                        item = (new_idx, c)
                    worklist.append(item)
                    in_worklist.add(item)

    return _build_minimized_dfa(dfa, partition)


def _build_minimized_dfa(old_dfa: DFA, partition: List[Set[int]]) -> DFA:
    """Build a new DFA from the partition, dropping the dead block."""
    new_dfa = DFA()

    # Identify the block that contains the virtual dead state (and any real trap
    # states equivalent to it). It must not appear in the output.
    dead_block = None
    state_to_block: Dict[int, int] = {}
    for idx, block in enumerate(partition):
        if _DEAD in block:
            dead_block = idx
        for state in block:
            state_to_block[state] = idx

    old_states = old_dfa.states
    accept_states = old_dfa.accept_states

    # Map each surviving block to a new state id, start block first.
    block_to_id: Dict[int, int] = {}
    start_block = state_to_block.get(old_dfa.start)
    if start_block is not None and start_block != dead_block:
        is_accept = any(s in accept_states for s in partition[start_block])
        start_id = new_dfa.new_state(is_accept)
        new_dfa.start = start_id
        block_to_id[start_block] = start_id

    for idx, block in enumerate(partition):
        if idx == dead_block or idx in block_to_id:
            continue
        is_accept = any(s in accept_states for s in block)
        block_to_id[idx] = new_dfa.new_state(is_accept)

    # Add transitions using a real representative state from each block.
    for idx, block in enumerate(partition):
        if idx == dead_block:
            continue
        new_state_id = block_to_id[idx]
        rep = next((s for s in block if s in old_states), None)
        if rep is None:
            continue
        for char, target in old_states[rep].transitions.items():
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

    # BFS from start state.
    visited = set()
    queue = deque([dfa.start])

    while queue:
        old_id = queue.popleft()
        if old_id in visited:
            continue
        visited.add(old_id)

        # Assign new ID.
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

    # Add transitions with new IDs.
    for old_id in visited:
        if old_id in dfa.states:
            new_id = old_to_new[old_id]
            for char, target in dfa.states[old_id].transitions.items():
                if target in old_to_new:
                    new_dfa.add_transition(new_id, char, old_to_new[target])

    return new_dfa
