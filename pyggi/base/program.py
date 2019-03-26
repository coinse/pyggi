"""

This module contains GranularityLevel and Program class.

"""
import os
import shutil
import json
from abc import abstractmethod
from enum import Enum
from distutils.dir_util import copy_tree
from ..utils.logger import Logger

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

    def __init__(self, path, config_file_name=CONFIG_FILE_NAME):
        self.path = path.strip()
        if self.path.endswith('/'):
            self.path = self.path[:-1]
        self.name = os.path.basename(self.path)
        self.logger = Logger(self.name)
        with open(os.path.join(self.path, config_file_name)) as config_file:
            config = json.load(config_file)
            self.test_command = config['test_command']
            self.target_files = config['target_files']
        Program.clean_tmp_dir(self.tmp_path)
        copy_tree(self.path, self.tmp_path)
        self.contents = self.parse(self.path, self.target_files)
        self.modification_weights = dict()
        self._modification_points = None

    @abstractmethod
    def __str__(self):
        pass

    def reset_tmp_dir(self):
        Program.clean_tmp_dir(self.tmp_path)
        copy_tree(self.path, self.tmp_path)

    @property
    def tmp_path(self):
        """
        :return: The path of the temporary dirctory
        :rtype: str
        """
        return os.path.join(Program.TMP_DIR, self.name)

    @property
    @abstractmethod
    def modification_points(self):
        """
        :return: The list of position of modification points for each target program
        :rtype: dict(str, ?)
        """
        pass

    def select_modification_point(self, target_file, method="random"):
        """
        :param str target_file: The modification point is chosen within target_file
        :param str method: The way how to choose a modification point, *'random'* or *'weighted'*
        :return: The **index** of modification point
        :rtype: int
        """
        import random
        assert target_file in self.target_files
        assert method in ['random', 'weighted']
        candidates = self.modification_points[target_file]
        if method == 'random' or target_file not in self.modification_weights:
            return random.randrange(len(candidates))
        elif method == 'weighted':
            cumulated_weights = sum(self.modification_weights[target_file])
            list_of_prob = list(map(lambda w: float(w)/cumulated_weights, self.modification_weights[target_file]))
            return random.choices(list(range(len(candidates))), weights=list_of_prob, k=1)[0]

    def set_modification_weights(self, target_file, weights):
        """
        :param str target_file: The path to file
        :param weights: The modification weight([0,1]) of each modification points
        :type weights: list(float)
        :return: None
        :rtype: None
        """
        from copy import deepcopy
        assert target_file in self.target_files
        assert len(self.modification_points[target_file]) == len(weights)
        assert not list(filter(lambda w: w < 0 or w > 1, weights))
        self.modification_weights[target_file] = deepcopy(weights)

    def write_to_tmp_dir(self, new_contents):
        """
        Write new contents to the temporary directory of program

        :param new_contents: The new contents of the program.
          Refer to *apply* method of :py:class:`.patch.Patch`
        :type new_contents: dict(str, ?)
        :rtype: None
        """
        for target_file in new_contents:
            with open(os.path.join(self.tmp_path, target_file), 'w') as tmp_file:
                tmp_file.write(Program.to_source(new_contents[target_file]))

    @abstractmethod
    def print_modification_points(self, target_file, indices=None):
        """
        Print the source of each modification points

        :param target_file: The path to target file
        :type target_file: str
        :return: None
        :rtype: None
        """
        pass

    @classmethod
    @abstractmethod
    def to_source(self, contents_of_file):
        """
        Change contents of file to the source code

        :param contents_of_file: The contents of the file which is the parsed form of source code
        :type contents_of_file: ?
        :return: The source code
        :rtype: str
        """
        pass

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

    @abstractmethod
    def parse(self, path, target_files):
        """
        :param str path: The project root path
        :param target_files: The paths to target files from the project root
        :type target_files: list(str)

        :return: The contents of the files, see `Hint`
        :rtype: dict(str, list(str))

        .. hint::
            - key: the file name
            - value: the contents of the file
        """
        pass

    @staticmethod
    def is_python_code(source_path):
        """
        :param source_path: The path of the source file
        :type source_path: str
        :return: whether the file's extention is *.py* or not
        :rtype: bool
        """
        _, file_extension = os.path.splitext(source_path)
        return file_extension == '.py'

    @staticmethod
    def is_java_code(source_path):
        """
        :param source_path: The path of the source file
        :type source_path: str
        :return: whether the file's extention is *.java* or not
        :rtype: bool
        """
        _, file_extension = os.path.splitext(source_path)
        return file_extension == '.java'

    @staticmethod
    def get_file_extension(file_path):
        """
        :param file_path: The path of file
        :type file_path: str
        :return: file extension
        :rtype: str
        """
        _, file_extension = os.path.splitext(file_path)
        return file_extension

    @staticmethod
    def have_the_same_file_extension(file_path_1, file_path_2):
        """
        :param file_path_1: The path of file 1
        :type file_path_1: str
        :param file_path_2: The path of file 2
        :type file_path_2: str
        :return: same or not
        :rtype: bool
        """
        return Program.get_file_extension(file_path_1) == Program.get_file_extension(file_path_2)
