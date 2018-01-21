from pyggi import Program, Patch, MnplLevel, TestResult
from pyggi.atomic_operator import LineReplacement, LineInsertion
from pyggi.edit import LineDeletion, LineMoving
import copy, random

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
    "sample/Triangle_bug_python", manipulation_level=MnplLevel.LINE)
triangle.print_modification_points('triangle.py')

# See sample/Triangle_bug_python/get_spectrum.py
weights = [0] * len(triangle.modification_points['triangle.py'])
weights[14] = 1
weights[15] = 1
weights[16] = 1

triangle.set_modification_weights('triangle.py', weights)
valid_edit_operators = [LineDeletion, LineMoving, LineReplacement]
for i in range(100):
    patch = Patch(triangle)
    edit_operator = random.choice(valid_edit_operators)
    patch.add(edit_operator.create(triangle, method='weighted'))
    print (patch)
    test_result = patch.run_test(timeout=30, result_parser=result_parser)
    if test_result.compiled and test_result.custom['pass_all'] == 'True':
        print("REPAIRED")
        break
