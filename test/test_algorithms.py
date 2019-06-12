import pytest
import random
from pyggi.base import Algorithm, Patch
from pyggi.tree import TreeProgram, StmtReplacement, StmtInsertion, StmtDeletion, StmtMoving
from pyggi.algorithms import LocalSearch

@pytest.fixture(scope='session')
def setup_program():
    class MyProgram(TreeProgram):
        def compute_fitness(self, result, return_code, stdout, stderr, elapsed_time):
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
    program = MyProgram('../sample/Triangle_bug_python')
    return program

class TestAlgorithm(object):

    def test_fails_without_override(self, setup_program):
        with pytest.raises(Exception) as e_info:
            program = setup_program
            algorithm = Algorithm(program)

    def test_init_and_setup(self, setup_program):

        class MyAlgorithm(Algorithm):
            def setup(self):
                self.name = "myalgo"

            def run(self):
                return True

        program = setup_program
        my_algo = MyAlgorithm(program)
        assert my_algo.name == "myalgo"


class TestLocalSearch(object):

    def test_fails_without_override(self, setup_program):
        with pytest.raises(Exception) as e_info:
            program = setup_program
            algorithm = LocalSearch(program)

    def test_init(self, setup_program):
        class MyLocalSearch(LocalSearch):
            def get_neighbour(self, patch):
                temp_patch = patch.clone()
                if len(temp_patch) > 0 and random.random() < 0.1:
                    temp_patch.remove(random.randrange(0, len(temp_patch)))
                else:
                    operators = [StmtReplacement, StmtInsertion, StmtDeletion, StmtMoving]
                    temp_patch.add(random.choice(operators).create(program, method="weighted"))
                return temp_patch

            def is_better_than_the_best(self, fitness, best_fitness):
                return fitness < best_fitness

            def stopping_criterion(self, iter, fitness):
                return fitness == 0

        max_iter = 10
        program = setup_program
        run = program.evaluate_patch(Patch(program))
        ls = MyLocalSearch(program)
        result = ls.run(warmup_reps=1, epoch=1, max_iter=max_iter, timeout=10)
        assert len(result) == 1
        assert result[0]['FitnessEval'] <= max_iter
        if result[0]['FitnessEval'] < max_iter:
            assert result[0]['BestFitness'] < run.fitness
