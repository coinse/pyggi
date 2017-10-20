from enum import Enum

class EditType(Enum):
    DELETE = 1
    COPY = 2
    MOVE = 3
    REPLACE = 4

class Edit(object):
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
