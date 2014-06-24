regex2dfa
---------

regex2dfa is a single-function module that takes an input regular expression and converts it to a deterministic finite automata (DFA).

### Installation

```
npm install regex2dfa
```

### Usage

```javascript
var regex2dfa = require('regex2dfa/regex2dfa.js');
var regex = "^(a|b)*$";
var dfa = regex2dfa.regex2dfa(regex);
console.log(dfa);
```

outputs

```
0    0    97    97
0    0    98    98
0
```

### Author

Kevin P. Dyer (kpdyer@gmail.com)
