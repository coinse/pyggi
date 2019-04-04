"""
This module contains Patch class.
"""
import os
import difflib
from copy import deepcopy
from .edit import AbstractEdit

class InvalidPatchError(Exception):
    pass

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
        return clone_patch

    @property
    def diff(self) -> str:
        """
        Compare the source codes of original program and the patch-applied program
        using *difflib* module(https://docs.python.org/3.6/library/difflib.html).

        :return: The file comparison result
        :rtype: str
        """
        diffs = ''
        new_contents = self.program.apply(self)
        for file_name in self.program.target_files:
            orig = self.program.dump(self.program.contents, file_name)
            modi = self.program.dump(new_contents, file_name)
            orig_list = list(map(lambda s: s+'\n', orig.splitlines()))
            modi_list = list(map(lambda s: s+'\n', modi.splitlines()))
            for diff in difflib.context_diff(orig_list, modi_list, fromfile="before: " + file_name,
                                                                   tofile="after: " + file_name):
                diffs += diff
        return diffs

    def add(self, edit):
        """
        Add an edit to the edit list

        :param edit: The edit to be added
        :type edit: :py:class:`.base.AbstractEdit`
        :return: None
        """
        assert isinstance(edit, AbstractEdit)
        assert isinstance(self.program, edit.domain)
        self.edit_list.append(edit)

    def remove(self, index: int):
        """
        Remove an edit from the edit list

        :param int index: The index of edit to delete
        """
        del self.edit_list[index]