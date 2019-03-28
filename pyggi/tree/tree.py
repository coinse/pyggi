import os
import ast
import astor
import random
from abc import abstractmethod
from . import astor_helper
from ..base import AbstractProgram, AtomicOperator, CustomOperator
from ..utils import check_file_extension, get_file_extension, have_the_same_file_extension

class TreeProgram(AbstractProgram):
    def __str__(self):
        return self.target_files

    @property
    def modification_points(self):
        if self._modification_points:
            return self._modification_points

        self._modification_points = dict()
        for target_file in self.target_files:
            if check_file_extension(target_file, 'py'):
                self._modification_points[target_file] = astor_helper.get_modification_points(
                    self.contents[target_file])
        return self._modification_points

    def print_modification_points(self, target_file, indices=None):
        """
        Print the source of each modification points

        :param target_file: The path to target file
        :type target_file: str
        :return: None
        :rtype: None
        """
        title_format = "=" * 25 + " {} {} " + "=" * 25
        if not indices:
            indices = range(len(self.modification_points[target_file]))

        if check_file_extension(target_file, 'py'):
            def print_modification_point(contents, modification_points, i):
                print(title_format.format('node', i))
                blk, idx = astor_helper.pos_2_block_n_index(contents, modification_points[i])
                print(astor.to_source(blk[idx]))
        
            for i in indices:
                print_modification_point(self.contents[target_file], self.modification_points[target_file], i)

    @classmethod
    def to_source(cls, contents_of_file):
        """
        Change contents of file to the source code

        :param granularity_level: The parsing level of the program
        :type granularity_level: :py:class:`GranularityLevel`
        :param contents_of_file: The contents of the file which is the parsed form of source code
        :type contents_of_file: ?
        :return: The source code
        :rtype: str
        """
        return astor.to_source(contents_of_file)

    @classmethod
    def parse(cls, path, target_files):
        contents = {}
        for target in target_files:
            if check_file_extension(target, 'py'):
                root = astor.parse_file(os.path.join(path, target))
                contents[target] = root
            else:
                raise Exception('Program', '{} file is not supported'.format(get_file_extension(target)))
        return contents


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
        if isinstance(program, TreeProgram):
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
        assert not self.ingredient or have_the_same_file_extension(
            self.stmt[0], self.ingredient[0])
        if check_file_extension(self.stmt[0], 'py'):
            dst_root = new_contents[self.stmt[0]]
            dst_pos = modification_points[self.stmt[0]][self.stmt[1]]
            if not self.ingredient:
                return astor_helper.replace((dst_root, dst_pos), self.ingredient)
            ingr_root = program.contents[self.ingredient[0]]
            ingr_pos = program.modification_points[self.ingredient[0]][self.ingredient[1]]
            return astor_helper.replace((dst_root, dst_pos), (ingr_root, ingr_pos))
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
        if isinstance(program, TreeProgram):
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
        assert have_the_same_file_extension(self.stmt[0], self.ingredient[0])
        success = False
        if check_file_extension(self.stmt[0], 'py'):
            dst_root = new_contents[self.stmt[0]]
            dst_pos = modification_points[self.stmt[0]][self.stmt[1]]
            ingr_root = program.contents[self.ingredient[0]]
            ingr_pos = astor_helper.get_modification_points(ingr_root)[self.ingredient[1]]
            if self.direction == 'before':
                success = astor_helper.insert_before((dst_root, dst_pos), (ingr_root, ingr_pos))
                if success:
                    depth = len(dst_pos)
                    parent = dst_pos[:depth-1]
                    index = dst_pos[depth-1][1]
                    for pos in modification_points[self.stmt[0]]:
                        if parent == pos[:depth-1] and len(pos) >= depth and index <= pos[depth-1][1]:
                            a, i = pos[depth-1]
                            pos[depth-1] = (a, i + 1)
            elif self.direction == 'after':
                success = astor_helper.insert_after((dst_root, dst_pos), (ingr_root, ingr_pos))
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

class StmtDeletion(CustomOperator):
    """
    StmtDeletion: Delete x (Actually, Replace x with an empty statement)
    """
    def __str__(self):
        return "StmtDeletion({})".format(self.x)

    def is_valid_for(self, program):
        if isinstance(program, TreeProgram):
            return True
        return False

    @property
    def x(self):
        """
        Delete **x**

        :return: The file path and the index of modification point to be deleted.
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
        :return: ``[StmtReplacement(self.x, None)]``
        :rtype: list(:py:class:`.atomic_operator.AtomicOperator`)
        """
        return [StmtReplacement(self.x, None)]

    @classmethod
    def create(cls, program, stmt_file=None, method='random'):
        """
        :param program: The program instance to which the created custom operator will be applied.
        :type program: :py:class:`.Program`
        :param str stmt_file: stmt is the target statement to delete.
          If stmt_file is specified, the target statement will be chosen within that file.
        :param str method: The way of choosing the modification point. **'random'** or **'weighted'**
        :return: The StmtDeletion instance with the randomly-selected modification point.
        :rtype: :py:class:`.custom_operator.StmtDeletion`
        """
        stmt_file = stmt_file or random.choice(program.target_files)
        stmt = (
            stmt_file,
            program.select_modification_point(stmt_file, method)
        )
        return cls(stmt)

class StmtMoving(CustomOperator):
    """
    StmtMoving: Move x [before|after] y
    """
    def __str__(self):
        return "StmtMoving({}, {}, '{}')".format(self.y, self.x, self.direction)

    def is_valid_for(self, program):
        if isinstance(program, TreeProgram):
            return True
        return False

    @property
    def x(self):
        """
        Move **x** [before|after] y

        :return: The file path and the index of ingredient statement to be moved.
        :rtype: tuple(str, int)
        """
        return self.args[1]

    @property
    def y(self):
        """
        Move x [before|after] **y**

        :return: The file path and the index of modification point.
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
        :return: ``[StmtInsertion(self.y, self.x, self.direction), StmtReplacement(self.x, None)]``
        :rtype: list(:py:class:`.atomic_operator.AtomicOperator`)
        """
        return [StmtInsertion(self.y, self.x, self.direction), StmtReplacement(self.x, None)]

    @classmethod
    def create(cls, program, stmt_file=None, ingr_file=None, direction='before', method='random'):
        """
        :param program: The program instance to which the created custom operator will be applied.
        :type program: :py:class:`.Program`
        :param str stmt_file: stmt means the modification point of the edit.
          If stmt_file is specified, the statement will be chosen within that file.
        :param str ingr_file: Ingredient is the statement to be moved.
          If ingr_file is specified, the ingredient statement will be chosen within that file.
        :param str method: The way of choosing the modification point. **'random'** or **'weighted'**
        :return: The StmtMoving instance with the randomly-selected stmt & ingr.
        :rtype: :py:class:`.custom_operator.StmtMoving`
        """
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
        return cls(ingredient, stmt, direction)