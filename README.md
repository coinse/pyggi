### PYGGI

#### Usage

./run.py
```python
# Program instance
program = Program(project_path, 'physical_line')

# Patch instance
patch = Patch(program)

# Run test from Patch
patch.run_test()

...
```

{target_dir_path}/PYGGI_CONFIG
```
{
  "target_files": [
    "Triangle.java"
  ],
  "test_script": "run.sh"
}
```

{target_dir_path}/run.sh
```sh
#!/bin/sh
set -e

# cd $1

rm -f *.class
javac -cp "./junit-4.10.jar" Triangle.java TriangleTest.java TestRunner.java
java -cp "./junit-4.10.jar:./" TestRunner TriangleTest
```

Run pyggi
```
python run.py [target_dir_path]
```

#### Example
An example of improving runtime of Triangle by deleting delay() function call.
```
python improve.py ./sample/Triangle_fast
```
