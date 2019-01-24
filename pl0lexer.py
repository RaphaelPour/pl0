#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   file:           pl0lexer.py
#   description:    Takes PL/0 file as input and provides tokens for the PL/0 parser
#   date:           24.01.2018
#   license:        GPL v3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
#
import sys
import re
import os
import logging
from enum import Enum


class MorphemCode(Enum):
    EMPTY = 1
    NUMBER = 2
    SYMBOL = 3
    IDENT = 4
    STRING = 5


class Symbol(Enum):
    NULL = 0
    ASSIGN = 128
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
    FOR = 142
    ELSE = 143

class Morphem():

    def __init__(self):
        self.code = MorphemCode.EMPTY
        self.value  = ""
        self.lines = 1
        self.cols = 1

    def setIdentifier(self, value):
        self.value = value
        self.code = MorphemCode.IDENT

    def setNumber(self,value):
        self.value = value
        self.code = MorphemCode.NUMBER

    def setSymbol(self,value):
        self.value = value
        self.code = MorphemCode.SYMBOL

    def setString(self, value):
        self.value = value
        self.code = MorphemCode.STRING

    def __str__(self):

        value = self.value
       # if self.code == MorphemCode.SYMBOL:
                #value = "<{}, {}>".format(Symbol(self.value).name, str(self.value))
        
        return "{:2}:{:2} {:18}: {}".format(self.lines, self.cols, self.code, value)

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
    #    8   | First letter of a valid keyword
    #    9   | '"'
    #   10   | '/'
    #   11   | '*'

    stateMat = []

    def __init__(self, inputFile):
        self.sourceFile = open(inputFile, "r")
        self.morphem = Morphem()
        self.currentChar = ""
        self.outBuffer = ""
        self.currentState = 0

        self.lines = 1
        self.cols = 1

        self.charVector = [
        #   0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
            7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,  # /* 0*/
            7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,  # /*10*/
        #         "                       *              /             
            7, 0, 9, 0, 0, 0, 0, 0, 0, 0,11, 0, 0, 0, 0,10,  # /*20*/
        #                                 :     <  =  >
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 0, 5, 4, 6, 0,  # /*30*/
        #      A  B  C  D  E  F  G  H  I  J  K  L  M  N  O
            0, 2, 8, 8, 8, 8, 8, 2, 2, 8, 2, 2, 2, 2, 2, 8,  # /*40*/
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
        RL_ = self.rewindRead
        RB_ = self.rewindEnd
        B__ = self.end
        
        # Build up state Matrix
        self.stateMat = [
            #  0 So       1 Zi       2 Bu       3 ':'      4 '='      5 '<'      6 '>'      7 Inv.     8 KB       9 '"'    10 /      11 *
            [(16, SLB), ( 1, SL_), ( 2, GL_), ( 3, SL_), (16, SLB), ( 4, SL_), ( 5, SL_), ( 0, L__), ( 9, GL_), (14,RL_), (10,SL_), (16,SLB)],  # 0 // Tabs/Whitespaces
            [(16, B__), ( 1, SL_), (16, B__), (16, B__), (16, B__), (16, B__), (16, B__), (16, B__), (16, B__), (16,B__), (16,B__), (16,B__)],  # 1 // Number
            [(16, B__), ( 2, SL_), ( 2, GL_), (16, B__), (16, B__), (16, B__), (16, B__), (16, B__), ( 2, GL_), (16,B__), (16,B__), (16,B__)],  # 2 // Ident
            [(16, B__), (16, B__), (16, B__), (16, B__), ( 6, SL_), (16, B__), (16, B__), (16, B__), (16, B__), (16,B__), (16,B__), (16,B__)],  # 3 // :
            [(16, B__), (16, B__), (16, B__), (16, B__), ( 7, SL_), (16, B__), (16, B__), (16, B__), (16, B__), (16,B__), (16,B__), (16,B__)],  # 4 // <
            [(16, B__), (16, B__), (16, B__), (16, B__), ( 8, SL_), (16, B__), (16, B__), (16, B__), (16, B__), (16,B__), (16,B__), (16,B__)],  # 5 // >
            [(16, B__), (16, B__), (16, B__), (16, B__), (16, B__), (16, B__), (16, B__), (16, B__), (16, B__), (16,B__), (16,B__), (16,B__)],  # 6 // :=
            [(16, B__), (16, B__), (16, B__), (16, B__), (16, B__), (16, B__), (16, B__), (16, B__), (16, B__), (16,B__), (16,B__), (16,B__)],  # 7 // <=
            [(16, B__), (16, B__), (16, B__), (16, B__), (16, B__), (16, B__), (16, B__), (16, B__), (16, B__), (16,B__), (16,B__), (16,B__)],  # 8 // >=
            [(16, B__), ( 2, SL_), ( 9, GL_), (16, B__), (16, B__), (16, B__), (16, B__), (16, B__), ( 9, GL_), (16,B__), (16,B__), (16,B__)],  # 9 // Potential Keyword

            [(16, SLB), (16, SLB), (16, SLB), (16, SLB), (16, SLB), (16, SLB), (16, SLB), (16, SLB), (16, SLB), (16,SLB), (16,SLB), (11,RL_)],  #10 // '/'
            [(11, L__), (11, L__), (11, L__), (11, L__), (11, L__), (11, L__), (11, L__), (11, L__), (11, L__), (11,L__), (11,L__), (12,L__)],  #11 // '/*'
            [(11, L__), (11, L__), (11, L__), (11, L__), (11, L__), (11, L__), (11, L__), (11, L__), (11, L__), (11,L__), (13,L__), (11,L__)],  #12 // '/*...|*'
            [( 0, L__), ( 0, L__), ( 0, L__), ( 0, L__), ( 0, L__), ( 0, L__), ( 0, L__), ( 0, L__), ( 0, L__), ( 0,L__), ( 0,L__), ( 0,L__)],  #13 // '/*...*/'

            [(14, SL_), (14, SL_), (14, SL_), (14, SL_), (14, SL_), (14, SL_), (14, SL_), (14, SL_), (14, SL_), (15,SL_), (14,SL_), (14,SL_)],  #14 // '"'
            [(16, RB_), (16, RB_), (16, RB_), (16, RB_), (16, RB_), (16, RB_), (16, RB_), (16, RB_), (16, RB_), (14,SL_), (16,RB_), (16,RB_)],  #15 // '"..."'
        ]

        # Read first char to give Lexer a one char look-ahead
        self.currentChar = self.sourceFile.read(1)

    def lex(self):
        self.currentState = 0
        self.outBuffer = ""

        self.morphem = Morphem()

        if self.currentChar == "":
            return self.morphem

        while self.currentState != 16:

            # Check if EOF is reached but current state is not 10
            # If there is an untokenized string -> call end without automaton table
            # and end the process
            if not self.currentChar:
                if self.outBuffer:
                    self.end()
                break

            cvIndex = ord(self.currentChar)
            if cvIndex >= len(self.charVector):
                logging.error("Char Vector Index out of range with char '{}' ({}), Char Vector's size is {}".format(
                    self.controlSymbolsToString(self.currentChar), ord(self.currentChar), len(self.charVector)))

            charClass = self.charVector[cvIndex]
            if charClass > 11:
                logging.error("Char Class Index '{}' out of range. There are only 11 classes.".format(charClass))

            if self.currentState > 16:
                logging.error("Invalid State '{}'. There are only 16 states.".format(self.currentState))

            #print("State: {}, charClass: {}".format(self.currentState, charClass))
            action = self.stateMat[self.currentState][charClass]
            action[1]()

            self.currentState = action[0]
            
        return self.morphem

    def next(self):
        
        self.cols += 1
        if self.currentChar in ("\n", "\r"):
            self.cols = 1
            self.lines += 1

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

    # Rewind, Lesen
    def rewindRead(self):
        self.rewind()
        self.read()

    # Rewind, Beenden
    def rewindEnd(self):
        self.rewind()
        self.end()

    # Rewind (Delete last char)
    def rewind(self):
        self.outBuffer = self.outBuffer[:-1] 

    # Beenden
    def end(self):

        # Subtract the length of the character-interpretation
        # of the value in order to get correct line/column values
        # for debugging (especially inside the parser)
        # But only if are not in the final state 16
        self.morphem.lines = self.lines
        self.morphem.cols = self.cols - len(str(self.outBuffer))

        # Valid Special Chars and :,<,>
        if self.currentState in (3, 4, 5,0):
            self.morphem.setSymbol(self.outBuffer)

        # Number
        elif self.currentState == 1:
            self.morphem.setNumber(float(self.outBuffer))

        # Letters
        elif self.currentState == 2:
            self.morphem.setIdentifier(self.outBuffer)

        # ASSIGN :=
        elif self.currentState == 6:
            self.morphem.setSymbol(Symbol.ASSIGN)

        # Lesser-Equal <=
        elif self.currentState == 7:
            self.morphem.setSymbol(Symbol.LESSER_EQUAL)
            
        # Greater-Equal =>
        elif self.currentState == 8:
            self.morphem.setSymbol(Symbol.GREATER_EQUAL)

        # Potential-Keyword
        elif self.currentState == 9:
            for name, member in Symbol.__members__.items():
                if self.outBuffer == name:
                    self.morphem.setSymbol(member)
                    break
            else:
                self.morphem.setIdentifier(self.outBuffer)

        # Comment -> Ignore
        elif self.currentState == 15:
            self.morphem.setString(self.outBuffer)
        else:
            logging.error("Unknown State '{}'".format(self.currentState))

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

    def __del__(self):
        if self.sourceFile is not None:
            self.sourceFile.close()


if __name__ == '__main__':

    sourceFile = "..\\testfiles\\tx.pl0"
    if len(sys.argv) != 2:
        #print("usage: {} <input file>".format(sys.argv[0]))
        #sys.exit(1)
        pass
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

    print("done.")