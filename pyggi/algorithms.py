"""

This module contains search algorithms.

"""
import time
from .patch import Patch

def local_search(program,
                 warmup_reps=10,
                 total_run=5,
                 iterations=100,
                 get_neighbours=lambda p: p.add_random_edit(),
                 validity_check=lambda p: p.test_result.compiled,
                 get_fitness=lambda p: p.test_result.elapsed_time,
                 compare_fitness=lambda a, b: a <= b,
                 stop=lambda i, p: False,
                 timeout=15):
    """
    It starts from a randomly generated candidate solution
    and iteratively moves to its neighbouring solution with
    a better fitness value by making small local changes to
    the candidate solution.
    """
    base_fitnesses = list()
    empty_patch = Patch(program)
    for i in range(warmup_reps):
        empty_patch.run_test()
        base_fitnesses.append(get_fitness(empty_patch))
    base_fitness = float(sum(base_fitnesses)) / len(base_fitnesses)
    program.logger.info(
        "The fitness value of original program: {}".format(base_fitness))
    cfc = 0  # Compilation failure count
    tic = 0  # Total iteration count
    best_patches = list()
    for run in range(1, total_run + 1):
        program.logger.info("===========TRY #{}==========".format(run))
        best_patch = empty_patch
        best_fitness = base_fitness
        start = time.time()
        for i in range(1, iterations + 1):
            tic += 1
            patch = get_neighbours(best_patch.clone())
            patch.run_test(timeout)
            program.logger.info("Iter #{}".format(i))
            program.logger.info("\tPatch: {}".format(patch))
            if not patch.test_result.compiled:
                cfc += 1
            if not (patch.test_result.compiled and validity_check(patch)):
                continue
            fitness = get_fitness(patch)
            program.logger.info("\tFitness: {}".format(fitness))
            if not compare_fitness(fitness, best_fitness):
                continue
            best_fitness, best_patch = fitness, patch
            program.logger.info("\t* New Best *")
            if stop(i, patch):
                program.logger.info("- NPS: {}".format(i - 1))
                break
        program.logger.info("- Duration Time: {}".format(time.time() - start))
        if best_patch:
            program.logger.info("- TRY #{}'s BEST patch: ".format(run))
            program.logger.info(best_patch)
            best_patches.append(best_patch)
    cfr = float(cfc) / tic * 100
    return cfr, best_patches
