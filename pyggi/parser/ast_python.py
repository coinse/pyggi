import sys
import ast

node_id = 0

def get_tree(ast, initlevel=1):
    "Pretty-print an AST to the given output stream."
    tree = []
    visit_node(ast, initlevel, tree)
    return tree

def visit_node(node, level, tree):
    global node_id
    node_id += 1
    if not isinstance(node, list):
        current = {'name': node.__class__.__name__, 'object': node, 'level': level, 'childrens': list(), 'id': node_id}
        """
        if isinstance(node, ast.stmt):
            current['lineno'] = node.lineno
            current['col_offset'] = node.col_offset
        """
        tree.append(current)
    if hasattr(node, 'body'):
        for child in node.body:
            visit_node(child, level+1, current['childrens'])
