"""
Improving non-functional properties ::

    python improve_python.py ../sample/Triangle_fast_python
"""
import sys
import random
import argparse
from pyggi import Program, Patch, GranularityLevel, TestResult
from pyggi.algorithms import LocalSearch
from pyggi.atomic_operator import LineReplacement, LineInsertion
from pyggi.custom_operator import LineDeletion

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PYGGI Improvment Example')
    parser.add_argument('project_path', type=str, default='../sample/Triangle_fast_python')
    parser.add_argument('--epoch', type=int, default=30,
        help='total epoch(default: 30)')
    parser.add_argument('--iter', type=int, default=100,
        help='total iterations per epoch(default: 100)')
    args = parser.parse_args()
    
    program = Program(args.project_path, GranularityLevel.LINE)
   
    class MyLocalSearch(LocalSearch):
        def get_neighbour(self, patch):
            if len(patch) > 0 and random.random() < 0.5:
                patch.remove(random.randrange(0, len(patch)))
            else:
                edit_operator = random.choice([LineDeletion, LineInsertion, LineReplacement])
                patch.add(edit_operator.create(program))
            return patch

        def get_fitness(self, patch):
            return float(patch.test_result.get('runtime'))

        def is_valid_patch(self, patch):
            return patch.test_result.compiled and patch.test_result.custom['pass_all']

        def stopping_criterion(self, iter, patch):
            return float(patch.test_result.get('runtime')) < 0.05

    def result_parser(stdout, stderr):
        import re
        m = re.findall("runtime: ([0-9.]+)", stdout)
        if len(m) > 0:
            runtime = m[0]
            failed = re.findall("([0-9]+) failed", stdout)
            pass_all = len(failed) == 0
            return TestResult(True, {'runtime': runtime, 'pass_all': pass_all})
        else:
            return TestResult(False, None)

    local_search = MyLocalSearch(program)
    result = local_search.run(warmup_reps=5, epoch=args.epoch, max_iter=args.iter, timeout=15, result_parser=result_parser)
    for epoch in result:
        print ("Epoch #{}".format(epoch))
        for key in result[epoch]:
            print ("- {}: {}".format(key, result[epoch][key]))
