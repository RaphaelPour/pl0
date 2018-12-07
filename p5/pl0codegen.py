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

    def __appendByte__(self,value):
        self.outputBuffer += (struct.pack("<B",value))

    def __frontInsertByte__(self,value):
        self.outputBuffer.insert(0,struct.pack("<B",value))
        
    def __append2Bytes__(self,value):
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

        logging.debug("{}({})".format(vmcode,args))

        vmcodenr = vmcode.value

        if vmcodenr > len(VMCode):
            logging.error("[CodeGen] Unknown VM Code '{}'".format(vmcode))

        # Write command
        self.__appendByte__(vmcodenr)

        # Write each argument as 2-byte value
        for arg in args:
            self.__append2Bytes__(arg)

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

        self.outputBuffer[1] = len(self.outputBuffer)

        return True

    def flushBuffer(self):
        self.outputFile.write(self.outputBuffer)
        self.outputBuffer = bytearray()

    def initOutputBuffer(self):
        self.outputBuffer = bytearray()
        
    def closeOutputfile(self):
        self.flushBuffer()
        self.outputFile.close()
