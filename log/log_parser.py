import sys

with open(sys.argv[1], 'r') as f:
    tsv_file = open(sys.argv[1] + '.tsv', 'w')
    for line in f.readlines():
        if "NPS" in line:
            tsv_file.write(line.split()[-1] + '\t')
        if "Duration" in line:
            tsv_file.write(line.split()[-1] + '\n')
