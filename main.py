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
        if len(patch) > 0 and random.uniform(0, 1) > 0.5:
            patch.remove()
        else:
            patch.add_random_edit()
        patch.run_test()
        if not patch.test_result.compiled:
            continue
        print (patch)
        print ("-------------------------------")
        print (patch.test_result)
        print ("-------------------------------")
        #if best_patch.test_result.custom['passed'] > patch.test_result.custom['passed']:
        #    continue
        #if best_patch.test_result.real_time < patch.test_result.real_time:
        #    continue
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
