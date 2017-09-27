import json
import os
import sys

from pyggi import *
from distutils.dir_util import copy_tree

ITERATIONS = 10

if __name__ == "__main__":
    '''
        python main.py sample/Triangle

        - argv[1]: project path
            ./{project_path}/config.json
    '''
    project_path = sys.argv[1]
    with open(project_path + '/config.json') as f:
        config = json.load(f)
    target_file_paths = list(
        map(lambda target_path: os.path.join(project_path, target_path), config[
            'target_files']))

    test_script_path = config['test_script']
    copy_tree(project_path, "tmp")  # FIXME

    p = Program(project_path, target_file_paths, 'physical_line')
    best_patch = Patch(p)
    best_patch.run_test(test_script_path)

    for i in range(ITERATIONS):
        patch = best_patch.clone()
        patch.add_random_edit()
        patch.run_test(test_script_path)
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
