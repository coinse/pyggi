"""
Improving non-functional properties ::

    python improve_srcml.py ../sample/Triangle_fast_srcml
"""
import sys
import random
import argparse
import re
from pyggi.base import Patch, ParseError, AbstractProgram
from pyggi.tree import XmlEngine
from pyggi.tree import StmtReplacement, StmtInsertion, StmtDeletion, StmtMoving
from pyggi.algorithms import LocalSearch
from improve_xml import MyProgram as Program
from improve_xml import MyLocalSearch

class MyXmlEngine(XmlEngine):
    @classmethod
    def process_tree(cls, tree):
        stmt_tags = ['if', 'decl_stmt', 'expr_stmt', 'return', 'try']
        cls.select_tags(tree, keep=stmt_tags)
        cls.rewrite_tags(tree, stmt_tags, 'stmt')
        cls.rotate_newlines(tree)

class MyProgram(Program):
    @classmethod
    def get_engine(cls, file_name):
        return MyXmlEngine

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PYGGI Improvement Example')
    parser.add_argument('--project_path', type=str, default='../sample/Triangle_fast_srcml')
    parser.add_argument('--epoch', type=int, default=30,
        help='total epoch(default: 30)')
    parser.add_argument('--iter', type=int, default=100,
        help='total iterations per epoch(default: 100)')
    args = parser.parse_args()

    program = MyProgram(args.project_path)
    local_search = MyLocalSearch(program)
    result = local_search.run(warmup_reps=5, epoch=args.epoch, max_iter=args.iter, timeout=15)
    print("======================RESULT======================")
    print(result)
    program.remove_tmp_variant()
