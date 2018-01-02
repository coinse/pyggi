# PYGGI(Python General Framework for Genetic Improvement)

PYGGI is the lightweight and simple framework for Genetic Improvement.
It helps one practice or experience GI with only few code lines
by lightneing the costs of implementing typical GI process
such as source code manipulation and patch management.

&nbsp;

## Prerequisites
* [Python 3.5+](https://www.continuum.io/downloads)

&nbsp;

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
An example of improving runtime of Triangle by deleting delay() function call.
```bash
$ cd example
$ python improve.py ../sample/Triangle_fast
```

## New program setup

#### 1. Config file
{target_dir_path}/PYGGI_CONFIG
```
{
  "target_files": [
    "Triangle.java"
  ],
  "test_script": "run.sh"
}
```

#### 2. Test script file
{target_dir_path}/run.sh
```sh
#!/bin/sh
set -e

# cd $1

rm -f *.class
javac -cp "./junit-4.10.jar" Triangle.java TriangleTest.java TestRunner.java
java -cp "./junit-4.10.jar:./" TestRunner TriangleTest
```
