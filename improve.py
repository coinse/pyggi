import sys
import random
import argparse
from pyggi import Program, Patch, MnplLevel, local_search
from pyggi.atomic_operator import LineReplacement, LineInsertion
from pyggi.edit import LineDeletion

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PYGGI Improvment Example')
    parser.add_argument('project_path', type=str, default='sample/Triangle_fast')
    parser.add_argument('--run', type=int, default=30,
        help='total runs (default: 30)')
    parser.add_argument('--iter', type=int, default=100,
        help='total iterations (default: 100)')
    args = parser.parse_args()
    
    program = Program(args.project_path, MnplLevel.PHYSICAL_LINE)
    
    def get_neighbours(patch):
        if len(patch) > 0 and random.random() < 0.5:
            patch.remove(random.randrange(0, len(patch)))
        else:
            edit_operator = random.choice([LineDeletion, LineInsertion, LineReplacement])
            patch.add_edit(edit_operator.random(program))
        return patch

    def validity_check(patch):
        return patch.test_result.compiled and patch.test_result.custom['pass_all'] == 'true'

    def get_fitness(patch):
        return float(patch.test_result.custom['runtime'])

    def compare_fitness(current, best):
        """
        Update the best patch to the current patch when
        the fitness value of current patch is equal or
        less than the best(min) fitness value
        """
        return current <= best

    def stop(i, patch):
        """Python"""
        # return float(patch.test_result.custom['runtime']) < 0.01
        """Java"""
        return float(patch.test_result.custom['runtime']) < 100

    cfr, patches = local_search(
        program,
        total_run=args.run,
        iterations=args.iter,
        get_neighbours=get_neighbours,
        validity_check=validity_check,
        get_fitness=get_fitness,
        compare_fitness=compare_fitness,
        stop=stop,
        timeout=10)

    patches = sorted(
        patches, key=lambda patch: (get_fitness(patch), len(patch)))
    for best_patch in patches:
        program.logger.info(best_patch)
        program.logger.info(best_patch.test_result)
        program.logger.info(best_patch.diff)
    program.logger.info("CFR: {}%".format(cfr))
