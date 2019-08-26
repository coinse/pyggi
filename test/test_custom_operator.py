import pytest
from pyggi import Program, GranularityLevel
from pyggi.custom_operator import LineDeletion, LineMoving
from pyggi.atomic_operator import LineReplacement, LineInsertion


@pytest.fixture(scope='session')
def setup_deletion():
    line_file = 'Triangle.java'
    line = (line_file, 0)
    return LineDeletion(line), line


@pytest.fixture(scope='session')
def setup_moving():
    point_file = 'Triangle.java'
    ingr_file = 'Triangle.java'
    point = (point_file, 1)
    ingredient = (ingr_file, 2)
    return LineMoving(point, ingredient, 'before'), ingredient, point


class TestCustomOperator(object):

    class TestLineDeletion(object):

        def test_length_of_args(self, setup_deletion):
            line_deletion, _ = setup_deletion

            assert line_deletion.length_of_args == 1

        def test_x(self, setup_deletion):
            line_deletion, line = setup_deletion

            assert line_deletion.x == line

        def test_atomic_operators(self, setup_deletion):
            line_deletion, _ = setup_deletion

            assert [LineReplacement(line_deletion.x,
                                    None)] == line_deletion.atomic_operators

        def test_create(self):
            program = Program('./resource/Triangle_bug',
                              GranularityLevel.LINE)
            random_line_deletion = LineDeletion.create(program)

            assert random_line_deletion.x is not None

    class TestLineMoving(object):

        def test_length_of_args(self, setup_moving):
            line_moving, _, _ = setup_moving

            assert line_moving.length_of_args == 3

        def test_x(self, setup_moving):
            line_moving, ingredient, _ = setup_moving

            assert line_moving.x == ingredient

        def test_y(self, setup_moving):
            line_moving, _, point = setup_moving

            assert line_moving.y == point

        def test_atomic_operators(self, setup_moving):
            line_moving, _, _ = setup_moving

            assert [
                LineInsertion(line_moving.y, line_moving.x),
                LineReplacement(line_moving.x, None)
            ] == line_moving.atomic_operators

        def test_create(self):
            program = Program('./resource/Triangle_bug',
                              GranularityLevel.LINE)
            random_line_moving = LineMoving.create(program)

            assert random_line_moving.x is not None
            assert random_line_moving.y is not None
