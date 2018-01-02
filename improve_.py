import sys
import random
from pyggi import Program, Patch, MnplLevel, local_search
from pyggi.atomic_operator import LineReplacement, LineInsertion
from pyggi.edit import LineDeletion

program = Program('sample/Triangle_fast', MnplLevel.PHYSICAL_LINE)

def get_neighbours(patch):
    if len(patch) > 0 and random.random() < 0.5:
        patch.remove(random.randrange(0, len(patch)))
    else:
        edit_operator = random.choice([LineDeletion, LineInsertion, LineReplacement])
        patch.add_edit(edit_operator.random(program))
    return patch

def validity_check(patch):
    return patch.test_result.compiled and patch.test_result.custom['pass_all'] == 'true'

def get_fitness(patch):
    return float(patch.test_result.custom['runtime'])

def stop(i, patch):
    return float(patch.test_result.custom['runtime']) < 100

cfr, patches = local_search(program,
    total_run=30,
    iterations=1000,
    get_neighbours=get_neighbours,
    validity_check=validity_check,
    get_fitness=get_fitness,
    compare_fitness=lambda(c,b): c <= b,
    stop=stop,
    timeout=10)

patches = sorted(patches, key=lambda patch: (get_fitness(patch), len(patch)))
program.logger.info(best_patch)
program.logger.info("CFR: {}%".format(cfr))
