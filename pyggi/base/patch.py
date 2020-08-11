"""
This module contains Patch class.
"""
import os
from copy import deepcopy
from . import AbstractEdit

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
        return ' | '.join(map(str, self.edit_list))

    def __len__(self):
        return len(self.edit_list)

    def __eq__(self, other):
        return isinstance(other, Patch) and self.edit_list == other.edit_list

    def __hash__(self):
        return hash(str(self))

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
    def diff(self):
        return self.program.diff(self)

    def add(self, edit):
        """
        Add an edit to the edit list

        :param edit: The edit to be added
        :type edit: :py:class:`.base.AbstractEdit`
        :return: None
        """
        assert isinstance(edit, AbstractEdit)
        self.edit_list.append(edit)

    def remove(self, index: int):
        """
        Remove an edit from the edit list

        :param int index: The index of edit to delete
        """
        del self.edit_list[index]
