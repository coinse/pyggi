import random
from .program import Program

class Patch:
    tmpdir = "tmp/"

    def __init__(self, program):
        self.program = program
        self.modified_program = None
        self.number_of_units = len(self.program.contents)
        self.edits = []
        self.test_result = None
        pass

    def __str__(self):
        return '|'.join(map(lambda e: str(e), self.edits))

    def length(self):
        return len(self.edits)

    def clone(self):
        clone_patch = Patch(self.program)
        clone_patch.edits = self.edits[:]
        clone_patch.number_of_units = self.number_of_units
        clone_patch.test_result = self.test_result
        return clone_patch

    def run_test(self, test_file_path):
        # patch.test_result = patch.apply().run_test(/path/to/test/suite)
        # is equal to
        # patch.run_test(/path/to/test/suite)
        self.test_result = self.apply().run_test(test_file_path)

    def apply(self):
        if self.program.manipulation_level == 'physical_line':
            contents = self.program.contents[:]
            for edit in self.edits:
                if edit['type'] == 'delete':
                    del contents[edit['target']]
                elif edit['type'] == 'copy':
                    contents.insert(edit['insertion_point'], contents[edit['target']])
                elif edit['type'] == 'move':
                    target_code = contents[edit['target']]
                    del contents[edit['target']]
                    contents.insert(edit['insertion_point'], target_code)
                else:
                    print("[Error] invalid edit type: {}".format(edit['type']))
            self.modified_program = Program.create_program_with_contents(self.program.get_program_name(), contents)
            return self.modified_program
        else:
            print("[Error] invalid manipulation level: {}".format(self.program.manipulation_level))
            sys.exit()

    def add_random_edit(self):
        if self.program.manipulation_level == 'physical_line':
            edit_type = random.choice(['delete', 'copy', 'move']) 
            if edit_type == 'delete':
                if self.number_of_units > 0:
                    target = random.randrange(0, self.number_of_units)
                    self.delete(target)
                else:
                    self.add_random_edit()
            elif edit_type == 'copy':
                target = random.randrange(0, self.number_of_units)
                insertion_point = random.randrange(0, self.number_of_units + 1)
                self.copy(target, insertion_point)
            elif edit_type == 'move':
                target = random.randrange(0, self.number_of_units)
                insertion_point = random.randrange(0, self.number_of_units)
                self.move(target, insertion_point)
        else:
            print("[Error] invalid manipulation level: {}".format(self.program.manipulation_level))
            sys.exit()
        return

    def delete(self, target):
        self.edits.append({ 'type': 'delete', 'target': target })
        self.number_of_units -= 1

    def copy(self, target, insertion_point):
        self.edits.append({ 'type': 'copy', 'target': target, 'insertion_point': insertion_point })
        self.number_of_units += 1

    def move(self, target, insertion_point):
        self.edits.append({ 'type': 'move', 'target': target, 'insertion_point': insertion_point })
