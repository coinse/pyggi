from enum import Enum


class EditType(Enum):
    DELETE = 1
    COPY = 2
    MOVE = 3
    REPLACE = 4


class LocType(Enum):
    INDEX = 'I'
    INSERTION_POINT = 'P'


class Edit(object):

    def __init__(self, edit_type, source=None, target=None):
        '''
         -------------------------------------------------
        |         | DELETE  | MOVE    | COPY    | REPLACE |
        | -------- --------- --------- --------- ---------|
        | Source  |         | index   | index   | index   |
        | Target  | index   | point   | point   | index   |
         -------------------------------------------------
        '''
        if not isinstance(edit_type, EditType):
            exit(1)
        self.edit_type = edit_type
        self.source = source
        self.target = target

    def __eq__(self, other):
        return self.edit_type == other.edit_type and self.source == other.source and self.target == other.target

    def __str__(self):

        def to_str(source, source_type, target, target_type):
            s = "[{0}:{2}:{1}]".format(target[0], target[1], target_type.value)
            if source:
                s = "[{0}:{2}:{1}] -> ".format(source[0], source[1],
                                               source_type.value) + s
            return s

        return "{} {}".format(self.edit_type.name,
                              to_str(self.source, self.source_type, self.target,
                                     self.target_type))

    def __copy__(self):
        return Edit(self.edit_type, self.source, self.target)

    @property
    def source_type(self):
        if self.edit_type == EditType.DELETE:
            return None
        return LocType.INDEX

    @property
    def target_type(self):
        if self.edit_type in (EditType.DELETE, EditType.REPLACE):
            return LocType.INDEX
        return LocType.INSERTION_POINT
