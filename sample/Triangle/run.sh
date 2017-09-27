#!/bin/sh
set -e

cd tmp
gradle clean

if gradle build; then
  echo "Gradle build succeeded" >&2
else
  echo "Gradle build failed" >&2
  exit 1
fi

gradle test
