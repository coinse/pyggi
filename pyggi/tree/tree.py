import os
import ast
import astor
import random
from abc import abstractmethod
from . import astor_helper
from ..base import AbstractProgram, AbstractEdit, Replacement, Insertion, Deletion, Moving
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

class TreeProgram(AbstractTreeProgram):
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

    def do_replace(self, op, new_contents, modification_points):
        assert have_the_same_file_extension(op.target[0], op.ingredient[0])
        if check_file_extension(op.target[0], 'py'):
            dst_root = new_contents[op.target[0]]
            dst_pos = modification_points[op.target[0]][op.target[1]]
            ingr_root = self.contents[op.ingredient[0]]
            ingr_pos = self.modification_points[op.ingredient[0]][op.ingredient[1]]
            return astor_helper.replace((dst_root, dst_pos), (ingr_root, ingr_pos))
        return False

    def do_insert(self, op, new_contents, modification_points):
        assert have_the_same_file_extension(op.target[0], op.ingredient[0])
        success = False
        if check_file_extension(op.target[0], 'py'):
            dst_root = new_contents[op.target[0]]
            dst_pos = modification_points[op.target[0]][op.target[1]]
            ingr_root = self.contents[op.ingredient[0]]
            ingr_pos = astor_helper.get_modification_points(ingr_root)[op.ingredient[1]]
            if op.direction == 'before':
                success = astor_helper.insert_before((dst_root, dst_pos), (ingr_root, ingr_pos))
                if success:
                    depth = len(dst_pos)
                    parent = dst_pos[:depth-1]
                    index = dst_pos[depth-1][1]
                    for pos in modification_points[op.target[0]]:
                        if parent == pos[:depth-1] and len(pos) >= depth and index <= pos[depth-1][1]:
                            a, i = pos[depth-1]
                            pos[depth-1] = (a, i + 1)
            elif op.direction == 'after':
                success = astor_helper.insert_after((dst_root, dst_pos), (ingr_root, ingr_pos))
                if success:
                    depth = len(dst_pos)
                    parent = dst_pos[:depth-1]
                    index = dst_pos[depth - 1][1]
                    for pos in modification_points[op.target[0]]:
                        if parent == pos[:depth-1] and len(pos) >= depth and index < pos[depth-1][1]:
                            a, i = pos[depth-1]
                            pos[depth-1] = (a, i + 1)
        return success

    def do_delete(self, op, new_contents, modification_points):
        if check_file_extension(op.target[0], 'py'):
            dst_root = new_contents[op.target[0]]
            dst_pos = modification_points[op.target[0]][op.target[1]]
            if not op.ingredient:
                return astor_helper.replace((dst_root, dst_pos), op.ingredient)
        return False

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