"""
PYGGI stands for Python General framework for Genetic Improvement(GI).
This module has developed to be used as an toolkit for practicing GI.

Written & maintained by COINSE KAIST.
"""

from . import algorithms, atomic_operator, edit
from .program import Program, MnplLevel
from .patch import Patch
from .test_result import TestResult

def oink():
    '''
    :return: ``'oink oink'``
    :rtype: str
    '''
    return 'oink oink'
