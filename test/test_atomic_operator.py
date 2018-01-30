import pytest
from pyggi import Program, GranularityLevel
from pyggi.atomic_operator import LineReplacement, LineInsertion


@pytest.fixture(scope='session')
def setup_replacement():
    line_file = 'Triangle.java'
    ingr_file = 'Triangle.java'
    line = (line_file, 1)
    ingredient = (ingr_file, 2)
    return LineReplacement(line, ingredient), line, ingredient


@pytest.fixture(scope='session')
def setup_insertion():
    line_file = 'Triangle.java'
    ingr_file = 'Triangle.java'
    line = (line_file, 1)
    ingredient = (ingr_file, 2)
    return LineInsertion(line, ingredient), line, ingredient


class TestAtomicOperator(object):

    class TestLineReplacement(object):

        def test_init(self, setup_replacement):
            line_replacement, line, ingredient = setup_replacement

            assert line_replacement.line == line
            assert line_replacement.ingredient == ingredient

        def test_create(self):
            program = Program('./resource/Triangle_bug',
                              GranularityLevel.LINE)
            random_line_deletion_0 = LineReplacement.create(
                program,
                line_file='Triangle.java',
                ingr_file='Triangle.java',
                del_rate=0)
            assert isinstance(random_line_deletion_0, LineReplacement)
            assert random_line_deletion_0.ingredient is not None

            random_line_deletion_1 = LineReplacement.create(
                program,
                line_file='Triangle.java',
                ingr_file='Triangle.java',
                del_rate=1)
            assert isinstance(random_line_deletion_1, LineReplacement)
            assert random_line_deletion_1.ingredient is None

    class TestLineInsertion(object):

        def test_init(self, setup_insertion):
            line_insertion, line, ingredient = setup_insertion

            assert line_insertion.line == line
            assert line_insertion.ingredient == ingredient

        def test_create(self):
            program = Program('./resource/Triangle_bug',
                              GranularityLevel.LINE)
            random_line_insertion = LineInsertion.create(
                program, line_file='Triangle.java', ingr_file='Triangle.java')

            assert isinstance(random_line_insertion, LineInsertion)
