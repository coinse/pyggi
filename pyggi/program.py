import sys
import os
import shutil
import json
from enum import Enum
from distutils.dir_util import copy_tree
from .test_result import TestResult


class MnplLevel(Enum):
    PHYSICAL_LINE = 'physical_line'
    # AST = 'ast'

    @classmethod
    def is_valid(cls, value):
        return (any(value == item.value for item in cls))


class Program:
    CONFIG_FILE_NAME = 'PYGGI_CONFIG'
    TMP_DIR = "pyggi_tmp/"

    def __init__(self, project_path, manipulation_level='physical_line'):

        if not MnplLevel.is_valid(manipulation_level):
            print("[Error] invalid manipulation level: {}".format(
                manipulation_level))
            sys.exit(1)

        self.manipulation_level = MnplLevel(manipulation_level)
        self.project_path = project_path.strip()
        if self.project_path[-1] == '/':
            self.project_path = self.project_path[:-1]
        with open(os.path.join(self.project_path,
                               Program.CONFIG_FILE_NAME)) as f:
            config = json.load(f)
            self.test_script_path = config['test_script']
            self.target_files = config['target_files']
        self.tmp_project_name = os.path.basename(self.project_path)
        if not Program.clean_tmp_dir(self.tmp_project_name):
            sys.exit(1)
        copy_tree(self.project_path,
                  os.path.join(Program.TMP_DIR, self.tmp_project_name))

        self.contents = self.parse()

    def __str__(self):
        if self.manipulation_level == MnplLevel.PHYSICAL_LINE:
            code = ''
            for k in sorted(self.contents.keys()):
                idx = 0
                for line in self.contents[k]:
                    code += "{}\t: {}\t: {}\n".format(k, idx, line)
                    idx += 1
            return code
        else:
            return self.target_files

    def get_tmp_project_path(self):
        return os.path.join(Program.TMP_DIR, self.tmp_project_name)

    def parse(self):
        contents = {}
        if self.manipulation_level == MnplLevel.PHYSICAL_LINE:
            for target_file_name in self.target_files:
                with open(
                        os.path.join(self.project_path, target_file_name),
                        'r') as f:
                    contents[target_file_name] = list(
                        map(str.rstrip, f.readlines()))
        return contents

    @classmethod
    def clean_tmp_dir(cls, project_name):
        try:
            tmp_project_path = os.path.join(cls.TMP_DIR, project_name)
            if os.path.exists(tmp_project_path):
                shutil.rmtree(tmp_project_path)
            os.mkdir(tmp_project_path)
            return True
        except Exception as e:
            print(e)
            return False
