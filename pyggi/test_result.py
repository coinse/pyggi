"""

This module contains TestResult class.

"""
import sys
import copy

class TestResult:
    """

    TestResult stores the result of the test suite executions
    on the original or patched source code. It records whether
    compilation succeeded, the elapsed execution time,
    as well as any other user-defined test results.

    """
    def __init__(self, compiled, elapsed_time, pyggi_result):
        self.compiled = compiled
        self.elapsed_time = elapsed_time
        self.custom = pyggi_result

    def __copy__(self):
        return TestResult(self.compiled, self.elapsed_time,
                          copy.deepcopy(self.custom))

    def __str__(self):
        if self.compiled:
            result = "compiled : True\n"
        else:
            result = "compiled : False\n"
        result += "elapsed_time : {}\n".format(self.elapsed_time)
        if self.custom:
            result += "custom\n"
            for key in self.custom:
                result += "- {} : {}\n".format(key, self.custom[key])
        return result.rstrip()

    def get(self, name: str):
        """
        Args:
            name (str): a name of the custom result

        Returns:
            a value of the custom result
        """
        return self.custom[name]

    @staticmethod
    def pyggi_result_parser(output: str):
        """
        The test script should print output in the predefined,
        PYGGI-recognisable format. This method parses the results.

        Args:
            output (str): an output of the test script

        Returns:
            bool: True if the PYGGI output detected, otherwise False.
            dict:
                key: a name of custom result
                value: a value of custom result

        Examples:
            when output is
            `[PYGGI_RESULT] {runtime: 7,pass_all: true}`,
            returns (True, {'runtime': 7, 'pass_all': 'true'})
        """
        import re
        matched = re.findall("\[PYGGI_RESULT\]\s*\{(.*?)\}\s", output)
        compiled = len(matched) != 0
        custom = None
        if compiled:
            custom = dict()
            for result in matched[0].split(','):
                if len(result.split(':')) != 2:
                    print("[Error] Result format is wrong!: {" + matched[0] + "}")
                    sys.exit(1)
                key, value = result.split(':')[0].strip(), result.split(':')[1].strip()
                custom[key] = value
        return (compiled, custom)
