import os
import sys
from pyggi import *

ITERATIONS = 10

if __name__ == "__main__":
    '''
        python main.py sample/Triangle
        - argv[1]: project path
            ./{project_path}/config.json
    '''
    project_path = sys.argv[1]
    p = Program(project_path, 'physical_line')
    best_patch = Patch(p)
    best_patch.run_test()

    for i in range(ITERATIONS):
        print("--- Iteration {} ---".format(i))
        patch = best_patch.clone()
        patch.add_random_edit()
        patch.run_test()
        if not patch.test_result.compiled:
            continue
        print (patch)
        print (patch.get_diff())
        if best_patch.test_result.passed > patch.test_result.passed:
            continue
        print("********* Best found (execution time: {})".format(
            i, patch.test_result.execution_time))
        print(patch)
        best_patch = patch

    print("===============================")
    print(best_patch.get_diff())
    print("===============================")
