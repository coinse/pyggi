import sys
import random
from pyggi import *

RUN = 50
ITERATIONS = 10000

if __name__ == "__main__":
    project_path = sys.argv[1]
    program = Program(project_path, 'physical_line')
    tabu = []

    def get_neighbours(patch):
        while True:
            c_patch = patch.clone()
            if len(c_patch) > 0 and random.random() < 0.5:
                c_patch.remove(random.randrange(0, len(c_patch)))
            else:
                c_patch.add_random_edit()
            if not any(item == c_patch for item in tabu):
                tabu.append(c_patch)
                break
        return c_patch

    def validity_check(patch):
        return patch.test_result.compiled and patch.test_result.custom['pass_all'] == 'true'

    def get_fitness(patch):
        return int(patch.test_result.custom['failed'])

    def compare_fitness(current, best):
        # update the best patch to the current patch when
        # the fitness value of current patch is less than
        # the best(min) fitness value
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
        total_run=RUN,
        iterations=ITERATIONS,
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
        program.logger.info(best_patch.get_diff())
    program.logger.info("CFR: {}%".format(cfr))
