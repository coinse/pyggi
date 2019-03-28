import pytest
from pyggi.line import LineProgram as Program
from pyggi.line import LineReplacement, LineInsertion


@pytest.fixture(scope='session')
def setup_replacement():
    target_file = 'Triangle.java'
    ingr_file = 'Triangle.java'
    target = (target_file, 1)
    ingredient = (ingr_file, 2)
    return LineReplacement(target, ingredient), target, ingredient


@pytest.fixture(scope='session')
def setup_insertion():
    target_file = 'Triangle.java'
    ingr_file = 'Triangle.java'
    target = (target_file, 1)
    ingredient = (ingr_file, 2)
    return LineInsertion(target, ingredient), target, ingredient


class TestAtomicOperator(object):

    class TestLineReplacement(object):

        def test_init(self, setup_replacement):
            line_replacement, target, ingredient = setup_replacement

            assert line_replacement.target == target
            assert line_replacement.ingredient == ingredient

        def test_create(self):
            program = Program('./resource/Triangle_bug')
            random_line_deletion_0 = LineReplacement.create(
                program,
                target_file='Triangle.java',
                ingr_file='Triangle.java',
                del_rate=0)
            assert isinstance(random_line_deletion_0, LineReplacement)
            assert random_line_deletion_0.ingredient is not None

            random_line_deletion_1 = LineReplacement.create(
                program,
                target_file='Triangle.java',
                ingr_file='Triangle.java',
                del_rate=1)
            assert isinstance(random_line_deletion_1, LineReplacement)
            assert random_line_deletion_1.ingredient is None

    class TestLineInsertion(object):

        def test_init(self, setup_insertion):
            line_insertion, target, ingredient = setup_insertion

            assert line_insertion.target == target
            assert line_insertion.ingredient == ingredient

        def test_create(self):
            program = Program('./resource/Triangle_bug')
            random_line_insertion = LineInsertion.create(
                program, target_file='Triangle.java', ingr_file='Triangle.java')

            assert isinstance(random_line_insertion, LineInsertion)
