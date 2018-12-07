#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

#
# All NL*-Classes are only Data-Structures to hold
# the neccessary information for building up a namelist
#

class NLIdent():
    def __init__(self, name, value=None):
        self.name = name
        self.value = value

class NLProc(NLIdent):
    def __init__(self, name,parent,index):
        super().__init__(name)
        self.parent = parent
        self.constants = []
        self.variables = []
        self.childProcedures = []
        self.addressOffset = 0
        self.index = index

class NLConst(NLIdent):
    def __init__(self, value,index,name=None):
        super().__init__(name,value)
        self.index = index

class NLVar(NLIdent):

    def __init__(self, name,addressOffset, parent,value=None):
        super().__init__(name,value)
        self.parent = parent
        self.addressOffset = addressOffset


#
# PL0NameList is an interface to access and arrange
# the Elements of a Name-List. It also does semantic checks and
# avoids duplicate idents depending on the context
#
class PL0NameList:
    def __init__(self):
        """ Initializes the NameList by building up the
        neccessary data-structure for semantic lookup operations. 
        It also adds a main/root procedure
        """

        # For the semantic checks and searches, it is neccessary to
        # carry additional lists which overlaps with the data-structure
        # build up with all the NL*-Classes.
        self.procedures = []
        self.constantList = []
        
        # Main Programm will be the first procedure without a parent
        self.procedures.append(NLProc(parent=None,name="main",index=0))
        self.currentProcedure = self.procedures[-1]
        
    def mainProc(self):
        """ Returns the Main/Root Procedure. This is the (grand)parent of
        all other procedures 
        """
        return self.procedures[0]

    def createConst(self, value, name=None):
        """Adds a new constant to the current procedure.
        It doesn't check if the ident is already existing,
        while this should be done in the parser when the
        ident-name is parsed
        
        In order to add anonym constants, the name can be left out.

        Additionally the value will be looked up in the global
        constant list to get the index of the previously added
        constant with the same value. The aim is to store each
        constant value only once, even used with differen idents.
        """

        # Check if ident-name already exists in local scope
        #result = self.searchIdentNameLocal(name)
        #if result is not None:
        #    logging.error("Ident " + name + " already exists.")
        #    return False

        # Check if value is already in the global constant list
        # If not: index will be the length of the list
        index = len(self.constantList)
        cachedConst = None
        for c in self.constantList:
            if c.value == value:
                cachedConst = c
                index = c.index
                break

        # If the constant is not already existent in the global
        # constant list, create it
        if cachedConst is None:
            cachedConst = NLConst(value,index=index)
            self.constantList.append(cachedConst)

        # If the constant is anonym, the procedure will get the
        # instance of the global constant list for more storage efficency
        # otherwise a new instance will be created with the name
        newConst = None
        if name is None:
            newConst = cachedConst
        else:
            newConst = NLConst(value,index,name)
        
        self.currentProcedure.childProcedures.append(newConst)
        return newConst

    def createVar(self, name):
        """Adds a new variable to the current procedure.
        It doesn't check if the ident is already existing,
        while this should be done in the parser when the
        ident-name is parsed
        """

        # Each variable has a relative address offset 
        currentOffset = self.currentProcedure.addressOffset

        newVar = NLVar(name=name,parent=self.currentProcedure,addressOffset=currentOffset)

        # Increase address offset for the next variable
        self.currentProcedure.addressOffset += 4

        # Add variable to the local variable list of the current procedure
        self.currentProcedure.variables.append(newVar)

        return newVar

    def createProc(self, name,parent=None):
        
        # The current procedure is the default value for procedure
        if parent is None:
            parent = self.currentProcedure

        newProc = NLProc(name=name, parent=parent, index=len(self.procedures))

        # Append new procedure as child to the current
        # Procedure
        parent.childProcedures.append(newProc)

        # Append new procedure to the global procedure list
        self.procedures.append(newProc)
        
        # Our current procedure is now the newly created until we
        # end the procedure with endProc() to go back to the parent
        self.currentProcedure = newProc

        return newProc

    def endProc(self):
        """ Ends the current procedure by resetting it to its parent.
        This is equal to leave a procedure and go back to the next
        higher one.
        """
        #if self.currentProcedure.parent is None and self.currentProcedure is not self.mainProc:
        #    logging.error("[NameList] Procedure can't be ended. Parent not found.")
        #    return False

        self.currentProcedure = self.currentProcedure.parent
        return True

    def searchConstByValue(self,value):
        for const in self.constantList:
            if const.value == value:
                return const
        return None

    def searchIdentNameLocal(self, name, procedure=None):
        """ The Local Scope is provided using the local search to
        find out if an ident is already in use.
        """
        # The current procedure is the default value for procedure
        if procedure is None:
            procedure = self.currentProcedure

        # Procedure itself is named after given ident-name?
        if procedure.name == name:
            return procedure

        # Procedure has child named after given ident-name?
        for cp in procedure.childProcedures:
            if cp.name == name:
                return cp

        # Local Constant named after the given ident-name?
        for c in procedure.constants:
            if c.name == name:
                return c

        # Local Variable named after the given ident-name?
        for v in procedure.variables:
            if v.name == name:
                return v

        return None

    def searchIdentNameGlobal(self,name,procedure=None):
        """ In order to check if an ident is used in global scope,
        this search goes from "inner to outer" scope and makes a local
        search in each one.
        The rule is: local scope overwrites global scope. 
        """
        while 1:
            ident = self.searchIdentNameLocal(name=name, procedure=procedure)

            if ident is None:

                # If the current procedure has no parent
                # -> we reached the main procedure and the ident
                # doesn't exist
                if procedure is None or procedure.parent is None:
                    return None
                else:
                    # Otherwise we use the parent of the current procedure
                    # for the next round. This enables the "from inner to outer"
                    # search
                    procedure = procedure.parent
            else:
                return ident

    def isLocalIdentName(self,name,procedure=None):
        return self.searchIdentNameLocal(procedure=procedure, name=name) != None

    def isGlobalIdentName(self,name,procedure=None):
        return self.searchIdentNameGlobal(procedure=procedure, name=name)
    