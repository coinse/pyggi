import random
import copy
import subprocess
import sys
import os
import re
import time
import difflib
from enum import Enum
from .program import Program, MnplLevel
from .test_result import TestResult
from .test_result import pyggi_result_parser


class Patch:

    def __init__(self, program):
        self.program = program
        self.test_result = None
        self.edit_list = []
        pass

    def __str__(self):
        return ' | '.join(list(map(lambda e: str(e), self.edit_list)))

    def __len__(self):
        return len(self.edit_list)

    def get_line_diff_count(self):
        insertions, deletions = self.history_to_del_ins()
        return len(insertions) - len(deletions)

    def history_to_del_ins(self):
        insertions = []
        deletions = []
        replacements = {}
        for edit in self.edit_list:
            if edit.edit_type == EditType.DELETE:
                deletions.append((edit.target_file, edit.target_line))
            elif edit.edit_type == EditType.COPY:
                insertions.append((edit.target_file, edit.source_line,
                                   edit.insertion_point))
            elif edit.edit_type == EditType.MOVE:
                deletions.append((edit.target_file, edit.source_line))
                insertions.append((edit.target_file, edit.source_line,
                                   edit.insertion_point))
            elif edit.edit_type == EditType.REPLACE:
                replacements[(edit.target_file,
                              edit.target_line)] = edit.source_line
        for key in replacements:
            target_file, target_line = key
            source_line = replacements[key]
            deletions.append((target_file, target_line))
            insertions.append((target_file, source_line, target_line))
        return (insertions, deletions)

    def print_diff(self):
        self.apply()
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
                    print(diff, end='')
        return

    def clone(self):
        clone_patch = Patch(self.program)
        clone_patch.edit_list = copy.deepcopy(self.edit_list)
        clone_patch.test_result = None
        return clone_patch

    def run_test(self):
        contents = self.apply()
        cwd = os.getcwd()

        os.chdir(self.program.get_tmp_path())
        sprocess = subprocess.Popen(
            ["./" + self.program.test_script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        start = time.time()
        stdout, stderr = sprocess.communicate()
        end = time.time()
        os.chdir(cwd)

        elapsed_time = end - start

        execution_result = re.findall("\[PYGGI_RESULT\]\s*\{(.*?)\}\s",
                                      stdout.decode("ascii"))

        if len(execution_result) == 0:
            self.test_result = TestResult(False, elapsed_time, None)
        else:
            self.test_result = TestResult(
                True, elapsed_time, pyggi_result_parser(execution_result[0]))

        return self.test_result

    def apply(self):
        if self.program.manipulation_level == MnplLevel.PHYSICAL_LINE:
            target_files = self.program.contents.keys()
            empty_codeline_list = []
            for i in range(len(target_files)):
                empty_codeline_list.append([])
            new_contents = dict(zip(target_files, empty_codeline_list))

            insertions, deletions = self.history_to_del_ins()
            for target_file in target_files:
                orig_codeline_list = self.program.contents[target_file]
                new_codeline_list = new_contents[target_file]

                # Create deletions set for target file: (target_file, target_line)
                target_file_deletions = set(
                    filter(lambda x: x[0] == target_file, deletions))
                # Create insertions dict for target file: insertion_point => [target_lines]
                target_file_insertions = list(
                    filter(lambda x: x[0] == target_file, insertions))
                insertion_points = list(
                    set(map(lambda x: x[2], target_file_insertions)))
                target_file_insertions = dict(zip(
                    insertion_points,
                    list(map(lambda key: list(map(lambda x: x[1],
                                                  list(filter(lambda y: y[2] == key,
                                                              target_file_insertions)))),
                             insertion_points))
                ))

                # Gathers the codelines along with applying the patches
                for i in range(len(orig_codeline_list) + 1):
                    # Handle insertions
                    if i in target_file_insertions.keys():
                        for target_line in target_file_insertions[i]:
                            new_codeline_list.append(
                                orig_codeline_list[target_line])
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

    def remove(self, index):
        del self.edit_list[index]

    def add_random_edit(self, operations, ignore_empty_line=True):
        if self.program.manipulation_level == MnplLevel.PHYSICAL_LINE:
            target_files = sorted(self.program.contents.keys())
            edit_type = random.choice(operations)

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
            target_file = weighted_choice(
                list(
                    map(lambda filename: (filename, len(self.program.contents[filename])),
                        target_files)))

            if edit_type == EditType.DELETE:
                target_line = get_random_line_index(target_file,
                                                    ignore_empty_line)
                self.delete(target_file, target_line)
            elif edit_type == EditType.COPY:
                source_line = get_random_line_index(target_file,
                                                    ignore_empty_line)
                insertion_point = get_random_insertion_point(target_file)
                self.copy(target_file, source_line, insertion_point)
            elif edit_type == EditType.MOVE:
                source_line = get_random_line_index(target_file,
                                                    ignore_empty_line)
                insertion_point = get_random_insertion_point(target_file)
                self.move(target_file, source_line, insertion_point)
            elif edit_type == EditType.REPLACE:
                source_line = get_random_line_index(target_file,
                                                    ignore_empty_line)
                target_line = get_random_line_index(target_file,
                                                    ignore_empty_line)
                self.replace(target_file, source_line, target_line)
        return

    def delete(self, target_file, target_line):
        self.edit_list.append(
            Edit(EditType.DELETE, target_file, None, target_line, None))

    def copy(self, target_file, source_line, insertion_point):
        self.edit_list.append(
            Edit(EditType.COPY, target_file, source_line, None,
                 insertion_point))

    def move(self, target_file, source_line, insertion_point):
        self.edit_list.append(
            Edit(EditType.MOVE, target_file, source_line, None,
                 insertion_point))

    def replace(self, target_file, source_line, target_line):
        # Replace line #(target_line) with line #(source_line)
        self.edit_list.append(
            Edit(EditType.REPLACE, target_file, source_line, target_line, None))


class EditType(Enum):
    DELETE = 1
    COPY = 2
    MOVE = 3
    REPLACE = 4


class Edit:

    def __init__(self, edit_type, target_file, source_line, target_line,
                 insertion_point):
        self.edit_type = edit_type
        self.target_file = target_file
        self.source_line = source_line
        self.target_line = target_line
        self.insertion_point = insertion_point

    def __str__(self):
        if self.edit_type == EditType.DELETE:
            return "DELETE {}:{}".format(self.target_file, self.target_line)
        elif self.edit_type == EditType.COPY:
            return "COPY {}:{} -> {}:{}".format(
                self.target_file, self.source_line, self.target_file,
                self.insertion_point)
        elif self.edit_type == EditType.MOVE:
            return "MOVE {}:{} -> {}:{}".format(
                self.target_file, self.source_line, self.target_file,
                self.insertion_point)
        elif self.edit_type == EditType.REPLACE:
            return "REPLACE {}:{} -> {}:{}".format(
                self.target_file, self.source_line, self.target_file,
                self.target_line)
        else:
            return ''

    def __copy__(self):
        return Edit(self.edit_type, self.target_file, self.source_line,
                    self.target_line, self.insertion_point)
