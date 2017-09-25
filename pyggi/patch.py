import random
import copy
import subprocess
from .program import Program

class Patch:
    tmpdir = "tmp/"

    def __init__(self, program):
        self.program = program
        self.modified_program = None
        self.test_result = None
        # A set of lines to delete
        self.deletions = set()
        # Key: Insertion point, Value: Queue of lines which should be inserted
        self.insertions = {}
        self.history = []
        pass

    def __str__(self):
        return ' | '.join(self.history)

    def get_diff(self):
        if not self.modified_program:
            self.apply()
        stdoutdata = subprocess.getoutput("diff -u {} {}".format(self.program.path, self.modified_program.path))
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
            new_contents = []
            for i in range(len(self.program.contents) + 1):
                if i in self.insertions:
                    for target in self.insertions[i]:
                        new_contents.append(self.program.contents[target])
                if i < len(self.program.contents) and i not in self.deletions:
                    new_contents.append(self.program.contents[i])
            self.modified_program = Program.create_program_with_contents(new_contents)
            return self.modified_program
        else:
            print("[Error] invalid manipulation level: {}".format(self.program.manipulation_level))
            sys.exit()

    def add_random_edit(self):
        if self.program.manipulation_level == 'physical_line':
            number_of_program_lines = len(self.program.contents)
            edit_type = random.choice(['delete', 'copy', 'move'])
            # line number starts from 0
            while True:
                target_line = random.randrange(0, number_of_program_lines)
                if not edit_type == 'delete' or target_line not in self.deletions:
                    break
            if edit_type == 'delete':
                self.delete(target_line)
            elif edit_type == 'copy':
                insertion_point = random.randrange(0, number_of_program_lines + 1)
                self.copy(target_line, insertion_point)
            elif edit_type == 'move':
                insertion_point = random.randrange(0, number_of_program_lines + 1)
                self.move(target_line, insertion_point)
        else:
            print("[Error] invalid manipulation level: {}".format(self.program.manipulation_level))
            sys.exit()
        return

    def delete(self, target):
        self.history.append("DELETE {}".format(target)) 
        self.deletions.add(target)

    def copy(self, target, insertion_point):
        self.history.append("COPY {} -> {}".format(target, insertion_point)) 
        if insertion_point in self.insertions:
            self.insertions[insertion_point].append(target)
        else:
            self.insertions[insertion_point] = [target]

    def move(self, target, insertion_point):
        self.history.append("MOVE {} -> {}".format(target, insertion_point)) 
        if insertion_point in self.insertions:
            self.insertions[insertion_point].append(target)
        else:
            self.insertions[insertion_point] = [target]
        self.deletions.add(target)
