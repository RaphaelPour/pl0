#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import os

import sys
sys.path.append("..")
from pl0parser import PL0Parser, EdgeType, Edge
from pl0lexer import Symbol


class TestPL0Parser(unittest.TestCase):

    def setUp(self):
        self.testFileFolder = "testfiles"

    def test_instance(self):
        inputFile = os.path.join(self.testFileFolder, "tx.pl0")
        outputFile = os.path.join(self.testFileFolder, "tx.cl0")
        
        p = PL0Parser(inputFile,outputFile)

        self.assertIsInstance(p, PL0Parser)


if __name__ == '__main__':
    unittest.main()
