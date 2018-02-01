import shlex, subprocess, math

MEASURE = "coverage run triangle.py {} {} {}"
REPORT = "coverage report -m"
NUM_LINES = 35

triangles = [
    (1, 2, 9), (1, 9, 2), (2, 1, 9), (2, 9, 1), (9, 1, 2),
    (9, 2, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1),
    (1, 1, 1), (100, 100, 100), (99, 99, 99),
    (100, 90, 90), (90, 100, 90), (90, 90, 100), (2, 2, 3),
    (5, 4, 3), (5, 3, 4), (4, 5, 3), (4, 3, 5), (3, 5, 4)
]
failing = [(2,9,1), (5,4,3), (9,2,1), (4,5,3)]

missing_lines = dict()
for triangle in triangles:
    args = shlex.split(MEASURE.format(*triangle))
    print(args)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = proc.communicate(timeout=15)
    except TimeoutExpired:
        proc.kill()
        continue
    proc = subprocess.Popen(shlex.split(REPORT), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = proc.communicate(timeout=15)
    except TimeoutExpired:
        proc.kill()
        continue
    results = stdout.decode("ascii")
    for line in results.split('\n'):
        if line.strip().startswith("triangle.py"):
            missing_lines[triangle] = list()
            for rng in line.split()[4:]:
                rng = rng.split(',')[0]
                if len(rng.split('-')) == 2:
                    start = int(rng.split('-')[0])
                    end = int(rng.split('-')[1])
                    for i in range(start, end+1):
                        missing_lines[triangle].append(i)
                else:
                    missing_lines[triangle].append(int(rng))
spectrum = {}
for l in range(1, NUM_LINES+1):
    spectrum[l] = { 'e_f':0, 'n_f':0, 'e_p':0, 'n_p':0 }

for triangle in triangles:
    if triangle in failing:
        # Failing test
        for line in range(1, NUM_LINES+1):
            if line in missing_lines[triangle]:
                spectrum[line]['n_f'] += 1
            else:
                spectrum[line]['e_f'] += 1
    else:
        # Passing test
        for line in range(1, NUM_LINES+1):
            if line in missing_lines[triangle]:
                spectrum[line]['n_p'] += 1
            else:
                spectrum[line]['e_p'] += 1

print("line #\te_f\tn_f\te_p\tn_p\tsusp")
for line in spectrum:
    spectra = spectrum[line]
    susp = float(spectra['e_f']) / math.sqrt((spectra['e_f'] + spectra['n_f']) * (spectra['e_f'] + spectra['e_p']))
    print("{}\t{}\t{}\t{}\t{}\t{}".format(
        line,
        spectra['e_f'],
        spectra['n_f'],
        spectra['e_p'],
        spectra['n_p'],
        susp
    ))
