#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   file:           xmlwriter.py
#   description:    Converts abstract syntax tree of a parsed PL/0 file to xml and 
#                   writes it to a file
#   date:           24.01.2018
#   license:        GPL v3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
#
import pl0parser

class XMLWriter:

    def __init__(self, filename="dump.xml"):
        self.filename = filename

    def writeAll(self, tree):

        xmlData = self.parse(tree)

        with open(self.filename, "w+") as out:
            out.write(xmlData)

    def parse(self, tree, depth=0):

        out = ""
        for el in tree:
            if el['type'].value == pl0parser.EdgeType.SUBGRAPH_.value:
                out += ("  " * depth) + "<{}>\n".format(el['value'])
                out += self.parse(el['sub'], depth+1)
                out += ("  " * depth) + "</{}>\n".format(el['value'])
            else:
                value = str(el['value'])
                if value == '<':
                    value = "&lt;"
                elif value == '>':
                    value = '&gt;'
                elif value == '"':
                    value = '&quot;'
                elif value == "'":
                    value = "&apos;"
                elif value == "&":
                    value = "&amp;"
                out += ("  " * depth) +  "<TERMINAL line='{}' col='{}'>{}</TERMINAL>\n".format(el['pos'][0],el['pos'][1],value)

        return out
