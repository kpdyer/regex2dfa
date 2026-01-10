"""
DFA (Deterministic Finite Automaton) data structures.
"""

from dataclasses import dataclass, field
from typing import Dict, Set, List, Tuple


@dataclass
class DFAState:
    """A state in the DFA."""
    id: int
    transitions: Dict[int, int] = field(default_factory=dict)  # char -> state id
    is_accept: bool = False


@dataclass
class DFA:
    """Deterministic Finite Automaton."""
    states: Dict[int, DFAState] = field(default_factory=dict)
    start: int = 0
    accept_states: Set[int] = field(default_factory=set)
    next_state_id: int = 0
    
    def new_state(self, is_accept: bool = False) -> int:
        """Create a new state and return its ID."""
        state_id = self.next_state_id
        self.states[state_id] = DFAState(state_id, is_accept=is_accept)
        if is_accept:
            self.accept_states.add(state_id)
        self.next_state_id += 1
        return state_id
    
    def add_transition(self, from_state: int, char: int, to_state: int):
        """Add a transition from one state to another."""
        self.states[from_state].transitions[char] = to_state
    
    def get_alphabet(self) -> Set[int]:
        """Get all characters used in transitions."""
        alphabet: Set[int] = set()
        for state in self.states.values():
            alphabet |= set(state.transitions.keys())
        return alphabet
    
    def get_transitions(self) -> List[Tuple[int, int, int, int]]:
        """Get all transitions as (src, dst, input, output) tuples."""
        transitions = []
        for state_id, state in self.states.items():
            for char, target in state.transitions.items():
                transitions.append((state_id, target, char, char))
        return transitions
