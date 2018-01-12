from pyggi import Program, Patch, MnplLevel, TestResult
from pyggi.atomic_operator import StmtReplacement
from pyggi.edit import StmtDeletion
import ast
import astor
import copy


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


def is_valid_pos(root, pos):
    node = root
    for block, index in pos:
        if not block in ['body', 'orelse', 'finalbody']:
            return False
        if not block in node.__dict__:
            return False
        if not index < len(node.__dict__[block]):
            return False
        node = node.__dict__[block][index]
    return True

def replace(root, dst, src):
    # dst = [('body', 4), ('body', 0)]
    # src = None or [('body', 4)]
    import copy
    if not is_valid_pos(root, dst):
        return False
    if src and not is_valid_pos(root, src):
        return False
    dst_node, src_node = root, root
    for i in range(len(dst) - 1):
        dst_node = dst_node.__dict__[dst[i][0]][dst[i][1]]
    if src:
        for j in range(len(src)):
            src_node = src_node.__dict__[src[j][0]][src[j][1]]
    else:
        src_node = ast.Pass()
    dst_node.__dict__[dst[-1][0]][dst[-1][1]] = copy.deepcopy(src_node)
    return True

def swap(root, a, b):
    import copy
    if not is_valid_pos(root, a) or not is_valid_pos(root, b):
        return False
    a_node, b_node = root, root
    for i in range(len(a) - 1):
        a_node = a_node.__dict__[a[i][0]][a[i][1]]
    for j in range(len(b) - 1):
        b_node = b_node.__dict__[b[j][0]][b[j][1]]
    # a_node, b_node = copy.deepcopy(a_node), copy.deepcopy(b_node)
    a_node.__dict__[a[-1][0]][a[-1][1]], b_node.__dict__[b[-1][0]][b[-1][
        1]] = copy.deepcopy(b_node.__dict__[b[-1][0]][b[-1][1]]), copy.deepcopy(
            a_node.__dict__[a[-1][0]][a[-1][1]])
    #dst_node.__dict__[dst[-1][0]][dst[-1][1]] = copy.deepcopy(src_node)
    return True


def insert_before(root, dst, src):
    import copy
    if not is_valid_pos(root, dst) or not is_valid_pos(root, src):
        return False
    dst_node, src_node = root, root
    for i in range(len(dst) - 1):
        dst_node = dst_node.__dict__[dst[i][0]][dst[i][1]]
    for j in range(len(src)):
        src_node = src_node.__dict__[src[j][0]][src[j][1]]
    dst_node.__dict__[dst[-1][0]].insert(dst[-1][1], copy.deepcopy(src_node))
    return True

def insert_after(root, dst, src):
    import copy
    if not is_valid_pos(root, dst) or not is_valid_pos(root, src):
        return False
    dst_node, src_node = root, root
    for i in range(len(dst) - 1):
        dst_node = dst_node.__dict__[dst[i][0]][dst[i][1]]
    for j in range(len(src)):
        src_node = src_node.__dict__[src[j][0]][src[j][1]]
    dst_node.__dict__[dst[-1][0]].insert(dst[-1][1] + 1,
                                         copy.deepcopy(src_node))
    return True


triangle = Program(
    "sample/Triangle_fast_python", manipulation_level=MnplLevel.AST)
print(Patch(triangle).run_test(timeout=30, result_parser=result_parser))
root = triangle.contents['triangle.py']

swap(root, [('body', 0)], [('body', 1)])
replace(root, [('body', 4)], [('body', 0)])
replace(root, [('body', 3)], None)
insert_after(root, [('body', 4)], [('body', 1)])
insert_before(root, [('body', 4), ('body', 0)], [('body', 0)])
#replace(root, [('body', 4), ('body', 0)], None)
#, root.body[1] = root.body[1], root.body[0]
#root.body[4].body[0] = ast.Pass()
#root.body.append(root.body[4].body[0])
print(astor.to_source(root))
"""
patch = Patch(triangle)
patch.add(StmtDeletion(('triangle.py', [4, 0])))
patch.add(StmtReplacement(('triangle.py', [4, 2, 0]), ('triangle.py', [4, 3, 0])))
print(patch.run_test(timeout=30, result_parser=result_parser))
print(patch.diff)
"""
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
