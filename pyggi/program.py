import sys
import os
import shutil
import json
from distutils.dir_util import copy_tree
from .test_result import TestResult

class Program:
    CONFIG_FILE_NAME = 'PYGGI_CONFIG'
    TMP_DIR = "pyggi_tmp/"
    available_manipulation_levels = ['physical_line']

    def __init__(self,
                 project_path,
                 manipulation_level='physical_line'):
        
        if manipulation_level not in Program.available_manipulation_levels:
            print("[Error] invalid manipulation level: {}".format(
                manipulation_level))
            sys.exit(1)
        
        self.manipulation_level = manipulation_level
        self.project_path = project_path
        with open(os.path.join(self.project_path, Program.CONFIG_FILE_NAME)) as f:
            config = json.load(f)
            self.test_script_path = config['test_script']
            self.target_files = config['target_files']
      
        if not Program.clean_tmp_dir():
            sys.exit(1)
        self.tmp_project_name = os.path.basename(self.project_path)
        copy_tree(self.project_path, os.path.join(Program.TMP_DIR, self.tmp_project_name))

        self.contents = self.parse(self.project_path, self.target_files, manipulation_level)

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
            return self.target_files

    def get_tmp_project_path(self):
        return os.path.join(Program.TMP_DIR, self.tmp_project_name)
    
    def parse(self, project_path, target_files, manipulation_level):
        contents = {}
        if manipulation_level == 'physical_line':
            for target_file_name in target_files:
                with open(os.path.join(project_path, target_file_name), 'r') as f:
                    contents[target_file_name] = list(map(str.rstrip, f.readlines()))
        else:
            print("[Error] invalid manipulation level: {}".format(
                manipulation_level))
            sys.exit(1)
        return contents

    @classmethod
    def clean_tmp_dir(cls):
        try:
            if os.path.exists(cls.TMP_DIR):
       	        shutil.rmtree(cls.TMP_DIR)
            os.mkdir(cls.TMP_DIR)
            return True
        except Exception as e:
            print(e)
            return False
