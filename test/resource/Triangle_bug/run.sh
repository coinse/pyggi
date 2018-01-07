#!/bin/sh
set -e

# cd $1

rm -f *.class
javac -cp "./junit-4.10.jar" Triangle.java TriangleTest.java TestRunner.java 
java -cp "./junit-4.10.jar:./" TestRunner TriangleTest
