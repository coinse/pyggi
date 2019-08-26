from abc import abstractmethod
from ..base import AbstractEngine

class AbstractLineEngine(AbstractEngine):
    @classmethod
    @abstractmethod
    def do_replace(cls, program, op, new_contents, modification_points):
        pass

    @classmethod
    @abstractmethod
    def do_insert(cls, program, op, new_contents, modification_points):
        pass

    @classmethod
    @abstractmethod
    def do_delete(cls, program, op, new_contents, modification_points):
        pass

class LineEngine(AbstractLineEngine):
    @classmethod
    def get_contents(cls, file_path):
        with open(file_path, 'r') as target_file:
            return list(map(str.rstrip, target_file.readlines()))
    
    @classmethod
    def get_modification_points(cls, contents_of_file):
        return list(range(len(contents_of_file)))

    @classmethod
    def get_source(cls, program, file_name, index):
        return program.contents[file_name][index]
    
    @classmethod
    def dump(cls, contents_of_file):
        return '\n'.join(contents_of_file) + '\n'

    @classmethod
    def do_replace(cls, program, op, new_contents, modification_points):
        l_f, l_n = op.target # line file and line number
        if op.ingredient:
            i_f, i_n = op.ingredient
            new_contents[l_f][modification_points[l_f][l_n]] = program.contents[i_f][i_n]
        else:
            new_contents[l_f][modification_points[l_f][l_n]] = ''
        return True
    
    @classmethod
    def do_insert(cls, program, op, new_contents, modification_points):
        l_f, l_n = op.target
        i_f, i_n = op.ingredient
        if op.direction == 'before':
            new_contents[l_f].insert(
                modification_points[l_f][l_n],
                program.contents[i_f][i_n]
            )
            for i in range(l_n, len(modification_points[l_f])):
                modification_points[l_f][i] += 1
        elif op.direction == 'after':
            new_contents[l_f].insert(
                modification_points[l_f][l_n] + 1,
                program.contents[i_f][i_n]
            )
            for i in range(l_n + 1, len(modification_points[l_f])):
                modification_points[l_f][i] += 1
        return True

    @classmethod
    def do_delete(cls, program, op, new_contents, modification_points):
        l_f, l_n = op.target # line file and line number
        new_contents[l_f][modification_points[l_f][l_n]] = ''
        return True