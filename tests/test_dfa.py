"""
DFA conversion tests - reads .regex/.dfa file pairs from tests/data/.

Each test case is a pair of files:
  - {name}.regex  - the input regex
  - {name}.dfa    - the expected DFA output in AT&T FST format
"""

import os
import pytest
from pathlib import Path

from regex2dfa import regex2dfa


# Find all test cases
DATA_DIR = Path(__file__).parent / "data"


def discover_test_cases():
    """Find all .regex files and return (name, regex_path, dfa_path) tuples."""
    cases = []
    for regex_file in sorted(DATA_DIR.glob("*.regex")):
        name = regex_file.stem
        dfa_file = regex_file.with_suffix(".dfa")
        if dfa_file.exists():
            cases.append((name, regex_file, dfa_file))
    return cases


TEST_CASES = discover_test_cases()


@pytest.mark.parametrize("name,regex_path,dfa_path", TEST_CASES, ids=[c[0] for c in TEST_CASES])
def test_regex_to_dfa(name, regex_path, dfa_path):
    """Test that regex produces expected DFA."""
    regex = regex_path.read_text().strip()
    expected = dfa_path.read_text().strip()
    
    result = regex2dfa(regex)
    
    assert result == expected, f"DFA mismatch for {name}"
