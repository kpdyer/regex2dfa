#!/usr/bin/env python

import os

from setuptools import setup
from setuptools.command.install import install


class R2DInstallstall(install):
    def run(self):
        os.system("chmod 755 configure")
        os.system("chmod 755 third_party/openfst/configure")
        os.system("./configure")
        os.system("make")
        install.run(self)


setup(
    name='regex2dfa',
    version='0.1.7-5',
    description='regex2dfa',
    author='Kevin P. Dyer',
    author_email='kpdyer@gmail.com',
    url='https://github.com/kpdyer/regex2dfa',
    py_modules=['regex2dfa'],
    setup_requires=['cffi>=1.0.0'],
    install_requires=['cffi>=1.0.0'],
    cffi_modules=['regex2dfa_build.py:ffi'],
    test_suite='tests',
    cmdclass={'install': R2DInstallstall}
)
