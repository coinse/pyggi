import pyggi


class TestResult:

    def __init__(self, compiled, execution_time, passed, failed, skipped):
        self.compiled = compiled
        self.execution_time = execution_time
        self.passed = passed
        self.failed = failed
        self.skipped = skipped
