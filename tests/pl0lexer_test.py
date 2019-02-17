#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import os

import sys
sys.path.append("..")

from pl0lexer import PL0Lexer, Morphem, MorphemCode, Symbol

class TestPL0Lexer(unittest.TestCase):

    def setUp(self):
        self.testFileFolder = "testfiles"

    def test_operator(self):
        testFile = os.path.join(self.testFileFolder, "test1.txt")
        lexer = PL0Lexer(testFile)

        morpheme = []

        currentMorphem = lexer.lex()
        while currentMorphem.code != MorphemCode.EMPTY:

            morpheme.append(currentMorphem.value)
            currentMorphem = lexer.lex()

        self.assertEqual(morpheme, [">", "<", Symbol.GREATER_EQUAL,
                                    Symbol.LESSER_EQUAL, "=", Symbol.ASSIGN])

    def test_pl01(self):
        testFile = os.path.join(self.testFileFolder, "tx.pl0")
        lexer = PL0Lexer(testFile)

        morpheme = []

        currentMorphem = lexer.lex()
        while currentMorphem.code != MorphemCode.EMPTY:

            morpheme.append(currentMorphem.value)
            currentMorphem = lexer.lex()

        self.assertEqual(morpheme,
                         [
                             Symbol.PROCEDURE, "P1", ";",
                             Symbol.VAR, "I", ";",
                             Symbol.BEGIN,
                             "I", Symbol.ASSIGN, 0.0, ";",
                             Symbol.WHILE, "I", "<", 7.0, Symbol.DO,
                             Symbol.BEGIN,
                             "I", Symbol.ASSIGN, "I", "+", 1.0, ";",
                             "!", "I",
                             Symbol.END,
                             Symbol.END, ";",
                             Symbol.CALL, "P1", "."
                         ])

    def test_pl02(self):
        testFile = os.path.join(self.testFileFolder, "t2.pl0")
        lexer = PL0Lexer(testFile)

        morpheme = []

        currentMorphem = lexer.lex()
        while currentMorphem.code != MorphemCode.EMPTY:

            morpheme.append(currentMorphem.value)
            currentMorphem = lexer.lex()

        self.assertEqual(morpheme,
                         [
                             Symbol.VAR, "A", ",", "B", ",", "MAX", ";",
                             Symbol.PROCEDURE, "P1", ";",
                             Symbol.BEGIN,
                             Symbol.IF, "A", Symbol.GREATER_EQUAL, "B", Symbol.THEN, "MAX", Symbol.ASSIGN, "A", ";",
                             Symbol.IF, "A", "<", "B", Symbol.THEN, "MAX", Symbol.ASSIGN, "B",
                             Symbol.END,";",
                             Symbol.BEGIN,
                             "?", "A",";",
                             "?", "B",";",
                             Symbol.CALL, "P1",";",
                             "!", "MAX",
                             Symbol.END, "."
                         ])
                         
    def test_pltmin(self):
        testFile = os.path.join(self.testFileFolder, "tmin.pl0")
        lexer = PL0Lexer(testFile)

        morpheme = []

        currentMorphem = lexer.lex()
        while currentMorphem.code != MorphemCode.EMPTY:

            morpheme.append(currentMorphem.value)
            currentMorphem = lexer.lex()

        self.assertEqual(morpheme,[ "!" , 5 , "."])
    
    def test_pltm(self):
        testFile = os.path.join(self.testFileFolder, "tm.pl0")
        lexer = PL0Lexer(testFile)

        morpheme = []

        currentMorphem = lexer.lex()
        while currentMorphem.code != MorphemCode.EMPTY:

            morpheme.append(currentMorphem.value)
            currentMorphem = lexer.lex()

        #!- 3+ (-4).
        self.assertEqual(morpheme,[ "!" , "-", 3.0 , "+", "(", "-", 4.0, ")", "."])

    def test_plfacult(self):
        testFile = os.path.join(self.testFileFolder, "fakultRecursiv.pl0")
        lexer = PL0Lexer(testFile)

        morpheme = []

        currentMorphem = lexer.lex()
        while currentMorphem.code != MorphemCode.EMPTY:

            morpheme.append(currentMorphem.value)
            currentMorphem = lexer.lex()

        self.assertEqual(morpheme,[ 
                Symbol.VAR, "A", ",", "FAC", ";",
                Symbol.PROCEDURE, "P1", ";",
                Symbol.VAR, "B", ",", "C", ";",
                Symbol.BEGIN,
                "B", Symbol.ASSIGN, "A", ";",
                "A", Symbol.ASSIGN, "A", "-", 1.0, ";",
                "C", Symbol.ASSIGN, "A", ";",
                "!", "C", ";",
                Symbol.IF, "C", ">", 1.0, Symbol.THEN, Symbol.CALL, "P1", ";",
                "FAC", Symbol.ASSIGN, "FAC", "*", "B", ";",
                "!", "FAC",
                Symbol.END, ";",
                Symbol.BEGIN,
                "?", "A", ";",
                "FAC", Symbol.ASSIGN, 1.0, ";",
                Symbol.CALL, "P1", ";",
                "!", "FAC",
                Symbol.END, "."
            ])

    def test_lines(self):
        testFile = os.path.join(self.testFileFolder, "tx.pl0")
        lexer = PL0Lexer(testFile)

        morpheme = []

        currentMorphem = lexer.lex()
        while currentMorphem.code != MorphemCode.EMPTY:

            morpheme.append( (currentMorphem.lines, currentMorphem.cols ))
            currentMorphem = lexer.lex()

        self.assertEqual(morpheme,
                         [
                             (2,3), (2,13),(2,15),
                             (3,3), (3,7), (3,8),
                             (4,3),
                             (5,5),(5,6),(5,8),(5,9),
                             (6,5),(6,11), (6,12),(6,13), (6, 15),
                             (7,6),
                             (8,7),(8,8),(8,10),(8,11),(8,12),(8,13),
                             (9,7),(9,8),
                             (10,6),
                             (11,3),(11,6),
                             (13,1), (13,6), (13,8)
                         ])
if __name__ == '__main__':
    unittest.main()
