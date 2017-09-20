import pyggi

class TestResult:
    def __init__(self, compiled, execution_time, t_c, t_p, t_f):
        self.compiled = compiled
        self.execution_time = execution_time
        self.t_c = t_c
        self.t_p = t_p
        self.t_f = t_f
