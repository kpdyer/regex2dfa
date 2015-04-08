#!/usr/bin/env python

from distutils.core import setup
from distutils.core import Extension

cRegex2dfa = Extension('cRegex2dfa',
                     include_dirs=[],
                     library_dirs=['.libs','/usr/local/Cellar/python/2.7.9/Frameworks/Python.framework/Versions/2.7/lib'],
                     extra_compile_args=['-O3',
                                         '-fstack-protector-all',
                                         '-D_FORTIFY_SOURCE',
                                         '-fPIE',
                                         ],
                     extra_link_args=['-fPIC',
                                      ],
                     libraries=['regex2dfa',
                                'python2.7',
                                ],
                     sources=['src/cRegex2dfa.cc'])

setup(name='cRegex2dfa',
      version='0.0.1',
      description='cRegex2dfa',
      author='Kevin P. Dyer',
      author_email='kpdyer@gmail.com',
      url='https://github.com/kpdyer/regex2dfa',
      packages=['cRegex2dfa',
                ],
      ext_modules=[cRegex2dfa],
      test_suite = 'regex2dfa.tests',
      )
