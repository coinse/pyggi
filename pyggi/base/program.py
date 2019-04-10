"""

This module contains GranularityLevel and Program class.

"""
import os
import shutil
import json
import time
import pathlib
import random
import enum
import collections
import subprocess
import shlex
import copy
import difflib
from abc import ABC, abstractmethod
from distutils.dir_util import copy_tree
from .. import PYGGI_DIR
from ..utils import Logger

class StatusCode(enum.Enum):
    NORMAL = 0
    TIME_OUT = 1
    PARSE_ERROR = 2

class ParseError(Exception):
    pass

class AbstractEngine(ABC):
    @abstractmethod
    def get_contents(self, file_path):
        pass

    @abstractmethod
    def get_modification_points(self, contents_of_file):
        pass

    @abstractmethod
    def get_source(self, program, file_name, index):
        pass

    @abstractmethod
    def dump(self, contents_of_file):
        pass

class AbstractProgram(ABC):
    """
    Program encapsulates the original source code.
    Currently, PYGGI stores the source code as a list of code lines,
    as lines are the only supported unit of modifications.
    For modifications at other granularity levels,
    this class needs to process and store the source code accordingly
    (for example, by parsing and storing the AST).
    """
    CONFIG_FILE_NAME = '.pyggi.config'
    TMP_DIR = os.path.join(PYGGI_DIR, 'tmp_variants')
    SAVE_DIR = os.path.join(PYGGI_DIR, 'saved_variants')
    Result = collections.namedtuple("Result", 'status_code elapsed_time stdout stderr')

    def __init__(self, path, config=None):
        self.timestamp = str(int(time.time()))
        self.path = os.path.abspath(path.strip())
        self.name = os.path.basename(self.path)
        self.logger = Logger(self.name + '_' + self.timestamp)

        # Configuration
        self.load_config(path, config)
        assert self.test_command
        assert self.target_files

        # Associate each file to its engine
        self.load_engines()

        # Load actual contents using the engines
        self.load_contents()
        assert self.modification_points
        assert self.contents

        # Create the temporary directory
        self.create_tmp_variant()

        self.logger.info("Path to the temporal program variants: {}".format(self.tmp_path))

    def __str__(self):
        return "{}({}):{}".format(self.__class__.__name__, self.path, ",".join(self.target_files))

    def load_config(self, path, config):
        assert config is None or isinstance(config, str) or isinstance(config, dict)

        from_file = False

        if config:
            if isinstance(config, str):
                config_file_name = config
                from_file = True
        else:
            config_file_name = AbstractProgram.CONFIG_FILE_NAME
            from_file = True

        if from_file:
            with open(os.path.join(self.path, config_file_name)) as config_file:
                config = json.load(config_file)

        self.test_command = config['test_command']
        self.target_files = config['target_files']

        return config

    @classmethod
    @abstractmethod
    def get_engine(cls, file_name):
        pass

    def load_engines(self):
        # Associate each file to its engine
        self.engines = dict()
        engine_instances = dict()
        for file_name in self.target_files:
            engine_class = self.__class__.get_engine(file_name)
            if not engine_class in engine_instances:
                engine_instances[file_name] = engine_class()
            self.engines[file_name] = engine_instances[file_name]

    def load_contents(self):
        self.contents = {}
        self.modification_points = dict()
        self.modification_weights = dict()
        for file_name in self.target_files:
            engine = self.engines[file_name]
            self.contents[file_name] = engine.get_contents(os.path.join(self.path, file_name))
            self.modification_points[file_name] = engine.get_modification_points(self.contents[file_name])

    def set_weight(self, file_name, index, weight):
        """
        :param file_name: the file containing the modification point
        :param index: the index of the modification point
        :param weight: The modification weight([0,1]) of the modification point
        :type file_name: str
        :type index: int
        :type weight: float
        :return: None
        :rtype: None
        """
        assert 0 <= weight <= 1
        if file_name not in self.modification_weights:
            self.modification_weights[file_name] = [1.0] * len(self.modification_points[file_name])
        self.modification_weights[file_name][index] = weight

    def get_source(self, file_name, index):
        """
        :param file_name: the file containing the modification point
        :param index: the index of the modification point
        :type file_name: str
        :type index: int
        :return: the sources of the modification point
        :rtype: str
        """
        return self.engines[file_name].get_source(self, file_name, index)

    def random_target(self, target_file=None, method="random"):
        """
        :param str target_file: The modification point is chosen within target_file
        :param str method: The way how to choose a modification point, *'random'* or *'weighted'*
        :return: The **index** of modification point
        :rtype: int
        """
        if target_file is None:
            target_file = target_file or random.choice(self.target_files)
        assert target_file in self.target_files
        assert method in ['random', 'weighted']
        candidates = self.modification_points[target_file]
        if method == 'random' or target_file not in self.modification_weights:
            return (target_file, random.randrange(len(candidates)))
        elif method == 'weighted':
            cumulated_weights = sum(self.modification_weights[target_file])
            list_of_prob = list(map(lambda w: float(w)/cumulated_weights, self.modification_weights[target_file]))
            return (target_file, random.choices(list(range(len(candidates))), weights=list_of_prob, k=1)[0])

    @property
    def tmp_path(self):
        """
        :return: The path of the temporary dirctory
        :rtype: str
        """
        return os.path.join(self.__class__.TMP_DIR, self.name, self.timestamp)

    def create_tmp_variant(self):
        """
        Clean the temporary project directory if it exists.

        :param str tmp_path: The path of directory to clean.
        :return: None
        """
        pathlib.Path(self.tmp_path).mkdir(parents=True, exist_ok=True)
        copy_tree(self.path, self.tmp_path)

    def remove_tmp_variant(self):
        shutil.rmtree(self.tmp_path)

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
                tmp_file.write(self.__class__.dump(new_contents, target_file))

    @classmethod
    def dump(cls, contents, file_name):
        """
        Convert contents of file to the source code

        :param contents_of_file: The contents of the file which is the parsed form of source code
        :type contents_of_file: ?
        :return: The source code
        :rtype: str
        """
        engine = cls.get_engine(file_name)
        return engine().dump(contents[file_name])

    def get_modified_contents(self, patch):
        target_files = self.contents.keys()
        modification_points = copy.deepcopy(self.modification_points)
        new_contents = copy.deepcopy(self.contents)
        for target_file in target_files:
            edits = list(filter(lambda a: a.target[0] == target_file, patch.edit_list))
            for edit in edits:
                edit.apply(self, new_contents, modification_points)
        return new_contents

    def apply(self, patch):
        """
        This method applies the patch to the target program.
        It does not directly modify the source code of the original program,
        but modifies the copied program within the temporary directory.

        :return: The contents of the patch-applied program, See *Hint*.
        :rtype: dict(str, list(str))

        .. hint::
            - key: The target file name(path) related to the program root path
            - value: The contents of the file
        """
        new_contents = self.get_modified_contents(patch)
        self.write_to_tmp_dir(new_contents)
        return new_contents

    def exec_cmd(self, cmd, timeout=15):
        cwd = os.getcwd()
        os.chdir(self.tmp_path)
        sprocess = subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        try:
            start = time.time()
            stdout, stderr = sprocess.communicate(timeout=timeout)
            end = time.time()
            result = self.__class__.Result(status_code=StatusCode.NORMAL,
                            elapsed_time=(end - start),
                            stdout=stdout.decode("ascii"),
                            stderr=stderr.decode("ascii"))
        except subprocess.TimeoutExpired:
            result = self.__class__.Result(status_code=StatusCode.TIME_OUT,
                            elapsed_time=None,
                            stdout=None,
                            stderr=None)
        os.chdir(cwd)
        return result

    def run(self, timeout=15):
        """
        Run the test script of the temporary variant

        :param float timeout: The time limit of test run (unit: seconds)
        :return: The fitness value of the patch
        """
        return self.exec_cmd(self.test_command, timeout)

    def compute_fitness(self, elapsed_time, stdout, stderr):
        try:
            return float(stdout.strip())
        except:
            raise ParseError

    def evaluate_patch(self, patch, timeout=15):
        # apply + run
        self.apply(patch)
        result = self.run(timeout)

        if result.status_code == StatusCode.TIME_OUT:
            return StatusCode.TIME_OUT, None

        try:
            fitness = self.compute_fitness(result.elapsed_time, result.stdout, result.stderr)
        except ParseError:
            return StatusCode.PARSE_ERROR, None

        return StatusCode.NORMAL, fitness

    def diff(self, patch) -> str:
        """
        Compare the source codes of original program and the patch-applied program
        using *difflib* module(https://docs.python.org/3.6/library/difflib.html).

        :return: The file comparison result
        :rtype: str
        """
        diffs = ''
        new_contents = self.get_modified_contents(patch)
        for file_name in self.target_files:
            orig = self.dump(self.contents, file_name)
            modi = self.dump(new_contents, file_name)
            orig_list = list(map(lambda s: s+'\n', orig.splitlines()))
            modi_list = list(map(lambda s: s+'\n', modi.splitlines()))
            for diff in difflib.context_diff(orig_list, modi_list, fromfile="before: " + file_name,
                                                                   tofile="after: " + file_name):
                diffs += diff
        return diffs