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
                 compare_fitness=lambda a, b: a <= b,
                 print_log=False):
    def logging(msg):
        if print_log:
            print(msg)
    base_fitnesses = list()
    empty_patch = Patch(program)
    for i in range(warmup_reps):
        empty_patch.run_test()
        base_fitnesses.append(get_fitness(empty_patch))
    base_fitness = float(sum(base_fitnesses)) / len(base_fitnesses)

    cfc = 0  # Compilation failure count
    best_patches = list()
    for t in range(1, total_try + 1):
        logging("===========TRY #{}==========".format(t))
        best_patch = empty_patch
        best_fitness = base_fitness
        for i in range(1, iterations + 1):
            patch = get_neighbours(best_patch.clone())
            patch.run_test()
            if not patch.test_result.compiled:
                cfc += 1
            if not validity_check(patch):
                logging("Iter #{}\n\tPatch: {}".format(i, patch))
                continue
            fitness = get_fitness(patch)
            logging("Iter #{}\n\tPatch: {}\n\tFitness: {}".format(i, patch, fitness))
            if not compare_fitness(fitness, best_fitness):
                continue
            best_fitness, best_patch = fitness, patch
            logging("\t* New Best *")
        logging("\nTRY #{}'s BEST".format(t))
        logging(best_patch)
        best_patches.append(best_patch)
    cfr = float(cfc) / (total_try * iterations) * 100
    return cfr, best_patches
