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
        int[][] invalidTriangles = {{1, 2, 9}, {-1, 1, 1}, {1, -1, 1}, {1, 1, -1}, {100, 80, 10000}, {2, 3, 1}, {1, 2, 1}};
        checkClassification(invalidTriangles, Triangle.TriangleType.INVALID);
    }

    @org.junit.Test
    public void testEqualateralTriangles() throws Exception {
        int[][] equalateralTriangles = {{1, 1, 1}, {100, 100, 100}, {99, 99, 99}};
        checkClassification(equalateralTriangles, Triangle.TriangleType.EQUALATERAL);
    }

    @org.junit.Test
    public void testIsocelesTriangles() throws Exception {
        int[][] isocelesTriangles = {{100, 90, 90}, {1000, 900, 900}, {2, 2, 3}, {30, 16, 16}, {16, 16, 28}, {20, 20, 10}, {2, 3, 2}, {1, 2, 2}};
        checkClassification(isocelesTriangles, Triangle.TriangleType.ISOCELES);
    }

    @org.junit.Test
    public void testScaleneTriangles() throws Exception {
        int[][] scaleneTriangles = {{5, 4, 3}, {1000, 900, 101}, {3,20,21}, {999, 501, 600}, {100, 101, 50}, {3, 4, 2}};
        checkClassification(scaleneTriangles, Triangle.TriangleType.SCALENE);
    }

}
