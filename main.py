from pyggi import *
import sys

ITERATIONS = 10

if __name__ == "__main__":
    '''
        python main.py sample/java/Triangle/ run.sh

        - argv[1]: A project path
        - argv[2]: Run script in the project path
    '''

    if len(sys.argv) < 3:
        print("[Error] No file name and test name")

    # Let all target code file paths are retrived by
    # first argument (a.k.a path) divided by white space
    path_list = sys.argv[1].split()
    p = Program(path_list, 'physical_line')
    best_patch = Patch(p)
    best_patch.run_test(sys.argv[2])

    for i in range(ITERATIONS):
        patch = best_patch.clone()
        patch.add_random_edit()
        patch.run_test(sys.argv[2])
        if not patch.test_result.compiled:
            continue
        if best_patch.test_result.execution_time <= patch.test_result.execution_time:
            continue
        print("#{}: Best found (execution time: {})".format(
            i, patch.test_result.execution_time))
        print(patch)
        best_patch = patch

    best_program = best_patch.apply()
    print("===============================")
    print(best_patch.get_diff())
    print("===============================")
    print(best_program)
