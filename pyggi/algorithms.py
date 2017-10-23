from .patch import Patch
from .program import Program
from .test_result import TestResult
from .edit import EditType

def local_search(program,
                 warmup_reps=10,
                 total_try=5,
                 iterations=100,
                 get_neighbours=lambda p: p.add_random_edit(),
                 validity_check=lambda p: p.test_result.compiled,
                 get_fitness=lambda p: p.test_result.elapsed_time,
                 compare_fitness=lambda a, b: a <= b):
    base_fitnesses = list()
    empty_patch = Patch(program)
    for i in range(warmup_reps):
        empty_patch.run_test()
        base_fitnesses.append(get_fitness(empty_patch))
    base_fitness = float(sum(base_fitnesses)) / len(base_fitnesses)
    program.logger.info("The fitness value of original program: {}".format(base_fitness))
    cfc = 0  # Compilation failure count
    best_patches = list()
    for t in range(1, total_try + 1):
        program.logger.debug("===========TRY #{}==========".format(t))
        best_patch = empty_patch
        best_fitness = base_fitness
        for i in range(1, iterations + 1):
            patch = get_neighbours(best_patch.clone())
            patch.run_test()
            program.logger.debug("Iter #{}".format(i))
            program.logger.debug("\tPatch: {}".format(patch))
            if not patch.test_result.compiled:
                cfc += 1
            if not (patch.test_result.compiled and validity_check(patch)):
                continue
            fitness = get_fitness(patch)
            program.logger.debug("\tFitness: {}".format(fitness))
            if not compare_fitness(fitness, best_fitness):
                continue
            best_fitness, best_patch = fitness, patch
            program.logger.debug("\t* New Best *")
        if len(best_patch) > 0:
            program.logger.info("TRY #{}'s BEST".format(t))
            program.logger.info(best_patch)
            best_patches.append(best_patch)
    cfr = float(cfc) / (total_try * iterations) * 100
    return cfr, best_patches
