from enum import Enum


class TriangleType(Enum):
    INVALID = 0
    EQUALATERAL = 1
    ISOCELES = 2
    SCALENE = 3


def classify_triangle(a, b, c):
    if a > b:
        tmp = a
        a = b
        b = tmp

    if a > c:
        tmp = a
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


if __name__ == "__main__":
    print(classify_triangle(1, 1, 1))
