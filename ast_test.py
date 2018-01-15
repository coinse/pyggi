from pyggi import Program, Patch, MnplLevel, TestResult
from pyggi.atomic_operator import StmtReplacement, StmtInsertion
from pyggi.edit import StmtDeletion
from pyggi.helper import stmt_python
import ast
import astor
import copy
import random

def result_parser(result):
    import re
    m = re.findall("runtime: ([0-9.]+)", result)
    if len(m) > 0:
        runtime = m[0]
        failed = re.findall("([0-9]+) failed", result)
        pass_all = len(failed) == 0
        return TestResult(True, {'runtime': runtime, 'pass_all': pass_all})
    else:
        return TestResult(False, None)

triangle = Program(
    "sample/Triangle_fast_python", manipulation_level=MnplLevel.AST)

patch = Patch(triangle)

a = random.choice(patch.modification_points['triangle.py'])
b = random.choice(patch.modification_points['triangle.py'])
print (a, b)
patch.add(StmtInsertion(('triangle.py', a), ('triangle.py', b), 'before'))
#patch.add(StmtReplacement(('triangle.py', a), ('triangle.py', b)))
print (patch.run_test(timeout=30, result_parser=result_parser))
print (patch.diff)
