import pytest
import os
from pyggi.line import LineProgram as Program

@pytest.fixture(scope='session')
def setup():
    program = Program('../sample/Triangle_bug')
    assert len(program.target_files) == 1
    assert program.target_files[0] == 'Triangle.java'
    return program

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

class TestProgram(object):

    def test_init(self, setup):
        program = setup
        check_program_validity(program)

    def test_init_with_config_file_name(self):
        program = Program('../sample/Triangle_bug', config='.pyggi.config')
        check_program_validity(program)

    def test_init_with_dict_type_config(self):
        target_files = ["Triangle.java"]
        test_command = "./run.sh"
        config = {
            "target_files": target_files,
            "test_command": test_command
        }

        program = Program('../sample/Triangle_bug', config=config)
        check_program_validity(program)
        assert program.test_command == test_command
        assert program.target_files == target_files

    def test_tmp_path(self, setup):
        program = setup

        assert program.tmp_path.startswith(os.path.join(program.TMP_DIR, program.name))

    def test_create_tmp_variant(self, setup):
        program = setup
        os.mkdir(os.path.join(program.tmp_path, 'test_dir'))
        program.create_tmp_variant()

        assert os.path.exists(program.tmp_path)

    def test_load_contents(self, setup):
        program = setup
        assert 'Triangle.java' in program.contents
        assert len(program.contents['Triangle.java']) > 0

    def test_set_weight(self, setup):
        program = setup
        assert 'Triangle.java' not in program.modification_weights
        program.set_weight('Triangle.java', 1, 0.1)
        assert 'Triangle.java' in program.modification_weights
        assert program.modification_weights['Triangle.java'][1] == 0.1

    def test_get_source(self, setup):
        program = setup
        file_contents = open(os.path.join(program.tmp_path, 'Triangle.java'), 'r').read()
        for i in range(len(program.modification_points['Triangle.java'])):
            program.get_source('Triangle.java', i) in file_contents