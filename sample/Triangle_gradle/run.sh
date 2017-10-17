#!/bin/sh
set -e

cd $1
gradle clean

if time gradle build; then
  echo "Gradle build succeeded" >&2
else
  echo "Gradle build failed" >&2
  exit 1
fi

gradle test
