import pytest
from pyggi import Program, Patch, MnplLevel
from pyggi.edit import LineDeletion, LineMoving


@pytest.fixture(scope='session')
def setup():
    program = Program('./resource/Triangle_bug', MnplLevel.PHYSICAL_LINE)
    assert len(program.target_files) == 1
    assert program.target_files[0] == 'Triangle.java'

    patch = Patch(program)
    return patch, program


class TestPatch(object):

    def test_init(self, setup):
        patch, program = setup

        assert patch.program == program
        assert patch.test_result == None
        assert len(patch.edit_list) == 0

    def test_str(self, setup):
        patch, program = setup

        assert ' | '.join(list(map(str, patch.edit_list))) == str(patch)

    def test_len(self, setup):
        patch, program = setup

        assert len(patch.edit_list) == len(patch)

    def test_eq(self, setup):
        patch, program = setup
        program2 = Program('./resource/Triangle_bug', MnplLevel.PHYSICAL_LINE)
        patch2 = Patch(program2)

        assert patch == patch2

    def test_clone(self, setup):
        patch, program = setup
        cloned_patch = patch.clone()

        assert cloned_patch.program == patch.program
        assert cloned_patch == patch
        assert cloned_patch.test_result == None

    def test_add(self, setup):
        patch, program = setup
        deletion_operator = LineDeletion
        deletion_instance = deletion_operator.random(program)
        patch.add(deletion_instance)

        assert len(patch) == 1
        assert patch.edit_list[0] == deletion_instance

        moving_operator = LineMoving
        moving_instance = moving_operator.random(program)
        patch.add(moving_instance)

        assert len(patch) == 2
        assert patch.edit_list[1] == moving_instance

    def test_atomics(self, setup):
        patch, program = setup
        atomics = patch.atomics

        assert 'LineReplacement' in atomics
        assert 'LineInsertion' in atomics

        assert len(atomics['LineReplacement']) == 2
        assert patch.edit_list[0].atomic_operators[0] in atomics[
            'LineReplacement']
        assert patch.edit_list[1].atomic_operators[1] in atomics[
            'LineReplacement']

        assert len(atomics['LineInsertion']) == 1
        assert patch.edit_list[1].atomic_operators[0] in atomics[
            'LineInsertion']

    def test_line_replacements(self, setup):
        patch, program = setup
        lrs = patch.line_replacements
        atomic_lrs = patch.atomics['LineReplacement']

        assert len(lrs) >= 1
        for key, val in lrs.items():
            assert any(key == atomic.line for atomic in atomic_lrs)
            assert any(val == atomic.ingredient for atomic in atomic_lrs)

    def test_line_insertions(self, setup):
        patch, program = setup
        lis = patch.line_insertions
        atomic_lis = patch.atomics['LineInsertion']

        assert len(lis) == 1
        for key, val in lis.items():
            assert key == atomic_lis[0].point
            assert len(val) == 1
            assert val[0] == atomic_lis[0].ingredient

    def test_apply(self, setup):
        patch, program = setup

        assert len(program.contents['Triangle.java']) + patch.edit_size == len(
            patch.apply()['Triangle.java'])

    def test_run_test(self, setup):
        patch, program = setup
        test_result = patch.run_test()

        assert test_result.compiled in [True, False]
        assert test_result.elapsed_time > 0

    def test_remove(self, setup):
        patch, program = setup
        old_patch = patch.clone()
        patch.remove(0)

        assert len(patch) == len(old_patch) - 1
        assert patch.edit_list == old_patch.edit_list[1:]
