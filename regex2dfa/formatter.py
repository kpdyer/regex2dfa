"""
AT&T FST format output.
"""

from typing import List
from .dfa import DFA


def format_att(dfa: DFA) -> str:
    """
    Format a DFA in AT&T FST format.

    Format:
    - Transitions: src<TAB>dst<TAB>input<TAB>output
    - Final states: state_id (one per line, at the end)

    Labels are ASCII byte values.
    """
    lines: List[str] = []
    states = dfa.states

    # Emit transitions in sorted (state, char) order for deterministic output.
    for state_id in sorted(states):
        transitions = states[state_id].transitions
        for char in sorted(transitions):
            target = transitions[char]
            lines.append(f"{state_id}\t{target}\t{char}\t{char}")

    # Output final states
    for state_id in sorted(dfa.accept_states):
        lines.append(str(state_id))

    return '\n'.join(lines)
