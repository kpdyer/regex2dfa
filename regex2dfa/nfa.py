"""
NFA (Nondeterministic Finite Automaton) data structures.
"""

from dataclasses import dataclass, field
from typing import Dict, Set, List, Optional

# Epsilon transition marker
EPSILON = -1


@dataclass
class NFAState:
    """A state in the NFA."""
    id: int
    transitions: Dict[int, Set[int]] = field(default_factory=dict)  # char -> set of state ids
    
    def add_transition(self, char: int, target: int):
        """Add a transition on character to target state."""
        if char not in self.transitions:
            self.transitions[char] = set()
        self.transitions[char].add(target)


@dataclass
class NFA:
    """Nondeterministic Finite Automaton."""
    states: Dict[int, NFAState] = field(default_factory=dict)
    start: int = 0
    accept: int = 0
    next_state_id: int = 0
    
    def new_state(self) -> int:
        """Create a new state and return its ID."""
        state_id = self.next_state_id
        self.states[state_id] = NFAState(state_id)
        self.next_state_id += 1
        return state_id
    
    def add_transition(self, from_state: int, char: int, to_state: int):
        """Add a transition from one state to another."""
        self.states[from_state].add_transition(char, to_state)
    
    def add_epsilon(self, from_state: int, to_state: int):
        """Add an epsilon transition."""
        self.add_transition(from_state, EPSILON, to_state)
    
    def epsilon_closure(self, states: Set[int]) -> Set[int]:
        """Compute epsilon closure of a set of states."""
        closure = set(states)
        stack = list(states)
        
        while stack:
            state = stack.pop()
            if state in self.states:
                eps_targets = self.states[state].transitions.get(EPSILON, set())
                for target in eps_targets:
                    if target not in closure:
                        closure.add(target)
                        stack.append(target)
        
        return closure
    
    def move(self, states: Set[int], char: int) -> Set[int]:
        """Get all states reachable from states on character."""
        result: Set[int] = set()
        for state in states:
            if state in self.states:
                targets = self.states[state].transitions.get(char, set())
                result |= targets
        return result
