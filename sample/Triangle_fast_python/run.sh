#!/bin/sh
set +e

pytest -s test_triangle.py > result.out
python parse_result.py
