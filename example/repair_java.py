"""
Automated program repair ::
"""
import sys
import random
import argparse
import os
from pyggi.base import Patch
from pyggi.line import LineProgram
from pyggi.line import LineReplacement, LineInsertion, LineDeletion
from pyggi.tree import TreeProgram, XmlEngine
from pyggi.tree import StmtReplacement, StmtInsertion, StmtDeletion
from pyggi.algorithms import LocalSearch

class MyXmlEngine(XmlEngine):
    @classmethod
    def process_tree(cls, tree):
        stmt_tags = ['if', 'decl_stmt', 'expr_stmt', 'return', 'try']
        cls.select_tags(tree, keep=stmt_tags)
        cls.rewrite_tags(tree, stmt_tags, 'stmt')
        cls.rotate_newlines(tree)

class MyTreeProgram(TreeProgram):
    def setup(self):
        if not os.path.exists(os.path.join(self.tmp_path, "Triangle.java.xml")):
            self.exec_cmd("srcml Triangle.java -o Triangle.java.xml")

    @classmethod
    def get_engine(cls, file_name):
        return MyXmlEngine

class MyTabuSearch(LocalSearch):
    def setup(self):
        self.tabu = []

    def get_neighbour(self, patch):
        while True:
            temp_patch = patch.clone()
            if len(temp_patch) > 0 and random.random() < 0.5:
                temp_patch.remove(random.randrange(0, len(temp_patch)))
            else:
                edit_operator = random.choice(self.operators)
                temp_patch.add(edit_operator.create(self.program, method="weighted"))
            if not any(item == temp_patch for item in self.tabu):
                self.tabu.append(temp_patch)
                break
        return temp_patch

    def is_better_than_the_best(self, fitness, best_fitness):
        return fitness < best_fitness

    def stopping_criterion(self, iter, fitness):
        if fitness == 0:
            return True
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PYGGI Bug Repair Example')
    parser.add_argument('--project_path', type=str, default='../sample/Triangle_bug_java')
    parser.add_argument('--mode', type=str, default='line')
    parser.add_argument('--epoch', type=int, default=30,
        help='total epoch(default: 30)')
    parser.add_argument('--iter', type=int, default=10000,
        help='total iterations per epoch(default: 10000)')
    args = parser.parse_args()
    assert args.mode in ['line', 'tree']

    if args.mode == 'line':
        config = {
            "target_files": ["Triangle.java"],
            "test_command": "./run.sh"
        }
        program = LineProgram(args.project_path, config=config)
        tabu_search = MyTabuSearch(program)
        tabu_search.operators = [LineReplacement, LineInsertion, LineDeletion]
    elif args.mode == 'tree':
        config = {
            "target_files": ["Triangle.java.xml"],
            "test_command": "./run.sh"
        }
        program = MyTreeProgram(args.project_path, config=config)
        tabu_search = MyTabuSearch(program)
        tabu_search.operators = [StmtReplacement, StmtInsertion, StmtDeletion]

    result = tabu_search.run(warmup_reps=1, epoch=args.epoch, max_iter=args.iter)
    print("======================RESULT======================")
    print(result)
    program.remove_tmp_variant()