from pyggi import *
import sys

ITERATIONS = 10

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print ("[Error] No file name and test name")
    p = Program(sys.argv[1], 'physical_line')
    
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
        print ("#{}: Best found".format(i))
        print (patch.test_result.execution_time)
        print (patch)
        best_patch = patch
    
    best_program = best_patch.apply()
    print (best_patch)
    print (best_program)
