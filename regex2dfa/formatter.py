"""
AT&T FST format output.
"""

from typing import List, Tuple
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
    
    # Collect and sort transitions for deterministic output
    transitions: List[Tuple[int, int, int, int]] = []
    
    for state_id in sorted(dfa.states.keys()):
        state = dfa.states[state_id]
        for char in sorted(state.transitions.keys()):
            target = state.transitions[char]
            transitions.append((state_id, target, char, char))
    
    # Output transitions
    for src, dst, inp, out in transitions:
        lines.append(f"{src}\t{dst}\t{inp}\t{out}")
    
    # Output final states
    for state_id in sorted(dfa.accept_states):
        lines.append(str(state_id))
    
    return '\n'.join(lines)
