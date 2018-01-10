from pyggi import Program, Patch, MnplLevel, TestResult
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


print(triangle.contents)
print(Patch(triangle).run_test(timeout=30, result_parser=result_parser))
root = triangle.contents['triangle.py']
root.body[0], root.body[1] = root.body[1], root.body[0]
print(astor.to_source(root))
print(triangle.contents)
print(Patch(triangle).run_test(timeout=30, result_parser=result_parser))

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
