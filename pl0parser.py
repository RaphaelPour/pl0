#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   file:           pl0parser.py
#   description:    PL/0 Parser implementing the PL/0 grammar
#   date:           24.01.2018
#   license:        GPL v3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
#
import sys
import os
from enum import Enum
import pprint
import logging
import xmlwriter
from pl0lexer import PL0Lexer, Morphem, MorphemCode, Symbol
from pl0namelist import NLIdent, NLProc, NLConst, NLVar, PL0NameList
from pl0codegen import PL0CodeGen,VMCode

class NonTerminal(Enum):
    PROGRAM = 0
    BLOCK = 1
    EXPRESSION = 2
    TERM = 3
    STATEMENT = 4
    FACTOR = 5
    CONDITION = 6
    CONSTANT_LIST = 7
    CONSTANT_DECLARATION = 8
    VARIABLE_LIST = 9
    VARIABLE_DECLARATION = 10
    PROCEDURE_DECLARATION = 11
    ASSIGNMENT_STATEMENT = 12
    CONDITIONAL_STATEMENT = 13
    LOOP_STATEMENT = 14
    COMPOUND_STATEMENT = 15
    PROCEDURE_CALL = 16
    INPUT_STATEMENT = 17
    OUTPUT_STATEMENT = 18

    # Compiler Extension
    FOR_STATEMENT = 19
    PARAMETER_LIST_CALL = 20
    PARAMETER_LIST_DECLARATION = 21
    ARRAY_INDEX = 22


class EdgeType(Enum):
    NIL______ = 0
    SYMBOL___ = 1
    MORPHEM__ = 2
    SUBGRAPH_ = 4
    GRAPH_END = 8


class Edge():
    def __init__(self, _type, value, emitter, nextEdge, alternativeEdge, nonterminal):

        # Also known as Bogen Description
        # Use _type to avoid python-keyword-clash
        self.type = _type

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
        result = "({:2d},{:2d}) {}".format(
            self.next, self.alternative, str(self.type))

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

    def __init__(self, inputFilename, outputFilenname):

        # Short identifier for the edge functions

        # Program
        PR1 = self.programmEnd

        # Block
        BL1 = self.blockCheckConstIdent
        BL2 = self.blockCreateConst
        BL3 = self.blockCreateVar
        BL4 = self.blockCreateProc
        BL5 = self.blockEndProcedure
        BL6 = self.blockInitCodeGen

        # Statement
        ST1 = self.statementAssignmentLeftSide
        ST2 = self.statementAssignmentRightSide
        ST3 = self.statementIfCondition
        ST4 = self.statementThenStatement
        ST5 = self.statementWhileCondition
        ST6 = self.statementWhileAfterCondition
        ST7 = self.statementWhileEnd
        #ST8 = self.statementCallBeforeParamsProc # Replaced with PL1/PL2
        ST9 = self.statementGetVal
        ST10 = self.statementPutVal
        ST11 = self.statementPutStr
        ST12 = self.statementElseKeyword
        ST13 = self.statementElseStatement

        # Condition
        CO1 = self.conditionOdd
        CO2 = self.conditionEQ
        CO3 = self.conditionNE
        CO4 = self.conditionLT
        CO5 = self.conditionLE
        CO6 = self.conditionGT
        CO7 = self.conditionGE
        CO8 = self.conditionReleaseCommand

        # Expression
        EX1 = self.expressionNegSign
        EX2 = self.expressionAdd
        EX3 = self.expressionSub

        TE1 = self.termMul
        TE2 = self.termDiv

        # Factor
        FA1 = self.factorPushNumber
        FA2 = self.factorPushIdent

        # Language Extension
        # For loop
        FOR1 = self.forBeforeCondition
        FOR2 = self.forBeforeIncrement
        FOR3 = self.forAfterIncrement
        FOR4 = self.forAfterStatement

        # Parameter list
        
        PL1 = self.statementCallBeforeParamsProc
        PL2 = self.statementCallAfterParamsProc

        PD1 = self.procedureParameter
        PD2 = self.procedureEndParameterList

        # Array
        ARR0 = self.arrayPushAddr
        AR1 = self.arraySetIndex
        AR2 = self.arrayCrate
        AR3 = self.arrayAccess
        AR4 = self.arraySwap
        FA3 = self.factorGetIdent

        # Init Syntax rules

        # Short identifier for edge definition
        PROG = NonTerminal.PROGRAM
        BLCK = NonTerminal.BLOCK
        EXPR = NonTerminal.EXPRESSION
        TERM = NonTerminal.TERM
        STAT = NonTerminal.STATEMENT
        FACT = NonTerminal.FACTOR
        COND = NonTerminal.CONDITION
        CLST = NonTerminal.CONSTANT_LIST
        CNST = NonTerminal.CONSTANT_DECLARATION
        VLST = NonTerminal.VARIABLE_LIST
        VARD = NonTerminal.VARIABLE_DECLARATION
        PROC = NonTerminal.PROCEDURE_DECLARATION
        ASSS = NonTerminal.ASSIGNMENT_STATEMENT
        CNDS = NonTerminal.CONDITIONAL_STATEMENT
        LOOP = NonTerminal.LOOP_STATEMENT
        COMP = NonTerminal.COMPOUND_STATEMENT
        PRCC = NonTerminal.PROCEDURE_CALL
        INST = NonTerminal.INPUT_STATEMENT
        OUTS = NonTerminal.OUTPUT_STATEMENT

        # Language Extension
        FORS = NonTerminal.FOR_STATEMENT
        PLC = NonTerminal.PARAMETER_LIST_CALL
        PLD = NonTerminal.PARAMETER_LIST_DECLARATION
        ARR = NonTerminal.ARRAY_INDEX

        programEdges = [
            Edge(EdgeType.SUBGRAPH_, BLCK, None, 1, 0, PROG),  # 0
            Edge(EdgeType.SYMBOL___, '.', PR1, 2, 0, PROG),    # 1

            # End
            Edge(EdgeType.GRAPH_END, 0, None, 0, 0, PROG)      # 2
        ]

        constListEdges = [
            Edge(EdgeType.SYMBOL___, Symbol.CONST, None, 1, 0, CLST),  # 0
            Edge(EdgeType.SUBGRAPH_, CNST, None, 2, 0, CLST),          # 1
            Edge(EdgeType.SYMBOL___, ',', None, 1, 3, CLST),           # 2
            Edge(EdgeType.SYMBOL___, ';', None, 4, 0, CLST),           # 3

            # End
            Edge(EdgeType.GRAPH_END, 0, None, 0, 0, CLST)              # 4
        ]

        constDeclarationEdges = [
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, BL1, 1, 0, CNST),  # 0
            Edge(EdgeType.SYMBOL___, '=', None, 2, 0, CNST),                # 1
            Edge(EdgeType.MORPHEM__, MorphemCode.NUMBER, BL2, 3, 0, CNST), # 2

            # End
            Edge(EdgeType.GRAPH_END, 0, None, 0, 0, CNST)                  # 3
        ]

        varListEdges = [
            Edge(EdgeType.SYMBOL___, Symbol.VAR, None, 1, 0, VLST),   # 0
            Edge(EdgeType.SUBGRAPH_, VARD, None, 2, 0, VLST),         # 1
            Edge(EdgeType.SYMBOL___, ',', None, 1, 3, VLST),          # 2
            Edge(EdgeType.SYMBOL___, ';', None, 4, 0, VLST),          # 3

            # End
            Edge(EdgeType.GRAPH_END, 0, None, 0, 0, VLST)             # 4
        ]

        varDeclarationEdges = [
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, BL3, 1, 0, VARD),  # 0

            # Array
            Edge(EdgeType.SYMBOL___,'[',None, 2,4, VARD),                  # 1
            Edge(EdgeType.MORPHEM__,MorphemCode.NUMBER,AR1, 3,0, VARD),    # 2
            Edge(EdgeType.SYMBOL___,']',AR2, 4,0, VARD),                   # 3

            # End
            Edge(EdgeType.GRAPH_END, 0, None, 0, 0, VARD)                  # 4
        ]


        arrayIndexEdges = [
            Edge(EdgeType.SYMBOL___,'[',ARR0, 1,0, ARR),        # 0
            Edge(EdgeType.SUBGRAPH_,EXPR,None, 2,0, ARR),       # 1
            Edge(EdgeType.SYMBOL___,']',AR3, 3,0, ARR),        # 2

            # End
            Edge(EdgeType.GRAPH_END,0, None, 0,0,ARR)           # 3
        ]

        procDeclatationEdges = [
            Edge(EdgeType.SYMBOL___, Symbol.PROCEDURE, None, 1, 0, PROC),  # 0
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, BL4, 2, 0, PROC),  # 1

            Edge(EdgeType.SYMBOL___,'(', None, 3,5,PROC),                  # 2
            Edge(EdgeType.SUBGRAPH_, PLD, None, 4,4, PROC),                # 3
            Edge(EdgeType.SYMBOL___,')', None, 5,0,PROC),                  # 4

            Edge(EdgeType.SYMBOL___, ';', PD2, 6, 0, PROC),                # 5
            Edge(EdgeType.SUBGRAPH_, BLCK, None, 7, 0, PROC),              # 6
            Edge(EdgeType.SYMBOL___, ';', None, 8, 0, PROC),               # 7
            Edge(EdgeType.GRAPH_END, 0, None, 0, 0, PROC)                  # 8
        ]
        

        procedureCallEdges = [
            Edge(EdgeType.SYMBOL___, Symbol.CALL, None, 1, 0, PRCC),            # 0
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, PL1, 2, 0, PRCC),       # 1

            Edge(EdgeType.SYMBOL___,'(', None, 3,5,PRCC),                       # 2
            Edge(EdgeType.SUBGRAPH_, PLC, None, 4,4, PRCC),                     # 3
            Edge(EdgeType.SYMBOL___,')', None, 5,0,PRCC),                       # 4
            Edge(EdgeType.NIL______,0, PL2,6,0,PRCC),                           # 5

            Edge(EdgeType.GRAPH_END, 0, None, 0, 0, PRCC)                        # 6
        ]

        parameterListCallEdges = [
            Edge(EdgeType.SUBGRAPH_, EXPR, None, 1,0,PLC),      # 0
            Edge(EdgeType.SYMBOL___, ',', None, 0,2, PLC),      # 1

            Edge(EdgeType.GRAPH_END, 0, None, 0,0, PLC)         # 2
        ]

        parameterListDeclarationEdges = [
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, PD1, 1,0,PLD),      # 0
            Edge(EdgeType.SYMBOL___, ',', None, 0,2, PLD),                   # 1

            Edge(EdgeType.GRAPH_END, 0, None, 0,0, PLD)                      # 2
        ]

        assignmentEdges = [
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT,ST1, 1, 0, ASSS),        # 0
            
            Edge(EdgeType.SYMBOL___,'[',None, 2,4, ASSS),                        # 1
            Edge(EdgeType.SUBGRAPH_,EXPR,None, 3,0, ASSS),                       # 2
            Edge(EdgeType.SYMBOL___,']',AR3, 4,0, ASSS),                         # 3
            
            Edge(EdgeType.SYMBOL___, Symbol.ASSIGN, None, 5, 0, ASSS),          # 4
            Edge(EdgeType.SUBGRAPH_, NonTerminal.EXPRESSION, ST2, 6, 0, ASSS),  # 5
            Edge(EdgeType.GRAPH_END, 0, None, 0, 0, ASSS)                       # 6
        ]

        conditionalEdges = [
            Edge(EdgeType.SYMBOL___, Symbol.IF, None, 1, 0, CNDS),             # 0
            Edge(EdgeType.SUBGRAPH_, NonTerminal.CONDITION, ST3, 2, 0, CNDS),  # 1
            Edge(EdgeType.SYMBOL___, Symbol.THEN, None, 3, 0, CNDS),           # 2
            Edge(EdgeType.SUBGRAPH_, NonTerminal.STATEMENT, None, 5, 0, CNDS), # 3
            Edge(EdgeType.NIL______, None, ST4, 7,0, CNDS),                    # 4 
            
            # ELSE
            Edge(EdgeType.SYMBOL___,Symbol.ELSE,ST12, 6,4, CNDS),              # 5
            Edge(EdgeType.SUBGRAPH_,NonTerminal.STATEMENT, ST13, 7,0,CNDS),    # 6

            Edge(EdgeType.GRAPH_END, 0, None, 0, 0, CNDS)                      # 7
        ]

        loopEdges = [
            Edge(EdgeType.SYMBOL___, Symbol.WHILE, ST5, 1, 0, LOOP),           # 0
            Edge(EdgeType.SUBGRAPH_, NonTerminal.CONDITION, ST6, 2, 0, LOOP),  # 1
            Edge(EdgeType.SYMBOL___, Symbol.DO,  None, 3, 0, LOOP),            # 2
            Edge(EdgeType.SUBGRAPH_, NonTerminal.STATEMENT, ST7, 4, 0, LOOP),  # 3
            Edge(EdgeType.GRAPH_END, 0, None, 0, 0, LOOP)                      # 5
        ]

        compoundEdges = [
            Edge(EdgeType.SYMBOL___, Symbol.BEGIN, None, 1, 0, COMP),          # 0
            Edge(EdgeType.SUBGRAPH_, NonTerminal.STATEMENT, None, 2, 0, COMP), # 1
            Edge(EdgeType.SYMBOL___, ";", None, 1, 3, COMP),                   # 2
            Edge(EdgeType.SYMBOL___, Symbol.END, None, 4, 0, COMP),            # 3
            Edge(EdgeType.GRAPH_END, 0, None, 0, 0, COMP)                      # 4
        ]
        inputEdges = [
            Edge(EdgeType.SYMBOL___, "?", None, 1, 0, INST),               # 0
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, ST9, 2, 0, INST), # 1
            Edge(EdgeType.GRAPH_END, 0, None, 0, 0, INST)                  # 2
        ]

        outputEdges = [
            Edge(EdgeType.SYMBOL___, "!", None, 1, 0, OUTS),                     # 0
            Edge(EdgeType.MORPHEM__, MorphemCode.STRING, ST11, 3,2, OUTS),       # 1
            Edge(EdgeType.SUBGRAPH_, NonTerminal.EXPRESSION, ST10, 3, 0, OUTS),  # 2
            Edge(EdgeType.GRAPH_END, 0, None, 0, 0, OUTS)                        # 3
        ]

        blockEdges = [
            # Constant Declaration
            Edge(EdgeType.SUBGRAPH_, CLST, None, 1, 1, BLCK),  # 0

            # Variable Declaration
            Edge(EdgeType.SUBGRAPH_, VLST, None, 2, 2, BLCK),  # 1

            # Procedure Declaration
            Edge(EdgeType.SUBGRAPH_, PROC, None, 2, 3, BLCK),   # 2

            # Nil Edge (needed for emitter function)
            Edge(EdgeType.NIL______, None, BL6, 4, 0, BLCK),   # 3

            # Statement Declaration
            Edge(EdgeType.SUBGRAPH_, STAT, BL5, 5, 0, BLCK),   # 4

            # End
            Edge(EdgeType.GRAPH_END, None, None, 0, 0, BLCK)   # 5
        ]

        expressionEdges = [
            # Detect negative sign
            Edge(EdgeType.SYMBOL___, '-', None, 1, 2, EXPR),  # 0
            Edge(EdgeType.SUBGRAPH_, TERM, EX1, 3, 0, EXPR),  # 1
            
            # No sign detected
            Edge(EdgeType.SUBGRAPH_, TERM, None, 3,0, EXPR),  # 2
            
            # Detect Add Operation
            Edge(EdgeType.SYMBOL___, '+', None, 4, 5, EXPR),  # 3
            Edge(EdgeType.SUBGRAPH_, TERM, EX2, 3, 0, EXPR),  # 4

            # Detect Sub Operation
            Edge(EdgeType.SYMBOL___, '-', None, 6, 7, EXPR),  # 5
            Edge(EdgeType.SUBGRAPH_, TERM, EX3, 3, 0, EXPR),  # 6

            Edge(EdgeType.GRAPH_END, None, None, 0, 0, EXPR)  # 7  
        ]

        statementEdges = [
            # A := b
            Edge(EdgeType.SUBGRAPH_, NonTerminal.ASSIGNMENT_STATEMENT, None, 8, 1, STAT),    # 0

            # If-Else
            Edge(EdgeType.SUBGRAPH_, NonTerminal.CONDITIONAL_STATEMENT, None, 8, 2, STAT),   # 1

            # While-Loop
            Edge(EdgeType.SUBGRAPH_, NonTerminal.LOOP_STATEMENT, None, 8, 3, STAT),          # 2

            # BEGIN, END
            Edge(EdgeType.SUBGRAPH_, NonTerminal.COMPOUND_STATEMENT, None, 8, 4,  STAT),     # 3

            # Call procedure
            Edge(EdgeType.SUBGRAPH_, NonTerminal.PROCEDURE_CALL, None,  8, 5, STAT),         # 4

            # Get value
            Edge(EdgeType.SUBGRAPH_, NonTerminal.INPUT_STATEMENT, None, 8, 6, STAT),         # 5

            # Print value
            Edge(EdgeType.SUBGRAPH_, NonTerminal.OUTPUT_STATEMENT, None, 8, 7, STAT),        # 6

            # For-Loop
            Edge(EdgeType.SUBGRAPH_,NonTerminal.FOR_STATEMENT,None,8,0,STAT),                # 7 

            # End
            Edge(EdgeType.GRAPH_END, 0, None, 0, 0, STAT)                                    # 8
        ]

        termEdges = [
            Edge(EdgeType.SUBGRAPH_, FACT, None, 1, 0, TERM), # 0
            Edge(EdgeType.SYMBOL___, '*', None, 2, 3, TERM),  # 1
            Edge(EdgeType.SUBGRAPH_, FACT, TE1, 1, 0, TERM),  # 2
            Edge(EdgeType.SYMBOL___, '/', None, 4, 5, TERM),  # 3
            Edge(EdgeType.SUBGRAPH_, FACT, TE2, 1, 0, TERM),  # 4

            # End
            Edge(EdgeType.GRAPH_END, None, None, 0, 0, TERM)  # 5
        ]

        factorEdges = [

            # 0-9
            Edge(EdgeType.MORPHEM__, MorphemCode.NUMBER, FA1, 7, 1, FACT),      # 0

            # ( EXPRESSION )
            Edge(EdgeType.SYMBOL___, '(', None, 2, 4, FACT),                    # 1
            Edge(EdgeType.SUBGRAPH_, EXPR, None, 3, 0, FACT),                   # 2
            Edge(EdgeType.SYMBOL___, ')', None, 7, 0, FACT),                    # 3

            # Variable or array
            Edge(EdgeType.MORPHEM__, MorphemCode.IDENT, FA3, 5, 0, FACT),       # 4
            Edge(EdgeType.SUBGRAPH_, ARR, AR4, 7,6, FACT),                      # 5

            Edge(EdgeType.NIL______,None, FA2,7,0,FACT),                        # 6
            # End
            Edge(EdgeType.GRAPH_END, None, None, 0, 0, FACT)                    # 7
        ]

        conditionEdges = [
            # ODD
            Edge(EdgeType.SYMBOL___, Symbol.ODD, None, 1, 2, COND),          #  0
            Edge(EdgeType.SUBGRAPH_, EXPR, CO1, 10, 0, COND),                #  1

            # Comparisson
            Edge(EdgeType.SUBGRAPH_, EXPR, None, 3, 0, COND),                #  2
            Edge(EdgeType.SYMBOL___, '=', CO2, 9, 4, COND),                  #  3
            Edge(EdgeType.SYMBOL___, '#', CO3, 9, 5, COND),                  #  4
            Edge(EdgeType.SYMBOL___, '>', CO6, 9, 6, COND),                  #  5
            Edge(EdgeType.SYMBOL___, '<', CO4, 9, 7, COND),                  #  6
            Edge(EdgeType.SYMBOL___, Symbol.LESSER_EQUAL, CO5, 9, 8, COND),  #  7
            Edge(EdgeType.SYMBOL___, Symbol.GREATER_EQUAL, CO7, 9, 0, COND), #  8
            Edge(EdgeType.SUBGRAPH_, EXPR, CO8, 10, 0, COND),                #  9

            # End
            Edge(EdgeType.GRAPH_END, None, None, 0, 0, COND)                 # 10
        ]


        forEdges = [
            Edge(EdgeType.SYMBOL___, Symbol.FOR, None, 1,0,FORS),   # 0
            Edge(EdgeType.SYMBOL___, '(', None, 2,0,FORS),          # 1
            Edge(EdgeType.SUBGRAPH_,ASSS,None, 3,0,FORS),           # 2
            Edge(EdgeType.SYMBOL___,';',FOR1, 4,0,FORS),            # 3
            Edge(EdgeType.SUBGRAPH_,COND,FOR2,5,0,FORS),            # 4
            Edge(EdgeType.SYMBOL___,';',None,6,0,FORS),             # 5
            Edge(EdgeType.SUBGRAPH_,ASSS,FOR3,7,0,FORS),            # 6
            Edge(EdgeType.SYMBOL___,')', None, 8,0,FORS),           # 7
            Edge(EdgeType.SUBGRAPH_,STAT,FOR4, 9,0,FORS),           # 8
            Edge(EdgeType.GRAPH_END,None,None,0,0,FORS)             # 9
        ]

        self.edges = {
            PROG: programEdges,                  #  0
            BLCK: blockEdges,                    #  1
            EXPR: expressionEdges,               #  2
            TERM: termEdges,                     #  3
            STAT: statementEdges,                #  4
            FACT: factorEdges,                   #  5
            COND: conditionEdges,                #  6
            CLST: constListEdges,                #  7
            CNST: constDeclarationEdges,         #  8
            VLST: varListEdges,                  #  9
            VARD: varDeclarationEdges,           # 10
            PROC: procDeclatationEdges,          # 11
            ASSS: assignmentEdges,               # 12
            CNDS: conditionalEdges,              # 13
            LOOP: loopEdges,                     # 14
            COMP: compoundEdges,                 # 15
            PRCC: procedureCallEdges,            # 16
            INST: inputEdges,                    # 17
            OUTS: outputEdges,                   # 18

            # Language Extension
            FORS: forEdges,                      # 19
            PLC : parameterListCallEdges,        # 20
            PLD : parameterListDeclarationEdges, # 21
            ARR : arrayIndexEdges                # 22
        }

        # Init Lexer
        self.inputFilename = inputFilename
        self.lexer = PL0Lexer(self.inputFilename)

        # Init NameList
        self.nameList = PL0NameList()
        self.currentIdent = None
        self.currentIndex = 0

        # Init Code Generator
        self.outputFilename = outputFilenname
        self.codeGen = PL0CodeGen(self.outputFilename)

    def parse(self, edge=None, path=[]):

        morphemProcessed = False
        localPath = []

        success = False

        # Initialize Parser if we are called for the first time
        if self.lexer.morphem.code == MorphemCode.EMPTY:
            self.lexer.lex()

        if not edge:
            startEdge = self.edges[NonTerminal.PROGRAM][0]
            startList = [{
                'value': str(startEdge.nonterminal.name),
                'type': EdgeType.SUBGRAPH_,
                'pos': (self.lexer.morphem.lines, self.lexer.morphem.cols),
                'sub': []
            }]
            result = self.parse(startEdge, startList)
            if result:
                startList[0]['sub'] = result
                return startList
            else:
                return False

        while True:

            # Check Edge type

            # Symbol detected -> Syntactically right Symbol?
            if edge.type == EdgeType.SYMBOL___:
                success = self.lexer.morphem.value == edge.value
                if success:
                    localPath.append({
                        'value': self.lexer.morphem.value,
                        'type': edge.type,
                        'pos': (self.lexer.morphem.lines, self.lexer.morphem.cols)})

            # Morphem detected -> Syntacticaly right morphem?
            elif edge.type == EdgeType.MORPHEM__:
                success = self.lexer.morphem.code == edge.value
                if success:
                    localPath.append({
                        'value': self.lexer.morphem.value,
                        'type': edge.type,
                        'pos': (self.lexer.morphem.lines, self.lexer.morphem.cols)
                    })

            # Subgraph detected -> Go deeper
            elif edge.type == EdgeType.SUBGRAPH_:
                nextEdge = self.edges[edge.value][0]
                localPath.append({
                    'value': nextEdge.nonterminal.name,
                    'type': EdgeType.SUBGRAPH_,
                    'pos': (self.lexer.morphem.lines, self.lexer.morphem.cols),
                    'sub': []
                })

                result = self.parse(nextEdge, path + localPath)
                if result:
                    success = True
                    
                    # Combines the local parse tree with the deeper one
                    # This allows to ignore the delivered path argument
                    localPath[-1]['sub'] = result
                else:
                    success = False

                    # Delete the subgraph from the local Path because it wasn't
                    # successful
                    localPath.pop()



            # End detected -> Return the current parse-tree
            elif edge.type == EdgeType.GRAPH_END:
                return localPath
            elif edge.type == EdgeType.NIL______:
                success = True

            # Call Emitter
            if success and edge.f:
                success = edge.f()
                if success is None:
                    logging.error("[Parser] Missing valid return value of edge function {}(). It returned with None".format(edge.f.__name__))

            # Check alternatives if evaluation of edge type
            # wasn't successful

            if not success:
                if edge.alternative != 0:
                    edge = self.edges[edge.nonterminal][edge.alternative]
                elif morphemProcessed:
                    logging.error("[Parser] Syntax Error near {}:{}: {}".format(
                        self.lexer.morphem.lines,
                        self.lexer.morphem.cols,
                        self.lexer.morphem.value))

                    errorEdge = {
                        'value': "ERROR",
                        'type': EdgeType.NIL______,
                        'pos': (self.lexer.morphem.lines, self.lexer.morphem.cols)
                    }
                    localPath.append(errorEdge)
                    x = xmlwriter.XMLWriter("error.xml")
                    x.writeAll(localPath)
                    sys.exit(1)
                else:
                    # It's BACKTRACKIN' TIME

                    return False
            else:
                # Accept morphem
                if edge.type in [EdgeType.SYMBOL___, EdgeType.MORPHEM__]:
                    self.lexer.lex()
                edge = self.edges[edge.nonterminal][edge.next]
                morphemProcessed = True
        return localPath

    #
    # EDGE FUNCTIONS
    #

    # PROGRAM

    # Also known as Pr1
    def programmEnd(self):
        # Write the count of procedures at the very beginning
        self.codeGen.setTotalCountOfProcedures(len(self.nameList.procedures))

        # Append List of constants to the end of the file before
        # closing it
        self.codeGen.writeConstList(self.nameList.constantList)

        self.codeGen.closeOutputfile()

        return True
        
    # BLOCK
    
    # Also known as BL1
    def blockCheckConstIdent(self):
        # Get ident by current morphem
        constIdent = str(self.lexer.morphem.value)

        # Create Constant, print error if locally existing
        if self.nameList.isLocalIdentName(constIdent):
            logging.error("[Parser] Can't create Const-Ident: Ident {} already existing.".format(constIdent))

            # Error-Handling  
            return False

        self.currentIdent = constIdent
        return True

    # Also known as BL2
    def blockCreateConst(self):
        
        # Check if current ident is set in order to add a new
        # constant to the namelist
        if self.currentIdent is None:
            logging.error("[Parser] Ident must be set before setting the value")
            return False
        
        # Get the value from our current morphem
        value = int(self.lexer.morphem.value)

        # Add Constant to our namelist
        self.nameList.createConst(name=self.currentIdent,value=value)

        # Reset ident to None in order to avoid errors
        self.currentIdent = None

        return True
                
    # Also known as BL3
    def blockCreateVar(self):
        # Check if ident is already defined in local scope
        ident = str(self.lexer.morphem.value)

        # Create Constant, print error if locally existing
        if self.nameList.isLocalIdentName(ident):
            logging.error("[Parser] Can't create Var-Ident: Ident {} already existing.".format(ident))

            # Error-Handling  
            return False

        self.currentIdent = ident
        # Add Variable to our namelist
        self.nameList.createVar(name=ident)

        return True
        
    # Also known as BL4
    def blockCreateProc(self):
        # Check if ident is already defined in local scope
        ident = str(self.lexer.morphem.value)
        
        if self.nameList.isLocalIdentName(ident):
            logging.error("[Parser] Can't create Const-Ident: Ident {} already existing.".format(ident))

            # Error-Handling  
            return False

        self.nameList.createProc(ident)
        return True
    
    def procedureParameter(self):
        # Check if ident is already defined in local scope
        ident = str(self.lexer.morphem.value)

        # Create Constant, print error if locally existing
        if self.nameList.isLocalIdentName(ident):
            logging.error("[Parser] Can't create Procedure-Parameter-Ident: Ident {} already existing.".format(ident))

            # Error-Handling  
            return False

        # Add Variable to our namelist
        self.nameList.createProcedureParam(name=ident)

        return True

    def procedureEndParameterList(self):
        # Recalculate the relative addresses of the parameters
        # otherwise the first one gets the highest address and
        # is used as last parameter
        self.nameList.correctParameterList()

        return True

    # Also known as BL5
    def blockEndProcedure(self):

        # Pop all parameters 
        for _ in filter(lambda v: v.procedureParameter ,self.nameList.currentProcedure.variables):
            if not self.codeGen.writeCommand(VMCode.POP):
                return False


        # Write Return Statement (Doesn't need an address, cause Beck's VM can handle it by itself)
        if not self.codeGen.writeCommand(VMCode.RET_PROC):
            return False

        # Write length of the current procedure at the very
        # beginning
        if not self.codeGen.setProcedureLength():
            return False

        # End current Procedure and reset it to the parrent
        if not self.nameList.endProc():
            return False

        # Write current output buffer to file
        self.codeGen.flushBuffer()

        return True

    # Also known as BL6
    def blockInitCodeGen(self):

        # Initialize the code generator
        self.codeGen.flushBuffer()

        # Write EntryProc command to introduce a new procedure
        length = 0
        index = self.nameList.currentProcedure.index
        varMemorySize = self.nameList.currentProcedure.localAddressOffset
        
        args = [length, index, varMemorySize]

        return self.codeGen.writeCommand(VMCode.ENTRY_PROC,args)


    # STATEMENT

    # Also known as ST1
    def statementAssignmentLeftSide(self):
        
        # Use current morphem as ident
        identName = str(self.lexer.morphem.value)

        # Search globally for ident
        ident = self.nameList.searchIdentNameGlobal(identName)

        # if ident not found -> Semantic Error!
        if ident is None:
            logging.error("[Parser] Declaration error: Var {} is used in assignment but not declared.".format(identName))
            return False

        # Check if const or proc -> Semantic error!
        if isinstance(ident, NLProc):
            logging.error("[Parser] Type error: Excepted Variable but got Procedure {} instead".format(identName))
            return False

        if isinstance(ident, NLConst):
            logging.error("[Parser] Type error: Excepted Variable but got Constant {} instead".format(identName))
            return False

        # Check if main/local/global variable
        displacement = ident.addressOffset
        args = [displacement]
        if ident.parent == self.nameList.mainProc:
            # Main Variable
            if not self.codeGen.writeCommand(VMCode.PUSH_ADDRESS_VAR_MAIN,args):
                return False
        elif ident.parent == self.nameList.currentProcedure:
            # Local Scope Variable
            if not self.codeGen.writeCommand(VMCode.PUSH_ADDRESS_VAR_LOCAL,args):
                return False
        else:
            # Global scope Variable
            args.append(ident.parent.index)
            if not self.codeGen.writeCommand(VMCode.PUSH_ADDRESS_VAR_GLOBAL,args):
                return False

        return True

    # Also known as ST2
    def statementAssignmentRightSide(self):

        # Value and address are on the stack
        # and we store the value to the address
        return self.codeGen.writeCommand(VMCode.STORE_VAL)

    # Also known as ST3
    def statementIfCondition(self):
        self.codeGen.pushLabel()
        return self.codeGen.writeCommand(VMCode.JMP_NOT,[0])

    # Also known as ST4
    def statementThenStatement(self):
        label = self.codeGen.popLabel()

        # Add length of jump command (3 bytes) 
        label.distance -= 3
        return self.codeGen.correctJmp(label)


    def statementElseKeyword(self):
        jmpNotLabel = self.codeGen.popLabel()

        # For the current JMP Command
        self.codeGen.pushLabel()

        if not self.codeGen.writeCommand(VMCode.JMP,[0]):
            return False

        # Add length of jump command (3 bytes) 
        #jmpNotLabel.distance += 3
        return self.codeGen.correctJmp(jmpNotLabel)


    def statementElseStatement(self):
        
        jmpLabel = self.codeGen.popLabel()
        jmpLabel.distance -= 3
        return self.codeGen.correctJmp(jmpLabel)

    # Also known as ST5
    def statementWhileCondition(self):
        # Generate Label for the jump at the
        # end of the loop. The Label has to point
        # to the head
        self.codeGen.pushLabel()
        return True

    # Also known as ST6
    def statementWhileAfterCondition(self):
        # Generate Label to save the position of the jump
        # where we have to replace the address later
        self.codeGen.pushLabel()

        # Generate JumpNot which jumps to the first command
        # after the loop if the condition is false
        # Use 0 as placeholder for JumpNot
        return self.codeGen.writeCommand(VMCode.JMP_NOT,[0])

    def statementWhileEnd(self):
        # Add jump pointing to the condition of the current while loop
        jmpNotRelAddr = self.codeGen.popLabel()
        conditionRelAddr = self.codeGen.popLabel()

        # Add jump to the condition, add 3 bytes for the jump command itself
        args1 = [ -conditionRelAddr.distance -3]
        if not self.codeGen.writeCommand(VMCode.JMP, args1):
            return False

        # Correct address of the JmpNot of the While-Condition
        return self.codeGen.correctJmp(label=jmpNotRelAddr)

    # Also known as ST8
    def statementCallBeforeParamsProc(self):

        # Use current morphem as ident for procedure
        identName = str(self.lexer.morphem.value)

        # Search globally for ident
        ident = self.nameList.searchIdentNameGlobal(identName)

        # if ident not found -> Semantic Error!
        if ident is None:
            logging.error("[Parser] Declaration error: Procedure {} is used in call but not declared.".format(identName))
            return False
        
        # Check if ident is const or var -> Semantic error!
        if isinstance(ident, NLConst):
            logging.error("[Parser] Type error: Excepted Procedure but got Constant {} instead".format(identName))
            return False

        if isinstance(ident, NLVar):
            logging.error("[Parser] Type error: Excepted Procedure but got Variable {} instead".format(identName))
            return False

        # Write Call Command with proc index as first argument
        args = [ident.index]
        self.codeGen.pushDelayedCommand(VMCode.CALL,args)
        return True

    def statementCallAfterParamsProc(self):
        command, args = self.codeGen.popDelayedCommand()
        return self.codeGen.writeCommand(command, args)

    # Also known as ST9
    def statementGetVal(self):

        # Use current morphem as ident
        identName = str(self.lexer.morphem.value)

        # Search globally for ident
        ident = self.nameList.searchIdentNameGlobal(identName)

        # if ident not found -> Semantic Error!
        if ident is None:
            logging.error("[Parser] Declaration error: Ident {} is used in assignment but not declared.".format(identName))
            return False

        # Check if const or proc -> Semantic error!
        if isinstance(ident, NLProc):
            logging.error("[Parser] Type error: Excepted Var ident but got Procedure ident {}".format(identName))
            return False

        if isinstance(ident, NLConst):
            logging.error("[Parser] Type error: Excepted Var ident but got Const ident {}".format(identName))
            return False

        # Check if main/local/global variable
        displacement = ident.addressOffset
        args = [displacement]
        if ident.parent == self.nameList.mainProc:
            # Main Variable
            if not self.codeGen.writeCommand(VMCode.PUSH_ADDRESS_VAR_MAIN,args):
                return False
        elif ident.parent == self.nameList.currentProcedure:
            # Local Scope Variable
            if not self.codeGen.writeCommand(VMCode.PUSH_ADDRESS_VAR_LOCAL,args):
                return False
        else:
            # Global scope Variable
            args.append(ident.parent.index)
            if not self.codeGen.writeCommand(VMCode.PUSH_ADDRESS_VAR_GLOBAL,args):
                return False

        # Write user-input command
        return self.codeGen.writeCommand(VMCode.GET_VAL)

    # Also known as ST10
    def statementPutVal(self):
        return self.codeGen.writeCommand(VMCode.PUSH_VAL)

    # Also known as ST11
    def statementPutStr(self):
        value = str(self.lexer.morphem.value)
        return self.codeGen.putString(value)


    # Array

    def arrayPushAddr(self):
        # Search globally for ident
        ident = self.nameList.searchIdentNameGlobal(self.currentIdent)

        # if ident not found -> Semantic Error!
        if ident is None:
            logging.error("[Parser] Declaration error: Ident {} is used in assignment but not declared.".format(self.currentIdent))
            return False

        # Check if const or proc -> Semantic error!
        if isinstance(ident, NLProc):
            logging.error("[Parser] Type error: Excepted Var ident but got Procedure ident {}".format(self.currentIdent))
            return False

        if isinstance(ident, NLConst):
            logging.error("[Parser] Type error: Excepted Var ident but got Const ident {}".format(self.currentIdent))
            return False


        # Check if main/local/global variable
        displacement = ident.addressOffset
        args = [displacement]
        if ident.parent == self.nameList.mainProc:
            # Main Variable
            if not self.codeGen.writeCommand(VMCode.PUSH_ADDRESS_VAR_MAIN,args):
                return False
        elif ident.parent == self.nameList.currentProcedure:
            # Local Scope Variable
            if not self.codeGen.writeCommand(VMCode.PUSH_ADDRESS_VAR_LOCAL,args):
                return False
        else:
            # Global scope Variable
            args.append(ident.parent.index)
            if not self.codeGen.writeCommand(VMCode.PUSH_ADDRESS_VAR_GLOBAL,args):
                return False

        return True

    def arraySetIndex(self):

        # Get number from the last read morphem
        self.currentIndex = int(self.lexer.morphem.value)
        return True

    def arrayCrate(self):

        self.nameList.turnLastVarToArray(self.currentIndex)
        return True

    def arrayAccess(self):

        # Currently the Start address of the array and the index which should be accessed is on the stack
        # the index has to be multiplied by the size (always 4) and added to the start address
        
        #
        # Push size of a single array filed onto the stack
        #

        value = 4

        # Looking for const with the current value
        const = self.nameList.searchConstByValue(value)

        # if not found -> add it as anonym const
        if const is None:
            const = self.nameList.createConst(value)

        # put index of the constant onto the stack
        args = [const.index]
        if not self.codeGen.writeCommand(VMCode.PUSH_CONST,args):
            return False

        #
        # Push Multiplication command onto the stack for index*size
        #
        
        if not self.codeGen.writeCommand(VMCode.OP_MULT):
            return False

        #
        # Add the result to the start address of the array
        #
        if not self.codeGen.writeCommand(VMCode.OP_ADD):
            return False
        return True

    def arraySwap(self):

        # Swap addres with the value on the address
        if not self.codeGen.writeCommand(VMCode.SWAP):
            return False
        return True

    # CONDITION

    # Also known as CO1
    def conditionOdd(self):
        return self.codeGen.writeCommand(VMCode.ODD)

    # Also known as CO2
    def conditionEQ(self):
        self.codeGen.pushDelayedCommand(VMCode.CMP_EQ)
        return True

    # Also known as CO3
    def conditionNE(self):
        self.codeGen.pushDelayedCommand(VMCode.CMP_NE)
        return True

    # Also known as CO4
    def conditionLT(self):
        self.codeGen.pushDelayedCommand(VMCode.CMP_LT)
        return True

    # Also known as CO5
    def conditionLE(self):
        self.codeGen.pushDelayedCommand(VMCode.CMP_LE)
        return True

    # Also known as CO6
    def conditionGT(self):
        self.codeGen.pushDelayedCommand(VMCode.CMP_GT)
        return True

    # Also known as CO7
    def conditionGE(self):
        self.codeGen.pushDelayedCommand(VMCode.CMP_GE)
        return True


    # Also known as CO8
    def conditionReleaseCommand(self):
        command, args = self.codeGen.popDelayedCommand()

        return self.codeGen.writeCommand(command, args)

    # Procedure with parameter list
    def procedureParameterDeclaration(self):
        pass

    # EXPRESSION

    # Also known as EX1
    def expressionNegSign(self):
        return self.codeGen.writeCommand(VMCode.VZ_MINUS)

    # Also known as EX2
    def expressionAdd(self):
        return self.codeGen.writeCommand(VMCode.OP_ADD)
        
    # Also known as EX3
    def expressionSub(self):
        return self.codeGen.writeCommand(VMCode.OP_SUB)


    # TERM

    # Also known as TE1
    def termMul(self):
        return self.codeGen.writeCommand(VMCode.OP_MULT)

    # Also known as TE2
    def termDiv(self):
        return self.codeGen.writeCommand(VMCode.OP_DIV)

    # FACTOR

    def factorGetIdent(self):
        self.currentIdent = str(self.lexer.morphem.value)
        return True

    # Also known as FA1
    def factorPushNumber(self):
        # Get number from the last read morphem
        value = int(self.lexer.morphem.value)

        # Looking for const with the current value
        const = self.nameList.searchConstByValue(value)

        # if not found -> add it as anonym const
        if const is None:
            const = self.nameList.createConst(value)

        # put index of the constant onto the stack
        args = [const.index]
        return self.codeGen.writeCommand(VMCode.PUSH_CONST,args)
    
    # Also known as FA2
    def factorPushIdent(self):
        # Get ident from the last read morphem
        #identName = str(self.lexer.morphem.value)
        identName = self.currentIdent     

        # Search globally for ident
        ident = self.nameList.searchIdentNameGlobal(identName)

        # if ident not found -> Semantic Error!
        if ident is None:
            logging.error("[Parser] Declaration error: Ident {} is used but not declared.".format(identName))
            return False

        # Check if ident is a procedure
        # If it is one -> Semantic Error!
        if isinstance(ident, NLProc):
            logging.error("[Parser] Type error: Excepted Const/Var ident but got Procedure ident {}".format(identName))
            return False

        # If the ident is a const, it doesn't matter
        # if main/local/global and we can directly
        # push the index onto the stack
        if isinstance(ident, NLConst):
            args = [ident.index]
            self.codeGen.writeCommand(VMCode.PUSH_CONST,args)
            return True


        # Check if main/local/global variable
        displacement = ident.addressOffset
        args = [displacement]
        if ident.parent == self.nameList.mainProc:
            # Main Variable
            return self.codeGen.writeCommand(VMCode.PUSH_VALUE_VAR_MAIN,args)
        elif ident.parent == self.nameList.currentProcedure:
            # Local Scope Variable
            return self.codeGen.writeCommand(VMCode.PUSH_VALUE_VAR_LOCAL,args)
        else:
            # Global scope Variable
            args.append(ident.parent.index)
            return self.codeGen.writeCommand(VMCode.PUSH_VALUE_VAR_GLOBAL,args)


    # Language Extension
    # Also known as FOR1
    def forBeforeCondition(self):
        self.codeGen.pushLabel()
        return True
        
    # Also known as FOR2
    def  forBeforeIncrement(self):

        self.codeGen.pushLabel()
        if not self.codeGen.writeCommand(VMCode.JMP_NOT,[0]):
            return False

        self.codeGen.recordCode()
        return True

    # Also known as FOR3
    def  forAfterIncrement(self):
        self.codeGen.stopRecordingCode()
        
        return True

    # Also known as FOR4
    def  forAfterStatement(self):
        self.codeGen.popRecordedCode()
        
        # Add jump pointing to the condition of the current while loop
        jmpNotRelAddr = self.codeGen.popLabel()
        conditionRelAddr = self.codeGen.popLabel()

        # Add jump to the condition, add 3 bytes for the jump command itself
        args1 = [ -conditionRelAddr.distance -3]
        if not self.codeGen.writeCommand(VMCode.JMP, args1):
            return False

        # Correct address of the JmpNot of the While-Condition
        return self.codeGen.correctJmp(label=jmpNotRelAddr)
        

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    inputFilename = "../testfiles/tmin.pl0"
    outputFilename = "../testfiles/tmin.cl0"

    if len(sys.argv) != 2:
        #logging.error("usage: {} <input file>".format(sys.argv[0]))
        # sys.exit(1)
        pass
    else:
        inputFilename = sys.argv[1]
        outputFilename = os.path.splitext(sys.argv[1])[0] + ".cl0"

    if not os.path.exists(inputFilename):
        logging.error("[main] File doesn't exist")
        sys.exit(1)

    #logging.info("[main] using inputfile {}".format(inputFilename))

    parser = PL0Parser(inputFilename, outputFilename)

    result = parser.parse()
    if not result:
        logging.error("[main]  Parser failed with Morphem " + str(parser.lexer.morphem))
    else:
        xmlFile = inputFilename + ".xml"
        x = xmlwriter.XMLWriter(xmlFile)
        x.writeAll(result)
        #logging.info("[main]  wrote Parsetree to {}".format(xmlFile))
        #logging.info("[main]  done ")
