import pyggi
import sys

def pyggi_result_parser(raw_result):
    result = {}
    for c in raw_result.split(','):
        if len(c.split(':')) != 2:
            print ("Result format is wrong!: {" + raw_result + "}")
            sys.exit(1)
        k, v = c.split(':')[0].strip(), c.split(':')[1].strip()
        result[k] = v
    return result

class TestResult:
    def __init__(self, compiled, elapsed_time, pyggi_result):
        self.compiled = compiled
        self.elapsed_time = elapsed_time
        self.custom = pyggi_result

    def __str__(self):
        if self.compiled:
            s = "compiled : True\n"
        else:
            s = "compiled : False\n"
        s += "elapsed_time : {}\n".format(self.elapsed_time)
        if self.custom:
            s += "custom\n"
            for k in self.custom:
                s += "- {} : {}\n".format(k, self.custom[k])
        return s.rstrip()


