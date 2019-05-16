import pytest
import copy
from pyggi.line import LineProgram
from pyggi.line import LineReplacement, LineInsertion, LineDeletion
from pyggi.tree import TreeProgram
from pyggi.tree import StmtReplacement, StmtInsertion, StmtDeletion

@pytest.fixture(scope='session')
def setup_line_replacement():
    target_file = 'Triangle.java'
    ingr_file = 'Triangle.java'
    target = (target_file, 1)
    ingredient = (ingr_file, 2)
    return LineReplacement(target, ingredient), target, ingredient

@pytest.fixture(scope='session')
def setup_line_insertion():
    target_file = 'Triangle.java'
    ingr_file = 'Triangle.java'
    target = (target_file, 1)
    ingredient = (ingr_file, 2)
    return LineInsertion(target, ingredient), target, ingredient

@pytest.fixture(scope='session')
def setup_line_deletion():
    target_file = 'Triangle.java'
    target = (target_file, 2)
    return LineDeletion(target), target

@pytest.fixture(scope='session')
def setup_stmt_replacement():
    target_file = 'triangle.py'
    ingr_file = 'triangle.py'
    target = (target_file, 1)
    ingredient = (ingr_file, 2)
    return StmtReplacement(target, ingredient), target, ingredient

@pytest.fixture(scope='session')
def setup_stmt_insertion():
    target_file = 'triangle.py'
    ingr_file = 'triangle.py'
    target = (target_file, 1)
    ingredient = (ingr_file, 2)
    return StmtInsertion(target, ingredient), target, ingredient

@pytest.fixture(scope='session')
def setup_stmt_deletion():
    target_file = 'triangle.py'
    target = (target_file, 1)
    return StmtDeletion(target), target

class TestEdit(object):
    def test_equal(self):
        target_file = 'Triangle.java'
        ingr_file = 'Triangle.java'
        target = (target_file, 1)
        ingredient = (ingr_file, 2)
        line_replacement = LineReplacement(target, ingredient)
        line_replacement2 = LineReplacement(target, ingredient)
        line_replacement3 = LineReplacement(target, target)
        line_insertion = LineInsertion(target, ingredient)
        assert line_replacement is not line_replacement2
        assert line_replacement == line_replacement2
        assert line_replacement != line_replacement3
        assert line_insertion != line_replacement

    def test_domain(self, setup_line_replacement, setup_stmt_replacement):
        line_replacement, target, ingredient = setup_line_replacement
        stmt_replacement, target2, ingredient2 = setup_stmt_replacement

        assert line_replacement != stmt_replacement
        assert line_replacement.domain != stmt_replacement.domain

    class TestLineReplacement(object):

        def test_init(self, setup_line_replacement):
            line_replacement, target, ingredient = setup_line_replacement

            assert line_replacement.target == target
            assert line_replacement.ingredient == ingredient

        def test_create(self):
            program = LineProgram('../sample/Triangle_bug_java')
            random_line_replacement = LineReplacement.create(
                program,
                target_file='Triangle.java',
                ingr_file='Triangle.java')

            assert isinstance(random_line_replacement, LineReplacement)
            assert random_line_replacement.ingredient is not None
            assert isinstance(program, random_line_replacement.domain)

        def test_apply(self, setup_line_replacement):
            line_replacement, target, ingredient = setup_line_replacement
            program = LineProgram('../sample/Triangle_bug_java')
            modification_points = copy.deepcopy(program.modification_points)
            new_contents = copy.deepcopy(program.contents)
            line_replacement.apply(program, new_contents, modification_points)
            assert program.contents[ingredient[0]][ingredient[1]] == new_contents[target[0]][target[1]]
            assert program.modification_points[target[0]] != len(modification_points[target[0]])
            assert program.contents != new_contents

    class TestLineInsertion(object):

        def test_init(self, setup_line_insertion):
            line_insertion, target, ingredient = setup_line_insertion

            assert line_insertion.target == target
            assert line_insertion.ingredient == ingredient

        def test_create(self):
            program = LineProgram('../sample/Triangle_bug_java')
            random_line_insertion = LineInsertion.create(
                program, target_file='Triangle.java', ingr_file='Triangle.java')

            assert isinstance(random_line_insertion, LineInsertion)
            assert isinstance(program, random_line_insertion.domain)
        
        def test_apply(self, setup_line_insertion):
            line_insertion, target, ingredient = setup_line_insertion
            program = LineProgram('../sample/Triangle_bug_java')
            modification_points = copy.deepcopy(program.modification_points)
            new_contents = copy.deepcopy(program.contents)
            line_insertion.apply(program, new_contents, modification_points)
            assert program.contents[ingredient[0]][ingredient[1]] == new_contents[target[0]][target[1]]
            assert program.modification_points[target[0]] != modification_points[target[0]]
            assert program.contents != new_contents

    class TestLineDeletion(object):

        def test_init(self, setup_line_deletion):
            line_insertion, target = setup_line_deletion

            assert line_insertion.target == target

        def test_create(self):
            program = LineProgram('../sample/Triangle_bug_java')
            random_line_deletion = LineDeletion.create(
                program, target_file='Triangle.java')

            assert isinstance(random_line_deletion, LineDeletion)
            assert isinstance(program, random_line_deletion.domain)
        
        def test_apply(self, setup_line_deletion):
            line_deletion, target = setup_line_deletion
            program = LineProgram('../sample/Triangle_bug_java')
            modification_points = copy.deepcopy(program.modification_points)
            new_contents = copy.deepcopy(program.contents)
            line_deletion.apply(program, new_contents, modification_points)
            assert new_contents[target[0]][target[1]] == ''
            assert program.modification_points[target[0]] == modification_points[target[0]]

    class TestStmtReplacement(object):

        def test_init(self, setup_stmt_replacement):
            stmt_replacement, target, ingredient = setup_stmt_replacement

            assert stmt_replacement.target == target
            assert stmt_replacement.ingredient == ingredient

        def test_create(self):
            program = TreeProgram('../sample/Triangle_bug_python')
            random_stmt_replacement = StmtReplacement.create(
                program,
                target_file='triangle.py',
                ingr_file='triangle.py')

            assert isinstance(random_stmt_replacement, StmtReplacement)
            assert random_stmt_replacement.ingredient is not None
            assert isinstance(program, random_stmt_replacement.domain)

        def test_apply(self, setup_stmt_replacement):
            stmt_replacement, target, ingredient = setup_stmt_replacement
            program = TreeProgram('../sample/Triangle_bug_python')
            modification_points = copy.deepcopy(program.modification_points)
            new_contents = copy.deepcopy(program.contents)
            stmt_replacement.apply(program, new_contents, modification_points)
            assert program.modification_points[target[0]] != len(modification_points[target[0]])
            assert program.contents != new_contents

    class TestStmtInsertion(object):

        def test_init(self, setup_stmt_insertion):
            stmt_insertion, target, ingredient = setup_stmt_insertion

            assert stmt_insertion.target == target
            assert stmt_insertion.ingredient == ingredient

        def test_create(self):
            program = TreeProgram('../sample/Triangle_bug_python')
            random_stmt_insertion = StmtInsertion.create(
                program, target_file='triangle.py', ingr_file='triangle.py')

            assert isinstance(random_stmt_insertion, StmtInsertion)
            assert isinstance(program, random_stmt_insertion.domain)
        
        def test_apply(self, setup_stmt_insertion):
            stmt_insertion, target, ingredient = setup_stmt_insertion
            program = TreeProgram('../sample/Triangle_bug_python')
            modification_points = copy.deepcopy(program.modification_points)
            new_contents = copy.deepcopy(program.contents)
            stmt_insertion.apply(program, new_contents, modification_points)
            assert program.modification_points[target[0]] != modification_points[target[0]]
            assert program.contents != new_contents

    class TestStmtDeletion(object):

        def test_init(self, setup_stmt_deletion):
            stmt_insertion, target = setup_stmt_deletion

            assert stmt_insertion.target == target

        def test_create(self):
            program = TreeProgram('../sample/Triangle_bug_python')
            random_stmt_deletion = StmtDeletion.create(
                program, target_file='triangle.py')

            assert isinstance(random_stmt_deletion, StmtDeletion)
            assert isinstance(program, random_stmt_deletion.domain)
        
        def test_apply(self, setup_stmt_deletion):
            stmt_deletion, target = setup_stmt_deletion
            program = TreeProgram('../sample/Triangle_bug_python')
            modification_points = copy.deepcopy(program.modification_points)
            new_contents = copy.deepcopy(program.contents)
            stmt_deletion.apply(program, new_contents, modification_points)
            assert program.modification_points[target[0]] == modification_points[target[0]]
