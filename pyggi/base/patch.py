"""
This module contains Patch class.
"""
import os
from copy import deepcopy
from .atomic_operator import AtomicOperator
from .custom_operator import CustomOperator
from ..utils.result_parsers import InvalidPatchError, standard_result_parser

class Patch:
    """

    Patch is a sequence of edit operators: both atomic and custom.
    During search iteration, PYGGI modifies the source code of the target program
    by applying a candidate patch. Subsequently, it runs the test script to collect
    dynamic information, such as the execution time or any other user-provided
    properties, via the predefined format that PYGGI recognises.

    """
    def __init__(self, program):
        self.program = program
        self.fitness = None
        self.elapsed_time = None
        self.timeout = False
        self.compiled = True
        self.edit_list = []

    def __str__(self):
        return ' | '.join(list(map(str, self.edit_list)))

    def __len__(self):
        return len(self.edit_list)

    def __eq__(self, other):
        return self.edit_list == other.edit_list

    def clone(self):
        """
        Create a new patch which has the same sequence of edits with the current one.

        :return: The created Patch
        :rtype: :py:class:`.Patch`
        """
        clone_patch = Patch(self.program)
        clone_patch.edit_list = deepcopy(self.edit_list)
        clone_patch.fitness = None
        clone_patch.elapsed_time = None
        return clone_patch

    @property
    def diff(self) -> str:
        """
        Compare the source codes of original program and the patch-applied program
        using *difflib* module(https://docs.python.org/3.6/library/difflib.html).

        :return: The file comparison result
        :rtype: str
        """
        import difflib
        self.apply()
        diffs = ''
        for i in range(len(self.program.target_files)):
            original_target_file = os.path.join(self.program.path,
                                                self.program.target_files[i])
            modified_target_file = os.path.join(self.program.tmp_path,
                                                self.program.target_files[i])
            with open(original_target_file) as orig, open(
                modified_target_file) as modi:
                for diff in difflib.context_diff(
                        orig.readlines(),
                        modi.readlines(),
                        fromfile=original_target_file,
                        tofile=modified_target_file):
                    diffs += diff
        return diffs

    def run_test(self, timeout=15, result_parser=standard_result_parser):
        """
        Run the test script provided by the user
        which is placed within the project directory.

        :param float timeout: The time limit of test run (unit: seconds)
        :param result_parser: The parser of test output
          (default: :py:meth:`.utils.result_parsers.standard_result_parser`)
        :type result_parser: None or callable((str, str), :py:class:`.TestResult`)
        :return: The fitness value of the patch
        """
        import time
        import subprocess
        import shlex
        self.apply()
        cwd = os.getcwd()

        os.chdir(self.program.tmp_path)
        sprocess = subprocess.Popen(
            shlex.split(self.program.test_command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        try:
            start = time.time()
            stdout, stderr = sprocess.communicate(timeout=timeout)
            self.elapsed_time = time.time() - start
            self.fitness = result_parser(stdout.decode("ascii"), stderr.decode("ascii"))
        except subprocess.TimeoutExpired:
            self.elapsed_time = timeout * 1000 # seconds to milliseconds
            self.timeout = True
        except InvalidPatchError:
            self.compiled = False

        os.chdir(cwd)

        return self.fitness

    def add(self, edit):
        """
        Add an edit to the edit list

        :param edit: The edit to be added
        :type edit: :py:class:`.atomic_operator.AtomicOperator` or :py:class:`.custom_operator.CustomOperator`
        :return: None
        """
        assert isinstance(edit, (AtomicOperator, CustomOperator))
        assert edit.is_valid_for(self.program)
        self.edit_list.append(edit)

    def remove(self, index: int):
        """
        Remove an edit from the edit list

        :param int index: The index of edit to delete
        """
        del self.edit_list[index]

    def get_atomics(self, atomic_class_name=None):
        """
        Combine all the atomic operators of the edits.
        A custom operator is originally a sequence of atomic operators,
        and a patch is a sequence of the edits.
        So this is a sort of flattening process.

        :return: The atomic operators, see *Hint*.
        :rtype: list(:py:class:`.atomic_operator.AtomicOperator`)
        """
        atomics = []
        for edit in self.edit_list:
            for atomic in edit.atomic_operators:
                if not atomic_class_name or atomic_class_name == atomic.__class__.__name__:
                    atomics.append(atomic)
        return atomics
    
    def apply(self):
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
        target_files = self.program.contents.keys()
        modification_points = deepcopy(self.program.modification_points)
        new_contents = deepcopy(self.program.contents)
        for target_file in target_files:
            atomics = list(filter(lambda a: a.modification_point[0] == target_file, self.get_atomics()))
            for atomic in atomics:
                atomic.apply(self.program, new_contents, modification_points)
        #self.program.reset_tmp_dir()
        for target_file in new_contents:
            with open(os.path.join(self.program.tmp_path, target_file), 'w') as tmp_file:
                tmp_file.write(self.program.__class__.to_source(new_contents[target_file]))
        return new_contents
