regex2dfa
=========

Building
--------

```
$ ./configure
$ make
$ ls bin/
fstcompile	fstminimize	fstprint	regex2dfa
```

Example Usage
-------------

```
PATH=bin:$PATH regex2dfa -r "^(a|b)+$"
0	1	97	97
0	1	98	98
1	1	97	97
1	1	98	98
1
```
