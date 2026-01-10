# regex2dfa

[![CI](https://github.com/kpdyer/regex2dfa/actions/workflows/ci.yml/badge.svg)](https://github.com/kpdyer/regex2dfa/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/regex2dfa.svg)](https://pypi.org/project/regex2dfa/)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Convert regular expressions to minimized DFAs in AT&T FST format.

**Pure Python. Zero dependencies. Results cached in memory.**

## Installation

```bash
pip install regex2dfa
```

Or install from source:

```bash
git clone https://github.com/kpdyer/regex2dfa.git
cd regex2dfa
pip install -e .
```

## Quick Start

```python
from regex2dfa import regex2dfa

dfa = regex2dfa("(a|b)+")
print(dfa)
```

Output:
```
0	1	97	97
0	1	98	98
1	1	97	97
1	1	98	98
1
```

## Caching

Results are automatically cached in memory. Repeated calls with the same regex return instantly:

```python
from regex2dfa import regex2dfa, cache_info, clear_cache

# First call computes the DFA
regex2dfa("(a|b)+")

# Second call returns from cache (instant)
regex2dfa("(a|b)+")

# Check cache statistics
print(cache_info())
# CacheInfo(hits=1, misses=1, maxsize=1024, currsize=1)

# Clear cache if needed
clear_cache()
```

## Object-Oriented Interface

```python
from regex2dfa import Regex2DFA

converter = Regex2DFA("(a|b)+")

# Access intermediate representations
print(f"NFA states: {len(converter.nfa.states)}")
print(f"DFA states: {len(converter.dfa.states)}")
print(f"Minimized DFA states: {len(converter.minimized_dfa.states)}")

# Get AT&T format
print(converter.to_att())
```

## Low-Level API

```python
from regex2dfa import parse_regex, build_nfa, nfa_to_dfa, minimize_dfa, format_att

# Step-by-step pipeline
postfix = parse_regex("(a|b)+")
nfa = build_nfa(postfix)
dfa = nfa_to_dfa(nfa)
min_dfa = minimize_dfa(dfa)
output = format_att(min_dfa)
```

## AT&T FST Format

The output uses tab-separated fields:
- **Transitions**: `src  dst  input  output`
- **Final states**: `state_id`

Labels are ASCII byte values (97 = 'a', 98 = 'b').

## Supported Regex Syntax

| Feature | Syntax | Description |
|---------|--------|-------------|
| Literal | `a` | Matches character |
| Any char | `.` | Matches any byte (0-255) |
| Char class | `[abc]` | Matches any listed char |
| Negated class | `[^abc]` | Matches any char not listed |
| Range | `[a-z]` | Matches range |
| Zero or more | `*` | Kleene star |
| One or more | `+` | Kleene plus |
| Optional | `?` | Zero or one |
| Alternation | `\|` | Either side |
| Grouping | `(...)` | Group expressions |
| Anchors | `^` `$` | Start/end (stripped, implicit) |
| Hex escape | `\x00` | Byte by hex value |
| Any byte | `\C` | Any byte (0-255) |
| Digits | `\d` | `[0-9]` |
| Word chars | `\w` | `[a-zA-Z0-9_]` |
| Whitespace | `\s` | Space, tab, newline, carriage return |

## How It Works

1. **Parser** — Tokenizes regex and converts to postfix notation (shunting-yard algorithm)
2. **Thompson's Construction** — Builds NFA from postfix tokens
3. **Subset Construction** — Converts NFA to DFA (powerset method)
4. **Hopcroft's Algorithm** — Minimizes DFA (partition refinement)

## Project Structure

```
regex2dfa/
├── __init__.py     # Public API
├── core.py         # Main regex2dfa() function with caching
├── parser.py       # Regex tokenizer + postfix conversion
├── nfa.py          # NFA data structures
├── thompson.py     # Thompson's construction (Regex → NFA)
├── dfa.py          # DFA data structures
├── subset.py       # Subset construction (NFA → DFA)
├── hopcroft.py     # DFA minimization
└── formatter.py    # AT&T FST output
```

## Tests

```bash
pytest tests/ -v
```

## License

MIT
