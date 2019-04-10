import os
import random
from abc import abstractmethod
from ..base import AbstractProgram, AbstractEdit

class LineProgram(AbstractProgram):
    def load_contents(self):
        self.contents = {}
        self.modification_points = dict()
        self.modification_weights = dict()
        for file_name in self.target_files:
            with open(os.path.join(self.path, file_name), 'r') as target_file:
                self.contents[file_name] = list(
                    map(str.rstrip, target_file.readlines()))
            self.modification_points[file_name] = list(range(len(self.contents[file_name])))

    def get_source(self, file_name, index):
        return self.contents[file_name][index]

    @classmethod
    def dump(cls, contents, file_name):
        return '\n'.join(contents[file_name]) + '\n'

    def do_replace(self, op, new_contents, modification_points):
        l_f, l_n = op.target # line file and line number
        if op.ingredient:
            i_f, i_n = op.ingredient
            new_contents[l_f][modification_points[l_f][l_n]] = self.contents[i_f][i_n]
        else:
            new_contents[l_f][modification_points[l_f][l_n]] = ''
        return True

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
        return True

class LineEdit(AbstractEdit):
    @property
    def domain(self):
        return LineProgram

class LineReplacement(LineEdit):
    def __init__(self, target, ingredient):
        self.target = target
        self.ingredient = ingredient

    def apply(self, program, new_contents, modification_points):
        return program.do_replace(self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, method='random'):
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'))

class LineInsertion(LineEdit):
    def __init__(self, target, ingredient, direction='before'):
        assert direction in ['before', 'after']
        self.target = target
        self.ingredient = ingredient
        self.direction = direction

    def apply(self, program, new_contents, modification_points):
        return program.do_insert(self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, direction='before', method='random'):
        return cls(program.random_target(target_file, 'random'),
                   program.random_target(ingr_file, 'random'),
                   direction)

class LineDeletion(LineEdit):
    def __init__(self, target):
        self.target = target

    def apply(self, program, new_contents, modification_points):
        return program.do_delete(self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, method='random'):
        return cls(program.random_target(target_file, method))

class LineMoving(LineEdit):
    def __init__(self, target, ingredient, direction='before'):
        assert direction in ['before', 'after']
        self.target = target
        self.ingredient = ingredient
        self.direction = direction

    def apply(self, program, new_contents, modification_points):
        program.do_insert(self, new_contents, modification_points)
        program.do_delete(self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, direction='before', method='random'):
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'),
                   direction)