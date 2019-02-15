#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import os

import sys
sys.path.append("..")
from pl0namelist import NLConst
from pl0codegen import PL0CodeGen

class TestPL0Parser(unittest.TestCase):

    def setUp(self):
        self.testFileFolder = "testfiles"
    
    def test_writeSingleConst(self):
        c = PL0CodeGen("1234.pl0")

        const = NLConst(10,0)

        c.writeConstList([const])
        self.assertEqual(c.outputBuffer, [10])


    def test_writeMultipleConst(self):
        c = PL0CodeGen("1234.pl0")

        constList = []

        for i in range(0,16):
            constList.append(NLConst(i,i))

        c.writeConstList(constList)
        self.assertEqual(c.outputBuffer, bytearray([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]))


if __name__ == '__main__':
    unittest.main()