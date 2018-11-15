#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
from enum import Enum
from pl0lexer import PL0Lexer,Morphem,MorphemCode,MorphemSymbol

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

class PL0Parser():

    def __init__(self, sourceFile):
        
        # Init Syntax rules

        programEdges = [
            Edge(EdgeType.SUBGRAPH_, NonTerminal.BLOCK, None, 1,0, NonTerminal.PROGRAM),
            Edge(EdgeType.SYMBOL___, '.', None, 2,0, NonTerminal.PROGRAM),

            # End
            Edge(EdgeType.GRAPH_END, 0, None, 0,0, NonTerminal.PROGRAM)
        ]

        blockEdges = [
            # Constant Declaration
            Edge(EdgeType.SYMBOL___, MorphemSymbol.CONST,None, 1,6, NonTerminal.BLOCK), # 0
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, None,2,0, NonTerminal.BLOCK),   # 1
            Edge(EdgeType.SYMBOL___, '=', None, 3,0, NonTerminal.BLOCK),                # 2
            Edge(EdgeType.MORPHEM__, MorphemCode.NUMBER,None,4,5, NonTerminal.BLOCK),   # 3
            Edge(EdgeType.SYMBOL___, ',',None, 1,0, NonTerminal.BLOCK),                 # 4
            Edge(EdgeType.SYMBOL___, ';', None, 6,10, NonTerminal.BLOCK),               # 5

            # Variable Declaration
            Edge(EdgeType.SYMBOL___, MorphemSymbol.VAR, None, 7,10, NonTerminal.BLOCK), # 6
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, None, 8,9, NonTerminal.BLOCK),  # 7
            Edge(EdgeType.SYMBOL___, ',', None, 7,0, NonTerminal.BLOCK),                # 8
            Edge(EdgeType.SYMBOL___, ';', None, 10,15, NonTerminal.BLOCK),              # 9

            # Procedure Declaration
            Edge(EdgeType.SYMBOL___, MorphemSymbol.PROCEDURE, None, 11,15, NonTerminal.BLOCK), # 10
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, None, 12,0, NonTerminal.BLOCK),        # 11
            Edge(EdgeType.SYMBOL___, ';', None, 13,0, NonTerminal.BLOCK),                      # 12
            Edge(EdgeType.SUBGRAPH_, NonTerminal.BLOCK, None, 14,0, NonTerminal.BLOCK),        # 13
            Edge(EdgeType.SYMBOL___, ';', None, 15,0, NonTerminal.BLOCK),                      # 14

            # Nil Edge (needed for emitter function)
            Edge(EdgeType.NIL______, None, None, 16,0, NonTerminal.BLOCK),             # 15

            # Statement Declaration
            Edge(EdgeType.SUBGRAPH_, NonTerminal.STATEMENT, None, 17,0, NonTerminal.BLOCK),  # 16

            # End
            Edge(EdgeType.GRAPH_END, None, None, 0,0, NonTerminal.BLOCK)                     # 17
        ]

    
        expressionEdges = [
            Edge(EdgeType.SYMBOL___,'-', None, 2,1),               # 0
            Edge(EdgeType.NIL______,None, None, 2,0),              # 1
            Edge(EdgeType.SUBGRAPH_, NonTerminal.TERM, None, 3,0), # 2
            Edge(EdgeType.SYMBOL___, '+', None, 4,5),              # 3
            Edge(EdgeType.SUBGRAPH_, NonTerminal.TERM, None, 3,0), # 4 
            Edge(EdgeType.SYMBOL___,'-', None, 6,7),               # 5
            Edge(EdgeType.SUBGRAPH_, NonTerminal.TERM, None, 3,0), # 6
            
            # End
            Edge(EdgeType.GRAPH_END, None, None, 0,0)              # 7
        ]

        termEdges = [
            Edge(EdgeType.SUBGRAPH_, NonTerminal.FACTOR, None, 1,0), # 0
            Edge(EdgeType.SYMBOL___, '+', None, 2,3),                # 1
            Edge(EdgeType.SUBGRAPH_, NonTerminal.FACTOR, None, 1,0), # 2 
            Edge(EdgeType.SYMBOL___,'-', None, 4,5),                 # 3
            Edge(EdgeType.SUBGRAPH_, NonTerminal.FACTOR, None, 1,0), # 4

            # End
            Edge(EdgeType.GRAPH_END, None, None, 0,0)                # 5
        ]

        statementEdges = [
            # Assignment
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, None, 1,3),       #  0
            Edge(EdgeType.SYMBOL___, MorphemSymbol.ASSIGN, None, 2,0),    #  1
            Edge(EdgeType.SUBGRAPH_, NonTerminal.EXPRESSION, None, 21,0), #  2

            # Condition
            Edge(EdgeType.SYMBOL___,MorphemSymbol.IF, None, 4,7),         #  3
            Edge(EdgeType.SUBGRAPH_, NonTerminal.CONDITION, None, 5,0),   #  4
            Edge(EdgeType.SYMBOL___, MorphemSymbol.THEN,None, 6,0),        #  5
            Edge(EdgeType.SUBGRAPH_, NonTerminal.STATEMENT,None, 21,0),    #  6

            # While Loop
            Edge(EdgeType.SYMBOL___, MorphemSymbol.WHILE, None, 8, 11),   #  7
            Edge(EdgeType.SUBGRAPH_, NonTerminal.CONDITION, None, 9,0),         #  8
            Edge(EdgeType.SYMBOL___, MorphemSymbol.DO,None, 10,0),        #  9
            Edge(EdgeType.SUBGRAPH_, NonTerminal.STATEMENT,None, 21,0),        # 10

            # BEGIN - END
            Edge(EdgeType.SYMBOL___, MorphemSymbol.BEGIN, None, 12,15),   # 11
            Edge(EdgeType.SUBGRAPH_, NonTerminal.STATEMENT, None,3, 0),    # 12
            Edge(EdgeType.SYMBOL___, ';', None, 12, 14),                  # 13
            Edge(EdgeType.SYMBOL___, MorphemSymbol.END,None, 21,0),       # 14

            # CALL
            Edge(EdgeType.SYMBOL___, MorphemSymbol.CALL,None, 16,17),     # 15
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, None, 21,0),      # 16

            # Input
            Edge(EdgeType.SYMBOL___, '?', None, 18, 19),                  # 17
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, None, 21, 0),     # 18

            # Output
            # Alternative Edge 21 or 0? This depends on the used
            # grammar
            Edge(EdgeType.SYMBOL___, '!', None, 20, 21),                  # 19
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, None, 21, 0),     # 20

            # End
            Edge(EdgeType.GRAPH_END, None, None, 0,0)                     # 21

        ]

        factorEdges = [
            Edge(EdgeType.MORPHEM__, MorphemCode.NUMBER, None, 5,1),     # 0
            Edge(EdgeType.SYMBOL___, '(', None, 2,4),                    # 1
            Edge(EdgeType.SUBGRAPH_, NonTerminal.EXPRESSION, None, 3,0), # 2
            Edge(EdgeType.SYMBOL___, ')', None, 5,0),                    # 3
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT,None, 5,0),       # 4

            # End
            Edge(EdgeType.GRAPH_END, None, None, 0,0)                    # 5
        ]

        conditionEdges = [
            # ODD
            Edge(EdgeType.SYMBOL___, MorphemSymbol.ODD, None, 1, 2),           #  0
            Edge(EdgeType.SUBGRAPH_, NonTerminal.EXPRESSION, None, 10, 0),     #  1

            # Comparisson
            Edge(EdgeType.SUBGRAPH_,NonTerminal.EXPRESSION, None, 3,0),        #  2
            Edge(EdgeType.SYMBOL___, '=', None, 9, 4),                         #  3
            Edge(EdgeType.SYMBOL___, '#', None, 9, 5),                         #  4
            Edge(EdgeType.SYMBOL___, '>', None, 9, 6),                         #  5
            Edge(EdgeType.SYMBOL___, '<', None, 9, 7),                         #  6
            Edge(EdgeType.SYMBOL___, MorphemSymbol.LESSER_EQUAL, None, 9, 8),  #  7
            Edge(EdgeType.SYMBOL___, MorphemSymbol.GREATER_EQUAL, None, 9, 0), #  8
            Edge(EdgeType.SUBGRAPH_, NonTerminal.EXPRESSION, None, 10,0),      #  9

            # End
            Edge(EdgeType.GRAPH_END, None, None, 0,0)                          # 10
        ]

        self.edges = [
            programEdges,    # 0
            blockEdges,      # 1
            expressionEdges, # 2
            termEdges ,      # 3
            statementEdges,  # 4
            factorEdges,     # 5
            conditionEdges   # 6
        ]


        # Init Lexer
        self.sourceFile = sourceFile
        self.lexer = PL0Lexer(self.sourceFile)

    def parse(self, edge=Edge(EdgeType.SUBGRAPH_, NonTerminal.PROGRAM,None, 0,0,, NonTerminal.PROGRAM)):
        
        success = False

        if(self.lexer.morphem.code == MorphemCode.EMPTY):
            self.lexer.lex()

        while(True):

            # Check Edge type 
            if(edge.type == EdgeType.SYMBOL___):
                pass
            elif(edge.type == EdgeType.MORPHEM__):
                pass
            elif(edge.type == EdgeType.SUBGRAPH_):
                pass
            elif(edge.type == EdgeType.GRAPH_END):
                return True
            elif(edge.type == EdgeType.NIL______):
                success = True

            # Call Emitter
            if success and edge.f:
                success = edge.f()

            # Check alternatives if evaluation of edge type 
            # wasn't successful

            if not success:
                if edge.alternative != 0:
                    edge = 
            else: 
                # Accept morphem
                pass


if __name__ == "__main__":
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

    parser = PL0Parser(sourceFile)

    if not parser.parse():
        print("[!] Parser failed")
    else:
        print("[i] done ")