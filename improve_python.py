import sys
from pyggi import *

RUN = 50
ITERATIONS = 1000

if __name__ == "__main__":
    project_path = sys.argv[1]
    program = Program(project_path, 'physical_line')

    def get_neighbours(patch):
        if len(patch) > 0 and random.random() < 0.5:
            patch.remove(random.randrange(0, len(patch)))
        else:
            patch.add_random_edit()
        return patch

    def validity_check(patch):
        return patch.test_result.compiled and patch.test_result.custom['pass_all'] == 'true'

    def get_fitness(patch):
        return float(patch.test_result.custom['runtime'])

    def compare_fitness(current, best):
        # update the best patch to the current patch when
        # the fitness value of current patch is equal or
        # less than the best(min) fitness value
        return current <= best

    def stop(i, patch):
        return float(patch.test_result.custom['runtime']) < 0.01

    cfr, patches = local_search(
        program,
        total_run=RUN,
        iterations=ITERATIONS,
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
        program.logger.info(best_patch.get_diff())

    program.logger.info("CFR: {}%".format(cfr))
