from enum import Enum

class MorphemCode(Enum):
    EMPTY = 1
    OPERATOR = 2
    DOUBLE = 3

class Lexer:
    def __init__(self, inputString):
        self.code = MorphemCode.EMPTY
        self.position = 0
        self.inputString = inputString
        self.doubleValue = 0.0

    def go(self):

