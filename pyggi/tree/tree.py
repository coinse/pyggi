import os
import ast
import astor
import random
from abc import abstractmethod
from .ast_engine import Astor#, SrcML
from ..base import AbstractProgram, AbstractEdit
from ..utils import get_file_extension

class TreeProgram(AbstractProgram):
    @classmethod
    def get_ast_engine(cls, file_name):
        # get_contents, get_modification_points, get_source, dump, do_replace, do_insert, do_delete
        if get_file_extension(file_name) in ['.py']:
            return Astor()
        #elif get_file_extension(target) in ['.java', '.cpp']:
        #    return SrcML()
        else:
            raise Exception('TreeProgram', '{} file is not supported'.format(get_file_extension(file_name)))

    def load_contents(self):
        self.contents = {}
        self.modification_points = dict()
        self.modification_weights = dict()
        for file_name in self.target_files:
            ast_engine = self.__class__.get_ast_engine(file_name)
            self.contents[file_name] = ast_engine.get_contents(os.path.join(self.path, file_name))
            self.modification_points[file_name] = ast_engine.get_modification_points(self.contents[file_name])

    def get_source(self, file_name, index):
        ast_engine = self.__class__.get_ast_engine(file_name)
        return ast_engine.get_source(self, file_name, index)

    @classmethod
    def dump(cls, contents, file_name):
        ast_engine = cls.get_ast_engine(file_name)
        return ast_engine.dump(contents[file_name])

    def do_replace(self, op, new_contents, modification_points):
        assert get_file_extension(op.target[0]) == get_file_extension(op.ingredient[0])
        ast_engine = self.__class__.get_ast_engine(op.target[0])
        return ast_engine.do_replace(self, op, new_contents, modification_points)

    def do_insert(self, op, new_contents, modification_points):
        assert get_file_extension(op.target[0]) == get_file_extension(op.ingredient[0])
        ast_engine = self.__class__.get_ast_engine(op.target[0])
        return ast_engine.do_insert(self, op, new_contents, modification_points)

    def do_delete(self, op, new_contents, modification_points):
        ast_engine = self.__class__.get_ast_engine(op.target[0])
        return ast_engine.do_delete(self, op, new_contents, modification_points)


class TreeEdit(AbstractEdit):
    @property
    def domain(self):
        return TreeProgram

class StmtReplacement(TreeEdit):
    def __init__(self, target, ingredient):
        self.target = target
        self.ingredient = ingredient

    def apply(self, program, new_contents, modification_points):
        return program.do_replace(self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, method='random'):
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'))

class StmtInsertion(TreeEdit):
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

class StmtDeletion(TreeEdit):
    def __init__(self, target):
        self.target = target

    def apply(self, program, new_contents, modification_points):
        return program.do_delete(self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, method='random'):
        return cls(program.random_target(target_file, method))

class StmtMoving(TreeEdit):
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