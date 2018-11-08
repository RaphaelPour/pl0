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


class MorphemSymbol(Enum):
    NULL = 0
    EQUALS = 128
    LESSER_EQUAL = 129
    GREATER_EQUAL = 130
    BEGIN = 131
    CALL= 132
    CONST= 133
    DO = 134
    END= 135
    IF= 136
    ODD= 137
    PROCEDURE= 138
    THEN = 139
    VAR = 140
    WHILE = 141

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

        value = self.value
       # if self.code == MorphemCode.SYMBOL:
                #value = "<{}, {}>".format(MorphemSymbol(self.value).name, str(self.value))
        
        return "[i] {}:{} {}: {}".format(self.lineCount, self.linePosition, self.code, value)

class PL0LexerWithKeywords():

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
    #    8   | First letter of a valid keyword

    stateMat = []

    def __init__(self, inputFile):
        self.sourceFile = open(inputFile, "r")
        self.morphem = Morphem()
        self.currentChar = ""
        self.outBuffer = ""
        self.currentState = 0


        self.charVector = [
            # 0 1  2  3  4  5  6  7  8  10  A  B  C  D  E  F
            7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,  # /* 0*/
            7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,  # /*10*/
            7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # /*20*/
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 0, 5, 4, 6, 0,  # /*30*/
        #      A  B  C  D  E  F  G  H  I  J  K  L  M  N  O
            0, 2, 8, 8, 8, 8, 2, 2, 2, 8, 2, 2, 2, 2, 2, 8,  # /*40*/
        #   P  Q  R  S  T  U  V  W  Y  Y  Z  
            8, 2, 2, 2, 8, 2, 8, 8, 2, 2, 2, 0, 0, 0, 0, 0,  # /*50*/
        #      a  b  c  d  e  f  g  h  i  j  k  l  m  n  o
            0, 2, 8, 8, 8, 8, 2, 2, 2, 8, 2, 2, 2, 2, 2, 8,  # /*60*/
        #   p  q  r  s  t  u  v  w  x  y  z 
            8, 2, 2, 2, 8, 2, 8, 8, 2, 2, 2, 0, 0, 0, 0, 0  # /*70*/
        ]

        # Make Shorter Functions for the State-Matrix
        SLB = self.writeReadEnd
        SL_ = self.writeRead
        GL_ = self.upperWriteEnd
        L__ = self.read
        B__ = self.end
        
        # Build up state Matrix
        self.stateMat = [
            #  0 So       1 Zi       2 Bu       3 ':'      4 '='      5 '<'      6 '>'      7 Inv.     8 Keyword Beginning
            [(10, SLB), ( 1, SL_), ( 2, GL_), ( 3, SL_), (10, SLB), ( 4, SL_), ( 5, SL_), ( 0, L__), ( 9, GL_)],  # 0 // Tabs/Whitespaces
            [(10, B__), ( 1, SL_), (10, B__), (10, B__), (10, B__), (10, B__), (10, B__), (10, B__), (10, B__)],  # 1 // Number
            [(10, B__), ( 2, SL_), ( 2, GL_), (10, B__), (10, B__), (10, B__), (10, B__), (10, B__), ( 2, GL_)],  # 2 // Ident
            [(10, B__), (10, B__), (10, B__), (10, B__), ( 6, SL_), (10, B__), (10, B__), (10, B__), (10, B__)],  # 3 // :
            [(10, B__), (10, B__), (10, B__), (10, B__), ( 7, SL_), (10, B__), (10, B__), (10, B__), (10, B__)],  # 4 // <
            [(10, B__), (10, B__), (10, B__), (10, B__), ( 8, SL_), (10, B__), (10, B__), (10, B__), (10, B__)],  # 5 // >
            [(10, B__), (10, B__), (10, B__), (10, B__), (10, B__), (10, B__), (10, B__), (10, B__), (10, B__)],  # 6 // :=
            [(10, B__), (10, B__), (10, B__), (10, B__), (10, B__), (10, B__), (10, B__), (10, B__), (10, B__)],  # 7 // <=
            [(10, B__), (10, B__), (10, B__), (10, B__), (10, B__), (10, B__), (10, B__), (10, B__), (10, B__)],  # 8 // >=
            [(10, B__), ( 2, SL_), ( 9, GL_), (10, B__), (10, B__), (10, B__), (10, B__), (10, B__), ( 9, GL_)]   # 9 // Potential Keyword
        ]

        # Read first char to give Lexer a one char look-ahead
        self.currentChar = self.sourceFile.read(1)

    def lex(self):
        self.currentState = 0
        self.outBuffer = ""
        self.morphem = Morphem()

        if self.currentChar == "":
            return self.morphem

        while self.currentState != 10 and self.currentChar:

            cvIndex = ord(self.currentChar)
            if cvIndex >= len(self.charVector):
                self.error("Char Vector Index out of range with char '{}' ({}), Char Vector's size is {}".format(
                    self.controlSymbolsToString(self.currentChar), ord(self.currentChar), len(self.charVector)))

            charClass = self.charVector[cvIndex]
            if charClass > 8:
                self.error(
                    "Char Class Index '{}' out of range. There are only 8 classes.".format(charClass))

            if self.currentState > 10:
                self.error("Invalid State '{}'. There are only 10 states.".format(self.currentState))

            action = self.stateMat[self.currentState][charClass]
            action[1]()

            self.currentState = action[0]
            
        return self.morphem

    def next(self):
        
        self.morphem.linePosition += 1
        if self.currentChar in ("\n", "\r"):
            self.morphem.linePosition = 0
            self.morphem.lineCount += 1

        self.currentChar = self.sourceFile.read(1)


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
        if self.currentState in (3, 4, 5,0):
            self.morphem.setSymbol(self.outBuffer)

        # Number
        elif self.currentState == 1:
            self.morphem.setNumber(float(self.outBuffer))

        # Letters
        elif self.currentState == 2:
            self.morphem.setIdentifier(self.outBuffer)

        # Equals :=
        elif self.currentState == 6:
            self.morphem.setSymbol(MorphemSymbol.EQUALS)

        # Lesser-Equal <=
        elif self.currentState == 7:
            self.morphem.setSymbol(MorphemSymbol.LESSER_EQUAL)
            
        # Greater-Equal =>
        elif self.currentState == 8:
            self.morphem.setSymbol(MorphemSymbol.GREATER_EQUAL)

        # Potential-Keyword
        elif self.currentState == 9:
            for name, member in MorphemSymbol.__members__.items():
                if self.outBuffer == name:
                    self.morphem.setSymbol(member)
                    break
            else:
                self.morphem.setIdentifier(self.outBuffer)
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

    def warning(self, message):
        print("[w] Warning in {}: {}".format(str(self.morphem), message))

    def __del__(self):
        if self.sourceFile is not None:
            self.sourceFile.close()


if __name__ == '__main__':

    sourceFile = "test.txt"
    if len(sys.argv) != 2:
        print("usage: {} <input file>".format(sys.argv[0]))
        sys.exit(1)
    else:
        sourceFile = sys.argv[1]

    if not os.path.exists(sourceFile):
        print("File doesn't exist")
        sys.exit(1)

    print("[i] using sourcefile {}".format(sourceFile))
    p = PL0LexerWithKeywords(inputFile=sourceFile)

    while True:
        morphem = p.lex()
    
        if morphem.code == MorphemCode.EMPTY :
            break

        print(str(morphem))
        

    print("done.")