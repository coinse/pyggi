import os
import sys
import random
from pyggi import *

ITERATIONS = 100
WARMUP_REPS = 10

if __name__ == "__main__":
    project_path = sys.argv[1]
    p = Program(project_path, 'physical_line')
    runtimes = []
    best_patch = Patch(p)
    for i in range(WARMUP_REPS):
        best_patch.run_test()
        runtimes.append(int(best_patch.test_result.custom['runtime']))
    best_time = float(sum(runtimes))/len(runtimes)
    print ("orig_time: " + str(best_time))

    for i in range(ITERATIONS):
        print()
        print("======== Iteration {} ========".format(i))
        patch = best_patch.clone()
        print ("current_best:\t" + str(best_patch))
        if len(patch) > 0 and random.uniform(0, 1) > 0.5:
            index_to_remove = random.randrange(0, len(patch))
            print ("remove index: {}".format(index_to_remove))
            patch.remove(index_to_remove)
        else:
            patch.add_random_edit()
            print ("add random edit")
        print ("current_patch:\t" + str(patch))
        patch.run_test()
        if not patch.test_result.compiled:
            continue
        print ("-------------------------------")
        print (patch.test_result)
        print ("-------------------------------")
        if patch.test_result.custom['pass_all'] == 'false':
            continue
        if best_time < int(patch.test_result.custom['runtime']):
            continue
        print ("********* Best found (execution time: {})".format(patch.test_result.custom['runtime']))
        print (patch.get_diff())
        best_patch = patch
        best_time = int(patch.test_result.custom['runtime'])

    print()
    print("============= BEST =============")
    print(best_patch)
    print(best_patch.get_diff())
    print("===============================")
