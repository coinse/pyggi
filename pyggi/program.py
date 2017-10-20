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

class Program(object):
    CONFIG_FILE_NAME = 'PYGGI_CONFIG'
    TMP_DIR = "pyggi_tmp/"

    def __init__(self, path, manipulation_level='physical_line'):

        def clean_tmp_dir(tmp_path):
            try:
                if os.path.exists(tmp_path):
                    shutil.rmtree(tmp_path)
                os.mkdir(tmp_path)
                return True
            except Exception as e:
                print(e)
                return False

        def parse(manipulation_level, path, target_files):
            contents = {}
            if manipulation_level == MnplLevel.PHYSICAL_LINE:
                for target_file in target_files:
                    with open(os.path.join(path, target_file), 'r') as f:
                        contents[target_file] = list(
                            map(str.rstrip, f.readlines()))
            return contents

        if not MnplLevel.is_valid(manipulation_level):
            print("[Error] invalid manipulation level: {}".format(
                manipulation_level))
            sys.exit(1)
        self.manipulation_level = MnplLevel(manipulation_level)
        self.path = path.strip()
        if self.path[-1] == '/':
            self.path = self.path[:-1]
        self.name = os.path.basename(self.path)
        with open(os.path.join(self.path, Program.CONFIG_FILE_NAME)) as f:
            config = json.load(f)
            self.test_script_path = config['test_script']
            self.target_files = config['target_files']
        if not clean_tmp_dir(self.get_tmp_path()):
            sys.exit(1)
        copy_tree(self.path, self.get_tmp_path())
        self.contents = parse(self.manipulation_level, self.path,
                              self.target_files)

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

    def get_tmp_path(self):
        return os.path.join(Program.TMP_DIR, self.name)
