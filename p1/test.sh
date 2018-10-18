#!/bin/bash

echo 1+2 = 3
./exlex 1+2

echo 1+2*3 = 7
./exlex 1+2*3

echo 1+2+3 = 6
./exlex 1+2+3

echo 1*2*3 = 6
./exlex 1*2*3

echo 1+2+3*4 = 15
./exlex 1+2+3*4

echo 1+2+3*4*5 = 63
./exlex 1+2+3*4*5
