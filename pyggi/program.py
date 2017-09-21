import sys
import os
import random
import shutil
from .test_result import TestResult

class Program:
    available_manipulation_levels = ['physical_line']
    tmp_dir = "tmp/"
    contents = []

    def __init__(self, path_list, manipulation_level = 'physical_line'):

        if manipulation_level not in Program.available_manipulation_levels:
            print("[Error] invalid manipulation level: {}".format(manipulation_level))
            sys.exit()
        self.path_list = path_list
        self.manipulation_level = manipulation_level
        self.contents = self.parse(path_list, manipulation_level)

    def __str__(self):
        if self.manipulation_level == 'physical_line':
            code = ''
            for i in range(len(self.contents)):
                code += "{}\t: {}\t: {}\n".format(i, self.contents[i][0], self.contents[i][1])
            return code
        else:
            return self.path_list

    def get_program_name_list(self):
        return list(map(os.path.basename, self.path_list))

    def parse(self, path_list, manipulation_level):
        if manipulation_level == 'physical_line':
            line_cnt = 0
            for path in path_list:
                code_lines = list(map(lambda x: (path, x),
                    open(path, 'r').readlines()))
                self.contents += code_lines
                f.close()
        else:
            print("[Error] invalid manipulation level: {}".format(manipulation_level))
            sys.exit()

    def run_test(self, test_file_path):
        shutil.copy2(test_file_path, Program.tmp_dir)
        shutil.copy2('TestRunner.java', Program.tmp_dir)
        
        # dummy data
        return TestResult(True, random.randrange(1,7), 5, 3, 4)

    @staticmethod
    def create_program_with_contents(filename_list, contents, manipulation_level = 'physical_line'):
        
        if manipulation_level == 'physical_line':
            new_path_list = []
            for filename in filename_list:
                path = Program.tmp_dir + filename
                new_path_list.append(path)
                f = open(path, 'w')
                for content in list(filter(lambda x: filename in x[0],
                                                     contents)):
                    f.write(content[1])
                f.close()
            return Program(new_path_list, manipulation_level)
        else:
            print("[Error] invalid manipulation level: {}".format(manipulation_level))
            sys.exit()
