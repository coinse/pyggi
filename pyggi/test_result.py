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
    def __init__(self, compiled, pyggi_result, elapsed_time=None):
        self.compiled = compiled
        self.custom = pyggi_result
        self.elapsed_time = elapsed_time

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
        :param str name: The a name of the custom result
        :return: The value of the custom result
        :rtype: str
        """
        assert name in self.custom
        return self.custom[name]

    @classmethod
    def pyggi_result_parser(cls, output: str):
        """
        The test script should print output in the predefined,
        PYGGI-recognisable format. This method parses the results.

        :param str output: The output of the test script

        :return: The TestResult instance. If the PYGGI output are
          not detected, it is regarded as compile(execution) failure.
        :rtype: :py:class:`.TestResult`

        .. note::
            When the output is

                [PYGGI_RESULT] {runtime: 7,pass_all: true}

            , returns ``TestResult(True, {'runtime': 7, 'pass_all': 'true'})``
        """
        import re
        matched = re.findall("\[PYGGI_RESULT\]\s*\{(.*?)\}\s", output)
        compiled = len(matched) != 0
        custom = None
        if compiled:
            custom = dict()
            for result in matched[0].split(','):
                assert len(result.split(':')) == 2
                # print("[Error] Result format is wrong!: {" + matched[0] + "}")
                key, value = result.split(':')[0].strip(), result.split(':')[1].strip()
                custom[key] = value
        return cls(compiled, custom)
