import os
from abc import abstractmethod
from ..base import AbstractProgram

class LineProgram(AbstractProgram):
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