regex2dfa
=========

This is a command-line utility that converts a regular expression to a DFA.

* **input**: A perl-compatible regular expression, as defined by re2 [1].
* **output**: An AT&T FST [2], which accepts an equivelent language to the input regular expression.

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

The language of strings of length at least one, over the alphabet ```{a, b}```.

```
PATH=bin:$PATH regex2dfa -r "^(a|b)+$"
0	1	97	97
0	1	98	98
1	1	97	97
1	1	98	98
1
```
