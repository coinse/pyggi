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
    def __init__(self, compiled, execution_time, pyggi_result):
        self.compiled = compiled
        self.real_time = execution_time['real']
        self.user_time = execution_time['user']
        self.sys_time = execution_time['sys']
        self.custom = pyggi_result

    def __str__(self):
        if self.compiled:
            s = "compiled : True\n"
        else:
            s = "compiled : False\n"
        s += "execution_time\n"
        s += "- real_time : {}\n".format(self.real_time)
        s += "- user_time : {}\n".format(self.user_time)
        s += "- sys_time : {}\n".format(self.sys_time)
        if self.custom:
            s += "custom\n"
            for k in self.custom:
                s += "- {} : {}\n".format(k, self.custom[k])
        return s.rstrip()


