import sys
import os
import random
import subprocess
import shutil
import re

from .test_result import TestResult


class Program:
    available_manipulation_levels = ['physical_line']
    tmp_dir = "tmp/"
    contents = {}

    def __init__(self,
                 project_path,
                 path_list,
                 manipulation_level='physical_line'):
        if manipulation_level not in Program.available_manipulation_levels:
            print("[Error] invalid manipulation level: {}".format(
                manipulation_level))
            sys.exit()
        self.project_path = project_path
        self.path_list = path_list
        self.manipulation_level = manipulation_level
        self.contents = self.parse(path_list, manipulation_level)

    def __str__(self):
        if self.manipulation_level == 'physical_line':
            code = ''
            for k in sorted(self.contents.keys()):
                idx = 0
                for line in self.contents[k]:
                    code += "{}\t: {}\t: {}\n".format(k, idx, line)
                    idx += 1
            return code
        else:
            return self.path_list

    def get_program_name_list(self):
        return list(map(os.path.basename, self.path_list))

    def parse(self, path_list, manipulation_level):
        contents = {}
        if manipulation_level == 'physical_line':
            for path in path_list:
                code_lines = list(
                    map(str.rstrip, list(open(path, 'r').readlines())))
                contents[path] = code_lines
        else:
            print("[Error] invalid manipulation level: {}".format(
                manipulation_level))
            sys.exit()
        return contents

    def run_test(self, test_file_path):
        tmp_test_file_path = os.path.join(Program.tmp_dir, test_file_path)

        sprocess = subprocess.Popen(
            "./" + tmp_test_file_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = sprocess.communicate()
        test_result = re.findall(
            "Result: \(([0-9]+) tests, ([0-9]+) passed, ([0-9]+) failed, ([0-9]+) skipped\)",
            stdout.decode("ascii"))
        if len(test_result) == 0:
            print("Build failed!")
            print(stderr.decode("ascii"))
            return TestResult(False, 0, 0, 0, 0)
        else:
            tests, passed, failed, skipped = test_result[0]
            print("Build succeed!")
            print(tests, passed, failed, skipped)
            return TestResult(True, 0, tests, passed, failed)

    @staticmethod
    def create_program_with_contents(project_path,
                                     contents,
                                     manipulation_level='physical_line'):
        if manipulation_level == 'physical_line':
            new_path_list = []
            for k in sorted(contents.keys()):
                path = os.path.join(Program.tmp_dir,
                                    os.path.relpath(k, project_path))
                new_path_list.append(path)
                with open(path, 'w') as f:
                    f.write('\n'.join(contents[k]))
            ret = Program(project_path, new_path_list, manipulation_level)
            return ret
        else:
            print("[Error] invalid manipulation level: {}".format(
                manipulation_level))
            sys.exit()
