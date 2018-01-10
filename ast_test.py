from pyggi import Program, Patch, MnplLevel, TestResult
from pyggi.atomic_operator import StmtReplacement
from pyggi.edit import StmtDeletion
import ast
import astor

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

triangle = Program("sample/Triangle_fast_python", manipulation_level=MnplLevel.AST)


print(Patch(triangle).run_test(timeout=30, result_parser=result_parser))
root = triangle.contents['triangle.py']
#root.body[0], root.body[1] = root.body[1], root.body[0]
#root.body[4].body[0] = ast.Pass()
#root.body.append(root.body[4].body[0])
print(astor.to_source(root))
patch = Patch(triangle)
patch.add(StmtDeletion(('triangle.py', [4, 0])))
patch.add(StmtReplacement(('triangle.py', [4, 2, 0]), ('triangle.py', [4, 3, 0])))
print(patch.run_test(timeout=30, result_parser=result_parser))
print(patch.diff)
"""
# del
root.body[1] = ast.Pass()

# swap
root.body[0], root.body[1] = root.body[1], root.body[0]

# replace
root.body[2] = root.body[3]

# insert
root.body[4].body.insert(2, root.body[2])
"""
