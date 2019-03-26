import os
import ast
import astor
from abc import abstractmethod
from ..base import Program
from . import astor_helper

class TreeProgram(Program):
    def __str__(self):
        return self.target_files

    @property
    def modification_points(self):
        if self._modification_points:
            return self._modification_points

        self._modification_points = dict()
        for target_file in self.target_files:
            if Program.is_python_code(target_file):
                from ..tree import astor_helper
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

        if Program.is_python_code(target_file):
            def print_modification_point(contents, modification_points, i):
                import astor
                from ..tree import astor_helper
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
            if cls.is_python_code(target):
                root = astor.parse_file(os.path.join(path, target))
                contents[target] = root
            else:
                raise Exception('Program', '{} file is not supported'.format(cls.get_file_extension(target)))
        return contents
