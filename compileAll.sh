#!/bin/bash

for file in examples/*.pl0
do
  echo "Compiling ${file}"
  python3 ./cpl0.py ${file}
done