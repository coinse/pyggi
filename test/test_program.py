import pytest
import os
import random
from pyggi.base import Patch
from pyggi.line import LineProgram, LineInsertion, LineEngine
from pyggi.tree import TreeProgram, StmtInsertion, AstorEngine

class MyLineProgram(LineProgram):
    def compute_fitness(self, result, return_code, stdout, stderr, elapsed_time):
        print(elapsed_time, stdout, stderr)
        import re
        m = re.findall("runtime: ([0-9.]+)", stdout)
        if len(m) > 0:
            runtime = m[0]
            failed = re.findall("([0-9]+) failed", stdout)
            pass_all = len(failed) == 0
            failed = int(failed[0]) if not pass_all else 0
            result.fitness = failed
        else:
            result.status = 'PARSE_ERROR'

class MyTreeProgram(TreeProgram):
    def compute_fitness(self, result, return_code, stdout, stderr, elapsed_time):
        print(elapsed_time, stdout, stderr)
        import re
        m = re.findall("runtime: ([0-9.]+)", stdout)
        if len(m) > 0:
            runtime = m[0]
            failed = re.findall("([0-9]+) failed", stdout)
            pass_all = len(failed) == 0
            failed = int(failed[0]) if not pass_all else 0
            result.fitness = failed
        else:
            result.status = 'PARSE_ERROR'

@pytest.fixture(scope='session')
def setup_line():
    line_program = MyLineProgram('../sample/Triangle_bug_python')
    return line_program

@pytest.fixture(scope='session')
def setup_tree():
    tree_program = MyTreeProgram('../sample/Triangle_bug_python')
    return tree_program

def check_program_validity(program):
    assert not program.path.endswith('/')
    assert program.name == os.path.basename(program.path)
    assert program.test_command is not None
    assert program.target_files is not None
    assert all([program.engines[target_file] is not None
        for target_file in program.target_files])
    assert all([program.modification_points[target_file] is not None
        for target_file in program.target_files])
    assert os.path.exists(program.tmp_path)

class TestLineProgram(object):

    def test_init(self, setup_line):
        program = setup_line
        check_program_validity(program)

    def test_init_with_config_file_name(self):
        program = LineProgram('../sample/Triangle_bug_python', config='.pyggi.config')
        check_program_validity(program)

    def test_init_with_dict_type_config(self):
        target_files = ["triangle.py"]
        test_command = "./run.sh"
        config = {
            "target_files": target_files,
            "test_command": test_command
        }

        program = LineProgram('../sample/Triangle_bug_python', config=config)
        check_program_validity(program)
        assert program.test_command == test_command
        assert program.target_files == target_files

    def test_get_engine(self, setup_line):
        program = setup_line
        assert program.get_engine('triangle.py') == LineEngine

    def test_random_target(self, setup_line):
        program = setup_line
        with pytest.raises(AssertionError) as e_info:
            program.random_target(target_file="triangle2.py")
        file, point = program.random_target()
        assert file in program.target_files
        assert point in range(len(program.modification_points[file]))

    def test_tmp_path(self, setup_line):
        program = setup_line
        assert program.tmp_path.startswith(os.path.join(program.TMP_DIR, program.name))

    def test_create_tmp_variant(self, setup_line):
        program = setup_line
        assert os.path.exists(program.tmp_path)

    def test_load_contents(self, setup_line):
        program = setup_line
        assert 'triangle.py' in program.contents
        assert len(program.contents['triangle.py']) > 0

    def test_set_weight(self, setup_line):
        program = setup_line
        assert 'triangle.py' not in program.modification_weights
        program.set_weight('triangle.py', 1, 0.1)
        assert 'triangle.py' in program.modification_weights
        assert program.modification_weights['triangle.py'][1] == 0.1

    def test_random_target_weighted(self, setup_line):
        program = setup_line
        file = program.random_file()
        index = random.randrange(len(program.modification_points[file]))
        for i in range(len(program.modification_points[file])):
            program.set_weight(file, i, 0)
        program.set_weight(file, index, 1)
        file, point = program.random_target(file, "weighted")
        assert point == index

    def test_get_source(self, setup_line):
        program = setup_line
        file_contents = open(os.path.join(program.tmp_path, 'triangle.py'), 'r').read()
        for i in range(len(program.modification_points['triangle.py'])):
            program.get_source('triangle.py', i) in file_contents

    def test_apply(self, setup_line):
        program = setup_line
        patch = Patch(program)
        patch.add(LineInsertion(('triangle.py', 1), ('triangle.py', 10), direction='after'))
        program.apply(patch)
        file_contents = open(os.path.join(program.tmp_path, 'triangle.py'), 'r').read()
        assert file_contents == program.dump(program.get_modified_contents(patch), 'triangle.py')

    def test_exec_cmd(self, setup_line):
        program = setup_line
        _, stdout, _, _ = program.exec_cmd(['echo', 'hello'])
        assert stdout.decode('ascii').strip() == "hello"

    def test_evaluate_patch(self, setup_line):
        program = setup_line
        patch = Patch(program)
        run = program.evaluate_patch(patch)
        assert run.status == 'SUCCESS'
        assert run.fitness is not None

    def test_remove_tmp_variant(self, setup_line):
        program = setup_line
        program.remove_tmp_variant()
        assert not os.path.exists(program.tmp_path)

class TestTreeProgram(object):

    def test_init(self, setup_tree):
        program = setup_tree
        check_program_validity(program)

    def test_init_with_config_file_name(self):
        program = MyTreeProgram('../sample/Triangle_bug_python', config='.pyggi.config')
        check_program_validity(program)

    def test_init_with_dict_type_config(self):
        target_files = ["triangle.py"]
        test_command = "./run.sh"
        config = {
            "target_files": target_files,
            "test_command": test_command
        }
        program = MyTreeProgram('../sample/Triangle_bug_python', config=config)
        check_program_validity(program)
        assert program.test_command == test_command
        assert program.target_files == target_files

    def test_get_engine(self, setup_tree):
        program = setup_tree
        with pytest.raises(Exception) as e_info:
            program.get_engine('triangle.html')
        assert program.get_engine('triangle.py') == AstorEngine

    def test_tmp_path(self, setup_tree):
        program = setup_tree

        assert program.tmp_path.startswith(os.path.join(program.TMP_DIR, program.name))

    def test_create_tmp_variant(self, setup_tree):
        program = setup_tree
        assert os.path.exists(program.tmp_path)

    def test_load_contents(self, setup_tree):
        program = setup_tree
        assert 'triangle.py' in program.contents
        assert program.contents['triangle.py'] is not None

    def test_set_weight(self, setup_tree):
        program = setup_tree
        assert 'triangle.py' not in program.modification_weights
        program.set_weight('triangle.py', 1, 0.1)
        assert 'triangle.py' in program.modification_weights
        assert program.modification_weights['triangle.py'][1] == 0.1

    def test_get_source(self, setup_tree):
        program = setup_tree
        file_contents = open(os.path.join(program.tmp_path, 'triangle.py'), 'r').read()
        for i in range(len(program.modification_points['triangle.py'])):
            program.get_source('triangle.py', i) in file_contents

    def test_apply(self, setup_tree):
        program = setup_tree
        patch = Patch(program)
        patch.add(StmtInsertion(('triangle.py', 1), ('triangle.py', 10), direction='after'))
        program.apply(patch)
        file_contents = open(os.path.join(program.tmp_path, 'triangle.py'), 'r').read()
        assert file_contents == program.dump(program.get_modified_contents(patch), 'triangle.py')

    def test_diff(self, setup_tree):
        program = setup_tree
        patch = Patch(program)
        assert not program.diff(patch).strip()
        patch.add(StmtInsertion(('triangle.py', 1), ('triangle.py', 10), direction='after'))
        assert program.diff(patch).strip()

    def test_exec_cmd(self, setup_tree):
        program = setup_tree
        _, stdout, _, _ = program.exec_cmd(['echo', 'hello'])
        assert stdout.decode('ascii').strip() == "hello"

    def test_evaluate_patch(self, setup_tree):
        program = setup_tree
        patch = Patch(program)
        run = program.evaluate_patch(patch)
        assert run.status == 'SUCCESS'
        assert run.fitness is not None

    def test_remove_tmp_variant(self, setup_tree):
        program = setup_tree
        program.remove_tmp_variant()
        assert not os.path.exists(program.tmp_path)
