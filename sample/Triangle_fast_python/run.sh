#!/bin/sh
set +e

rm -f *.pyc
rm -rf __pycache__

pytest -s test_triangle.py > result.out
python parse_result.py
