import random
import copy
import subprocess
import sys
from .program import Program

class Patch:
    tmpdir = "tmp/"

    def __init__(self, program):
        self.program = program
        self.modified_program = None
        self.test_result = None
        # A list of deletions: (target_file, target_line)
        self.deletions = []
        # A list of insertions: (target_file, target_line, insertion_point)
        self.insertions = []
        self.history = []
        pass

    def __str__(self):
        return ' | '.join(self.history)

    def get_diff(self):
        if not self.modified_program:
            self.apply()
        stdoutdata = ''
        for i in range(len(self.program.path_list)):
            stdoutdata += subprocess.getoutput("diff -u {} {}".format(self.program.path_list[i], self.modified_program.path_list[i]))
        return stdoutdata

    def clone(self):
        clone_patch = Patch(self.program)
        clone_patch.deletions = copy.deepcopy(self.deletions)
        clone_patch.insertions = copy.deepcopy(self.insertions) 
        clone_patch.history = copy.deepcopy(self.history)
        clone_patch.test_result = None
        return clone_patch

    def run_test(self, test_file_path):
        # patch.test_result = patch.apply().run_test(/path/to/test/suite)
        # is equal to
        # patch.run_test(/path/to/test/suite)
        self.test_result = self.apply().run_test(test_file_path)

    def apply(self):
        if self.program.manipulation_level == 'physical_line':
            target_file_list = self.program.contents.keys()
            new_contents = dict(zip(target_file_list, [[]] * len(target_file_list)))

            for target_file in target_file_list:
                orig_codeline_list = self.program.contents[target_file]
                new_codeline_list = new_contents[target_file]

                # Create deletions set for target file: (target_file, target_line)
                target_file_deletions = set(filter(lambda x: x[0] == target_file,
                                                   self.deletions))
                # Create insertions dict for target file: insertion_point => [target_lines]
                target_file_insertions = list(filter(lambda x: x[0] == target_file,
                                                    self.insertions))
                insertion_points = list(set(map(lambda x: x[2], target_file_insertions)))
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
                            new_codeline_list.append(orig_codeline_list[target_line])
                    # Handle deletions
                    if i < len(orig_codeline_list) and (target_file, i) not in target_file_deletions:
                        new_codeline_list.append(orig_codeline_list[i])

            # Write modified program
            self.modified_program = Program.create_program_with_contents(new_contents)
            return self.modified_program
        else:
            print("[Error] invalid manipulation level: {}".format(self.program.manipulation_level))
            sys.exit()

    def add_random_edit(self):
        if self.program.manipulation_level == 'physical_line':
            target_file_list = sorted(self.program.contents.keys())
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
                                                   target_file_list)))
                target_line = random.randrange(0, len(self.program.contents[target_file]))
                if not edit_type == 'delete' or (target_file, target_line) not in self.deletions:
                    break
            if edit_type == 'delete':
                self.delete(target_file, target_line)
            elif edit_type == 'copy':
                insertion_point = random.randrange(0, len(self.program.contents[target_file]) + 1)
                self.copy(target_file, target_line, insertion_point)
            elif edit_type == 'move':
                insertion_point = random.randrange(0, len(self.program.contents[target_file]) + 1)
                self.move(target_file, target_line, insertion_point)
        else:
            print("[Error] invalid manipulation level: {}".format(self.program.manipulation_level))
            sys.exit()
        return

    def delete(self, target_file, target_line):
        self.history.append("DELETE {}: {}".format(target_file, target_line))
        self.deletions.append((target_file, target_line))

    def copy(self, target_file, target_line, insertion_point):
        self.history.append("COPY {}: {} -> {}".format(target_file, target_line, insertion_point))
        self.insertions.append((target_file, target_line, insertion_point))

    def move(self, target_file, target_line, insertion_point):
        self.history.append("MOVE {}: {} -> {}".format(target_file, target_line, insertion_point))
        self.insertions.append((target_file, target_line, insertion_point))
        self.deletions.append((target_file, target_line))
