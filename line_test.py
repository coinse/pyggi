from pyggi import Program, Patch, GranularityLevel, TestResult
from pyggi.atomic_operator import LineReplacement, LineInsertion
from pyggi.custom_operator import LineDeletion, LineMoving
import copy, random

def result_parser(stdout, stderr):
    import re
    m = re.findall("runtime: ([0-9.]+)", stdout)
    if len(m) > 0:
        runtime = m[0]
        failed = re.findall("([0-9]+) failed", stdout)
        pass_all = len(failed) == 0
        return TestResult(True, {'runtime': runtime, 'pass_all': pass_all})
    else:
        return TestResult(False, None)

triangle = Program(
    "sample/Triangle_bug_python", granularity_level=GranularityLevel.LINE)
# triangle.print_modification_points('triangle.py')

# See sample/Triangle_bug_python/get_spectrum.py
weights = [0] * len(triangle.modification_points['triangle.py'])
weights[14] = 1
weights[15] = 1
weights[16] = 1

triangle.set_modification_weights('triangle.py', weights)
valid_edit_operators = [LineDeletion, LineMoving, LineReplacement]
tabu = []

patch = Patch(triangle)

for i in range(1000):
    while patch in tabu:
        edit_operator = random.choice(valid_edit_operators)
        patch = Patch(triangle)
        patch.add(edit_operator.create(triangle, method='weighted'))
    tabu.append(patch)
    print (patch)
    test_result = patch.run_test(timeout=30, result_parser=result_parser)
    print (test_result)
    if test_result.compiled and test_result.get('pass_all'):
        print("REPAIRED")
        break

print (patch.diff)
