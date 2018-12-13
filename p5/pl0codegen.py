#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from enum import Enum
import struct


class VMCode(Enum):
    # Stack
    PUSH_VALUE_VAR_LOCAL = 0
    PUSH_VALUE_VAR_MAIN = 1
    PUSH_VALUE_VAR_GLOBAL = 2
    PUSH_ADDRESS_VAR_LOCAL = 3
    PUSH_ADDRESS_VAR_MAIN = 4
    PUSH_ADDRESS_VAR_GLOBAL = 5
    PUSH_CONST = 6
    STORE_VAL = 7
    PUSH_VAL = 8
    GET_VAL = 9

    # Arithmetic
    VZ_MINUS = 10
    ODD = 11

    # Binary Operations
    OP_ADD = 12
    OP_SUB = 13
    OP_MULT = 14
    OP_DIV = 15
    CMP_EQ = 16
    CMP_NE = 17
    CMP_LT = 18
    CMP_GT = 19
    CMP_LE = 20
    CMP_GE = 21

    # Jumps
    CALL = 22
    RET_PROC = 23
    JMP = 24
    JMP_NOT = 25
    ENTRY_PROC = 26

    # Extension of PL0 (Not neccessary)
    PUTSTRG = 27
    POP = 28
    SWAP = 29

    END_OF_CODE = 20 #1E

class CGLabel:
    def __init__(self, address):
        self.address = address
        self.distance = 0

class PL0CodeGen:

    def __init__(self, outputFilename):
        self.outputFilename = outputFilename
        self.outputFile = open(self.outputFilename, "wb+")
        self.outputBuffer = bytearray()

        # Add 2 byte placehoder for procedurecount at the
        # very beginning
        self.__append2Bytes__(48879) # hex(48879)=BEEF
        self.__append2Bytes__(0)
        self.flushBuffer()

        self.labels = []
        self.delayedCommands = []

    def __appendByte__(self,value):
        self.outputBuffer += (struct.pack("<B",value))

    def __frontInsertByte__(self,value):
        self.outputBuffer.insert(0,struct.pack("<B",value))
        
    def __append2Bytes__(self,value):
        if(value < 0):
            self.outputBuffer += (struct.pack("<h",value))
        else:
            # Write value as 2-byte little-endian to the buffer
            self.outputBuffer += (struct.pack("<H",value))

    def __append4Bytes__(self, value):
        # Write value as 4-byte little-endian to the buffer
        self.outputBuffer += (struct.pack("<L",value))

    def writeConstList(self, constList):

        # Const is 4 byte long
        # 255 -> ff 00 00 00
        for const in constList:
            self.__append4Bytes__(int(const.value))

    def writeCommand(self,vmcode, args=[]):

        #logging.debug("{}({})".format(vmcode,args))

        vmcodenr = vmcode.value

        if vmcodenr > len(VMCode):
            logging.error("[CodeGen] Unknown VM Code '{}'".format(vmcode))
            return False

        # Write command
        self.__appendByte__(vmcodenr)

        # Write each argument as 2-byte value
        for arg in args:
            self.__append2Bytes__(arg)

        return True

    def setTotalCountOfProcedures(self, procedureCount):

        # Remember where the file pointer is currently at
        currentPosition = self.outputFile.tell()

        # Go to the very beginning of the file
        self.outputFile.seek(0, 0)

        # Write directly the count of procedure as 4 Byte number
        # to the very first byte of the file
        self.outputFile.write(struct.pack("H",int(procedureCount)))

        # Go back where we were before
        self.outputFile.seek(currentPosition, 0)

    def setProcedureLength(self):
        
        length = len(self.outputBuffer)

        if length < 2:
            logging.error("[CodeGen] Procedure length can't be set with an empty or too short output buffer.")
            return False

        # Code length is from index 1 with size of 2 bytes
        # First byte is the EntryProc command
        b = struct.pack("<H", len(self.outputBuffer))
        self.outputBuffer[1] = b[0]
        self.outputBuffer[2] = b[1]

        return True

    def pushDelayedCommand(self,vmcode, args=[]):
        self.delayedCommands.append((vmcode, args))

    def popDelayedCommand(self):
        if len(self.delayedCommands) == 0:
            logging.error("No delayed commands left")
            return (0,)

        return self.delayedCommands.pop()

    def pushLabel(self):
        # Store the current position (=length of the current buffer)
        # in order to calculate the relative address for if/while later
        self.labels.append(CGLabel(len(self.outputBuffer)))

    def popLabel(self):
        # Calculate relative address for if/while so they know
        # where to jump to if condition is true 
        label = self.labels.pop()

        # Calculate relative address
        label.distance = len(self.outputBuffer) - label.address
        return label

    def correctJmp(self, label,offset=0):

        # Check if jump command (2 byte) + its first argument (2 byte)
        # is inside the output buffer
        if label.address + 4 >= len(self.outputBuffer):
            logging.error("[CodeGen] Invalid Jump address")
            return False
        
        #logging.info("Relative address: " + label.distance+offset)
        b = struct.pack("<h", label.distance+offset)
        self.outputBuffer[label.address+1] = b[0]
        self.outputBuffer[label.address+2] = b[1]

        return True

    def flushBuffer(self):
        self.outputFile.write(self.outputBuffer)
        self.outputBuffer = bytearray()

    def initOutputBuffer(self):
        self.outputBuffer = bytearray()
        
    def closeOutputfile(self):
        self.flushBuffer()
        self.outputFile.close()
