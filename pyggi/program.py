import sys
import os
import random
import shutil
from .test_result import TestResult

class Program:
    available_manipulation_levels = ['physical_line']
    tmp_dir = "tmp/"

    def __init__(self, path, manipulation_level = 'physical_line'):
        if manipulation_level not in Program.available_manipulation_levels:
            print("[Error] invalid manipulation level: {}".format(manipulation_level))
            sys.exit()
        self.path = path
        self.manipulation_level = manipulation_level
        self.contents = self.parse(path, manipulation_level)

    def __str__(self):
        if self.manipulation_level == 'physical_line':
            code = ''
            for i in range(len(self.contents)):
                code += "{}: {}".format(i, self.contents[i])
            return code
        else:
            return path

    def get_program_name(self):
        return os.path.basename(self.path)

    def parse(self, path, manipulation_level):
        if manipulation_level == 'physical_line':
            f = open(path)
            lines = f.readlines()
            f.close()
            return lines
        else:
            print("[Error] invalid manipulation level: {}".format(manipulation_level))
            sys.exit()

    def run_test(self, test_file_path):
        shutil.copy2(test_file_path, Program.tmp_dir)
        shutil.copy2('TestRunner.java', Program.tmp_dir)
        
        # dummy data
        return TestResult(True, random.randrange(1,7), 5, 3, 4)

    @staticmethod
    def create_program_with_contents(file_name, contents, manipulation_level = 'physical_line'):
        path = Program.tmp_dir + file_name
        if manipulation_level == 'physical_line':
            f = open(path, 'w')
            for content in contents:
                f.write(content)
            f.close()
            return Program(path, manipulation_level)
        else:
            print("[Error] invalid manipulation level: {}".format(manipulation_level))
            sys.exit()
