import time
from enum import Enum

class TriangleType(Enum):
    INVALID, EQUALATERAL, ISOCELES, SCALENE = 0, 1, 2, 3

def classify_triangle(a, b, c):
    # Sort the sides so that a <= b <= c
    if a > b:
        tmp = a
        a = b
        b = tmp

    if a > c:
        tmp = b
        a = c
        c = tmp

    if b > c:
        tmp = b
        b = c
        c = tmp

    if a + b <= c:
        return TriangleType.INVALID
    elif a == b and b == c:
        return TriangleType.EQUALATERAL
    elif a == b or b == c:
        return TriangleType.ISOCELES
    else:
        return TriangleType.SCALENE

if __name__ == "__main__": # pragma: no cover
    import sys
    classify_triangle(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
