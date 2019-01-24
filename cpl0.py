#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   file:           cpl0.py
#   description:    PL/0 Compiler main program with argument parser
#   date:           24.01.2018
#   license:        GPL v3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
#

import argparse
import os
import logging
import xmlwriter
from pl0parser import PL0Parser

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='PL0 Compiler')
    parser.add_argument("--ast","-a",help="writes abstract syntax tree", action="store_true")
    parser.add_argument("inputFile")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    outputFile = os.path.splitext(args.inputFile)[0] + ".cl0"
    
    parser = PL0Parser(args.inputFile, outputFile)

    result = parser.parse()
    if not result:
        logging.error("[main]  Parser failed with Morphem " + str(parser.lexer.morphem))
    elif args.ast:
        xmlFile = args.inputFile + ".xml"
        x = xmlwriter.XMLWriter(xmlFile)
        x.writeAll(result)