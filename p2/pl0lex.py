#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
import os
from enum import Enum

class MorphemCode(Enum):
    EMPTY = 1
    NUMBER = 2
    SYMBOL = 4
    IDENT = 5

class MorphemSymbols(Enum):
    NULL = 0
    EQUAL = 128
    LESSER_EQUAL = 129
    GREATER_EQUAL = 130
    # BEGIN = 131
    # CALL = 132
    # CAST = 133
    # DO = 134
    # END = 135
    # IF = 136
    # ODD = 137
    # PROC = 138
    # THEN = 139
    # VAR = 140
    # WHILE = 141


class PL0Lexer():

    charVector = [#0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F 
                   7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,#/* 0*/
                   7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,#/*10*/
                   7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,#/*20*/
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 0, 5, 4, 6, 0,#/*30*/
                   0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,#/*40*/
                   2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0,#/*50*/
                   0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,#/*60*/
                   2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0
                  ]

    
    stateMat = []

    def __init__(self, inputFile):
        self.sourceFile = open(inputFile,"r")
        self.linePosition = 0
        self.lineCount = 1
        self.morophemCode = MorphemCode.EMPTY
        self.morphemLength = 0
        self.morphem = ""
        self.currentChar = ""
        self.outBuffer = ""
        self.currentState = 0

        # Build Action Vector
        self.actions = [
            self.slb, #0
            self.sl,  #1
            self.gl,  #2
            self.l,   #3
            self.b    #4
        ]

        # Build up state Matrix
        self.stateMat = [
        #   0 So   1 Zi   2 Bu   3 ':'  4 '='  5 '<'  6 '>'  7 Space      
            [(9,0), (1,1), (2,2), (3,1), (9,0), (4,1), (5,1), (0,3)], #0
            [(9,4), (1,1), (9,4), (9,4), (9,4), (9,4), (9,4), (9,4)], #1
            [(9,4), (2,1), (2,2), (9,4), (9,4), (9,4), (9,4), (9,4)], #2
            [(9,4), (9,4), (9,4), (9,4), (6,1), (9,4), (9,4), (9,4)], #3
            [(9,4), (9,4), (9,4), (9,4), (7,1), (9,4), (9,4), (9,4)], #4
            [(9,4), (9,4), (9,4), (9,4), (8,1), (9,4), (9,4), (9,4)], #5
            [(9,4), (9,4), (9,4), (9,4), (9,4), (9,4), (9,4), (9,4)], #6
            [(9,4), (9,4), (9,4), (9,4), (9,4), (9,4), (9,4), (9,4)], #7
            [(9,4), (9,4), (9,4), (9,4), (9,4), (9,4), (9,4), (9,4)] #8
        ]

        # Read first char to give Lexer a one char look-ahead
        self.l()
        
        # Test next()
        #while self.morophemCode is not MorphemCode.EMPTY:
        #    print(str(self.lineCount) + "." + str(self.linePosition) + ": " + self.currentChar)
        #    self.next()

    def lex(self):
        self.currentState = 0
        self.outBuffer = ""

        while True:

            cell = self.stateMat[self.currentState][self.charVector[ord(self.currentChar)]]
            self.actions[cell[1]]()
            self.currentState = cell[0]

            if self.currentState == 9:
                # 9 is our End-State -> Terminate Process
                break        

    def next(self):
        self.currentChar = self.sourceFile.read(1)


        if not self.currentChar:
            print("EOF")
            self.morophemCode = MorphemCode.EMPTY
            return

        if self.currentChar == "\n":
            self.linePosition = 0
            self.lineCount += 1
        else:
            self.linePosition += 1

    # Schreiben
    def s(self):
        self.outBuffer += self.currentChar

    # Lesen
    def l(self):
        self.next()
        
    # Schreiben, Beenden
    def sb(self):
        self.outBuffer += self.currentChar
        self.b()
        
    # In Großbuchstaben schreiben, Lesen
    def gl(self):
        self.outBuffer += self.currentChar.upper()
        self.l()
        
    # Schreiben, Lesen
    def sl(self):
        self.outBuffer += self.currentChar
        self.l()
        
    # Schreiben, Lesen, Beenden
    def slb(self):
        self.sl()
        self.b()

    # Beenden
    def b(self):                #: < > Symbol
        if self.currentState in (3,4,5,0):
            self.morphem = self.outBuffer
            self.morophemCode = MorphemCode.SYMBOL
        elif self.currentState == 2:
            self.morphem = self.outBuffer
            self.morophemCode = MorphemCode.STRING7
        elif self.currentState == 1:
            self.morphem = int(self.outBuffer)
            self.morphemCode = MorphemCode.NUMBER
        elif self.currentState == 6:
            self.morphem = MorphemSymbols.EQUAL
            self.morophemCode = MorphemCode.SYMBOL
        elif self.currentState == 7:
            self.morphem = MorphemSymbols.LESSER_EQUAL
            self.morophemCode = MorphemCode.SYMBOL
        elif self.currentState == 8:
            self.morphem = MorphemSymbols.GREATER_EQUAL
            self.morophemCode = MorphemCode.SYMBOL

        print(str(self.morophemCode) + ": " +str(self.morphem))
        

    def __del__(self):
        if self.sourceFile is not None:
            self.sourceFile.close()
        



if __name__ == '__main__':

    sourceFile = "test.txt"
    if len(sys.argv) != 2:
        pass
        #print("usage: {} <input file>".format(sys.argv[0]))
        #sys.exit(1)
    else:
        sourceFile = sys.argv[1]

    if not os.path.exists(sourceFile):
        print("File doesn't exist")
        sys.exit(1)

    p = PL0Lexer(inputFile=sourceFile)
    
    
