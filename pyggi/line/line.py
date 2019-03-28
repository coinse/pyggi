import os
import random
from abc import abstractmethod
from ..base import AbstractProgram, AtomicOperator, CustomOperator

class LineProgram(AbstractProgram):
    def __str__(self):
        code = ''
        for k in sorted(self.contents.keys()):
            idx = 0
            for line in self.contents[k]:
                code += "{}\t: {}\t: {}\n".format(k, idx, line)
                idx += 1
        return code

    @property
    def modification_points(self):
        if self._modification_points:
            return self._modification_points

        self._modification_points = dict()
        for target_file in self.target_files:
            self._modification_points[target_file] = list(range(len(self.contents[target_file])))
        return self._modification_points

    def print_modification_points(self, target_file, indices=None):
        def print_modification_point(contents, modification_points, i):
            print(title_format.format('line', i))
            print(contents[modification_points[i]])
        title_format = "=" * 25 + " {} {} " + "=" * 25
        if not indices:
            indices = range(len(self.modification_points[target_file]))
        for i in indices:
            print_modification_point(self.contents[target_file], self.modification_points[target_file], i)
    
    def parse(self, path, target_files):
        contents = {}
        for target in target_files:
            with open(os.path.join(path, target), 'r') as target_file:
                contents[target] = list(
                    map(str.rstrip, target_file.readlines()))
        return contents

    @classmethod
    def to_source(self, contents_of_file):
        return '\n'.join(contents_of_file) + '\n'


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
        if isinstance(program, LineProgram):
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
        if isinstance(program, LineProgram):
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

class LineDeletion(CustomOperator):
    """
    LineDeletion: Delete x
    
    It replaces the code line with an empty line.
    """
    def __str__(self):
        return "LineDeletion({})".format(self.x)

    def is_valid_for(self, program):
        if isinstance(program, LineProgram):
            return True
        return False

    @property
    def x(self):
        """
        Delete **x**

        :return: The file path and the index of target line to be deleted.
        :rtype: tuple(str, int)
        """
        return self.args[0]

    @property
    def length_of_args(self):
        """
        :return: ``1``
        :rtype: int
        """
        return 1

    @property
    def atomic_operators(self):
        """
        :return: ``[LineReplacement(self.x, None)]``
        :rtype: list(:py:class:`.atomic_operator.AtomicOperator`)
        """
        return [LineReplacement(self.x, None)]

    @classmethod
    def create(cls, program, line_file=None, method='random'):
        """
        :param program: The program instance to which the random custom operator will be applied.
        :type program: :py:class:`.Program`
        :param str line_file: Line is the target line to delete.
          If line_file is specified, the target line will be chosen within the file.
        :param str method: The way of choosing the modification point. **'random'** or **'weighted'**
        :return: The LineDeletion instance with the randomly-selected line index.
        :rtype: :py:class:`.custom_operator.LineDeletion`
        """
        line_file = line_file or random.choice(program.target_files)
        line = (
            line_file,
            program.select_modification_point(line_file, method)
        )
        return cls(line)

class LineMoving(CustomOperator):
    """
    LineMoving: Move x [before|after] y
    """
    def __str__(self):
        return "LineMoving({}, {}, '{}')".format(self.y, self.x, self.direction)

    def is_valid_for(self, program):
        if isinstance(program, LineProgram):
            return True
        return False

    @property
    def x(self):
        """
        Move **x** [before|after] y

        :return: The file path and the index of target line to be moved.
        :rtype: tuple(str, int)
        """
        return self.args[1]

    @property
    def y(self):
        """
        Move x [before|after] **y**

        :return: The file path and the index of the point to which line x is inserted.
        :rtype: tuple(str, int)
        """
        return self.args[0]

    @property
    def direction(self):
        """
        Move x **[before|after]** y

        :return: **'before'** or **'after'**
        :rtype: str
        """
        return self.args[2]

    @property
    def length_of_args(self):
        """
        :return: ``3``
        :rtype: int
        """
        return 3

    @property
    def atomic_operators(self):
        """
        :return: ``[LineInsertion(self.y, self.x, self.direction), LineReplacement(self.x, None)]``
        :rtype: list(:py:class:`.atomic_operator.AtomicOperator`)
        """
        return [LineInsertion(self.y, self.x, self.direction), LineReplacement(self.x, None)]

    @classmethod
    def create(cls, program, line_file=None, ingr_file=None, direction='before', method='random'):
        """
        :param program: The program instance to which the created custom operator will be applied.
        :type program: :py:class:`.Program`
        :param str line_file: Line means the modification point of the edit. If line_file is specified, the line will be chosen within the file.
        :param str ingr_file: Ingredient is the line to be moved.
          If ingr_file is specified, the ingredient line will be chosen within the file.
        :param str method: The way of choosing the modification point. **'random'** or **'weighted'**
        :return: The LineMoving instance with the randomly-selected line & ingr.
        :rtype: :py:class:`.custom_operator.LineMoving`
        """
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
        return cls(ingredient, line, direction)