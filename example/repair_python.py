"""
Automated program repair ::

    python repair.py ../sample/Triangle_bug
"""
import sys
import random
import argparse
from pyggi.base import Patch, InvalidPatchError
from pyggi.line import LineProgram
from pyggi.base.atomic_operator import LineReplacement, LineInsertion
from pyggi.base.custom_operator import LineDeletion
from pyggi.algorithms import LocalSearch

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PYGGI Bug Repair Example')
    parser.add_argument('project_path', type=str, default='../sample/Triangle_bug_python')
    parser.add_argument('--epoch', type=int, default=30,
        help='total epoch(default: 30)')
    parser.add_argument('--iter', type=int, default=100,
        help='total iterations per epoch(default: 100)')
    args = parser.parse_args()

    class MyProgram(LineProgram):
        def result_parser(self, stdout, stderr):
            import re
            m = re.findall("runtime: ([0-9.]+)", stdout)
            if len(m) > 0:
                runtime = m[0]
                failed = re.findall("([0-9]+) failed", stdout)
                pass_all = len(failed) == 0
                failed = int(failed[0]) if not pass_all else 0
                return failed
            else:
                raise InvalidPatchError

    class MyTabuSearch(LocalSearch):
        def setup(self):
            self.tabu = []

        def get_neighbour(self, patch):
            while True:
                temp_patch = patch.clone()
                if len(temp_patch) > 0 and random.random() < 0.5:
                    temp_patch.remove(random.randrange(0, len(temp_patch)))
                else:
                    edit_operator = random.choice([LineDeletion, LineInsertion, LineReplacement])
                    temp_patch.add(edit_operator.create(program, method="weighted"))
                if not any(item == temp_patch for item in self.tabu):
                    self.tabu.append(temp_patch)
                    break
            return temp_patch

        def is_better_than_the_best(self, fitness, best_fitness):
            return fitness < best_fitness

        def stopping_criterion(self, iter, patch):
            if patch.fitness == 0:
                return True
            return False

    program = MyProgram(args.project_path)
    tabu_search = MyTabuSearch(program)
    result = tabu_search.run(warmup_reps=1, epoch=args.epoch, max_iter=args.iter, timeout=10)
    for epoch in result:
        print ("Epoch #{}".format(epoch))
        for key in result[epoch]:
            print ("- {}: {}".format(key, result[epoch][key]))
