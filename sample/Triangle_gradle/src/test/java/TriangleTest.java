import static org.junit.Assert.*;

public class TriangleTest {

    private void checkClassification(int[][] triangles, Triangle.TriangleType expectedResult) {
        for (int[] triangle: triangles) {
            Triangle.TriangleType triangleType = Triangle.classifyTriangle(triangle[0], triangle[1], triangle[2]);
            assertEquals(expectedResult, triangleType);
        }
    }

    @org.junit.Test
    public void testInvalidTriangles() throws Exception {
        int[][] invalidTriangles = {
          {1, 2, 9}, {1, 9, 2}, {2, 1, 9}, {2, 9, 1}, {9, 1, 2}, {9, 2, 1},
          {1, 1, -1}, {1, -1, 1}, {-1, 1, 1},
          {100, 80, 10000}, {100, 10000, 80}, {80, 100, 10000}, {80, 10000, 100}, {10000, 100, 80}, {10000, 80, 100},
          {1, 2, 1}, {1, 1, 2}, {2, 1, 1}
        };
        checkClassification(invalidTriangles, Triangle.TriangleType.INVALID);
    }

    @org.junit.Test
    public void testEqualateralTriangles() throws Exception {
        int[][] equalateralTriangles = {{1, 1, 1}, {100, 100, 100}, {99, 99, 99}};
        checkClassification(equalateralTriangles, Triangle.TriangleType.EQUALATERAL);
    }

    @org.junit.Test
    public void testIsocelesTriangles() throws Exception {
        int[][] isocelesTriangles = {
          {100, 90, 90}, {90, 100, 90}, {90, 90, 100},
          {2, 2, 3}, {2, 3, 2}, {3, 2, 2},
          {30, 16, 16}, {16, 30, 16}, {16, 16, 30},
          {100, 90, 90}, {1000, 900, 900},
          {20, 20, 10}, {20, 10, 20}, {10, 20, 20},
          {1, 2, 2}, {2, 1, 2}, {2, 2, 1}
        };
        checkClassification(isocelesTriangles, Triangle.TriangleType.ISOCELES);
    }

    @org.junit.Test
    public void testScaleneTriangles() throws Exception {
        int[][] scaleneTriangles = {
          {5, 4, 3}, {5, 3, 4}, {4, 5, 3}, {4, 3, 5}, {3, 5, 4}, {3, 4, 5},
          {1000, 900, 101}, {1000, 101, 900}, {900, 1000, 101}, {900, 101, 1000}, {101, 1000, 900}, {101, 900, 1000},
          {3, 20, 21}, {3, 21, 20}, {20, 3, 21}, {20, 21, 3}, {21, 3, 20}, {21, 20, 3},
          {999, 501, 600}, {999, 600, 501}, {501, 999, 600}, {501, 600, 999}, {600, 999, 501}, {600, 501, 999},
          {100, 101, 50}, {100, 50, 101}, {101, 100, 50}, {101, 50, 100}, {50, 100, 101}, {50, 101, 100},
          {3, 4, 2}, {3, 2, 4}, {4, 3, 2}, {4, 2, 3}, {2, 3, 4}, {2, 4, 3}
        };
        checkClassification(scaleneTriangles, Triangle.TriangleType.SCALENE);
    }

}
