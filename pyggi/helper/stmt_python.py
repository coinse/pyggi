import ast
from copy import deepcopy

def is_pos_type(pos):
    """
    :param pos: The position of the node
    :type pos: ?
    :return: whether it is type of tuple(str, list(tuple(str, int))) and all integers >= 0
    :rtype: bool
    """
    if not isinstance(pos, list):
        return False
    return all(isinstance(t, tuple) and isinstance(t[0], str)
        and isinstance(t[1], int) and t[1] >= 0 for t in pos)

def get_modification_points(root):
    """
    :param root: The root node of AST
    :type root: :py:class:`ast.AST`
    :return: The list of positions of the modification points
    :rtype: list(tuple(str, int))
    """
    modification_points = list()
    def visit_node(parent_pos, node):
        for attr in ['body', 'orelse', 'finalbody']:
            if hasattr(node, attr):
                for i in range(len(node.__dict__[attr])):
                    current_pos = parent_pos[:] + [(attr, i)]
                    modification_points.append(current_pos)
                    visit_node(current_pos, node.__dict__[attr][i])
    visit_node([], root)
    return modification_points

def is_valid_pos(root, pos):
    """
    :param root: The root node of AST
    :type root: :py:class:`ast.AST`
    :param pos: The position of the node in the tree
    :type pos: list(tuple(str, int))
    :return: valid or not(i.e., node exists in the tree or not)
    :rtype: bool
    """
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


def pos_2_block_n_index(root, pos):
    """
    :param root: The root node of AST
    :type root: :py:class:`ast.AST`
    :param pos: The position of the node in the tree
    :type pos: list(tuple(str, int))
    :return: The node's parent block and the index within the block
    :rtype: tuple(:py:class:`ast.AST`, int)
    """
    node = root
    for i in range(len(pos) - 1):
        block, index = pos[i]
        node = node.__dict__[block][index]
    return (node.__dict__[pos[-1][0]], pos[-1][1])


def replace(dst, src):
    """
    Replace *dst* with *src*
    :param dst: The root and the position of the destination node
    :type dst: tuple(:py:class:`ast.AST`, list(tuple(str, int)))
    :param src: None or The root and the position of the source node. If none, *dst* is replaced with a pass statement.
    :type src: None or tuple(:py:class:`ast.AST`, list(tuple(str, int))
    :return: Success or not
    :rtype: bool
    """
    if not is_valid_pos(*dst):
        return False
    if src and not is_valid_pos(*src):
        return False
    dst_block, dst_index = pos_2_block_n_index(*dst)
    if src:
        src_block, src_index = pos_2_block_n_index(*src)
        dst_block[dst_index] = deepcopy(src_block[src_index])
    else:
        dst_block[dst_index] = ast.Pass()
    return True


def swap(a, b):
    """
    Swap *a* and *b*

    :param a: The root and position of node a
    :type a: tuple(:py:class:`ast.AST`, list(tuple(str, int)))
    :param b: The root and position of node b
    :type b: tuple(:py:class:`ast.AST`, list(tuple(str, int)))
    :return: Success or not
    :rtype: bool
    """
    if not is_valid_pos(*a) or not is_valid_pos(*b):
        return False
    a_block, a_index = pos_2_block_n_index(*a)
    b_block, b_index = pos_2_block_n_index(*b)
    a_block[a_index], b_block[b_index] = deepcopy(b_block[b_index]), deepcopy(
        a_block[a_index])
    return True


def insert_before(dst, src):
    """
    Insert *src* before *dst*

    :param dst: The root and position of the destination node
    :type dst: tuple(:py:class:`ast.AST`, list(tuple(str, int)))
    :param src: The root and position of the source node
    :type src: tuple(:py:class:`ast.AST`, list(tuple(str, int)))
    :return: Success or not
    :rtype: bool
    """
    if not is_valid_pos(*dst) or not is_valid_pos(*src):
        return False
    dst_block, dst_index = pos_2_block_n_index(*dst)
    src_block, src_index = pos_2_block_n_index(*src)
    dst_block.insert(dst_index, deepcopy(src_block[src_index]))
    return True


def insert_after(dst, src):
    """
    Insert *src* after *dst*

    :param dst: The root and position of the destination node
    :type dst: tuple(:py:class:`ast.AST`, list(tuple(str, int)))
    :param src: The root and position of the source node
    :type src: tuple(:py:class:`ast.AST`, list(tuple(str, int)))
    :return: Success or not
    :rtype: bool
    """
    if not is_valid_pos(*dst) or not is_valid_pos(*src):
        return False
    dst_block, dst_index = pos_2_block_n_index(*dst)
    src_block, src_index = pos_2_block_n_index(*src)
    dst_block.insert(dst_index + 1, deepcopy(src_block[src_index]))
    return True
