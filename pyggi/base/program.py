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
from copy import deepcopy
from abc import ABC, abstractmethod
from distutils.dir_util import copy_tree
from . import InvalidPatchError
from .. import PYGGI_DIR
from ..utils import Logger

class StatusCode(enum.Enum):
    NORMAL = 0
    TIME_OUT = 1
    PARSE_ERROR = 2

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

    def __init__(self, path, config=None):
        self.timestamp = str(int(time.time()))
        self.path = os.path.abspath(path.strip())
        self.name = os.path.basename(self.path)
        self.logger = Logger(self.name + '_' + self.timestamp)
        if not config:
            with open(os.path.join(self.path, self.__class__.CONFIG_FILE_NAME)) as config_file:
                config = json.load(config_file)
        self.test_command = config['test_command']
        self.target_files = config['target_files']
        self.load_contents()
        assert self.modification_points
        assert self.modification_weights
        assert self.contents
        self.create_tmp_variant()
        self.logger.info("Path to the temporal program variants: {}".format(self.tmp_path))

    def __str__(self):
        return "{}({}):{}".format(self.__class__.__name__, self.path, ",".join(self.target_files))

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

    @abstractmethod
    def load_contents(self):
        pass

    def set_weight(self, modification_point, weight):
        """
        :param str target_file: The path to file
        :param weights: The modification weight([0,1]) of each modification points
        :type weight: float
        :return: None
        :rtype: None
        """
        assert 0 <= weight <= 1
        file, index = modification_point
        self.modification_weights[file][index] = weight

    @abstractmethod
    def get_source(self, target_file, indices=None):
        """
        :param target_file: The path to target file
        :param indices: the indices of modification points
        :type target_file: str
        :return: the sources of each modification point
        :rtype: str
        """
        pass

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
                tmp_file.write(self.__class__.dump(new_contents[target_file]))

    @classmethod
    @abstractmethod
    def dump(cls, contents, file_name):
        """
        Convert contents of file to the source code

        :param contents_of_file: The contents of the file which is the parsed form of source code
        :type contents_of_file: ?
        :return: The source code
        :rtype: str
        """
        pass

    def get_modified_contents(self, patch):
        target_files = self.contents.keys()
        modification_points = deepcopy(self.modification_points)
        new_contents = deepcopy(self.contents)
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
        for target_file in new_contents:
            with open(os.path.join(self.tmp_path, target_file), 'w') as tmp_file:
                tmp_file.write(self.__class__.dump(new_contents, target_file))
        return new_contents

    def run(self, timeout=15):
        """
        Run the test script of the temporary variant

        :param float timeout: The time limit of test run (unit: seconds)
        :return: The fitness value of the patch
        """
        Result = collections.namedtuple("Result", 'status_code elapsed_time stdout stderr')
        cwd = os.getcwd()
        os.chdir(self.tmp_path)
        sprocess = subprocess.Popen(
            shlex.split(self.test_command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        try:
            start = time.time()
            stdout, stderr = sprocess.communicate(timeout=timeout)
            end = time.time()
            result = Result(status_code=StatusCode.NORMAL,
                            elapsed_time=(end - start),
                            stdout=stdout.decode("ascii"),
                            stderr=stderr.decode("ascii"))
        except subprocess.TimeoutExpired:
            result = Result(status_code=StatusCode.TIME_OUT,
                            elapsed_time=None,
                            stdout=None,
                            stderr=None)
        os.chdir(cwd)
        return result

    def compute_fitness(self, elapsed_time, stdout, stderr):
        try:
            return float(stdout.strip())
        except:
            raise InvalidPatchError

    def evaluate_patch(self, patch, timeout=15):
        # apply + run_test
        self.apply(patch)
        result = self.run(timeout)

        if result.status_code == StatusCode.TIME_OUT:
            return StatusCode.TIME_OUT, None

        try:
            fitness = self.compute_fitness(result.elapsed_time, result.stdout, result.stderr)
        except InvalidPatchError:
            return StatusCode.PARSE_ERROR, None

        return StatusCode.NORMAL, fitness