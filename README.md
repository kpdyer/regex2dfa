# regex2dfa

[![CI](https://github.com/kpdyer/regex2dfa/actions/workflows/ci.yml/badge.svg)](https://github.com/kpdyer/regex2dfa/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/regex2dfa.svg)](https://pypi.org/project/regex2dfa/)

Convert regular expressions to minimized deterministic finite automata (DFAs) in
AT&T FST text format. Pure Python, no runtime dependencies; requires Python 3.10+.

## Install and use

```sh
pip install regex2dfa
```

```python
from regex2dfa import regex2dfa

print(regex2dfa("(a|b)+"))
```

```text
0	1	97	97
0	1	98	98
1	1	97	97
1	1	98	98
1
```

Transitions contain tab-separated `source destination input output` fields;
final states appear on separate lines. State 0 is the start state. Input and
output labels are identical integer character values (`97` is `a`). Byte-range
characters use labels 0–255; other literal characters use their Unicode code
points, without UTF-8 encoding. An empty pattern returns `"0"` (accepts only the
empty string).

## Regex syntax

| Syntax | Meaning |
| --- | --- |
| `abc`, `(ab)` | Literals, concatenation and grouping |
| `a\|b` | Alternation |
| `*`, `+`, `?` | Zero or more, one or more, zero or one |
| `[abc]`, `[a-z]`, `[^abc]` | Character sets, ranges, negation |
| `.`, `\C` | Any byte (0–255), including newline |
| `\d`, `\w` | `[0-9]`, `[a-zA-Z0-9_]` |
| `\s` | Space, tab, newline or carriage return |
| `\n`, `\r`, `\t`, `\0`, `\xFF` | Control characters and hex byte values |
| `\.`, `\*`, `\$`, etc. | Escaped literals |

DFAs describe whole strings. Unescaped `^` and `$` outside character classes are
ignored. Negated classes are limited to bytes 0–255. Use Python raw strings for
regex escapes, for example `regex2dfa(r"\d+\.")`.

This is a small regex dialect: counted repetition (`{m,n}`), lookarounds,
backreferences and lazy quantifiers are unsupported. Escapes are not expanded
inside character classes; use `[0-9]` instead of `[\d]`.

## API

`regex2dfa(pattern)` caches up to 1,024 results in memory. Use `cache_info()` for
hit/miss statistics and `clear_cache()` to reset the cache.

`Regex2DFA` lazily exposes each conversion stage without using the shared cache:

```python
from regex2dfa import Regex2DFA

converter = Regex2DFA("(a|b)+")
print(len(converter.nfa.states), len(converter.minimized_dfa.states))
print(converter.to_att())  # str(converter) also returns AT&T text
```

The stages are also available as functions:

| Function | Result | `Regex2DFA` property |
| --- | --- | --- |
| `parse_regex(pattern)` | Postfix tokens (shunting-yard parser) | `postfix` |
| `build_nfa(postfix)` | NFA (Thompson's construction) | `nfa` |
| `nfa_to_dfa(nfa)` | DFA (subset construction) | `dfa` |
| `minimize_dfa(dfa)` | Minimal DFA (Hopcroft's algorithm) | `minimized_dfa` |
| `format_att(dfa)` | AT&T text | — |

## Development

```sh
git clone https://github.com/kpdyer/regex2dfa.git
cd regex2dfa
python -m pip install -e ".[dev]"
python -m pytest
python benchmark.py --quick
```

The benchmark supports `--stages` for stage timings and `--json` for machine-readable
output. Package versions come from `regex2dfa/__init__.py`; this README is also
the PyPI description.

Licensed under [MIT](https://github.com/kpdyer/regex2dfa/blob/master/LICENSE).
