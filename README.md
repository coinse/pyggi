# PYGGI(Python General Framework for Genetic Improvement) [![Build Status](https://travis-ci.org/coinse/pyggi.svg?branch=master)](https://travis-ci.org/coinse/pyggi) [![Coverage Status](https://coveralls.io/repos/github/coinse/pyggi/badge.svg?branch=master)](https://coveralls.io/github/coinse/pyggi?branch=master)

<p align="center">
  <img alt="PYGGI logo" src="/images/pyggi_logo.png" />
</p>


PYGGI is the lightweight and simple framework for Genetic Improvement.
It helps one practice or experience GI with only few code lines
by reducing the costs of implementing typical GI process
such as source code manipulation and patch management.


## Prerequisites
* [Python 3.5+](https://www.continuum.io/downloads)


## Documentation
You can find the PYGGI's documentation [here](https://coinse.github.io/pyggi/)


## Getting Started

#### 1. Clone the repository
```bash
$ git clone ~
$ cd PYGGI
```

#### 2. Install
```bash
$ python setup.py install
```

#### 3. Run the example
###### 1. Improving runtime of Triangle by deleting delay() function call
* java

```bash
$ cd example
$ python improve.py ../sample/Triangle_fast
```

* python

```bash
$ cd example
$ python improve_python.py ../sample/Triangle_fast_python
```

###### 2. Repairing the bug of Triangle
```bash
$ cd example
$ python repair.py ../sample/Triangle_bug
```

## Program setup convention

Two files should be provided: a configuration file and a test script.
You can refer the sample programs in the sample directory.

#### 1. Config file
{target_dir_path}/PYGGI_CONFIG

ex) sample/Triangle_fast/PYGGI_CONFIG
```
{
  "target_files": [
    "Triangle.java"
  ],
  "test_command": "./run.sh"
}
```

#### 2. Test script file
{target_dir_path}/run.sh

ex) sample/Triangle_fast/run.sh
```sh
#!/bin/sh
set -e

# cd $1

rm -f *.class
javac -cp "./junit-4.10.jar" Triangle.java TriangleTest.java TestRunner.java
java -cp "./junit-4.10.jar:./" TestRunner TriangleTest
```

The output of the test command should look like this,
```
[PYGGI_RESULT] {runtime: 7, pass_all: true, ...}
```
or, you can use own result parser when generating a `TestResult` instance.

See more details in [here](https://coinse.github.io/pyggi/pyggi.test_result.html).

This is the example of a custom result parser,
```python
def result_parser(stdout, stderr):
    import re
    m = re.findall("runtime: ([0-9.]+)", stdout)
    if len(m) > 0:
        runtime = m[0]
        failed = re.findall("([0-9]+) failed", stdout)
        pass_all = len(failed) == 0
        return TestResult(True, {'runtime': runtime, 'pass_all': pass_all})
    else:
  return TestResult(False, None)
```
, when the standard output is following:
```
======================================== test session starts ========================================
platform linux -- Python 3.6.2, pytest-3.2.3, py-1.4.34, pluggy-0.4.0
rootdir: /media/ssd/Workspace/PYGGI, inifile:
collected 4 items                                                                                    

test_triangle.py ....runtime: 0.22184443473815918


===================================== 4 passed in 0.23 seconds ======================================
```
