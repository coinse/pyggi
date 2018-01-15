"""

This module contains AtomicOperator class which is an abstact base class,
and several classes inherit the AtomicOperator class.

"""
from abc import ABCMeta, abstractmethod
import ast

class AtomicOperator(metaclass=ABCMeta):
    """
    PYGGI-defined Atomic Operator:
    User can generate the own edit operators
    which can be converted into a list of atomic operators.
    For example, **MOVE x -> y** operator can be represented as
    **[LineReplacement(x, None),LineInsertion(x, y)]**

    **Available List**

    * LineReplacement
    * LineInsertion

    .. hint::

        +---------+---------+---------------------+
        | Point # | Line #  | Code                |
        +=========+=========+=====================+
        |    0    |         |                     |
        +---------+---------+---------------------+
        |         |    0    | from math import *  |
        +---------+---------+---------------------+
        |    1    |         |                     |
        +---------+---------+---------------------+
        |         |    1    | for i in range(3):  |
        +---------+---------+---------------------+
        |    2    |         |                     |
        +---------+---------+---------------------+
        |         |    2    |   print(i)          |
        +---------+---------+---------------------+
        |    3    |         |                     |
        +---------+---------+---------------------+
        |         |    3    |   if (sqrt(i) > 2): |
        +---------+---------+---------------------+
        |    4    |         |                     |
        +---------+---------+---------------------+
        |         |    4    |       return        |
        +---------+---------+---------------------+
        |   ...   |   ...   | ..................  |
        +---------+---------+---------------------+


    """
    def __eq__(self, other):
        if self.__class__.__name__ != other.__class__.__name__:
            return False
        for prop in self.__dict__:
            if self.__dict__[prop] != other.__dict__[prop]:
                return False
        return True

    @property
    def atomic_operators(self):
        """
        :return: ``[self]``, the list that only contains the AtomicOperator instance itself.
        :rtype: list(:py:class:`.atomic_operator.AtomicOperator`)
        """
        return [self]

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def is_valid_for(self, program):
        """
        :param program: The program instance to which this edit will be applied
        :type program: :py:class:`.Program`
        :return: Whether the edit is able to be applied to the program
        :rtype: bool
        """
        pass

    @classmethod
    @abstractmethod
    def random(cls):
        """
        :return: The operator instance with randomly-selected properties.
        :rtype: :py:class:`.atomic_operator.AtomicOperator`
        """
        pass


class LineReplacement(AtomicOperator):
    """
    .. note::
        1. LineReplacement((*[file_path]*, 3), (*[file_path]*, 2))

        ======== ========
        Before   After
        ======== ========
        0        0
        1        1
        2        2
        3        2
        4        4
        ======== ========

        2. LineReplacement((*[file_path]*, 3), None)

        ======== ========
        Before   After
        ======== ========
        0        0
        1        1
        2        2
        3        4
        4
        ======== ========
    """
    def __init__(self, line, ingredient=None):
        """
        :param line: The file path and index of line which should be replaced
        :type line: tuple(str, int)
        :param ingredient: The file path and index of code line which is an ingredient
        :type ingredient: None or tuple(str, int)
        """
        super().__init__()
        assert isinstance(line[0], str)
        assert isinstance(line[1], int)
        assert line[1] >= 0
        if ingredient:
            assert isinstance(ingredient[0], str)
            assert isinstance(ingredient[1], int)
            assert ingredient[1] >= 0
        self.line = line
        self.ingredient = ingredient

    def __str__(self):
        """
        :return: ``Replace [line] with [ingredient]``
        """
        return "Replace {} with {}".format(self.line, self.ingredient)

    def is_valid_for(self, program):
        from .program import MnplLevel
        if program.manipulation_level == MnplLevel.PHYSICAL_LINE:
            return True
        return False

    @classmethod
    def random(cls, program, line_file=None, ingr_file=None, del_rate=0):
        """
        :param program: The program instance to which the random edit will be applied.
        :type program: :py:class:`.Program`
        :param str line_file: Line is the target line to delete.
          If line_file is specified, the target line will be chosen within the file.
        :param str ingr_file: Ingredient is the line to be copied.
          If ingr_file is specified, the target line will be chosen within the file.
        :param float del_rate: The probability of that line is deleted
          instead of replaced with another line
        :return: The LineReplacement instance with the randomly-selected properties:
          line and ingredient.
        :rtype: :py:class:`.atomic_operator.LineReplacement`
        """
        import random
        assert del_rate >= 0 and del_rate <= 1
        line_file = line_file or random.choice(program.target_files)
        ingr_file = ingr_file or random.choice(program.target_files)
        line = (
            line_file,
            random.randrange(0, len(program.contents[line_file]))
        )
        ingredient = (
            ingr_file,
            random.randrange(0, len(program.contents[ingr_file]))
        )
        if random.random() < del_rate:
            ingredient = None
        return cls(line, ingredient)


class LineInsertion(AtomicOperator):
    """
    .. note::
        1. LineInsertion((*[file_path]*, 4), (*[file_path]*, 2))

        ======== ========
        Before   After
        ======== ========
        0        0
        1        1
        2        2
        3        3
        4        2
        ...      4
        ======== ========
    """

    def __init__(self, point, ingredient):
        """
        :param point: The file path and point to which the code
          line should be inserted
        :type point: tuple(str, int)
        :param ingredient: The file path and index of code line
          which is an ingredient
        :type ingredient: tuple(str, int)
        """
        super().__init__()
        assert isinstance(point[0], str)
        assert isinstance(point[1], int)
        assert point[1] >= 0
        assert isinstance(ingredient[0], str)
        assert isinstance(ingredient[1], int)
        assert ingredient[1] >= 0
        self.point = point
        self.ingredient = ingredient

    def __str__(self):
        return "Insert {} into {}".format(self.ingredient, self.point)

    def is_valid_for(self, program):
        from .program import MnplLevel
        if program.manipulation_level == MnplLevel.PHYSICAL_LINE:
            return True
        return False

    @classmethod
    def random(cls, program, point_file=None, ingr_file=None):
        """
        :param program: The program instance to which the random edit will be applied.
        :type program: :py:class:`.Program`
        :param str point_file: Point means the insertion point to which the ingr will be inserted.
          If point_file is specified, the point will be chosen within the file.
        :param str ingr_file: Ingredient is the line to be copied.
          If ingr_file is specified, the target line will be chosen within the file.
        :return: The LineInsertion instance with the randomly-selected properties:
          point and ingredient.
        :rtype: :py:class:`.atomic_operator.LineInsertion`
        """
        import random
        point_file = point_file or random.choice(program.target_files)
        ingr_file = ingr_file or random.choice(program.target_files)
        point = (
            point_file,
            random.randrange(0, len(program.contents[point_file])+1)
        )
        ingredient = (
            ingr_file,
            random.randrange(0, len(program.contents[ingr_file]))
        )
        return cls(point, ingredient)


class StmtReplacement(AtomicOperator):
    def __init__(self, stmt, ingredient=None):
        """
        :param stmt: The file path and the position of statement which should be replaced
        :type stmt: tuple(str, list(tuple(str, int)))
        :param ingredient: The file path and the position of statement which is an ingredient
        :type ingredient: None or tuple(str, list(tuple(str, int)))
        """
        super().__init__()
        assert isinstance(stmt[0], str)
        assert isinstance(stmt[1], list)
        assert all(isinstance(t, tuple) and isinstance(t[0], str)
            and isinstance(t[1], int) and t[1] >= 0 for t in stmt[1])
        if ingredient:
            assert isinstance(ingredient[0], str)
            assert isinstance(ingredient[1], list)
            assert all(isinstance(t, tuple) and isinstance(t[0], str)
                and isinstance(t[1], int) and t[1] >= 0 for t in ingredient[1])
        self.stmt = stmt
        self.ingredient = ingredient

    def __str__(self):
        """
        :return: ``Replace [stmt] with [ingredient]``
        """
        return "Replace {} with {}".format(self.stmt, self.ingredient)

    def is_valid_for(self, program):
        from .program import MnplLevel
        if program.manipulation_level == MnplLevel.AST:
            return True
        return False

    def apply(self, contents):
        from .helper import stmt_python
        stmt_python.replace((contents[self.stmt[0]], self.stmt[1]),
            (contents[self.ingredient[0]], self.ingredient[1]))

    @classmethod
    def random(cls, program):
        pass


class StmtInsertion(AtomicOperator):
    def __init__(self, stmt, ingredient, direction='before'):
        """
        :param stmt: The file path and position of statement which is a target of modification
        :type stmt: tuple(str, list(tuple(str, int)))
        :param ingredient: The file path and the position of statement which will be inserted
        :type ingredient: None or tuple(str, list(tuple(str, int)))
        :param direction: *'before'* or *'after'*
        :type direction: str
        """
        super().__init__()
        assert isinstance(stmt[0], str)
        assert isinstance(stmt[1], list)
        assert all(isinstance(t, tuple) and isinstance(t[0], str)
            and isinstance(t[1], int) and t[1] >= 0 for t in stmt[1])
        assert isinstance(ingredient[0], str)
        assert isinstance(ingredient[1], list)
        assert all(isinstance(t, tuple) and isinstance(t[0], str)
            and isinstance(t[1], int) and t[1] >= 0 for t in ingredient[1])
        assert direction in ['before', 'after']
        self.stmt = stmt
        self.ingredient = ingredient
        self.direction = direction

    def __str__(self):
        """
        :return: ``Insert [ingredient] [direction] [stmt]``
        """
        return "Insert {} {} {}".format(self.ingredient, self.direction, self.stmt)

    def is_valid_for(self, program):
        from .program import MnplLevel
        if program.manipulation_level == MnplLevel.AST:
            return True
        return False

    def apply(self, contents):
        from .helper import stmt_python
        if self.direction == 'before':
            stmt_python.insert_before((contents[self.stmt[0]], self.stmt[1]),
                (contents[self.ingredient[0]], self.ingredient[1]))
        elif self.direction == 'after':
            stmt_python.insert_after((contents[self.stmt[0]], self.stmt[1]),
                (contents[self.ingredient[0]], self.ingredient[1]))

    @classmethod
    def random(cls, program):
        pass
