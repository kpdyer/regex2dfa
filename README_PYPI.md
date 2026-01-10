# regex2dfa

Convert regular expressions to minimized DFAs in AT&T FST format.

**Pure Python · Zero dependencies · Results cached in memory**

## Installation

```bash
pip install regex2dfa
```

## Usage

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

## Features

- **Pure Python** — No external dependencies
- **Fast** — Results cached with LRU (1024 entries)
- **Complete pipeline** — Thompson's → Subset → Hopcroft minimization

## Supported Syntax

| Feature | Syntax | Example |
|---------|--------|---------|
| Literal | `a` | `abc` |
| Any char | `.` | `a.b` |
| Character class | `[abc]`, `[a-z]`, `[^abc]` | `[0-9]+` |
| Quantifiers | `*`, `+`, `?` | `a*`, `b+`, `c?` |
| Alternation | `\|` | `cat\|dog` |
| Grouping | `(...)` | `(ab)+` |
| Escapes | `\x00`, `\d`, `\w`, `\s`, `\C` | `\xFF`, `\d+` |

## Output Format

AT&T FST format with tab-separated fields:
- **Transitions**: `src  dst  input  output`
- **Final states**: `state_id`

Labels are ASCII byte values (e.g., 97 = 'a').

## Links

- [GitHub](https://github.com/kpdyer/regex2dfa)
- [Documentation](https://github.com/kpdyer/regex2dfa#readme)

## License

MIT
