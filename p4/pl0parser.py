#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
from enum import Enum
import pprint
from pl0lexer import PL0Lexer,Morphem,MorphemCode,Symbol

class NonTerminal(Enum):
    PROGRAM = 0
    BLOCK = 1
    EXPRESSION = 2
    TERM = 3
    STATEMENT = 4
    FACTOR = 5
    CONDITION = 6

class EdgeType(Enum):
    NIL______ = 0
    SYMBOL___ = 1
    MORPHEM__ = 2
    SUBGRAPH_ = 4
    GRAPH_END = 8

class Edge():
    def __init__(self, type, value, emitter, nextEdge, alternativeEdge, nonterminal):

        # Also known as Bogen Description
        self.type = type 

        # Emitter will be implemented later, also known as fx
        self.f = emitter 

        # value is depending on the type a symbol, morphem, subgraph or graph end
        
        self.value = value
 
        # Index of the next Edge, also known as iNext
        self.next = nextEdge

        # Index of an alternative Edge, also known as iAlt
        self.alternative = alternativeEdge

        # Stores the current non-terminal for the list lookup
        self.nonterminal = nonterminal

    def __str__(self):
        result = "({},{}) {}".format(self.next,self.alternative, str(self.type))

        if self.type == EdgeType.SYMBOL___:
            if(isinstance(self.value, Symbol)):
                result += ": " + self.value.name
            else:
                result += ": " + self.value 
        elif self.type == EdgeType.MORPHEM__:
            result += ": " + self.value.name
        elif self.type == EdgeType.SUBGRAPH_:
            result += ": " + self.nonterminal.name
        

        return result

class PL0Parser():

    def __init__(self, sourceFile):
        
        # Init Syntax rules

        # Short identifier for edge definition
        PROG = NonTerminal.PROGRAM
        BLCK = NonTerminal.BLOCK
        EXPR = NonTerminal.EXPRESSION
        TERM = NonTerminal.TERM
        STAT = NonTerminal.STATEMENT
        FACT = NonTerminal.FACTOR
        COND = NonTerminal.CONDITION

        programEdges = [
            Edge(EdgeType.SUBGRAPH_, BLCK, None, 1,0, PROG),
            Edge(EdgeType.SYMBOL___, '.', None, 2,0, PROG),

            # End
            Edge(EdgeType.GRAPH_END, 0, None, 0,0, PROG)
        ]

        blockEdges = [
            # Constant Declaration
            Edge(EdgeType.SYMBOL___, Symbol.CONST,None, 1,6, BLCK), # 0
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, None,2,0, BLCK),   # 1
            Edge(EdgeType.SYMBOL___, '=', None, 3,0, BLCK),                # 2
            Edge(EdgeType.MORPHEM__, MorphemCode.NUMBER,None,4,5, BLCK),   # 3
            Edge(EdgeType.SYMBOL___, ',',None, 1,0, BLCK),                 # 4
            Edge(EdgeType.SYMBOL___, ';', None, 6,10, BLCK),               # 5

            # Variable Declaration
            Edge(EdgeType.SYMBOL___, Symbol.VAR, None, 7,10, BLCK), # 6
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, None, 8,0, BLCK),  # 7
            Edge(EdgeType.SYMBOL___, ',', None, 7,9, BLCK),                # 8
            Edge(EdgeType.SYMBOL___, ';', None, 10,15, BLCK),              # 9

            # Procedure Declaration
            Edge(EdgeType.SYMBOL___, Symbol.PROCEDURE, None, 11,15, BLCK), # 10
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, None, 12,0, BLCK),        # 11
            Edge(EdgeType.SYMBOL___, ';', None, 13,0, BLCK),                      # 12
            Edge(EdgeType.SUBGRAPH_, BLCK, None, 14,0, BLCK),                     # 13
            Edge(EdgeType.SYMBOL___, ';', None, 15,0, BLCK),                      # 14

            # Nil Edge (needed for emitter function)
            Edge(EdgeType.NIL______, None, None, 16,0, BLCK),                     # 15

            # Statement Declaration
            Edge(EdgeType.SUBGRAPH_, STAT, None, 17,0, BLCK),                     # 16

            # End
            Edge(EdgeType.GRAPH_END, None, None, 0,0, BLCK)                       # 17
        ]

    
        expressionEdges = [
            Edge(EdgeType.SYMBOL___,'-', None, 2,1,EXPR),               # 0
            Edge(EdgeType.NIL______,None, None, 2,0,EXPR),              # 1
            Edge(EdgeType.SUBGRAPH_, TERM, None, 3,0,EXPR),             # 2
            Edge(EdgeType.SYMBOL___, '+', None, 4,5,EXPR),              # 3
            Edge(EdgeType.SUBGRAPH_, TERM, None, 3,0,EXPR),             # 4 
            Edge(EdgeType.SYMBOL___,'-', None, 6,7,EXPR),               # 5
            Edge(EdgeType.SUBGRAPH_, TERM, None, 3,0,EXPR),             # 6
            
            # End
            Edge(EdgeType.GRAPH_END, None, None, 0,0,EXPR)              # 7
        ]

        termEdges = [
            Edge(EdgeType.SUBGRAPH_, FACT, None, 1,0,TERM),             # 0
            Edge(EdgeType.SYMBOL___, '+', None, 2,3,TERM),              # 1
            Edge(EdgeType.SUBGRAPH_, FACT, None, 1,0,TERM),             # 2 
            Edge(EdgeType.SYMBOL___,'-', None, 4,5,TERM),               # 3
            Edge(EdgeType.SUBGRAPH_, FACT, None, 1,0,TERM),             # 4

            # End
            Edge(EdgeType.GRAPH_END, None, None, 0,0,TERM)              # 5
        ]

        statementEdges = [
            # Assignment
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, None, 1,3,STAT),   #  0
            Edge(EdgeType.SYMBOL___, Symbol.ASSIGN, None, 2,0,STAT),       #  1
            Edge(EdgeType.SUBGRAPH_, EXPR, None, 21,0,STAT),               #  2

            # Condition
            Edge(EdgeType.SYMBOL___,Symbol.IF, None, 4,7,STAT),            #  3
            Edge(EdgeType.SUBGRAPH_, COND, None, 5,0,STAT),                #  4
            Edge(EdgeType.SYMBOL___, Symbol.THEN,None, 6,0,STAT),          #  5
            Edge(EdgeType.SUBGRAPH_, STAT,None, 21,0,STAT),                #  6

            # While Loop
            Edge(EdgeType.SYMBOL___, Symbol.WHILE, None, 8, 11,STAT),      #  7
            Edge(EdgeType.SUBGRAPH_, COND, None, 9,0,STAT),                #  8
            Edge(EdgeType.SYMBOL___, Symbol.DO,None, 10,0,STAT),           #  9
            Edge(EdgeType.SUBGRAPH_, STAT,None, 21,0,STAT),                # 10

            # BEGIN - END
            Edge(EdgeType.SYMBOL___, Symbol.BEGIN, None, 12,15,STAT),      # 11
            Edge(EdgeType.SUBGRAPH_, STAT, None,13, 0,STAT),               # 12
            Edge(EdgeType.SYMBOL___, ';', None, 12, 14,STAT),              # 13
            Edge(EdgeType.SYMBOL___, Symbol.END,None, 21,0,STAT),          # 14

            # CALL
            Edge(EdgeType.SYMBOL___, Symbol.CALL,None, 16,17,STAT),     # 15
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, None, 21,0,STAT),      # 16

            # Input
            Edge(EdgeType.SYMBOL___, '?', None, 18, 19,STAT),                  # 17
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, None, 21, 0,STAT),     # 18

            # Output
            # Alternative Edge 21 or 0? This depends on the used
            # grammar
            Edge(EdgeType.SYMBOL___, '!', None, 20, 21,STAT),                  # 19
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, None, 21, 0,STAT),     # 20

            # End
            Edge(EdgeType.GRAPH_END, None, None, 0,0,STAT)                     # 21

        ]

        factorEdges = [
            Edge(EdgeType.MORPHEM__, MorphemCode.NUMBER, None, 5,1,FACT),     # 0
            Edge(EdgeType.SYMBOL___, '(', None, 2,4,FACT),                    # 1
            Edge(EdgeType.SUBGRAPH_, EXPR, None, 3,0,FACT),                   # 2
            Edge(EdgeType.SYMBOL___, ')', None, 5,0,FACT),                    # 3
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT,None, 5,0,FACT),       # 4

            # End
            Edge(EdgeType.GRAPH_END, None, None, 0,0,FACT)                    # 5
        ]

        conditionEdges = [
            # ODD
            Edge(EdgeType.SYMBOL___, Symbol.ODD, None, 1, 2,COND),   #  0
            Edge(EdgeType.SUBGRAPH_, EXPR, None, 10, 0,COND),               #  1

            # Comparisson
            Edge(EdgeType.SUBGRAPH_,EXPR, None, 3,0,COND),                          #  2
            Edge(EdgeType.SYMBOL___, '=', None, 9, 4,COND),                         #  3
            Edge(EdgeType.SYMBOL___, '#', None, 9, 5,COND),                         #  4
            Edge(EdgeType.SYMBOL___, '>', None, 9, 6,COND),                         #  5
            Edge(EdgeType.SYMBOL___, '<', None, 9, 7,COND),                         #  6
            Edge(EdgeType.SYMBOL___, Symbol.LESSER_EQUAL, None, 9, 8,COND),  #  7
            Edge(EdgeType.SYMBOL___, Symbol.GREATER_EQUAL, None, 9, 0,COND), #  8
            Edge(EdgeType.SUBGRAPH_, EXPR, None, 10,0,COND),                        #  9

            # End
            Edge(EdgeType.GRAPH_END, None, None, 0,0,COND)                          # 10
        ]

        self.edges = {
            PROG : programEdges,    # 0
            BLCK : blockEdges,      # 1
            EXPR : expressionEdges, # 2
            TERM : termEdges ,      # 3
            STAT : statementEdges,  # 4
            FACT : factorEdges,     # 5
            COND : conditionEdges   # 6
        }

        # Init Lexer
        self.sourceFile = sourceFile
        self.lexer = PL0Lexer(self.sourceFile)

    def parse(self, edge=None, path=[]):
        
        if not edge:
            edge = self.edges[NonTerminal.PROGRAM][0]
        success = False

        if(self.lexer.morphem.code == MorphemCode.EMPTY):
            self.lexer.lex()

        while(True):

            # Check Edge type 
            if(edge.type == EdgeType.SYMBOL___):
                success = self.lexer.morphem.value == edge.value
                if success:
                    path.append({ 'value' : self.lexer.morphem.value, 'type' : edge.type, 'line' : self.lexer.morphem.lines})
            elif(edge.type == EdgeType.MORPHEM__):
                success = self.lexer.morphem.code == edge.value
                if success:
                    path.append({ 'value' : self.lexer.morphem.value, 'type' : edge.type, 'line' : self.lexer.morphem.lines})
            elif(edge.type == EdgeType.SUBGRAPH_):
                path.append({ 'value' : edge.nonterminal.name, 'type' : edge.type, 'line' : self.lexer.morphem.lines})
                success = self.parse(self.edges[edge.value][0],path)
                if not success:
                    path.pop()
            elif(edge.type == EdgeType.GRAPH_END):
                return path
            elif(edge.type == EdgeType.NIL______):
                success = True

            # Call Emitter
            if success and edge.f:
                success = edge.f()

            # Check alternatives if evaluation of edge type 
            # wasn't successful

            if not success:
                if edge.alternative != 0:
                    edge = self.edges[edge.nonterminal][edge.alternative]
                else:
                    print("[!] Parser failed at " + str(edge))

                    pp = pprint.PrettyPrinter(indent=4, depth=3)
                    pp.pprint(path)
                    return False
            else: 
                # Accept morphem
                if edge.type in [EdgeType.SYMBOL___, EdgeType.MORPHEM__]:
                    print("[i] {}".format(edge))
                    self.lexer.lex()
                edge = self.edges[edge.nonterminal][edge.next]


if __name__ == "__main__":
    sourceFile = "../testfiles/tx.pl0"
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

    parser = PL0Parser(sourceFile)

    if not parser.parse():
        print("[!] Parser failed with Morphem " + str(parser.lexer.morphem))
    else:
        print("[i] done ")