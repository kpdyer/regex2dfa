#!/usr/bin/env python

import subprocess

from distutils.command.build_ext import build_ext
from setuptools import setup


class R2DBuild(build_ext):

    def build_extension(self, ext):
        # subprocess.check_call will raise an exception if any of the commands
        # do not complete successfully.
        subprocess.check_call(['chmod', '755', 'configure'])
        subprocess.check_call(['chmod', '755', 'third_party/openfst/configure'])
        subprocess.check_call(['./configure'])
        subprocess.check_call(['make'])
        return build_ext.build_extension(self, ext)


setup(
    name='regex2dfa',
    version='0.1.8-2',
    description='regex2dfa',
    author='Kevin P. Dyer',
    author_email='kpdyer@gmail.com',
    url='https://github.com/kpdyer/regex2dfa',
    py_modules=['regex2dfa'],
    setup_requires=['cffi>=1.0.0'],
    install_requires=['cffi>=1.0.0'],
    cffi_modules=['regex2dfa_build.py:ffi'],
    test_suite='tests',
    cmdclass={'build_ext': R2DBuild},
)
