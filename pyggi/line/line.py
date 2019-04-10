import os
import random
from abc import abstractmethod
from ..base import AbstractProgram, AbstractEdit
from .engine import LineEngine

class LineProgram(AbstractProgram):
    @classmethod
    def get_engine(cls, file_name):
        return LineEngine

    def do_replace(self, op, new_contents, modification_points):
        assert self.engines[op.target[0]] == self.engines[op.ingredient[0]]
        engine = self.engines[op.target[0]]
        return engine.do_replace(self, op, new_contents, modification_points)

    def do_insert(self, op, new_contents, modification_points):
        assert self.engines[op.target[0]] == self.engines[op.ingredient[0]]
        engine = self.engines[op.target[0]]
        return engine.do_insert(self, op, new_contents, modification_points)

    def do_delete(self, op, new_contents, modification_points):
        engine = self.engines[op.target[0]]
        return engine.do_delete(self, op, new_contents, modification_points)

"""
Possible Edit Operators
"""
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
        return cls(program.random_target(target_file, method),
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