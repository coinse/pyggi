public class Triangle {

    public enum TriangleType {
        INVALID, SCALENE, EQUALATERAL, ISOCELES
    }

    public static TriangleType classifyTriangle(int a, int b, int c) {
        if (a > b) {
            int tmp = a;
            a = b;
            b = tmp;
        }

        if (a > c) {
            int tmp = b; // original: int tmp = a;
            a = c;
            c = tmp;
        }

        if (b > c) {
            int tmp = b;
            b = c;
            c = tmp;
        }

        if (a + b <= c) {
            return TriangleType.INVALID;
        } else if (a == b && b == c) {
            return TriangleType.EQUALATERAL;
        } else if (a == b || b == c) {
            return TriangleType.ISOCELES;
        } else {
            return TriangleType.SCALENE;
        }

    }

    public static void main(String[] args) {
      System.out.println("INV");
      System.out.println(classifyTriangle(1,2,9));
      System.out.println(classifyTriangle(-1,1,1));
      System.out.println(classifyTriangle(1,-1,1));
      System.out.println(classifyTriangle(1,1,-1));
      System.out.println(classifyTriangle(100,80,10000));
      System.out.println("EQU");
      System.out.println(classifyTriangle(1,1,1));
      System.out.println(classifyTriangle(100,100,100));
      System.out.println(classifyTriangle(99,99,99));
      System.out.println("ISO");
      System.out.println(classifyTriangle(100,90,90));
      System.out.println(classifyTriangle(1000,900,900));
      System.out.println(classifyTriangle(3,2,2));
      System.out.println(classifyTriangle(30,16,16));
      System.out.println("SCA");
      System.out.println(classifyTriangle(5,4,3));
      System.out.println(classifyTriangle(1000,900,101));
      System.out.println(classifyTriangle(3,20,21));
      System.out.println(classifyTriangle(999,501,600));
    }
}
