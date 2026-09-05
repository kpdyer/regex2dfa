"""Check both conversion APIs against the .regex/.dfa fixture pairs."""

from pathlib import Path

import pytest

from regex2dfa import Regex2DFA, regex2dfa


DATA_DIR = Path(__file__).parent / "data"


@pytest.mark.parametrize("convert", [regex2dfa, Regex2DFA], ids=["function", "object"])
@pytest.mark.parametrize("regex_path", sorted(DATA_DIR.glob("*.regex")), ids=lambda path: path.stem)
def test_regex_to_dfa(convert, regex_path):
    regex = regex_path.read_text().strip()
    expected = regex_path.with_suffix(".dfa").read_text().strip()
    assert str(convert(regex)) == expected
