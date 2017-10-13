import random
import copy
import subprocess
import sys
import os
import re
import time
from .program import Program
from .test_result import TestResult
from .test_result import pyggi_result_parser

class Patch:
    def __init__(self, program):
        self.program = program
        self.test_result = None
        self.history = []
        pass

    def __str__(self):
        return ' | '.join(list(map(lambda e: str(e), self.history)))
    
    def __len__(self):
        return len(self.history)

    def history_to_del_ins(self):
        insertions = []
        deletions = []
        for edit in self.history:
            if edit.edit_type == "DELETE":
                if not (edit.target_file, edit.target_line) in deletions: 
                    deletions.append((edit.target_file, edit.target_line))
            elif edit.edit_type == "COPY":
                insertions.append((edit.target_file, edit.target_line, edit.insertion_point))
            elif edit.edit_type == "MOVE":
                if not (edit.target_file, edit.target_line) in deletions: 
                    deletions.append((edit.target_file, edit.target_line))
                insertions.append((edit.target_file, edit.target_line, edit.insertion_point))
        return (insertions, deletions)
    
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
        clone_patch.history = copy.deepcopy(self.history)
        clone_patch.test_result = None
        return clone_patch

    def run_test(self):
        contents = self.apply()
        test_script_path = os.path.join(self.program.tmp_project_path, self.program.test_script_path)
        sprocess = subprocess.Popen(
            ["./" + test_script_path, self.program.tmp_project_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        
        start = time.time()
        stdout, stderr = sprocess.communicate()
        end = time.time()
        
        elapsed_time = end - start
        
        execution_result = re.findall(
            "\[PYGGI_RESULT\]\s*\{(.*?)\}\s",
            stdout.decode("ascii"))

        if len(execution_result) == 0:
            print("Build failed!")
            self.test_result = TestResult(False, elapsed_time, None)
        else:
            print("Build succeed!")
            self.test_result = TestResult(True, elapsed_time, pyggi_result_parser(execution_result[0]))

        return self.test_result
    
    def apply(self):
        if self.program.manipulation_level == 'physical_line':
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
                target_file_path = os.path.join(self.program.tmp_project_path, target_file)
                with open(target_file_path, 'w') as f:
                    f.write('\n'.join(new_contents[target_file]) + '\n')
        else:
            print("[Error] invalid manipulation level: {}".format(
                self.program.manipulation_level))
            sys.exit()

    def remove(self, index):
        del self.history[index]

    def add_random_edit(self, ignore_empty_line=True):
        if self.program.manipulation_level == 'physical_line':
            target_files = sorted(self.program.contents.keys())
            edit_type = random.choice(['DELETE', 'COPY', 'MOVE'])
            insertions, deletions = self.history_to_del_ins()
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
                target_line = random.randrange(0, len(self.program.contents[target_file]))
                if (target_file, target_line) in deletions:
                    continue
                if ignore_empty_line and len(self.program.contents[target_file][target_line]) > 0:
                    break

            if edit_type == 'DELETE':
                self.delete(target_file, target_line)
            elif edit_type == 'COPY':
                insertion_point = random.randrange(
                    0, len(self.program.contents[target_file]) + 1)
                self.copy(target_file, target_line, insertion_point)
            elif edit_type == 'MOVE':
                insertion_point = random.randrange(
                    0, len(self.program.contents[target_file]) + 1)
                self.move(target_file, target_line, insertion_point)
        else:
            print("[Error] invalid manipulation level: {}".format(
                self.program.manipulation_level))
            sys.exit()
        return

    def delete(self, target_file, target_line):
        self.history.append(Edit('DELETE', target_file, target_line, None))

    def copy(self, target_file, target_line, insertion_point):
        self.history.append(Edit('COPY', target_file, target_line, insertion_point))

    def move(self, target_file, target_line, insertion_point):
        self.history.append(Edit('MOVE', target_file, target_line, insertion_point))

class Edit:
    def __init__(self, edit_type, target_file, target_line, insertion_point):
        self.edit_type = edit_type
        self.target_file = target_file
        self.target_line = target_line
        self.insertion_point = insertion_point

    def __str__(self):
        if self.edit_type == 'DELETE':
            return "DELETE {}:{}".format(self.target_file, self.target_line)
        elif self.edit_type == 'COPY':
            return "COPY {}:{} -> {}:{}".format(self.target_file, self.target_line, self.target_file, self.insertion_point)
        elif self.edit_type == 'MOVE':
            return "MOVE {}:{} -> {}:{}".format(self.target_file, self.target_line, self.target_file, self.insertion_point)
        else:
            return ''
    
    def __copy__(self):
        return Edit(self.edit_type, self.target_file, self.target_line, self.insertion_point)
