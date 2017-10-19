import time
import pytest
from triangle import TriangleType, classify_triangle


def check_classification(triangles, expected_result):
    for triangle in triangles:
        assert classify_triangle(*triangle) == expected_result


def test_invalid_triangles():
    triangles = [(1, 2, 9), (1, 9, 2), (2, 1, 9), (2, 9, 1), (9, 1, 2), (
        9, 2, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1), (100, 80, 10000),
                 (100, 10000, 80), (80, 100, 10000), (80, 10000, 100),
                 (10000, 100, 80), (10000, 80, 100), (1, 2, 1), (1, 1,
                                                                 2), (2, 1, 1)]
    check_classification(triangles, TriangleType.INVALID)


def test_equalateral_triangles():
    triangles = [(1, 1, 1), (100, 100, 100), (99, 99, 99)]
    check_classification(triangles, TriangleType.EQUALATERAL)


def test_isoceles_triangles():
    triangles = [(100, 90, 90), (90, 100, 90), (90, 90, 100), (2, 2, 3),
                 (2, 3, 2), (3, 2, 2), (30, 16, 16), (16, 30, 16), (16, 16, 30),
                 (100, 90, 90), (1000, 900, 900), (20, 20, 10), (20, 10, 20), (
                     10, 20, 20), (1, 2, 2), (2, 1, 2), (2, 2, 1111)]

    check_classification(triangles, TriangleType.ISOCELES)


def test_scalene_triangles():
    triangles = [(5, 4, 3), (5, 3, 4), (4, 5, 3), (4, 3, 5), (3, 5, 4), (
        3, 4, 5), (1000, 900, 101), (1000, 101, 900), (900, 1000, 101), (
            900, 101, 1000), (101, 1000, 900), (101, 900, 1000), (3, 20, 21), (
                3, 21, 20), (20, 3, 21), (20, 21, 3), (21, 3, 20), (21, 20, 3),
                 (999, 501, 600), (999, 600, 501), (501, 999, 600), (
                     501, 600, 999), (600, 999, 501), (600, 501, 999),
                 (100, 101, 50), (100, 50, 101), (101, 100, 50), (
                     101, 50, 100), (50, 100, 101), (50, 101, 100), (3, 4, 2), (
                         3, 2, 4), (4, 3, 2), (4, 2, 3), (2, 3, 4), (2, 4, 3)]
    check_classification(triangles, TriangleType.SCALENE)


@pytest.fixture(scope="session", autouse=True)
def starter(request):
    start_time = time.time()

    def finalizer():
        print("elapsed_time: {}".format(str(time.time() - start_time)))

    request.addfinalizer(finalizer)
