import logging
from enum import Enum
import struct


class VMCode(Enum):
    # Stack
    PUT_VALUE_VAR_LOCAL = 0
    PUT_VALUE_VAR_MAIN = 1
    PUT_VALUE_VAR_GLOBAL = 2
    PUT_ADDRESS_VAR_LOCAL = 3
    PUT_ADDRESS_VAR_MAIN = 4
    PUT_ADDRESS_VAR_GLOBAL = 5
    PUT_CONST = 6
    STORE_VAL = 7
    PUT_VAL = 8
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
        self.outputBuffer = ""

        # Add 2 byte placehoder for procedurecount at the
        # very beginning
        self.__write2Bytes__(48879) # hex(48879)=BEEF
        self.flushBuffer()

    def __writeByte__(self,value):
        self.outputBuffer += struct.pack("<c",value)

    def __write2Bytes__(self,value):
        # Write value as 2-byte little-endian to the buffer
        self.outputBuffer += struct.pack("<H",value)

    def __write4Bytes__(self, value):
        # Write value as 4-byte little-endian to the buffer
        self.outputBuffer += struct.pack("<L",value)

    def writeConstList(self, constList):

        # Const is 4 byte long
        # 255 -> ff 00 00 00
        for const in constList:
            self.__write4Bytes__(int(const.value))

    def writeCommand(self,vmcode, args=[]):
        if vmcode > len(VMCode):
            logging.error("CodeGen: Unknown VM Code '{}'".format(vmcode))

        # Write command
        self.__writeByte__(vmcode)

        # Write arguments
        for arg in args:
            self.__write2Bytes__(arg)

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

    def writeEntryProc(self, length, index, varMemorySize):

        # 0000: 1A EntryProc            000C,0001,0000 <-- Procedure
        self.__write2Bytes__(int(length))
        self.__write2Bytes__(int(index))
        self.__write2Bytes__(int(varMemorySize))

    def flushBuffer(self):
        self.outputFile.write(self.outputBuffer)
        self.outputBuffer = ""

    def initOutputBuffer(self):
        self.outputBuffer = ""
        
    def closeOutputfile(self):
        self.flushBuffer()
        self.outputFile.close()
