import sys
import random
from pyggi import *

TRY = 20
ITERATIONS = 100

if __name__ == "__main__":
    project_path = sys.argv[1]
    p = Program(project_path, 'physical_line')
    runtimes = []
    empty_patch = Patch(p)
    empty_patch.run_test()
    orig_failed = int(empty_patch.test_result.custom['failed'])
    print("orig_failed: " + empty_patch.test_result.custom['failed'])

    best_patches = []
    for t in range(1, TRY + 1):
        best_patch = empty_patch
        min_failed = orig_failed
        for i in range(1, ITERATIONS + 1):
            patch = best_patch.clone()
            if len(patch) > 0 and random.uniform(0, 1) > 0.5:
                index_to_remove = random.randrange(0, len(patch))
                patch.remove(index_to_remove)
            else:
                patch.add_random_edit(
                    [EditType.DELETE, EditType.REPLACE, EditType.COPY])
            patch.run_test()
            print("Iter #{}-{}\t(compiled: {})\t{}".format(
                t, i, patch.test_result.compiled, patch))
            if not patch.test_result.compiled:
                continue
            if patch.test_result.custom['pass_all'] == 'false':
                continue
            print("*** NEW BEST found (failed: {})".format(
                patch.test_result.custom['failed']))
            patch.print_diff()
            min_failed = int(patch.test_result.custom['failed'])
            best_patch = patch
        if best_patch.test_result.custom['pass_all'] == 'true':
            best_patches.append(best_patch)

    best_patches = sorted(
        best_patches,
        key=lambda patch: (int(patch.test_result.custom['failed']), patch.get_line_diff_count())
    )
    print("\n=============ALL POSSIBLE PATCHES==============")
    for best_patch in best_patches:
        print(best_patch)
        print(best_patch.test_result)
        best_patch.print_diff()
        print()
