"""
Improving non-functional properties ::

    python improve.py ../sample/Triangle_fast
"""
import sys
import random
import argparse
from pyggi.base import Patch, InvalidPatchError
from pyggi.line import LineProgram
from pyggi.line import LineReplacement, LineInsertion, LineDeletion
from pyggi.algorithms import LocalSearch

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PYGGI Improvement Example')
    parser.add_argument('project_path', type=str, default='../sample/Triangle_fast')
    parser.add_argument('--epoch', type=int, default=30,
        help='total epoch(default: 30)')
    parser.add_argument('--iter', type=int, default=100,
        help='total iterations per epoch(default: 100)')
    args = parser.parse_args()
    
    class MyProgram(LineProgram):
        def compute_fitness(self, elapsed_time, stdout, stderr):
            try:
                runtime, pass_all = stdout.strip().split(',')
                runtime = float(runtime)
                if not pass_all == 'true':
                    raise InvalidPatchError
                else:
                    return runtime
            except:
                raise InvalidPatchError
   
    class MyLocalSearch(LocalSearch):
        def get_neighbour(self, patch):
            if len(patch) > 0 and random.random() < 0.5:
                patch.remove(random.randrange(0, len(patch)))
            else:
                edit_operator = random.choice([LineDeletion, LineInsertion, LineReplacement])
                patch.add(edit_operator.create(program))
            return patch

        def stopping_criterion(self, iter, fitness):
            return fitness < 100

    program = MyProgram(args.project_path)
    local_search = MyLocalSearch(program)
    result = local_search.run(warmup_reps=5, epoch=args.epoch, max_iter=args.iter, timeout=15)

    for epoch in result:
        print ("Epoch #{}".format(epoch))
        for key in result[epoch]:
            print ("- {}: {}".format(key, result[epoch][key]))
