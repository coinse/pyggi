"""

This module contains MnplLevel and Program class.

"""
import os
import shutil
import json
from enum import Enum
from distutils.dir_util import copy_tree
from .logger import Logger


class MnplLevel(Enum):
    """

    MnplLevel represents the granularity levels of program.

    """
    PHYSICAL_LINE = 'physical_line'
    # AST = 'ast'

    @classmethod
    def is_valid(cls, value):
        """
        :param value: The value of enum to check

        :return: Whether there is an enum that has a value equal to the `value`
        :rtype: bool

        .. hint::
            There are some examples,
            ::
                MnplLevel.is_valid('physical_line')
                >> True
                MnplLevel.is_valid('random_text')
                >> False
        """
        return any(value == item.value for item in cls)


class Program(object):
    """

    Program encapsulates the original source code.
    Currently, PYGGI stores the source code as a list of code lines,
    as lines are the only supported unit of modifications.
    For modifications at other granularity levels,
    this class needs to process and store the source code accordingly
    (for example, by parsing and storing the AST).

    """
    CONFIG_FILE_NAME = 'PYGGI_CONFIG'
    TMP_DIR = "./pyggi_tmp/"

    def __init__(self, path, manipulation_level=MnplLevel.PHYSICAL_LINE):
        assert isinstance(manipulation_level, MnplLevel)
        self.path = path.strip()
        if self.path.endswith('/'):
            self.path = self.path[:-1]
        self.name = os.path.basename(self.path)
        self.logger = Logger(self.name)
        self.manipulation_level = manipulation_level
        with open(os.path.join(self.path, Program.CONFIG_FILE_NAME)) as config_file:
            config = json.load(config_file)
            self.test_command = config['test_command']
            self.target_files = config['target_files']
        Program.clean_tmp_dir(self.tmp_path)
        copy_tree(self.path, self.tmp_path)
        self.contents = Program.parse(self.manipulation_level, self.path, self.target_files)

    def __str__(self):
        if self.manipulation_level == MnplLevel.PHYSICAL_LINE:
            code = ''
            for k in sorted(self.contents.keys()):
                idx = 0
                for line in self.contents[k]:
                    code += "{}\t: {}\t: {}\n".format(k, idx, line)
                    idx += 1
            return code
        return self.target_files

    @property
    def tmp_path(self):
        """
        :return: The path of the temporary dirctory
        :rtype: str
        """
        return os.path.join(Program.TMP_DIR, self.name)

    @classmethod
    def clean_tmp_dir(cls, tmp_path):
        """
        Clean the temporary project directory if it exists.

        :param str tmp_path: The path of directory to clean.
        :return: None
        """
        if os.path.exists(tmp_path):
            shutil.rmtree(tmp_path)
        if not os.path.exists(Program.TMP_DIR):
            os.mkdir(Program.TMP_DIR)
        os.mkdir(tmp_path)

    @classmethod
    def parse(cls, manipulation_level, path, target_files):
        """

        :param manipulation_level: The granularity level
        :type manipulation_level: :py:class:`.program.MnplLevel`
        :param str path: The project root path
        :param target_files: The relative paths of target files within the project root
        :type target_files: list(str)

        :return: the contents of the files, see `Hint`
        :rtype: dict(str, list(str))

        .. hint::
            - key: the file name
            - value: the contents of the file
        """
        contents = {}
        if manipulation_level == MnplLevel.PHYSICAL_LINE:
            for target in target_files:
                with open(os.path.join(path, target), 'r') as target_file:
                    contents[target] = list(
                        map(str.rstrip, target_file.readlines()))
        return contents
