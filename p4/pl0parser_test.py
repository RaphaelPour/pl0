import unittest
import os

from pl0parser import PL0Parser

class TestPL0Parser(unittest.TestCase):

    def setUp(self):
        self.testFileFolder = "../testfiles"

    def test_operator(self):
        testFile = os.path.join(self.testFileFolder, "test1.txt")
        lexer = PL0Parser(testFile)

        morpheme = []

        currentMorphem = lexer.lex()
        while currentMorphem.code != MorphemCode.EMPTY:

            morpheme.append(currentMorphem.value)
            currentMorphem = lexer.lex()

        self.assertEqual(morpheme, [">", "<", MorphemSymbol.GREATER_EQUAL,
                                    MorphemSymbol.LESSER_EQUAL, "=", MorphemSymbol.ASSIGN])

if __name__ == '__main__':
    unittest.main()
