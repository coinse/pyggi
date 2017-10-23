import sys
import random
from pyggi import *

TRY = 50
ITERATIONS = 100

if __name__ == "__main__":
    project_path = sys.argv[1]
    program = Program(project_path, 'physical_line')
    visited = []

    def get_neighbours(patch):
        cnt = 0
        while True and cnt < 50:
            cnt += 1
            if len(patch) > 0 and random.random() < 0.5:
                patch.remove(random.randrange(0, len(patch)))
            else:
                patch.add_random_edit()
            if patch not in visited:
                visited.append(patch)
                break
        return patch

    def validity_check(patch):
        return patch.test_result.compiled and patch.test_result.custom['pass_all'] == 'true'

    def get_fitness(patch):
        return int(patch.test_result.custom['failed'])

    def compare_fitness(current, best):
        # update the best patch to the current patch when
        # the fitness value of current patch is less than
        # the best(min) fitness value
        return current < best

    cfr, patches = local_search(
        program,
        warmup_reps=1,
        total_try=TRY,
        iterations=ITERATIONS,
        get_neighbours=get_neighbours,
        validity_check=validity_check,
        get_fitness=get_fitness,
        compare_fitness=compare_fitness,
        print_log=True)

    patches = sorted(
        patches, key=lambda patch: (get_fitness(patch), patch.edit_size))
    print("=============ALL POSSIBLE PATCHES==============")
    for best_patch in patches:
        print(best_patch)
        print(best_patch.test_result)
        best_patch.print_diff()
    print("CFR: {}%".format(cfr))
