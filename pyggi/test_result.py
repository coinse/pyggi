import pyggi


class TestResult:

    def __init__(self, compiled, execution_time, execution_result):
        self.compiled = compiled
        self.real_time = float(execution_time[0])
        self.user_time = float(execution_time[1])
        self.sys_time = float(execution_time[2])
        self.passed = int(execution_result[1])
        self.failed = int(execution_result[2])
        self.skipped = int(execution_result[3])
