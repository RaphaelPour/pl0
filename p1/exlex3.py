#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
import inspect
from enum import Enum

#
#   Expression Parser with grammar:
#   Non-Teminals: Factor, Term, Expression
#   Terminals: Number, '+', '-', '*', '/', '(', ')'
#   Start: Expression
#   Rules:
#       Expression  -> Term RExpr
#       RExpr       -> '+' Term RExpr | ε
#       Term        -> Factor RTerm
#       RTerm       -> '*' Factor RTerm | ε
#       Factor      -> Number | '(' Expression ')'
#

class MorphemCode(Enum):
    EMPTY = 1
    OPERATOR = 2
    VALUE = 3

class ExpressionParser:
    def __init__(self, inputString, printAST=False, printOperations=True):
        self.code = MorphemCode.EMPTY
        self.position = 0
        self.inputString = inputString
        self.value = 0.0
        self.operator = ''
        self.depth =0
        self.printAST = printAST
        self.printOperations = printOperations

    def evaluate(self):
        self.lex()
        return self.expression()

    def lex(self):
        
        if self.position == len(self.inputString):
            self.code = MorphemCode.EMPTY
            return

        m = re.match(r'^([0-9]+(\.[0-9]*)?)',
            self.inputString[self.position:])
        if m is not None:
            self.position += len(m.group(0))
            self.code = MorphemCode.VALUE
            self.value = float(m.group(0))
            return

        m = re.match(r'^[+|\-|*|/|(|)]',
            self.inputString[self.position:])


        if m is not None:
            self.position += 1
            self.code = MorphemCode.OPERATOR
            self.operator = m.group(0)
            return
        
        print("Unknown symbol '{}'".format(self.inputString[self.position]))
        sys.exit(1)

 
    def expression(self):
        self.printASTNode("Expression")
        value = self.term()
        return self.rexpr(value)

    def rexpr(self, value):
        self.printASTNode("RExpr")

        if self.code == MorphemCode.OPERATOR:
            if self.operator == '-':
                self.printASTNode(" O({}) ".format(self.operator))
                self.lex()
                value -= self.term()
                value = self.rexpr(value)
            elif self.operator == '+':
                self.printASTNode(" O({}) ".format(self.operator))
                self.lex()
                value += self.term()
                value = self.rexpr(value)

        return value

    def term(self):
        self.printASTNode("Term")
        value = self.factor()
        return self.rterm(value)

    def rterm(self, value):
        self.printASTNode("RTerm")
        if self.code == MorphemCode.OPERATOR:
            if self.operator == '*':
                self.printASTNode(" O({}) ".format(self.operator))
                self.lex()
                value *= self.factor()
                value = self.rterm(value)
            elif self.operator == '/':
                self.printASTNode(" O({}) ".format(self.operator))
                self.lex()
                value /= self.factor()
                value = self.rterm(value)
        return value

    def factor(self):   
        self.printASTNode("Factor")
        value = 0.0

        if self.code == MorphemCode.OPERATOR and self.operator == '(':
            self.printASTNode(" O({}) ".format(self.operator))
            self.lex()
            value = self.expression()
            if self.code != MorphemCode.OPERATOR or self.operator != ')':
               self.error("Expected ')'")
            self.printASTNode(" O({}) ".format(self.operator))
            self.lex()
        elif self.code == MorphemCode.VALUE:
            self.printASTNode(" V({}) ".format(self.value))
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

    def printASTNode(self, function):
        if self.printAST:
            depth = len(inspect.stack())-4
            print("{}{}".format(" "*depth, function))

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("usage {} <arithmetic expression>".format(sys.argv[0]))
        sys.exit(1)
    
    e = ExpressionParser(sys.argv[1],True,False)
    print("{} = {}".format(sys.argv[1],e.evaluate()))

