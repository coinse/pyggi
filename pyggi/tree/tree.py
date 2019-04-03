import os
import ast
import astor
import random
from abc import abstractmethod
from .ast_engine import Astor#, SrcML
from ..base import AbstractProgram, Replacement, Insertion, Deletion, Moving
from ..utils import check_file_extension, get_file_extension, have_the_same_file_extension

class AbstractTreeProgram(AbstractProgram):
    @abstractmethod
    def do_replace(self, op, new_contents, modification_points):
        pass

    @abstractmethod
    def do_insert(self, op, new_contents, modification_points, direction='before'):
        pass

    @abstractmethod
    def do_delete(self, op, new_contents, modification_points):
        pass

class StmtReplacement(Replacement):
    @property
    def domain(self):
        return AbstractTreeProgram

class StmtInsertion(Insertion):
    @property
    def domain(self):
        return AbstractTreeProgram

class StmtDeletion(Deletion):
    @property
    def domain(self):
        return AbstractTreeProgram

class StmtMoving(Moving):
    @property
    def domain(self):
        return AbstractTreeProgram

class TreeProgram(AbstractTreeProgram):
    @classmethod
    def get_ast_engine(cls, file_name):
        # get_contents, get_modification_points, get_source, dump, do_replace, do_insert, do_delete
        if get_file_extension(file_name) in ['.py']:
            return Astor()
        #elif get_file_extension(target) in ['.java', '.cpp']:
        #    return srcml_helper
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
            self.modification_weights[file_name] = [1.0] * len(self.modification_points[file_name])

    def get_source(self, file_name, indices=None):
        ast_engine = self.__class__.get_ast_engine(file_name)
        if not indices:
            indices = range(len(self.modification_points[file_name]))
        return { i: ast_engine.get_source(self, file_name, i) for i in indices }

    @classmethod
    def dump(cls, contents, file_name):
        ast_engine = cls.get_ast_engine(file_name)
        return ast_engine.dump(contents[file_name])

    def do_replace(self, op, new_contents, modification_points):
        assert have_the_same_file_extension(op.target[0], op.ingredient[0])
        ast_engine = self.__class__.get_ast_engine(op.target[0])
        return ast_engine.do_replace(self, op, new_contents, modification_points)

    def do_insert(self, op, new_contents, modification_points):
        assert have_the_same_file_extension(op.target[0], op.ingredient[0])
        ast_engine = self.__class__.get_ast_engine(op.target[0])
        return ast_engine.do_insert(self, op, new_contents, modification_points)

    def do_delete(self, op, new_contents, modification_points):
        ast_engine = self.__class__.get_ast_engine(op.target[0])
        return ast_engine.do_delete(self, op, new_contents, modification_points)