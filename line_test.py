from pyggi.base import Patch, InvalidPatchError
from pyggi.line import LineProgram
from pyggi.line import LineReplacement, LineInsertion, LineDeletion, LineMoving
import copy, random

class MyProgram(LineProgram):
    def result_parser(self, stdout, stderr):
        import re
        m = re.findall("runtime: ([0-9.]+)", stdout)
        if len(m) > 0:
            runtime = m[0]
            failed = re.findall("([0-9]+) failed", stdout)
            pass_all = len(failed) == 0
            if len(failed) == 0:
                return 1
            else:
                return 0
        else:
            raise InvalidPatchError

triangle = MyProgram("sample/Triangle_bug_python")
# triangle.print_modification_points('triangle.py')

# See sample/Triangle_bug_python/get_spectrum.py
for i in range(len(triangle.modification_points['triangle.py'])):
    if i not in [14, 15, 16]:
        triangle.set_weight(('triangle.py', i), 0)

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
    fitness = patch.run_test(timeout=30)
    if patch.valid and patch.fitness == 1:
        print("REPAIRED")
        break

print (patch.diff)
