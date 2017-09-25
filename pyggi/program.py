import sys
import os
import random
import shutil
from .test_result import TestResult


class Program:
    available_manipulation_levels = ['physical_line']
    tmp_dir = "tmp/"
    contents = {}

    def __init__(self, path_list, manipulation_level='physical_line'):

        if manipulation_level not in Program.available_manipulation_levels:
            print("[Error] invalid manipulation level: {}".format(
                manipulation_level))
            sys.exit()
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
        shutil.copy2(test_file_path, Program.tmp_dir)
        shutil.copy2('TestRunner.java', Program.tmp_dir)

        # dummy data
        return TestResult(True, random.randrange(1, 7), 5, 3, 4)

    @staticmethod
    def create_program_with_contents(contents,
                                     manipulation_level='physical_line'):

        if manipulation_level == 'physical_line':
            new_path_list = []
            for k in sorted(contents.keys()):
                path = Program.tmp_dir + os.path.basename(k)
                new_path_list.append(path)
                with open(path, 'w') as f:
                    f.write('\n'.join(contents[k]))
            ret = Program(new_path_list, manipulation_level)
            return ret
        else:
            print("[Error] invalid manipulation level: {}".format(
                manipulation_level))
            sys.exit()
