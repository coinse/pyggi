"""

This module contains AtomicOperator class which is an abstact base class,
and several classes inherit the AtomicOperator class.

"""
from abc import ABCMeta, abstractmethod
from .program import Program
import ast


class AtomicOperator(metaclass=ABCMeta):
    """
    
    PYGGI-defined Atomic Operator:
    User can generate the own custom edit operators
    which can be converted into a list of atomic operators.
    For example, **MOVE x -> y** operator can be represented as
    **[LineReplacement(x, None),LineInsertion(x, y)]**

    **Available List**

    * LineReplacement
    * LineInsertion
    * StmtReplacement
    * StmtInsertion

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

    @property
    @abstractmethod
    def modification_point(self):
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

    @abstractmethod
    def apply(self, program, new_contents, modification_points):
        """"
        Apply the operator to the contents of program
        :param program: The original program instance
        :type program: :py:class:`.Program`
        :param new_contents: The new contents of program to which the edit will be applied
        :type new_contents: dict(str, list(?))
        :param modification_points: The original modification points
        :type modification_points: list(?)
        :return: success or not
        :rtype: bool
        """
        pass

    @classmethod
    @abstractmethod
    def create(cls):
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
        :return: ``LineReplacement([line], [ingredient])``
        """
        return "LineReplacement({}, {})".format(self.line, self.ingredient)

    @property
    def modification_point(self):
        return self.line

    def is_valid_for(self, program):
        from .program import GranularityLevel
        if program.granularity_level == GranularityLevel.LINE:
            return True
        return False

    def apply(self, program, new_contents, modification_points):
        """"
        Apply the operator to the contents of program
        :param program: The original program instance
        :type program: :py:class:`.Program`
        :param new_contents: The new contents of program to which the edit will be applied
        :type new_contents: dict(str, list(str))
        :param modification_points: The original modification points
        :type modification_points: list(int)
        :return: success or not
        :rtype: bool
        """
        assert self.is_valid_for(program)
        l_f, l_n = self.line # line file and line number
        if self.ingredient:
            i_f, i_n = self.ingredient
            new_contents[l_f][modification_points[l_f][l_n]] = program.contents[i_f][i_n]
        else:
            new_contents[l_f][modification_points[l_f][l_n]] = ''
        return modification_points

    @classmethod
    def create(cls, program, line_file=None, ingr_file=None, del_rate=0, method='random'):
        """
        :param program: The program instance to which the random edit will be applied.
        :type program: :py:class:`.Program`
        :param str line_file: Line is the target line to delete.
          If line_file is specified, the target line will be chosen within the file.
        :param str ingr_file: Ingredient is the line to be copied.
          If ingr_file is specified, the target line will be chosen within the file.
        :param float del_rate: The probability of that line is deleted
          instead of replaced with another line
        :param str method: The way of choosing the modification point. **'random'** or **'weighted'**
        :return: The LineReplacement instance with the randomly-selected properties:
          line and ingredient.
        :rtype: :py:class:`.atomic_operator.LineReplacement`
        """
        import random
        assert del_rate >= 0 and del_rate <= 1
        line_file = line_file or random.choice(program.target_files)
        line = (line_file, program.select_modification_point(line_file, method))
        if random.random() < del_rate:
            ingredient = None
        else:
            ingr_file = ingr_file or random.choice(program.target_files)
            ingredient = (ingr_file, program.select_modification_point(ingr_file, 'random'))
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

    def __init__(self, line, ingredient, direction='before'):
        """
        :param line: The file path and position of line which is a target of modification
        :type line: tuple(str, int)
        :param ingredient: The file path and index of code line which is an ingredient
        :type ingredient: tuple(str, int)
        :param direction: *'before'* or *'after'*
        :type direction: str
        """
        super().__init__()
        assert isinstance(line[0], str)
        assert isinstance(line[1], int)
        assert line[1] >= 0
        assert isinstance(ingredient[0], str)
        assert isinstance(ingredient[1], int)
        assert ingredient[1] >= 0
        assert direction in ['before', 'after']
        self.line = line
        self.ingredient = ingredient
        self.direction = direction

    def __str__(self):
        return "LineInsertion({}, {}, '{}')".format(self.line, self.ingredient, self.direction)

    @property
    def modification_point(self):
        return self.line
    
    def is_valid_for(self, program):
        from .program import GranularityLevel
        if program.granularity_level == GranularityLevel.LINE:
            return True
        return False

    def apply(self, program, new_contents, modification_points):
        """"
        Apply the operator to the contents of program
        :param program: The original program instance
        :type program: :py:class:`.Program`
        :param new_contents: The new contents of program to which the edit will be applied
        :type new_contents: dict(str, list(str))
        :param modification_points: The original modification points
        :type modification_points: list(int)
        :return: success or not
        :rtype: bool
        """
        assert self.is_valid_for(program)
        l_f, l_n = self.line
        i_f, i_n = self.ingredient
        if self.direction == 'before':
            new_contents[l_f].insert(
                modification_points[l_f][l_n],
                program.contents[i_f][i_n]
            )
            for i in range(l_n, len(modification_points[l_f])):
                modification_points[l_f][i] += 1
        elif self.direction == 'after':
            new_contents[l_f].insert(
                modification_points[l_f][l_n] + 1,
                program.contents[i_f][i_n]
            )
            for i in range(l_n + 1, len(modification_points[l_f])):
                modification_points[l_f][i] += 1
        return True

    @classmethod
    def create(cls, program, line_file=None, ingr_file=None, direction='before', method='random'):
        """
        :param program: The program instance to which the random edit will be applied.
        :type program: :py:class:`.Program`
        :param str line_file: Line means the modification point of the edit.
          If line_file is specified, the line will be chosen within the file.
        :param str ingr_file: Ingredient is the line to be copied.
          If ingr_file is specified, the target line will be chosen within the file.
        :param str method: The way of choosing the modification point. **'random'** or **'weighted'**
        :return: The LineInsertion instance with the randomly-selected properties:
          line and ingredient.
        :rtype: :py:class:`.atomic_operator.LineInsertion`
        """
        import random
        line_file = line_file or random.choice(program.target_files)
        ingr_file = ingr_file or random.choice(program.target_files)
        line = (
            line_file,
            program.select_modification_point(line_file, method)
        )
        ingredient = (
            ingr_file,
            program.select_modification_point(ingr_file, 'random')
        )
        return cls(line, ingredient, direction)


class StmtReplacement(AtomicOperator):

    def __init__(self, stmt, ingredient=None):
        """
        :param stmt: The file path and the node # of statement which should be replaced
        :type stmt: tuple(str, int)
        :param ingredient: The file path and the node # of statement which is an ingredient
        :type ingredient: None or tuple(str, int)
        """
        super().__init__()
        assert isinstance(stmt[0], str)
        assert isinstance(stmt[1], int)
        assert stmt[1] >= 0
        if ingredient:
            assert isinstance(ingredient[0], str)
            assert isinstance(ingredient[1], int)
            assert ingredient[1] >= 0
        self.stmt = stmt
        self.ingredient = ingredient

    def __str__(self):
        """
        :return: ``StmtReplacement([stmt], [ingredient])``
        """
        return "StmtReplacement({}, {})".format(self.stmt, self.ingredient)

    @property
    def modification_point(self):
        return self.stmt

    def is_valid_for(self, program):
        from .program import GranularityLevel
        if program.granularity_level == GranularityLevel.AST:
            return True
        return False

    def apply(self, program, new_contents, modification_points):
        """"
        Apply the operator to the contents of program
        :param program: The original program instance
        :type program: :py:class:`.Program`
        :param new_contents: The new contents of program to which the edit will be applied
        :type new_contents: dict(str, ?)
        :param modification_points: The original modification points
        :type modification_points: list(int, )
        :return: success or not
        :rtype: bool
        """
        assert self.is_valid_for(program)
        assert not self.ingredient or Program.have_the_same_file_extension(
            self.stmt[0], self.ingredient[0])
        if Program.is_python_code(self.stmt[0]):
            from .helper import stmt_python
            dst_root = new_contents[self.stmt[0]]
            dst_pos = modification_points[self.stmt[0]][self.stmt[1]]
            if not self.ingredient:
                return stmt_python.replace((dst_root, dst_pos), self.ingredient)
            ingr_root = program.contents[self.ingredient[0]]
            ingr_pos = program.modification_points[self.ingredient[0]][self.ingredient[1]]
            return stmt_python.replace((dst_root, dst_pos), (ingr_root, ingr_pos))
        return False

    @classmethod
    def create(cls, program, stmt_file=None, ingr_file=None, del_rate=0, method='random'):
        """
        :param program: The program instance to which the random edit will be applied.
        :type program: :py:class:`.Program`
        :param str stmt_file: stmt is the target statement to delete.
          If stmt_file is specified, the target statement will be chosen within that file.
        :param str ingr_file: Ingredient is the statement to be copied.
          If ingr_file is specified, the ingredient statement will be chosen within that file.
        :param float del_rate: The probability of ingredient will be None. ([0,1])
        :param str method: The way of choosing the modification point. **'random'** or **'weighted'**
        :return: The StmtReplacement instance with the randomly-selected properties:
          stmt and ingredient.
        :rtype: :py:class:`.atomic_operator.StmtReplacement`
        """
        import random
        assert del_rate >= 0 and del_rate <= 1
        stmt_file = stmt_file or random.choice(program.target_files)
        stmt = (stmt_file, program.select_modification_point(stmt_file, method))
        if random.random() < del_rate:
            ingredient = None
        else:
            ingr_file = ingr_file or random.choice(program.target_files)
            ingredient = (ingr_file, program.select_modification_point(ingr_file, 'random'))
        return cls(stmt, ingredient)


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
        assert isinstance(stmt[1], int)
        assert stmt[1] >= 0
        assert isinstance(ingredient[0], str)
        assert isinstance(ingredient[1], int)
        assert ingredient[1] >= 0
        assert direction in ['before', 'after']
        self.stmt = stmt
        self.ingredient = ingredient
        self.direction = direction

    def __str__(self):
        """
        :return: ``StmtInsertion([line], [ingredient], [direction])``
        """
        return "StmtInsertion({}, {}, '{}')".format(self.stmt, self.ingredient, self.direction)

    @property
    def modification_point(self):
        return self.stmt

    def is_valid_for(self, program):
        from .program import GranularityLevel
        if program.granularity_level == GranularityLevel.AST:
            return True
        return False

    def apply(self, program, new_contents, modification_points):
        """
        Apply the operator to the contents of program

        :param program: The original program instance
        :type program: :py:class:`.Program`
        :param new_contents: The new contents of program to which the edit will be applied
        :type new_contents: dict(str, ?)
        :param modification_points: The original modification points
        :type modification_points: list(int, )
        :return: success or not
        :rtype: bool
        """
        assert self.is_valid_for(program)
        assert Program.have_the_same_file_extension(self.stmt[0],
            self.ingredient[0])
        success = False
        if Program.is_python_code(self.stmt[0]):
            from .helper import stmt_python
            dst_root = new_contents[self.stmt[0]]
            dst_pos = modification_points[self.stmt[0]][self.stmt[1]]
            ingr_root = program.contents[self.ingredient[0]]
            ingr_pos = stmt_python.get_modification_points(ingr_root)[self.ingredient[1]]
            if self.direction == 'before':
                success = stmt_python.insert_before((dst_root, dst_pos), (ingr_root, ingr_pos))
                if success:
                    depth = len(dst_pos)
                    parent = dst_pos[:depth-1]
                    index = dst_pos[depth-1][1]
                    for pos in modification_points[self.stmt[0]]:
                        if parent == pos[:depth-1] and len(pos) >= depth and index <= pos[depth-1][1]:
                            a, i = pos[depth-1]
                            pos[depth-1] = (a, i + 1)
            elif self.direction == 'after':
                success = stmt_python.insert_after((dst_root, dst_pos), (ingr_root, ingr_pos))
                if success:
                    depth = len(dst_pos)
                    parent = dst_pos[:depth-1]
                    index = dst_pos[depth - 1][1]
                    for pos in modification_points[self.stmt[0]]:
                        if parent == pos[:depth-1] and len(pos) >= depth and index < pos[depth-1][1]:
                            a, i = pos[depth-1]
                            pos[depth-1] = (a, i + 1)
        return success

    @classmethod
    def create(cls, program, stmt_file=None, ingr_file=None, direction='before', method='random'):
        """
        :param program: The program instance to which the random edit will be applied.
        :type program: :py:class:`.Program`
        :param str line_file: stmt means the modification point of the edit.
          If stmt_file is specified, the stmt will be chosen within that file.
        :param str ingr_file: Ingredient is the stmt to be copied.
          If ingr_file is specified, the target stmt will be chosen within that file.
        :param str method: The way of choosing the modification point. **'random'** or **'weighted'**
        :return: The StmtInsertion instance with the randomly-selected properties:
          stmt and ingredient.
        :rtype: :py:class:`.atomic_operator.StmtInsertion`
        """
        import random
        stmt_file = stmt_file or random.choice(program.target_files)
        ingr_file = ingr_file or random.choice(program.target_files)
        stmt = (
            stmt_file,
            program.select_modification_point(stmt_file, method)
        )
        ingredient = (
            ingr_file,
            program.select_modification_point(ingr_file, 'random')
        )
        return cls(stmt, ingredient, direction)
