"""

This module contains AtomicOperator class which is an abstact base class,
and several classes inherit the AtomicOperator class.

"""
from abc import ABCMeta, abstractmethod

class AtomicOperator(metaclass=ABCMeta):
    """
    PYGGI-defined Atomic Operator

    User can generate the own edit operators
    which can be converted into a list of atomic operators.
    For example, MOVE x -> y operator can be represented as
    [ LineReplacement(x, None), LineInsertion(x, y) ]

    - Available list
    1. Line-based Edit Operators
        | Point # | Line # | Code                 |
        |    0    |        |                      |
        |         |    0   | -------------------- |
        |    1    |        |                      |
        |         |    1   | -------------------- |
        |    2    |        |                      |
        |         |    2   | -------------------- |
        |    3    |        |                      |
        |         |    3   | -------------------- |
        |    4    |        |                      |
        |         |        |                      |
        |    .    |    .   |           .          |
        |    .    |    .   |           .          |
        |    .    |    .   |           .          |
        |    .
    1.1 ``LineReplacement``
    1.2 ``LineInsertion``

    2. ...
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
        Returns:
            list: a list that only contains the current atomic operator instance.
        """
        return [self]

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @classmethod
    @abstractmethod
    def random(cls):
        """
        Return the operator instance with randomly-selected properties.
        """
        pass


class LineReplacement(AtomicOperator):
    """Line Replacement

    - line: an index of line which should be replaced
    - ingredient: an index of code line which is an ingredient.
        when ingredient is None, it is the same as deletion.

    Examples:
        1) LineReplacement(3, 2)
            <Before>    <After>
                0           0
                1           1
                2           2
                3     ->    2
                4           4
        2) LineReplacement(3, None)
            <Before>    <After>
                0           0
                1           1
                2           2
                3           4
                4
    """
    def __init__(self, line, ingredient=None):
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
        return "Replace {} with {}".format(self.line, self.ingredient)

    @classmethod
    def random(cls, program, line_file=None, ingr_file=None, del_rate=0):
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
    """Line Insertion
    - point: a point to which the code line should be inserted
    - ingredient: an index of code line which is an ingredient

    Examples:
        1) LineInsertion(4, 2)
            <Before>    <After>
                0           0
                1           1
                2           2
                3           3
                4           2   <-  'Inserted'
                            4
    """

    def __init__(self, point, ingredient):
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

    @classmethod
    def random(cls, program, point_file=None, ingr_file=None):
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
