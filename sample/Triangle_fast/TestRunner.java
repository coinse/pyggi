import org.junit.runner.JUnitCore;
import org.junit.runner.Result;
import org.junit.runner.notification.Failure;

public class TestRunner {
   public static void main(String[] args) throws ClassNotFoundException {
      Class klass = Class.forName(args[0]);
      Result result = JUnitCore.runClasses(klass);

      //System.out.println(result.getFailureCount());
      /* for (Failure failure : result.getFailures()) {
         System.out.println(failure.toString());
      } */

      //System.out.println(result.getIgnoreCount());
      //System.out.println(result.getRunCount());
      //System.out.println(result.getRunTime());
      //System.out.println(result.wasSuccessful());
      System.out.println("[PYGGI_RESULT] {" +
        "runtime: " + result.getRunTime() + "," +
        "pass_all: " + result.wasSuccessful() + "}"
      );
   }
}
