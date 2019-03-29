import os
import random
from abc import abstractmethod
from ..base import AbstractProgram, AbstractEdit, CustomOperator

class AbstractLineProgram(AbstractProgram):
    @abstractmethod
    def do_replace(self, target, ingredient):
        pass

    @abstractmethod
    def do_insert(self, target, ingredient, direction='before'):
        pass

    @abstractmethod
    def do_delete(self, target):
        pass

class LineProgram(AbstractLineProgram):
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

    def do_replace(self, op, new_contents, modification_points):
        l_f, l_n = op.target # line file and line number
        if op.ingredient:
            i_f, i_n = op.ingredient
            new_contents[l_f][modification_points[l_f][l_n]] = self.contents[i_f][i_n]
        else:
            new_contents[l_f][modification_points[l_f][l_n]] = ''
        return modification_points

    def do_insert(self, op, new_contents, modification_points):
        l_f, l_n = op.target
        i_f, i_n = op.ingredient
        if op.direction == 'before':
            new_contents[l_f].insert(
                modification_points[l_f][l_n],
                self.contents[i_f][i_n]
            )
            for i in range(l_n, len(modification_points[l_f])):
                modification_points[l_f][i] += 1
        elif op.direction == 'after':
            new_contents[l_f].insert(
                modification_points[l_f][l_n] + 1,
                self.contents[i_f][i_n]
            )
            for i in range(l_n + 1, len(modification_points[l_f])):
                modification_points[l_f][i] += 1
        return True

    def do_delete(self, op, new_contents, modification_points):
        l_f, l_n = op.target # line file and line number
        new_contents[l_f][modification_points[l_f][l_n]] = ''
        return modification_points

class LineReplacement(AbstractEdit):
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

    def __init__(self, target, ingredient=None):
        self.__class__.is_modi(target)
        if ingredient:
            self.__class__.is_modi(ingredient)
        self.target = target
        self.ingredient = ingredient

    @property
    def domain(self):
        return AbstractLineProgram

    def apply(self, program, new_contents, modification_points):
        return program.do_replace(self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, method='random'):
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'))

class LineInsertion(AbstractEdit):
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

    def __init__(self, target, ingredient, direction='before'):
        super().__init__()
        self.__class__.is_modi(target, ingredient)
        assert direction in ['before', 'after']
        self.target = target
        self.ingredient = ingredient
        self.direction = direction

    @property
    def domain(self):
        return AbstractLineProgram

    def apply(self, program, new_contents, modification_points):
        return program.do_insert(self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, direction='before', method='random'):
        return cls(program.random_target(target_file, 'random'),
                   program.random_target(ingr_file, 'random'),
                   direction)

class LineDeletion(AbstractEdit):
    def __init__(self, target):
        super().__init__()
        self.__class__.is_modi(target)
        self.target = target

    @property
    def domain(self):
        return AbstractLineProgram

    def apply(self, program, new_contents, modification_points):
        return program.do_delete(self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, method='random'):
        return cls(program.random_target(target_file, method))

class LineMoving(AbstractEdit):
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

    def __init__(self, target, ingredient, direction='before'):
        super().__init__()
        self.__class__.is_modi(target, ingredient)
        assert direction in ['before', 'after']
        self.target = target
        self.ingredient = ingredient
        self.direction = direction

    @property
    def domain(self):
        return AbstractLineProgram

    def apply(self, program, new_contents, modification_points):
        program.do_insert(self, new_contents, modification_points)
        program.do_delete(self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, direction='before', method='random'):
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'),
                   direction)