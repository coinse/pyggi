import sys
from pyggi import *

TRY = 5
ITERATIONS = 100

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
        return int(patch.test_result.custom['runtime'])

    def compare_fitness(current, best):
        # update the best patch to the current patch when
        # the fitness value of current patch is equal or
        # less than the best(min) fitness value
        return current <= best

    cfr, patches = local_search(
        program,
        total_try=TRY,
        iterations=ITERATIONS,
        get_neighbours=get_neighbours,
        validity_check=validity_check,
        get_fitness=get_fitness,
        compare_fitness=compare_fitness)

    patches = sorted(
        patches, key=lambda patch: (get_fitness(patch), len(patch)))
    best_patch = patches[0]
    program.logger.info("=============BEST==============")
    program.logger.info(best_patch)
    program.logger.info(best_patch.test_result)
    program.logger.info(best_patch.get_diff())
    program.logger.info("CFR: {}%".format(cfr))
