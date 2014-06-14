regex2dfa
=========

[![Build Status](https://travis-ci.org/kpdyer/regex2dfa.svg?branch=master)](https://travis-ci.org/kpdyer/regex2dfa)

This is a command-line utility that converts a regular expression to a DFA.

* **input**: A perl-compatible regular expression, as defined by re2 [1].
* **output**: An AT&T DFA [2], which accepts an equivelent language to the input regular expression.

### References

* [1] https://code.google.com/p/re2/
* [2] https://openfst.org/

Building
--------

This utillity requires standard build tools: autoconf, make, gcc, etc.

Once you have your developement environment setup:

```
$ ./configure
$ make
$ ls bin/
fstcompile	fstminimize	fstprint	regex2dfa
```

Example Usage
-------------

```
$ ./bin/regex2dfa -r "^(a|b)*$"
0	0	97	97
0	0	98	98
0
```

```
$ ./bin/regex2dfa -r "^(a|b)+$"
0	1	97	97
0	1	98	98
1	1	97	97
1	1	98	98
1
```
