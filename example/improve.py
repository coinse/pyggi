"""
Improving non-functional properties ::

    python improve.py ../sample/Triangle_fast
"""
import sys
import random
import argparse
from pyggi import Program, Patch, MnplLevel
from pyggi.algorithms import LocalSearch
from pyggi.atomic_operator import LineReplacement, LineInsertion
from pyggi.edit import LineDeletion

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PYGGI Improvment Example')
    parser.add_argument('project_path', type=str, default='../sample/Triangle_fast')
    parser.add_argument('--epoch', type=int, default=30,
        help='total epoch(default: 30)')
    parser.add_argument('--iter', type=int, default=100,
        help='total iterations per epoch(default: 100)')
    args = parser.parse_args()
    
    program = Program(args.project_path, MnplLevel.PHYSICAL_LINE)
   
    class MyLocalSearch(LocalSearch):
        def get_neighbour(self, patch):
            if len(patch) > 0 and random.random() < 0.5:
                patch.remove(random.randrange(0, len(patch)))
            else:
                edit_operator = random.choice([LineDeletion, LineInsertion, LineReplacement])
                patch.add_edit(edit_operator.random(program))
            return patch

        def get_fitness(self, patch):
            return float(patch.test_result.custom['runtime'])

        def is_valid_patch(self, patch):
            return patch.test_result.compiled and patch.test_result.custom['pass_all'] == 'true'

        def stopping_criterion(self, iter, patch):
            return float(patch.test_result.custom['runtime']) < 100

    local_search = MyLocalSearch(program)
    result = local_search.run(warmup_reps=5, epoch=args.epoch, max_iter=args.iter, timeout=15)

    for epoch in result:
        print ("Epoch #{}".format(epoch))
        for key in result[epoch]:
            print ("- {}: {}".format(key, result[epoch][key]))
