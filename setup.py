#!/usr/bin/env python

import os
import glob

from setuptools.command.install import install

from distutils.core import setup
from distutils.core import Extension

class R2DInstallstall(install):
    def run(self):
        os.system("./configure")
        os.system("make")
        install.run(self)

cRegex2dfa_ext = Extension('regex2dfa.cRegex2dfa',
                     include_dirs=[],
                     library_dirs=['.libs'],
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

setup(name='regex2dfa',
      version='0.1.7',
      description='regex2dfa',
      author='Kevin P. Dyer',
      author_email='kpdyer@gmail.com',
      url='https://github.com/kpdyer/regex2dfa',
      packages=['regex2dfa',
                ],
      ext_modules=[cRegex2dfa_ext],
      test_suite = 'regex2dfa.tests',
      cmdclass={'install': R2DInstallstall}
      )
