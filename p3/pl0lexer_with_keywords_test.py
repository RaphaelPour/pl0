import unittest
import os

from pl0lexer_with_keywords import PL0LexerWithKeywords, Morphem, MorphemCode, MorphemSymbol

class TestPL0LexerWithKeywords(unittest.TestCase):

    def setUp(self):
        self.testFileFolder = "../testfiles"

    def test_operator(self):
        testFile = os.path.join(self.testFileFolder, "test1.txt")
        lexer = PL0LexerWithKeywords(testFile)

        morpheme = []

        currentMorphem = lexer.lex()
        while currentMorphem.code != MorphemCode.EMPTY:

            morpheme.append(currentMorphem.value)
            currentMorphem = lexer.lex()

        self.assertEqual(morpheme, [">", "<", MorphemSymbol.GREATER_EQUAL,
                                    MorphemSymbol.LESSER_EQUAL, "=", MorphemSymbol.ASSIGN])

    def test_pl01(self):
        testFile = os.path.join(self.testFileFolder, "tx.pl0")
        lexer = PL0LexerWithKeywords(testFile)

        morpheme = []

        currentMorphem = lexer.lex()
        while currentMorphem.code != MorphemCode.EMPTY:

            morpheme.append(currentMorphem.value)
            currentMorphem = lexer.lex()

        self.assertEqual(morpheme,
                         [
                             MorphemSymbol.PROCEDURE, "P1", ";",
                             MorphemSymbol.VAR, "I", ";",
                             MorphemSymbol.BEGIN,
                             "I", MorphemSymbol.ASSIGN, 0.0, ";",
                             MorphemSymbol.WHILE, "I", "<", 7.0, MorphemSymbol.DO,
                             MorphemSymbol.BEGIN,
                             "I", MorphemSymbol.ASSIGN, "I", "+", 1.0, ";",
                             "!", "I",
                             MorphemSymbol.END,
                             MorphemSymbol.END, ";",
                             MorphemSymbol.CALL, "P1", "."
                         ])

    def test_pl02(self):
        testFile = os.path.join(self.testFileFolder, "t2.pl0")
        lexer = PL0LexerWithKeywords(testFile)

        morpheme = []

        currentMorphem = lexer.lex()
        while currentMorphem.code != MorphemCode.EMPTY:

            morpheme.append(currentMorphem.value)
            currentMorphem = lexer.lex()

        self.assertEqual(morpheme,
                         [
                             MorphemSymbol.VAR, "A", ",", "B", ",", "MAX", ";",
                             MorphemSymbol.PROCEDURE, "P1", ";",
                             MorphemSymbol.BEGIN,
                             MorphemSymbol.IF, "A", MorphemSymbol.GREATER_EQUAL, "B", MorphemSymbol.THEN, "MAX", MorphemSymbol.ASSIGN, "A", ";",
                             MorphemSymbol.IF, "A", "<", "B", MorphemSymbol.THEN, "MAX", MorphemSymbol.ASSIGN, "B",
                             MorphemSymbol.END,";",
                             MorphemSymbol.BEGIN,
                             "?", "A",";",
                             "?", "B",";",
                             MorphemSymbol.CALL, "P1",";",
                             "!", "MAX",
                             MorphemSymbol.END, "."
                         ])
                         
    def test_pltmin(self):
        testFile = os.path.join(self.testFileFolder, "tmin.pl0")
        lexer = PL0LexerWithKeywords(testFile)

        morpheme = []

        currentMorphem = lexer.lex()
        while currentMorphem.code != MorphemCode.EMPTY:

            morpheme.append(currentMorphem.value)
            currentMorphem = lexer.lex()

        self.assertEqual(morpheme,[ "!" , 5 , "."])
    
    def test_pltm(self):
        testFile = os.path.join(self.testFileFolder, "tm.pl0")
        lexer = PL0LexerWithKeywords(testFile)

        morpheme = []

        currentMorphem = lexer.lex()
        while currentMorphem.code != MorphemCode.EMPTY:

            morpheme.append(currentMorphem.value)
            currentMorphem = lexer.lex()

        #!- 3+ (-4).
        self.assertEqual(morpheme,[ "!" , "-", 3.0 , "+", "(", "-", 4.0, ")", "."])

    def test_plfacult(self):
        testFile = os.path.join(self.testFileFolder, "fakultRecursiv.pl0")
        lexer = PL0LexerWithKeywords(testFile)

        morpheme = []

        currentMorphem = lexer.lex()
        while currentMorphem.code != MorphemCode.EMPTY:

            morpheme.append(currentMorphem.value)
            currentMorphem = lexer.lex()

        self.assertEqual(morpheme,[ 
                MorphemSymbol.VAR, "A", ",", "FAC", ";",
                MorphemSymbol.PROCEDURE, "P1", ";",
                MorphemSymbol.VAR, "B", ",", "C", ";",
                MorphemSymbol.BEGIN,
                "B", MorphemSymbol.ASSIGN, "A", ";",
                "A", MorphemSymbol.ASSIGN, "A", "-", 1.0, ";",
                "C", MorphemSymbol.ASSIGN, "A", ";",
                "!", "C", ";",
                MorphemSymbol.IF, "C", ">", 1.0, MorphemSymbol.THEN, MorphemSymbol.CALL, "P1", ";",
                "FAC", MorphemSymbol.ASSIGN, "FAC", "*", "B", ";",
                "!", "FAC",
                MorphemSymbol.END, ";",
                MorphemSymbol.BEGIN,
                "?", "A", ";",
                "FAC", MorphemSymbol.ASSIGN, 1.0, ";",
                MorphemSymbol.CALL, "P1", ";",
                "!", "FAC",
                MorphemSymbol.END, "."
            ])

    def test_lines(self):
        testFile = os.path.join(self.testFileFolder, "tx.pl0")
        lexer = PL0LexerWithKeywords(testFile)

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
