"""
PYGGI: Python General framework for Genetic Improvement
"""

from . import algorithms, atomic_operator, custom_operator
from .program import Program, GranularityLevel
from .patch import Patch
from .test_result import TestResult

def oink():
    '''
    :return: ``'oink oink'``
    :rtype: str
    '''
    return 'oink oink'
