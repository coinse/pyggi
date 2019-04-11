from ..base import AbstractEngine

class LineEngine(AbstractEngine):
    def get_contents(self, file_path):
        with open(file_path, 'r') as target_file:
            return list(map(str.rstrip, target_file.readlines()))
    
    def get_modification_points(self, contents_of_file):
        return list(range(len(contents_of_file)))

    def get_source(self, program, file_name, index):
        return program.contents[file_name][index]
    
    def dump(self, contents_of_file):
        return '\n'.join(contents_of_file) + '\n'

    def do_replace(self, program, op, new_contents, modification_points):
        l_f, l_n = op.target # line file and line number
        if op.ingredient:
            i_f, i_n = op.ingredient
            new_contents[l_f][modification_points[l_f][l_n]] = program.contents[i_f][i_n]
        else:
            new_contents[l_f][modification_points[l_f][l_n]] = ''
        return True
    
    def do_insert(self, program, op, new_contents, modification_points):
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

    def do_delete(self, program, op, new_contents, modification_points):
        l_f, l_n = op.target # line file and line number
        new_contents[l_f][modification_points[l_f][l_n]] = ''
        return True