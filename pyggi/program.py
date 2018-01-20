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
    LINE = 'line'
    AST = 'AST'

    @classmethod
    def is_valid(cls, value):
        """
        :param value: The value of enum to check

        :return: Whether there is an enum that has a value equal to the `value`
        :rtype: bool

        .. hint::
            There are some examples,
            ::
                MnplLevel.is_valid('line')
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

    def __init__(self, path, manipulation_level=MnplLevel.LINE,
                 config_file_name=CONFIG_FILE_NAME):
        assert isinstance(manipulation_level, MnplLevel)
        self.path = path.strip()
        if self.path.endswith('/'):
            self.path = self.path[:-1]
        self.name = os.path.basename(self.path)
        self.logger = Logger(self.name)
        self.manipulation_level = manipulation_level
        with open(os.path.join(self.path, config_file_name)) as config_file:
            config = json.load(config_file)
            self.test_command = config['test_command']
            self.target_files = config['target_files']
        Program.clean_tmp_dir(self.tmp_path)
        copy_tree(self.path, self.tmp_path)
        self.contents = Program.parse(self.manipulation_level, self.path, self.target_files)
        self._modification_points = None

    def __str__(self):
        if self.manipulation_level == MnplLevel.LINE:
            code = ''
            for k in sorted(self.contents.keys()):
                idx = 0
                for line in self.contents[k]:
                    code += "{}\t: {}\t: {}\n".format(k, idx, line)
                    idx += 1
            return code
        return self.target_files

    @property
    def modification_points(self):
        """
        :return: The list of position of modification points for each target program
        :rtype: dict(str, ?)
        """
        assert isinstance(self.manipulation_level, MnplLevel)

        if self._modification_points:
            return self._modification_points

        self._modification_points = dict()
        if self.manipulation_level == MnplLevel.LINE:
            for target_file in self.target_files:
                self._modification_points[target_file] = list(range(len(self.contents[target_file])))
        elif self.manipulation_level == MnplLevel.AST:
            for target_file in self.target_files:
                if Program.is_python_code(target_file):
                    from .helper import stmt_python
                    self._modification_points[target_file] = stmt_python.get_modification_points(
                        self.contents[target_file])
        return self._modification_points

    @property
    def tmp_path(self):
        """
        :return: The path of the temporary dirctory
        :rtype: str
        """
        return os.path.join(Program.TMP_DIR, self.name)

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
                tmp_file.write(Program.to_source(self.manipulation_level, new_contents[target_file]))

    def print_modification_points(self, target_file):
        """
        Print the source of each modification points

        :param target_file: The path to target file
        :type target_file: str
        :return: None
        :rtype: None
        """
        title_format = "=" * 25 + " {} {} " + "=" * 25
        if self.manipulation_level == MnplLevel.LINE:
            for i, index in enumerate(self.modification_points[target_file]):
                print(title_format.format('line', i))
                print(self.contents[target_file][index])
        elif self.manipulation_level == MnplLevel.AST:
            if Program.is_python_code(target_file):
                import astor
                from .helper import stmt_python
                for i, pos in enumerate(self.modification_points[target_file]):
                    print(title_format.format('node', i))
                    blk, idx = stmt_python.pos_2_block_n_index(self.contents[target_file], pos)
                    print(astor.to_source(blk[idx]))

    @classmethod
    def to_source(cls, manipulation_level, contents_of_file):
        """
        Change contents of file to the source code

        :param manipulation_level: The manipulation level of the program
        :type manipulation_level: :py:class:`MnplLevel`
        :param contents_of_file: The contents of the file which is the parsed form of source code
        :type contents_of_file: ?
        :return: The source code
        :rtype: str
        """
        if manipulation_level == MnplLevel.LINE:
            return '\n'.join(contents_of_file) + '\n'
        elif manipulation_level == MnplLevel.AST:
            import astor
            return astor.to_source(contents_of_file)
        return ''

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
        assert isinstance(manipulation_level, MnplLevel)
        if manipulation_level == MnplLevel.LINE:
            contents = {}
            for target in target_files:
                with open(os.path.join(path, target), 'r') as target_file:
                    contents[target] = list(
                        map(str.rstrip, target_file.readlines()))
            return contents
        elif manipulation_level == MnplLevel.AST:
            import ast
            import astor
            contents = {}
            for target in target_files:
                if cls.is_python_code(target):
                    root = astor.parse_file(os.path.join(path, target))
                    contents[target] = root
                else:
                    raise Exception('Program', '{} file is not supported'.format(cls.get_file_extension(target)))
            return contents
        return None

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
