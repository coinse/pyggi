"""

This module contains meta-heuristic search algorithms.

"""
import time
from abc import ABCMeta, abstractmethod
from .patch import Patch
from .test_result import TestResult

class LocalSearch(metaclass=ABCMeta):
    """
    Local Search (Abstact Class)

    All children classes need to override

    * :py:meth:`get_neighbour`
    * :py:meth:`get_fitness`

    .. hint::
        Example of LocalSearch class. ::

            from pyggi import Program, Patch, GranularityLevel
            from pyggi.algorithms import LocalSearch
            from pyggi.atomic_operator import LineReplacement, LineInsertion
            from pyggi.custom_operator import LineDeletion

            program = Program("<PROGRAM_ROOT_PATH>", GranularityLevel.LINE)

            class MyLocalSearch(LocalSearch):
                def get_neighbour(self, patch):
                    import random
                    if len(patch) > 0 and random.random() < 0.5:
                        patch.remove(random.randrange(0, len(patch)))
                    else:
                        edit_operator = random.choice([LineDeletion, LineInsertion, LineReplacement])
                        patch.add(edit_operator.random(program))
                    return patch

                def get_fitness(self, patch):
                    return float(patch.test_result.custom['runtime'])

                def is_valid_patch(self, patch):
                    return patch.test_result.compiled and patch.test_result.custom['pass_all'] == 'true'

                def stopping_criterion(self, iter, patch):
                    return float(patch.test_result.custom['runtime']) < 100

            local_search = MyLocalSearch(program)
            results = local_search.run(warmup_reps=5, epoch=3, max_iter=100, timeout=15)
    """
    def __init__(self, program):
        """
        :param program: The Program instance to optimize.
        :type program: :py:class:`.Program`
        """
        self.program = program
        self.best_fitness = None

    def is_valid_patch(self, patch):
        """
        :param patch: The Patch instance whose validity should be checked.
        :type patch: :py:class:`.Patch`
        :return: The validity of the patch
        :rtype: bool
        """
        return patch.test_result.compiled

    def is_better_than_the_best(self, fitness, best_fitness):
        """
        :param fitness: The fitness value of the current patch
        :param best_fitness: The best fitness value ever in the current epoch
        :return: If the current fitness are better than the best one, return True.
          False otherwise.
        :rtype: bool
        """
        return fitness <= best_fitness

    def stopping_criterion(self, iter, patch):
        """
        :param int iter: The current iteration number in the epoch
        :param patch: The patch visited in the current iteration
        :type patch: :py:class:`.Patch`
        :return: If the satisfying patch is found or the budget is out of run,
          return True to stop the current epoch. False otherwise.
        :rtype: bool
        """
        return False

    @abstractmethod
    def get_neighbour(self, patch):
        """
        :param patch: The patch that the search is visiting now
        :type patch: :py:class:`.Patch`
        :return: The next(neighbour) patch
        :rtype: :py:class:`.Patch`

        .. hint::
            An example::

                return patch.add(LineDeletion.random(program))
        """
        pass

    @abstractmethod
    def get_fitness(self, patch):
        """
        Define the fitness value of the patch

        If you want to use original one(elapsed_time),
        simply call ``super()``.

        :param patch: The patch instacne
        :type patch: :py:class:`.Patch`
        :return: The fitness value
        """
        return patch.test_result.elapsed_time

    def run(self, warmup_reps=1, epoch=5, max_iter=100, timeout=15,
            result_parser=TestResult.pyggi_result_parser):
        """
        It starts from a randomly generated candidate solution
        and iteratively moves to its neighbouring solution with
        a better fitness value by making small local changes to
        the candidate solution.

        :param int warmup_reps: The number of warming-up test runs to get
          the base fitness value. For some properties, non-functional
          properties in particular, fitness value cannot be fixed. In that
          case, the base fitness value should be acquired by averaging the
          fitness values of original program.
        :param int epoch: The total epoch
        :param int max_iter: The maximum iterations per epoch
        :param float timeout: The time limit of test run (unit: seconds)
        :param result_parser: The parser of test output
          (default: :py:meth:`.TestResult.pyggi_result_parser`)
        :type result_parser: None or callable((str, str), :py:class:`.TestResult`)
        :return: The result of searching(Time, Success, FitnessEval, CompileFailed, BestPatch)
        :rtype: dict(int, dict(str, ))
        """
        self.program.logger.info(self.program.logger.log_file_path)
        warmup = list()
        empty_patch = Patch(self.program)
        for i in range(warmup_reps):
            empty_patch.run_test(timeout=timeout, result_parser=result_parser)
            warmup.append(self.get_fitness(empty_patch))
        original_fitness = float(sum(warmup)) / len(warmup)

        self.program.logger.info(
            "The fitness value of original program: {}".format(original_fitness))

        result = {ep: dict() for ep in range(1, epoch + 1)}

        self.program.logger.info("Epoch\tIter\tFitness\tPatch")
        for cur_epoch in range(1, epoch + 1):
            best_patch = empty_patch
            best_fitness = original_fitness

            # Result Initilization
            result[cur_epoch]['BestPatch'] = None
            result[cur_epoch]['Success'] = False
            result[cur_epoch]['FitnessEval'] = 0
            result[cur_epoch]['CompileFailed'] = 0

            start = time.time()
            for cur_iter in range(1, max_iter + 1):
                patch = self.get_neighbour(best_patch.clone())
                patch.run_test(timeout=timeout, result_parser=result_parser)
                result[cur_epoch]['FitnessEval'] += 1
                if not patch.test_result.compiled:
                    result[cur_epoch]['CompileFailed'] += 1
                if not (patch.test_result.compiled and self.is_valid_patch(patch)):
                    self.program.logger.info("{}\t{}\tnull\t{}".format(cur_epoch, cur_iter, patch))
                    continue
                fitness = self.get_fitness(patch)
                if not self.is_better_than_the_best(fitness, best_fitness):
                    self.program.logger.info("{}\t{}\t{}\t{}".format(cur_epoch, cur_iter, fitness, patch))
                    continue
                self.program.logger.info("{}\t{}\t*{}\t{}".format(cur_epoch, cur_iter, fitness, patch))
                best_fitness, best_patch = fitness, patch
                if self.stopping_criterion(cur_iter, patch):
                    result[cur_epoch]['Success'] = True
                    break
            result[cur_epoch]['Time'] = time.time() - start
            if best_patch:
                result[cur_epoch]['BestPatch'] = best_patch
                result[cur_epoch]['BestFitness'] = best_fitness
        return result
