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
    parser.add_argument('--iter', type=int, default=10000,
        help='total iterations (default: 10000)')
    args = parser.parse_args()
    
    program = Program(args.project_path, MnplLevel.PHYSICAL_LINE)
    tabu = []

    def get_neighbours(patch):
        while True:
            c_patch = patch.clone()
            if len(c_patch) > 0 and random.random() < 0.5:
                c_patch.remove(random.randrange(0, len(c_patch)))
            else:
                edit_operator = random.choice([LineDeletion, LineInsertion, LineReplacement])
                c_patch.add_edit(edit_operator.random(program))
            if not any(item == c_patch for item in tabu):
                tabu.append(c_patch)
                break
        return c_patch

    def validity_check(patch):
        return patch.test_result.compiled and patch.test_result.custom['pass_all'] == 'true'

    def get_fitness(patch):
        return int(patch.test_result.custom['failed'])

    def compare_fitness(current, best):
        """
        Update the best patch to the current patch when
        the fitness value of current patch is less than
        the best(min) fitness value
        """
        return current < best

    def stop(i, patch):
        global tabu
        if not int(patch.test_result.custom['failed']) == 0:
            return False
        tabu = []
        return True

    cfr, patches = local_search(
        program,
        warmup_reps=1,
        total_run=args.run,
        iterations=args.iter,
        get_neighbours=get_neighbours,
        validity_check=validity_check,
        get_fitness=get_fitness,
        compare_fitness=compare_fitness,
        stop=stop)

    patches = sorted(
        patches, key=lambda patch: (get_fitness(patch), patch.edit_size))
    program.logger.info("=============ALL POSSIBLE PATCHES==============")
    for best_patch in patches:
        program.logger.info(best_patch)
        program.logger.info(best_patch.test_result)
        program.logger.info(best_patch.diff)
    program.logger.info("CFR: {}%".format(cfr))
