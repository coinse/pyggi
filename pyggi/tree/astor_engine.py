import ast
import astor
import copy
from . import AbstractTreeEngine

class AstorEngine(AbstractTreeEngine):
    @classmethod
    def get_contents(cls, file_path):
        return astor.parse_file(file_path)

    @classmethod
    def get_modification_points(cls, root):
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

    @classmethod
    def get_source(cls, program, file_name, index):
        blk, idx = cls.pos_2_block_n_index(program.contents[file_name],
                                       program.modification_points[file_name][index])
        return astor.to_source(blk[idx])

    @classmethod
    def dump(cls, contents_of_file):
        return astor.to_source(contents_of_file)

    @classmethod
    def do_replace(cls, program, op, new_contents, modification_points):
        dst_root = new_contents[op.target[0]]
        dst_pos = modification_points[op.target[0]][op.target[1]]
        ingr_root = program.contents[op.ingredient[0]]
        ingr_pos = program.modification_points[op.ingredient[0]][op.ingredient[1]]
        return cls.replace((dst_root, dst_pos), (ingr_root, ingr_pos))

    @classmethod
    def do_insert(cls, program, op, new_contents, modification_points):
        dst_root = new_contents[op.target[0]]
        dst_pos = modification_points[op.target[0]][op.target[1]]
        ingr_root = program.contents[op.ingredient[0]]
        ingr_pos = program.modification_points[op.ingredient[0]][op.ingredient[1]]
        if op.direction == 'before':
            success = cls.insert_before((dst_root, dst_pos), (ingr_root, ingr_pos))
            if success:
                depth = len(dst_pos)
                parent = dst_pos[:depth-1]
                index = dst_pos[depth-1][1]
                for pos in modification_points[op.target[0]]:
                    if parent == pos[:depth-1] and len(pos) >= depth and index <= pos[depth-1][1]:
                        a, i = pos[depth-1]
                        pos[depth-1] = (a, i + 1)
        elif op.direction == 'after':
            success = cls.insert_after((dst_root, dst_pos), (ingr_root, ingr_pos))
            if success:
                depth = len(dst_pos)
                parent = dst_pos[:depth-1]
                index = dst_pos[depth - 1][1]
                for pos in modification_points[op.target[0]]:
                    if parent == pos[:depth-1] and len(pos) >= depth and index < pos[depth-1][1]:
                        a, i = pos[depth-1]
                        pos[depth-1] = (a, i + 1)
        return success

    @classmethod
    def do_delete(cls, program, op, new_contents, modification_points):
        dst_root = new_contents[op.target[0]]
        dst_pos = modification_points[op.target[0]][op.target[1]]
        return cls.replace((dst_root, dst_pos), None)

    @classmethod
    def is_pos_type(cls, pos):
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

    @classmethod
    def is_valid_pos(cls, root, pos):
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

    @classmethod
    def pos_2_block_n_index(cls, root, pos):
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

    @classmethod
    def replace(cls, dst, src):
        """
        Replace *dst* with *src*
        :param dst: The root and the position of the destination node
        :type dst: tuple(:py:class:`ast.AST`, list(tuple(str, int)))
        :param src: None or The root and the position of the source node. If none, *dst* is replaced with a pass statement.
        :type src: None or tuple(:py:class:`ast.AST`, list(tuple(str, int))
        :return: Success or not
        :rtype: bool
        """
        if not cls.is_valid_pos(*dst):
            return False
        if src and not cls.is_valid_pos(*src):
            return False
        dst_block, dst_index = cls.pos_2_block_n_index(*dst)
        if src:
            src_block, src_index = cls.pos_2_block_n_index(*src)
            dst_block[dst_index] = copy.deepcopy(src_block[src_index])
        else:
            dst_block[dst_index] = ast.Pass()
        return True

    @classmethod
    def swap(cls, a, b):
        """
        Swap *a* and *b*

        :param a: The root and position of node a
        :type a: tuple(:py:class:`ast.AST`, list(tuple(str, int)))
        :param b: The root and position of node b
        :type b: tuple(:py:class:`ast.AST`, list(tuple(str, int)))
        :return: Success or not
        :rtype: bool
        """
        if not cls.is_valid_pos(*a) or not cls.is_valid_pos(*b):
            return False
        a_block, a_index = cls.pos_2_block_n_index(*a)
        b_block, b_index = cls.pos_2_block_n_index(*b)
        a_block[a_index], b_block[b_index] = copy.deepcopy(b_block[b_index]), copy.deepcopy(
            a_block[a_index])
        return True

    @classmethod
    def insert_before(cls, dst, src):
        """
        Insert *src* before *dst*

        :param dst: The root and position of the destination node
        :type dst: tuple(:py:class:`ast.AST`, list(tuple(str, int)))
        :param src: The root and position of the source node
        :type src: tuple(:py:class:`ast.AST`, list(tuple(str, int)))
        :return: Success or not
        :rtype: bool
        """
        if not cls.is_valid_pos(*dst) or not cls.is_valid_pos(*src):
            return False
        dst_block, dst_index = cls.pos_2_block_n_index(*dst)
        src_block, src_index = cls.pos_2_block_n_index(*src)
        dst_block.insert(dst_index, copy.deepcopy(src_block[src_index]))
        return True

    @classmethod
    def insert_after(cls, dst, src):
        """
        Insert *src* after *dst*

        :param dst: The root and position of the destination node
        :type dst: tuple(:py:class:`ast.AST`, list(tuple(str, int)))
        :param src: The root and position of the source node
        :type src: tuple(:py:class:`ast.AST`, list(tuple(str, int)))
        :return: Success or not
        :rtype: bool
        """
        if not cls.is_valid_pos(*dst) or not cls.is_valid_pos(*src):
            return False
        dst_block, dst_index = cls.pos_2_block_n_index(*dst)
        src_block, src_index = cls.pos_2_block_n_index(*src)
        dst_block.insert(dst_index + 1, copy.deepcopy(src_block[src_index]))
        return True
