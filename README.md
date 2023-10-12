# PYGGI(Python General Framework for Genetic Improvement)

[![Build Status](https://travis-ci.org/coinse/pyggi.svg?branch=master)](https://travis-ci.org/coinse/pyggi) [![Coverage Status](https://coveralls.io/repos/github/coinse/pyggi/badge.svg?branch=master)](https://coveralls.io/github/coinse/pyggi?branch=master)

<p align="center">
  <img alt="PYGGI logo" src="/images/pyggi_logo.png" />
</p>


PYGGI is the lightweight and simple framework for Genetic Improvement.
It helps one practice or experience GI with only few code lines
by reducing the costs of implementing typical GI process
such as source code manipulation and patch management.


## Prerequisites
* [Python 3.5+](https://www.continuum.io/downloads)
* [srcML](https://www.srcml.org/#download) (optional if you want to use the XML engine on srcML translated files. [example](https://github.com/coinse/pyggi/blob/master/example/repair_java.py))

## Documentation
You can find the PYGGI's documentation [here](https://coinse.github.io/pyggi/).
(Currently outdated, will be updated soon!)

## Citation

```
@inproceedings{An:2019:PLI:3338906.3341184,
 author = {An, Gabin and Blot, Aymeric and Petke, Justyna and Yoo, Shin},
 title = {PyGGI 2.0: Language Independent Genetic Improvement Framework},
 booktitle = {Proceedings of the 2019 27th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering},
 series = {ESEC/FSE 2019},
 year = {2019},
 isbn = {978-1-4503-5572-8},
 location = {Tallinn, Estonia},
 pages = {1100--1104},
 numpages = {5},
 url = {http://doi.acm.org/10.1145/3338906.3341184},
 doi = {10.1145/3338906.3341184},
 acmid = {3341184},
 publisher = {ACM},
 address = {New York, NY, USA},
 keywords = {Genetic Improvement, Search-based Software Engineering},
}
```

The pdf file is available at [link](https://dl.acm.org/citation.cfm?id=3341184).

## Getting Started

#### 1. Clone the repository
```bash
$ git clone https://github.com/coinse/pyggi
$ cd PYGGI
```

#### 2. Install
```bash
$ python setup.py install
```

#### 3. Run the example
##### 1. Improving runtime of Triangle by deleting delay() function call
* java

```bash
$ cd example
$ python improve_java.py --project_path ../sample/Triangle_fast_java --mode [line|tree] --epoch [EPOCH] --iter [MAX_ITER]
```

* python

```bash
$ cd example
$ python improve_python.py --project_path ../sample/Triangle_fast_python/ --mode [line|tree] --epoch [EPOCH] --iter [MAX_ITER]
```

##### 2. Repairing the bug of Triangle
* java

```bash
$ cd example
$ python repair_java.py --project_path ../sample/Triangle_bug_java --mode [line|tree] --epoch [EPOCH] --iter [MAX_ITER]
```

* python

```bash
$ cd example
$ python repair_python.py --project_path ../sample/Triangle_bug_python/ --mode [line|tree] --epoch [EPOCH] --iter [MAX_ITER]
```

##### Important notes about using `tree` mode for Java, C++, or C programs
For the Java samples (`Triangle_fast_java`, `Triangle_bug_java`), we provide the `XML` version of `Triangle.java` files translated by [srcML (download)](https://www.srcml.org/#download).
However, in the general case, you should translate the target `Java`, `C++`, or `C` files into `XML` files before initialising Program instances and provide the translated those `XML` files as target files.

Or, you can simply override the `setup` method of `AbstractProgram`, which is initially empty, to execute the translation command.

ex) Translating `Triangle.java` to `Triangle.java.xml` using srcML (See the context at `example/improve_java.py`)
```
class MyTreeProgram(TreeProgram):
    def setup(self):
        if not os.path.exists(os.path.join(self.tmp_path, "Triangle.java.xml")):
            self.exec_cmd("srcml Triangle.java -o Triangle.java.xml")
```

Then, PyGGI will manipulate the XML files using `XmlEngine`(in `pyggi/tree/xml_engine.py`) and convert it back to the original language by stripping all the XML tags before running the test command.

## Program setup convention

To run PyGGI, these files should be provided in the target directory:
 1. A **Configuration File** (`.pyggi.config`) containing the information about the path to the target files that you want to _improve_, and the test command that can be used to calculate the fitness values of program variants during the GI process.
 2. A **Test Script** 

#### 1. Config file (JSON format)

ex) [`sample/Triangle_fast_java/.pyggi.config`](sample/Triangle_fast_java/.pyggi.config)
```json
{
  "target_files": [
    "Triangle.java"
  ],
  "test_command": "./run.sh"
}
```

You can also specify the config file name in Python script if you want it be different from the default value `.pyggi.config`,

ex)
```python
program = LineProgram(
    "sample/Triangle_fast_java",   # directory containing the program  
    config='.custom.pyggi.config') # config file name
```

or directly provide the `dict` type configuration when initialising Program.
ex)

```python
config = {
    "target_files": ["Triangle.java"],
    "test_command": "./run.sh"
}
program = LineProgram(
    "sample/Triangle_fast_java",
    config=config # config
)
```

#### 2. Test script file
`{target_dir_path}/run.sh`

ex) [`sample/Triangle_fast_java/run.sh`](./sample/Triangle_fast_java/run.sh)
```sh
#!/bin/sh
set -e

# cd $1

rm -f *.class
javac -cp "./junit-4.10.jar" Triangle.java TriangleTest.java TestRunner.java
java -cp "./junit-4.10.jar:./" TestRunner TriangleTest
```

The output of the test command should be the fitness of the program (only number),
```
7.0
```
or, you can use own result parser by overriding the `compute_fitness` method of Program classes.

This is the example of a custom result parser from `example/improve_python.py`,
```python
class MyProgram(AbstractProgram):
    def compute_fitness(self, elapsed_time, stdout, stderr):
        import re
        m = re.findall("runtime: ([0-9.]+)", stdout)
        if len(m) > 0:
            runtime = m[0]
            failed = re.findall("([0-9]+) failed", stdout)
            pass_all = len(failed) == 0
            if pass_all:
                return round(float(runtime), 3)
            else:
                raise ParseError
        else:
            raise ParseError

class MyLineProgram(LineProgram, MyProgram):
    pass

class MyTreeProgram(TreeProgram, MyProgram):
    pass
```
which can parse the output from `pytest`, such as:
```
======================================== test session starts ========================================
platform linux -- Python 3.6.2, pytest-3.2.3, py-1.4.34, pluggy-0.4.0
rootdir: /media/ssd/Workspace/PYGGI, inifile:
collected 4 items                                                                                    

test_triangle.py ....runtime: 0.22184443473815918


===================================== 4 passed in 0.23 seconds ======================================
```
