#!/usr/bin/env python

import glob
import sys
import warnings

from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--cov', 'glabra' ,'--cov-report' ,'term-missing']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

def get_readme():
    """ Get the README from the current directory. If there isn't one, return an empty string """
    all_readmes = sorted(glob.glob("README*"))
    if len(all_readmes) > 1:
        warnings.warn("There seems to be more than one README in this directory. Choosing the "
                      "first in lexicographic order.")
    if len(all_readmes) > 0:
        return open(all_readmes[0], 'r').read()

    warnings.warn("There doesn't seem to be a README in this directory.")
    return ""

setup(
    name='glabra',
    version='1.0',
    url='github.com/chedbrandh/glabra',
    author='Christofer Hedbrandh',
    author_email='chedbrandh@gmail.com',
    license='The MIT License (MIT)',
    packages=find_packages(),
    cmdclass={'test': PyTest},
    install_requires=open('requirements.txt', 'r').readlines(),
    tests_require=open('requirements.testing.txt', 'r').readlines(),
    description='Glabra is a library for generating sequences using n-grams ' + \
        'of sequences in some training data.',
    long_description='\n' + get_readme()
)
