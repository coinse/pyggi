import re


def main():
    result = ""
    with open("./result.out", "r") as f:
        for line in f:
            result += line

    m = re.findall("elapsed_time: ([0-9.]+)", result)
    assert len(m) > 0
    elapsed_time = m[0]

    failed = re.findall("([0-9]+) failed", result)
    if len(failed) == 0:
        passed = "true"
    else:
        passed = "false"

    print("[PYGGI_RESULT] {{runtime: {}, pass_all: {}}} ".format(
        elapsed_time, passed))


if __name__ == "__main__":
    main()
