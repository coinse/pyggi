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
    def __str__(self):
        code = ''
        for k in sorted(self.contents.keys()):
            idx = 0
            for line in self.contents[k]:
                code += "{}\t: {}\t: {}\n".format(k, idx, line)
                idx += 1
        return code

    def load_contents(self):
        self.contents = {}
        self.modification_points = dict()
        self.modification_weights = dict()
        for target in self.target_files:
            with open(os.path.join(self.path, target), 'r') as target_file:
                self.contents[target] = list(
                    map(str.rstrip, target_file.readlines()))
            self.modification_points[target] = list(range(len(self.contents[target])))
            self.modification_weights[target] = [1.0] * len(self.modification_points[target])

    def print_modification_points(self, target_file, indices=None):
        def print_modification_point(contents, modification_points, i):
            print(title_format.format('line', i))
            print(contents[modification_points[i]])
        title_format = "=" * 25 + " {} {} " + "=" * 25
        if not indices:
            indices = range(len(self.modification_points[target_file]))
        for i in indices:
            print_modification_point(self.contents[target_file], self.modification_points[target_file], i)

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