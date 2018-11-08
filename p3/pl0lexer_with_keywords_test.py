import unittest
import os

from pl0lexer_with_keywords import PL0LexerWithKeywords, Morphem, MorphemCode, MorphemSymbols

class TestPL0Lexer(unittest.TestCase):

    def setUp(self):
        self.testFileFolder = "testfiles"

    def test_operator(self):
        testFile = os.path.join(self.testFileFolder, "test1.txt")
        lexer = PL0LexerWithKeywords(testFile)

        morpheme = []

        currentMorphem = lexer.lex()
        while currentMorphem.code != MorphemCode.EMPTY:

            morpheme.append(currentMorphem.value)
            currentMorphem = lexer.lex()

        self.assertEqual(morpheme, [">", "<", MorphemSymbols.GREATER_EQUAL,
                                    MorphemSymbols.LESSER_EQUAL, "=", MorphemSymbols.EQUALS])

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
                             "PROCEDURE", "P1", ";",
                             "VAR", "I", ";",
                             "BEGIN",
                             "I", MorphemSymbols.EQUALS, 0.0, ";",
                             "WHILE", "I", "<", 7.0, "DO",
                             "BEGIN",
                             "I", MorphemSymbols.EQUALS, "I", "+", 1.0, ";",
                             "!", "I",
                             "END",
                             "END", ";",
                             "CALL", "P1", "."
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
                             "VAR", "A", ",", "B", ",", "MAX", ";",
                             "PROCEDURE", "P1", ";",
                             "BEGIN",
                             "IF", "A", MorphemSymbols.GREATER_EQUAL, "B", "THEN", "MAX", MorphemSymbols.EQUALS, "A", ";",
                             "IF", "A", "<", "B", "THEN", "MAX", MorphemSymbols.EQUALS, "B",
                             "END",";",
                             "BEGIN",
                             "?", "A",";",
                             "?", "B",";",
                             "CALL", "P1",";",
                             "!", "MAX",
                             "END", "."
                         ])


if __name__ == '__main__':
    unittest.main()
