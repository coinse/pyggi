import random
import copy
import subprocess
import sys
import os
import re
from .program import Program
from .test_result import TestResult
from .test_result import pyggi_result_parser

class Patch:
    def __init__(self, program):
        self.program = program
        self.test_result = None
        # A list of deletions: (target_file, target_line)
        self.deletions = []
        # A list of insertions: (target_file, target_line, insertion_point)
        self.insertions = []
        self.history = []
        pass

    def __str__(self):
        return ' | '.join(self.history)
    
    def __len__(self):
        return len(self.history)

    def get_diff(self):
        self.apply()
        stdoutdata = ''
        for i in range(len(self.program.target_files)):
            original_target_file = os.path.join(self.program.project_path, self.program.target_files[i])
            modified_target_file = os.path.join(self.program.tmp_project_path, self.program.target_files[i])
            stdoutdata += subprocess.getoutput("diff -u {} {}".format(original_target_file, modified_target_file))
        return stdoutdata
    
    def clone(self):
        clone_patch = Patch(self.program)
        clone_patch.deletions = copy.deepcopy(self.deletions)
        clone_patch.insertions = copy.deepcopy(self.insertions)
        clone_patch.history = copy.deepcopy(self.history)
        clone_patch.test_result = None
        return clone_patch

    def run_test(self):
        contents = self.apply()
        test_script_path = os.path.join(self.program.tmp_project_path, self.program.test_script_path)
        sprocess = subprocess.Popen(
            ['time', "./" + test_script_path, self.program.tmp_project_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = sprocess.communicate()
        
        # Execution time (real, user, sys)
        real_time, user_time, sys_time = re.findall(
            "\s+(.*)\sreal\s+(.*)\suser\s+(.*)\ssys",
            stderr.decode("ascii"))[-1]

        execution_time = {
            'real': real_time,
            'user': user_time,
            'sys': sys_time
        }

        # print(stdout.decode("ascii"))
        execution_result = re.findall(
            "\[PYGGI_RESULT\]\s*\{(.*?)\}\s",
            stdout.decode("ascii"))

        if len(execution_result) == 0:
            print("Build failed!")
            self.test_result = TestResult(False, execution_time, None)
        else:
            print("Build succeed!")
            self.test_result = TestResult(True, execution_time, pyggi_result_parser(execution_result[0]))

        return self.test_result
    
    def apply(self):
        if self.program.manipulation_level == 'physical_line':
            target_files = self.program.contents.keys()
            empty_codeline_list = []
            for i in range(len(target_files)):
                empty_codeline_list.append([])
            new_contents = dict(zip(target_files, empty_codeline_list))

            for target_file in target_files:
                orig_codeline_list = self.program.contents[target_file]
                new_codeline_list = new_contents[target_file]

                # Create deletions set for target file: (target_file, target_line)
                target_file_deletions = set(
                    filter(lambda x: x[0] == target_file, self.deletions))
                # Create insertions dict for target file: insertion_point => [target_lines]
                target_file_insertions = list(
                    filter(lambda x: x[0] == target_file, self.insertions))
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
                target_file_path = os.path.join(self.program.tmp_project_path, target_file)
                with open(target_file_path, 'w') as f:
                    f.write('\n'.join(new_contents[target_file]) + '\n')
        else:
            print("[Error] invalid manipulation level: {}".format(
                self.program.manipulation_level))
            sys.exit()

    def remove(self):
        last_edit = self.history.pop()
        edit_type = last_edit.split()[0].strip()
        if edit_type == "DELETE":
            self.deletions.pop()
        elif edit_type == "COPY":
            self.insertions.pop()
        elif edit_type == "MOVE":
            self.insertions.pop()
            self.deletions.pop()

    def add_random_edit(self):
        if self.program.manipulation_level == 'physical_line':
            target_files = sorted(self.program.contents.keys())
            edit_type = random.choice(['delete', 'copy', 'move'])
            # line number starts from 0
            while True:
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

                # Choose files based on the probability distribution by number of the code lines
                target_file = weighted_choice(list(map(lambda filename: (filename, len(self.program.contents[filename])),
                                                   target_files)))
                target_line = random.randrange(
                    0, len(self.program.contents[target_file]))
                if not edit_type == 'delete' or (
                        target_file, target_line) not in self.deletions:
                    break
            if edit_type == 'delete':
                self.delete(target_file, target_line)
            elif edit_type == 'copy':
                insertion_point = random.randrange(
                    0, len(self.program.contents[target_file]) + 1)
                self.copy(target_file, target_line, insertion_point)
            elif edit_type == 'move':
                insertion_point = random.randrange(
                    0, len(self.program.contents[target_file]) + 1)
                self.move(target_file, target_line, insertion_point)
        else:
            print("[Error] invalid manipulation level: {}".format(
                self.program.manipulation_level))
            sys.exit()
        return

    def delete(self, target_file, target_line):
        self.history.append("DELETE {}: {}".format(target_file, target_line))
        self.deletions.append((target_file, target_line))

    def copy(self, target_file, target_line, insertion_point):
        self.history.append("COPY {}: {} -> {}".format(target_file, target_line,
                                                       insertion_point))
        self.insertions.append((target_file, target_line, insertion_point))

    def move(self, target_file, target_line, insertion_point):
        self.history.append("MOVE {}: {} -> {}".format(target_file, target_line,
                                                       insertion_point))
        self.insertions.append((target_file, target_line, insertion_point))
        self.deletions.append((target_file, target_line))
