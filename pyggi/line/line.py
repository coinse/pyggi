import os
import random
from abc import abstractmethod
from ..base import AbstractProgram, Replacement, Insertion, Deletion, Moving

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

class LineReplacement(Replacement):
    @property
    def domain(self):
        return AbstractLineProgram

class LineInsertion(Insertion):
    @property
    def domain(self):
        return AbstractLineProgram

class LineDeletion(Deletion):
    @property
    def domain(self):
        return AbstractLineProgram

class LineMoving(Moving):
    @property
    def domain(self):
        return AbstractLineProgram

class LineProgram(AbstractLineProgram):
    def load_contents(self):
        self.contents = {}
        self.modification_points = dict()
        self.modification_weights = dict()
        for file_name in self.target_files:
            with open(os.path.join(self.path, file_name), 'r') as target_file:
                self.contents[file_name] = list(
                    map(str.rstrip, target_file.readlines()))
            self.modification_points[file_name] = list(range(len(self.contents[file_name])))
            self.modification_weights[file_name] = [1.0] * len(self.modification_points[file_name])

    def get_source(self, target_file, indices=None):
        if not indices:
            indices = range(len(self.modification_points[target_file]))
        return { i: self.contents[modification_points[i]] for i in indices }

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