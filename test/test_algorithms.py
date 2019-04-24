import pytest
from pyggi.base import Algorithm
from pyggi.line import LineProgram

@pytest.fixture(scope='session')
def setup_program():
    program = LineProgram('../sample/Triangle_bug')
    return program

class MyAlgorithm(Algorithm):
    def setup(self):
        self.name = "myalgo"

    def run(self):
        return True

class TestAlgorithm(object):

    def test_fails_without_override(self, setup_program):
        with pytest.raises(Exception) as e_info:
            program = setup_program
            algorithm = Algorithm(program)

    def test_init_and_setup(self, setup_program):
        program = setup_program
        my_algo = MyAlgorithm(program)
        assert my_algo.name == "myalgo"