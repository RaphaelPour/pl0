#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
import os
from enum import Enum


class MorphemCode(Enum):
    EMPTY = 1
    NUMBER = 2
    SYMBOL = 3
    IDENT = 4


class MorphemSymbols(Enum):
    NULL = 0
    EQUALS = 128
    LESSER_EQUAL = 129
    GREATER_EQUAL = 130


class Morphem():

    def __init__(self):
        self.lineCount = 1
        self.linePosition = 0
        self.code = MorphemCode.EMPTY
        self.value  = ""

    def setIdentifier(self, value):
        self.value = value
        self.code = MorphemCode.IDENT

    def setNumber(self,value):
        self.value = value
        self.code = MorphemCode.NUMBER

    def setSymbol(self,value):
        self.value = value
        self.code = MorphemCode.SYMBOL

    def __str__(self):
        return "[i] {}.{}, Code: {}, Value: {}".format(self.lineCount, self.linePosition, self.code, self.value)


class PL0Lexer():

    #  Class | Description
    #  ------+---------------------------
    #    0   | Valid Special Chars
    #    1   | Numbers
    #    2   | Letters
    #    3   | ':'
    #    4   | '='
    #    5   | '<'
    #    6   | '>'
    #    7   | Control Chars

    stateMat = []

    def __init__(self, inputFile):
        self.sourceFile = open(inputFile, "r")
        self.morphem = Morphem()
        self.currentChar = ""
        self.outBuffer = ""
        self.currentState = 0



        self.charVector = [
            # 0 1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
            7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,  # /* 0*/
            7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,  # /*10*/
            7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # /*20*/
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 0, 5, 4, 6, 0,  # /*30*/
            0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,  # /*40*/
            2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0,  # /*50*/
            0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,  # /*60*/
            2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0  # /*70*/
        ]

        # Make Shorter Functions for the State-Matrix
        SLB = self.writeReadEnd
        SL_ = self.writeRead
        GL_ = self.upperWriteEnd
        L__ = self.read
        B__ = self.end
        
        # Build up state Matrix
        self.stateMat = [
            #  0 So      1 Zi      2 Bu      3 ':'     4 '='     5 '<'     6 '>'     7 Space
            [(9, SLB), (1, SL_), (2, GL_), (3, SL_), (9, SLB), (4, SL_), (5, SL_), (0, L__)],  # 0
            [(9, B__), (1, SL_), (9, B__), (9, B__), (9, B__), (9, B__), (9, B__), (9, B__)],  # 1
            [(9, B__), (2, SL_), (2, GL_), (9, B__), (9, B__), (9, B__), (9, B__), (9, B__)],  # 2
            [(9, B__), (9, B__), (9, B__), (9, B__), (6, SL_), (9, B__), (9, B__), (9, B__)],  # 3
            [(9, B__), (9, B__), (9, B__), (9, B__), (7, SL_), (9, B__), (9, B__), (9, B__)],  # 4
            [(9, B__), (9, B__), (9, B__), (9, B__), (8, SL_), (9, B__), (9, B__), (9, B__)],  # 5
            [(9, B__), (9, B__), (9, B__), (9, B__), (9, B__), (9, B__), (9, B__), (9, B__)],  # 6
            [(9, B__), (9, B__), (9, B__), (9, B__), (9, B__), (9, B__), (9, B__), (9, B__)],  # 7
            [(9, B__), (9, B__), (9, B__), (9, B__), (9, B__), (9, B__), (9, B__), (9, B__)]  # 8
        ]

        # Read first char to give Lexer a one char look-ahead
        self.read()

    def lex(self):
        self.currentState = 0
        self.outBuffer = ""
        self.morphem = Morphem()

        if self.currentChar == "":
            return self.morphem

        while self.currentState != 9:

            #print("ord({}) = {}".format(self.currentChar, ord(self.currentChar)))

            if not self.currentChar:
                self.end()
                return self.morphem

            cvIndex = ord(self.currentChar)
            if cvIndex >= len(self.charVector):
                self.error("Char Vector Index out of range with char '{}' ({}), Char Vector's size is {}".format(
                    self.controlSymbolsToString(self.currentChar), ord(self.currentChar), len(self.charVector)))

            charClass = self.charVector[cvIndex]
            if charClass > 7:
                self.error(
                    "Char Class Index '{}' out of range. There are only 7 classes.".format(charClass))

            if self.currentState > 9:
                self.error("Invalid State '{}'. There are only 9 states.".format(self.currentState))

            action = self.stateMat[self.currentState][charClass]
            action[1]()

            self.currentState = action[0]
            
        return self.morphem

    def next(self):
        self.currentChar = self.sourceFile.read(1)

        self.morphem.linePosition += 1
        if self.currentChar == "\n":
            self.morphem.linePosition = 0
            self.morphem.lineCount += 1

    # Schreiben
    def write(self):
        self.outBuffer += self.currentChar

    # Lesen
    def read(self):
        self.next()

    # Schreiben, Beenden
    def writeEnd(self):
        self.write()
        self.end()

    # In Großbuchstaben schreiben, Lesen
    def upperWriteEnd(self):
        self.outBuffer += self.currentChar.upper()
        self.read()

    # Schreiben, Lesen
    def writeRead(self):
        self.write()
        self.read()

    # Schreiben, Lesen, Beenden
    def writeReadEnd(self):
        self.writeRead()
        self.end()

    # Beenden
    def end(self):

        # Valid Special Chars and :,<,>
        if self.currentState in (3, 4, 5, 0):
            self.morphem.setSymbol(self.outBuffer)

        # Number
        elif self.currentState == 1:
            self.morphem.setNumber(float(self.outBuffer))

        # Letters
        elif self.currentState == 2:
            self.morphem.setIdentifier(self.outBuffer)

        # Equals :=
        elif self.currentState == 6:
            self.morphem.setSymbol(MorphemSymbols.EQUALS)

        # Lesser-Equal <=
        elif self.currentState == 7:
            self.morphem.setSymbol(MorphemSymbols.LESSER_EQUAL)
            
        # Greater-Equal =>
        elif self.currentState == 8:
            self.morphem.setSymbol(MorphemSymbols.GREATER_EQUAL)

        else:
            self.error("Unknown State '{}'".format(self.currentState))

    def controlSymbolsToString(self, s):
        out = ""
        if s == '\n':
            out = "<NEWLINE>"
        elif s == '\t':
            out = "<TAB>"
        elif s == ' ':
            out = "<SPACE>"
        else:
            out = s

        return out

    def error(self, message):
        print("[!] Error in {}: {}".format(str(self.morphem), message))
        sys.exit(1)

    def __del__(self):
        if self.sourceFile is not None:
            self.sourceFile.close()


if __name__ == '__main__':

    sourceFile = "test.txt"
    if len(sys.argv) != 2:
        pass
        #print("usage: {} <input file>".format(sys.argv[0]))
        # sys.exit(1)
    else:
        sourceFile = sys.argv[1]

    if not os.path.exists(sourceFile):
        print("File doesn't exist")
        sys.exit(1)

    print("[i] using sourcefile {}".format(sourceFile))
    p = PL0Lexer(inputFile=sourceFile)

    while True:
        morphem = p.lex()
    
        if morphem.code == MorphemCode.EMPTY :
            break

        print(str(morphem))
