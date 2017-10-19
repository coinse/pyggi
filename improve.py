import sys
import random
from pyggi import *

TRY = 5
ITERATIONS = 100
WARMUP_REPS = 10

if __name__ == "__main__":
    project_path = sys.argv[1]
    p = Program(project_path, 'physical_line')
    runtimes = []
    empty_patch = Patch(p)
    for i in range(WARMUP_REPS):
        empty_patch.run_test()
        runtimes.append(int(empty_patch.test_result.custom['runtime']))
    orig_time = float(sum(runtimes)) / len(runtimes)
    print("orig_time: " + str(orig_time))

    compilation_failure_count = 0
    best_patches = []
    for t in range(1, TRY + 1):
        best_patch = empty_patch
        best_time = orig_time
        for i in range(1, ITERATIONS + 1):
            patch = best_patch.clone()
            if len(patch) > 0 and random.uniform(0, 1) > 0.5:
                index_to_remove = random.randrange(0, len(patch))
                patch.remove(index_to_remove)
            else:
                patch.add_random_edit(
                    [EditType.DELETE, EditType.COPY, EditType.REPLACE])
            patch.run_test()
            print("Iter #{}-{}\t(compiled: {})\t{}".format(
                t, i, patch.test_result.compiled, patch))
            if not patch.test_result.compiled:
                compilation_failure_count += 1
                continue
            if patch.test_result.custom['pass_all'] == 'false':
                continue
            if best_time < int(patch.test_result.custom['runtime']):
                continue
            print("*** NEW BEST found (execution time: {})".format(
                patch.test_result.custom['runtime']))
            patch.print_diff()
            best_time = int(patch.test_result.custom['runtime'])
            best_patch = patch
        best_patches.append(best_patch)

    best_patches = sorted(
        best_patches,
        key=lambda patch: (int(patch.test_result.custom['runtime']), len(patch))
    )
    best_patch = best_patches[0]
    print("\n=============BEST==============")
    print(best_patch)
    print(best_patch.test_result)
    best_patch.print_diff()
    print("\n=========CFR==============")
    print("{}%: {}/{}".format(
        float(compilation_failure_count) / (TRY * ITERATIONS) * 100,
        compilation_failure_count, TRY * ITERATIONS))
