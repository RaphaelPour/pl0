#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
import os
from enum import Enum

class PL0Lexer():

    charVector = [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,#/* 0*/
                  7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,#/*10*/
                  7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,#/*20*/
                  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 0, 5, 4, 6, 0,#/*30*/
                  0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,#/*40*/
                  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0,#/*50*/
                  0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,#/*60*/
                  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0]

    def __init__(self):
        print(self.charVector)
        



if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("usage: {} <input file>".format(sys.argv[0]))
        sys.exit(1)

    if not os.path.exists(sys.argv[1]):
        print("File doesn't exist")
        sys.exit(1)

    p = PL0Lexer()

