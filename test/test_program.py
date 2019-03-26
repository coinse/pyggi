import pytest
import os
from pyggi.line import LineProgram as Program


@pytest.fixture(scope='session')
def setup():
    program = Program('./resource/Triangle_bug')
    assert len(program.target_files) == 1
    assert program.target_files[0] == 'Triangle.java'

    return program


class TestProgram(object):

    def test_init(self, setup):
        program = setup

        assert not program.path.endswith('/')
        assert program.name == os.path.basename(program.path)
        assert program.test_command is not None
        assert program.target_files is not None

    def test_tmp_path(self, setup):
        program = setup

        assert program.tmp_path == os.path.join(Program.TMP_DIR, program.name)

    def test_clean_tmp_dir(self, setup):
        program = setup
        os.mkdir(os.path.join(program.tmp_path, 'test_dir'))
        Program.clean_tmp_dir(program.tmp_path)

        assert not os.listdir(program.tmp_path)

    def test_parse(self, setup):
        program = setup
        contents = program.parse(program.path, program.target_files)
        assert 'Triangle.java' in contents
        assert len(contents['Triangle.java']) > 0
