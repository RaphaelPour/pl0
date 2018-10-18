#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
from enum import Enum

#
#   Expression Parser with grammar:
#   Non-Teminals: Factor, Term, Expression
#   Terminals: Number, '+', '-', '*', '/', '(', ')'
#   Start: Expression
#   Rules:
#       Expression  -> Term | Term '+' Expression |
#                      Term '-' Expression
#       Term        -> Faktor | Faktor '*' Term
#       Faktor      -> Zahl | '(' Expression ')'
#

class MorphemCode(Enum):
    EMPTY = 1
    OPERATOR = 2
    VALUE = 3

class ExpressionParser:
    def __init__(self, inputString):
        self.code = MorphemCode.EMPTY
        self.position = 0
        self.inputString = inputString
        self.value = 0.0
        self.operator = ''

    def evaluate(self):
        self.lex()
        return self.expression()

    def lex(self):
        
        if self.position == len(self.inputString):
            self.code = MorphemCode.EMPTY
            return

        m = re.match(r'^[-]?([0-9]+(\.[0-9]*)?)',
            self.inputString[self.position:])
        if m is not None:
            print("V({}) ".format(m.group(0)), end='')
            self.position += len(m.group(0))
            self.code = MorphemCode.VALUE
            self.value = float(m.group(0))
            return

        m = re.match(r'^[+|\-|*|/(|)]',
            self.inputString[self.position:])

        if m is not None:
            print("O({}) ".format(m.group(0)),end='')
            self.position += 1
            self.code = MorphemCode.OPERATOR
            self.operator = m.group(0)
            return

        print("Unknown symbol '{}'".format(self.inputString[self.position]))
        sys.exit(1)

 
    def expression(self):
        value = self.term()

        if self.code == MorphemCode.OPERATOR:
            if self.operator == '+':
                self.lex()
                value += self.expression()
            elif self.operator == '-':
                self.lex()
                value -= self.term()

        return value

    def term(self):
        value = self.factor()

        if self.code == MorphemCode.OPERATOR:
            if self.operator == '*':
                self.lex()
                value *= self.term()
            elif self.operator == '/':
                self.lex()
                value /= self.term()
        return value

    def factor(self):
        value = 0.0

        if self.code == MorphemCode.OPERATOR and self.operator == '(':
            self.lex()
            value = self.expression()
            if self.code != MorphemCode.OPERATOR or self.operator != ')':
               self.error("Expected ')'")
            self.lex()
        elif self.code == MorphemCode.VALUE:
            value = self.value
            self.lex()
        else:
            self.error("Expected '(' or Value")
        return value

    def error(self, hint):
        print("Error at position {} '{}', MCode:{},MOp:{}: {}".format(
            self.position,
            self.inputString[self.position],
            self.code,
            self.operator,
            hint))
        sys.exit(1)

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("usage {} <arithmetic expression>".format(sys.argv[0]))
        sys.exit(1)
    
    e = ExpressionParser(sys.argv[1])
    print("{} = {}".format(sys.argv[1],e.evaluate()))

