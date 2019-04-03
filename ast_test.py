from pyggi.base import Patch, InvalidPatchError
from pyggi.tree import TreeProgram
from pyggi.tree import StmtReplacement, StmtInsertion, StmtDeletion, StmtMoving
import ast
import astor
import copy
import random

class MyProgram(TreeProgram):
    # Custom parser for the results of pytest
    def result_parser(self, stdout, stderr):
        import re
        m = re.findall("runtime: ([0-9.]+)", stdout)
        if len(m) > 0:
            runtime = m[0]
            failed = re.findall("([0-9]+) failed", stdout)
            pass_all = len(failed) == 0
            if pass_all:
                return runtime
            else:
                raise InvalidPatchError
        else:
            raise InvalidPatchError

# Create new Program instance for 'sample/Triangle_fast_python'
triangle = MyProgram("sample/Triangle_fast_python")
triangle.print_modification_points('triangle.py')

# Set modification weights
for i in range(len(triangle.modification_weights['triangle.py'])):
    if i != 7:
        triangle.set_weight(('triangle.py', i), 0.01)

# Create new Patch
patch = Patch(triangle)
valid_edit_operators = [StmtDeletion, StmtMoving, StmtReplacement]
edit_operator = random.choice(valid_edit_operators)
patch.add(edit_operator.create(triangle, method='weighted'))

# Print the patch's info, test results, and line differences made by the patch
print (patch)
print (patch.run_test(timeout=30))
print (patch.diff)
