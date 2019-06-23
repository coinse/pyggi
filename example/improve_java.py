"""
Improving non-functional properties ::
"""
import sys
import random
import argparse
import os
from pyggi.base import Patch, AbstractProgram
from pyggi.line import LineProgram
from pyggi.line import LineReplacement, LineInsertion, LineDeletion
from pyggi.tree import TreeProgram, XmlEngine
from pyggi.tree import StmtReplacement, StmtInsertion, StmtDeletion
from pyggi.algorithms import LocalSearch

class MyProgram(AbstractProgram):
    def compute_fitness(self, result, return_code, stdout, stderr, elapsed_time):
        try:
            runtime, pass_all = stdout.strip().split(',')
            runtime = float(runtime)
            if not pass_all == 'true':
                result.status = 'PARSE_ERROR'
            else:
                result.fitness = runtime
        except:
            result.status = 'PARSE_ERROR'

class MyLineProgram(LineProgram, MyProgram):
    pass

class MyXmlEngine(XmlEngine):
    @classmethod
    def process_tree(cls, tree):
        stmt_tags = ['if', 'decl_stmt', 'expr_stmt', 'return', 'try']
        cls.select_tags(tree, keep=stmt_tags)
        cls.rewrite_tags(tree, stmt_tags, 'stmt')
        cls.rotate_newlines(tree)

class MyTreeProgram(TreeProgram, MyProgram):
    def setup(self):
        if not os.path.exists(os.path.join(self.tmp_path, "Triangle.java.xml")):
            self.exec_cmd("srcml Triangle.java -o Triangle.java.xml")

    @classmethod
    def get_engine(cls, file_name):
        return MyXmlEngine

class MyLocalSearch(LocalSearch):
    def get_neighbour(self, patch):
        if len(patch) > 0 and random.random() < 0.5:
            patch.remove(random.randrange(0, len(patch)))
        else:
            edit_operator = random.choice(self.operators)
            patch.add(edit_operator.create(self.program))
        return patch

    def stopping_criterion(self, iter, fitness):
        return fitness < 100

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PYGGI Improvement Example')
    parser.add_argument('--project_path', type=str, default='../sample/Triangle_fast_java')
    parser.add_argument('--mode', type=str, default='line')
    parser.add_argument('--epoch', type=int, default=30,
        help='total epoch(default: 30)')
    parser.add_argument('--iter', type=int, default=100,
        help='total iterations per epoch(default: 100)')
    args = parser.parse_args()
    assert args.mode in ['line', 'tree']

    if args.mode == 'line':
        config = {
            "target_files": ["Triangle.java"],
            "test_command": "./run.sh"
        }
        program = MyLineProgram(args.project_path, config=config)
        local_search = MyLocalSearch(program)
        local_search.operators = [LineReplacement, LineInsertion, LineDeletion]
    elif args.mode == 'tree':
        config = {
            "target_files": ["Triangle.java.xml"],
            "test_command": "./run.sh"
        }
        program = MyTreeProgram(args.project_path, config=config)
        local_search = MyLocalSearch(program)
        local_search.operators = [StmtReplacement, StmtInsertion, StmtDeletion]

    result = local_search.run(warmup_reps=5, epoch=args.epoch, max_iter=args.iter, timeout=15)
    print("======================RESULT======================")
    for epoch in range(len(result)):
        print("Epoch {}".format(epoch))
        print(result[epoch])
        print(result[epoch]['diff'])
    program.remove_tmp_variant()
