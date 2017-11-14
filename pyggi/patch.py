import random
import copy
import subprocess
import sys
import os
import re
import time
import difflib
from .program import *
from .edit import *
from .test_result import *


class Patch(object):

    def __init__(self, program):
        self.program = program
        self.test_result = None
        self.edit_list = []
        pass

    def __str__(self):
        return ' | '.join(list(map(lambda e: str(e), self.edit_list)))

    def __len__(self):
        return len(self.edit_list)

    def __eq__(self, other):
        return self.edit_list == other.edit_list

    @property
    def _deletions(self):
        deletions = list()
        for edit in self.edit_list:
            if edit.edit_type == EditType.DELETE:
                deletions.append(edit.target)
            elif edit.edit_type == EditType.MOVE:
                deletions.append(edit.source)
            elif edit.edit_type == EditType.REPLACE:
                deletions.append(edit.target)
        return list(set(deletions))

    @property
    def _insertions(self):
        insertions, replacements = list(), dict()
        for edit in self.edit_list:
            if edit.edit_type == EditType.COPY:
                insertions.append((edit.source, edit.target))
            elif edit.edit_type == EditType.MOVE:
                insertions.append((edit.source, edit.target))
            elif edit.edit_type == EditType.REPLACE:
                replacements[edit.target] = edit.source
        for target in replacements:
            source = replacements[target]
            insertions.append((source, target))
        return insertions

    @property
    def edit_size(self):
        return len(self._insertions) - len(self._deletions)

    def clone(self):
        clone_patch = Patch(self.program)
        clone_patch.edit_list = copy.deepcopy(self.edit_list)
        clone_patch.test_result = None
        return clone_patch

    def get_diff(self):
        self.apply()
        diffs = ''
        for i in range(len(self.program.target_files)):
            original_target_file = os.path.join(self.program.path,
                                                self.program.target_files[i])
            modified_target_file = os.path.join(self.program.get_tmp_path(),
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

    def delete(self, target):
        self.edit_list.append(Edit(EditType.DELETE, target=target))

    def copy(self, source, target):
        self.edit_list.append(Edit(EditType.COPY, source=source, target=target))

    def move(self, source, target):
        self.edit_list.append(Edit(EditType.MOVE, source=source, target=target))

    def replace(self, source, target):
        # Replace line #(target) with line #(source)
        self.edit_list.append(
            Edit(EditType.REPLACE, source=source, target=target))

    def remove(self, index):
        del self.edit_list[index]

    def add_random_edit(
            self,
            edit_types=[EditType.DELETE, EditType.COPY, EditType.REPLACE],
            ignore_empty_line=True):
        if self.program.manipulation_level == MnplLevel.PHYSICAL_LINE:
            target_files = sorted(self.program.contents.keys())
            edit_type = random.choice(edit_types)

            # Choice according to the probability distribution
            def weighted_choice(choice_weight_list):
                total = sum(weight for choice, weight in choice_weight_list)
                ridx = random.uniform(0, total)
                upto = 0
                for choice, weight in choice_weight_list:
                    if upto + weight >= ridx:
                        return choice
                    upto += weight
                assert False, "weighted_choice error."

            def get_random_line_index(target_file, ignore_empty_line=True):
                while True:
                    index = random.randrange(
                        0, len(self.program.contents[target_file]))
                    if not ignore_empty_line or len(
                            self.program.contents[target_file][index]) > 0:
                        break
                return index

            def get_random_insertion_point(target_file):
                return random.randrange(
                    0, len(self.program.contents[target_file]) + 1)

            # Choose files based on the probability distribution by number of the code lines
            source_file = weighted_choice(
                list(
                    map(lambda filename: (filename, len(self.program.contents[filename])),
                        target_files)))
            target_file = weighted_choice(
                list(
                    map(lambda filename: (filename, len(self.program.contents[filename])),
                        target_files)))

            source, target = None, None
            if edit_type == EditType.DELETE:
                target = (target_file, get_random_line_index(
                    target_file, ignore_empty_line))
                self.delete(target)
            elif edit_type == EditType.COPY:
                source = (source_file, get_random_line_index(
                    source_file, ignore_empty_line))
                target = (target_file, get_random_insertion_point(target_file))
                self.copy(source, target)
            elif edit_type == EditType.MOVE:
                source = (source_file, get_random_line_index(
                    source_file, ignore_empty_line))
                target = (target_file, get_random_insertion_point(target_file))
                self.move(source, target)
            elif edit_type == EditType.REPLACE:
                source = (source_file, get_random_line_index(
                    source_file, ignore_empty_line))
                while not target or source == target:
                    target = (target_file, get_random_line_index(
                        target_file, ignore_empty_line))
                self.replace(source, target)
        return

    def apply(self):
        if self.program.manipulation_level == MnplLevel.PHYSICAL_LINE:
            target_files = self.program.contents.keys()
            new_contents = dict()

            for target_file in target_files:
                new_contents[target_file] = list()
                orig_codeline_list = self.program.contents[target_file]
                new_codeline_list = new_contents[target_file]

                # Create deletions set for target file: (target_file, target_index)
                target_file_deletions = set(
                    filter(lambda x: x[0] == target_file, self._deletions))
                # Create insertions dict for target file: insertion_point => [target_index*]
                target_file_insertions = list(
                    filter(lambda x: x[1][0] == target_file, self._insertions))
                insertion_points = list(
                    set(map(lambda x: x[1][1], target_file_insertions)))
                target_file_insertions = dict(zip(
                    insertion_points,
                    list(map(lambda key: list(map(lambda x: x[0],
                                                  list(filter(lambda y: y[1][1] == key,
                                                              target_file_insertions)))),
                             insertion_points))
                ))

                # Gathers the codelines along with applying the patches
                for i in range(len(orig_codeline_list) + 1):
                    # Handle insertions
                    if i in target_file_insertions.keys():
                        for source in target_file_insertions[i]:
                            new_codeline_list.append(
                                self.program.contents[source[0]][source[1]])
                    # Handle deletions
                    if i < len(orig_codeline_list) and (
                            target_file, i) not in target_file_deletions:
                        new_codeline_list.append(orig_codeline_list[i])

            for target_file in sorted(new_contents.keys()):
                target_file_path = os.path.join(self.program.get_tmp_path(),
                                                target_file)
                with open(target_file_path, 'w') as f:
                    f.write('\n'.join(new_contents[target_file]) + '\n')
        return

    def run_test(self, timeout=15):
        contents = self.apply()
        cwd = os.getcwd()

        os.chdir(self.program.get_tmp_path())
        sprocess = subprocess.Popen(
            ["./" + self.program.test_script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        try:
            start = time.time()
            stdout, stderr = sprocess.communicate(timeout=timeout)
            end = time.time()
            elapsed_time = end - start
            execution_result = re.findall("\[PYGGI_RESULT\]\s*\{(.*?)\}\s",
                                          stdout.decode("ascii"))
            if len(execution_result) == 0:
                self.test_result = TestResult(False, elapsed_time, None)
            else:
                self.test_result = TestResult(True, elapsed_time,
                                              TestResult.pyggi_result_parser(
                                                  execution_result[0]))
        except subprocess.TimeoutExpired:
            elapsed_time = timeout * 1000
            self.test_result = TestResult(False, elapsed_time, None)
        os.chdir(cwd)

        return self.test_result
