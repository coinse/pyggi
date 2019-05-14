"""
Improving non-functional properties ::

    python improve_xml.py ../sample/Triangle_fast_xml
"""
import sys
import random
import argparse
import re
from pyggi.base import Patch, ParseError, AbstractProgram
from pyggi.tree import XmlEngine
from pyggi.tree import StmtReplacement, StmtInsertion, StmtDeletion, StmtMoving
from pyggi.algorithms import LocalSearch

class MyProgram(AbstractProgram):
    @classmethod
    def get_engine(cls, file_name):
        return XmlEngine

    def compute_fitness(self, elapsed_time, stdout, stderr):
        try:
            runtime, pass_all = stdout.strip().split(',')
            runtime = float(runtime)
            if not pass_all == 'true':
                raise ParseError
            return runtime
        except:
            raise ParseError

class MyLocalSearch(LocalSearch):
    def get_neighbour(self, patch):
        if len(patch) > 0 and random.random() < 0.5:
            patch.remove(random.randrange(0, len(patch)))
        else:
            edit_operator = random.choice([StmtDeletion, StmtInsertion, StmtReplacement])
            patch.add(edit_operator.create(self.program))
        return patch

    def stopping_criterion(self, iter, fitness):
        return fitness < 100

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PYGGI Improvement Example')
    parser.add_argument('project_path', type=str, default='../sample/Triangle_fast_xml')
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
