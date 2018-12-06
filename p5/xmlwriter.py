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
                out += ("  " * depth) +  "<TERMINAL line='{}' col='{}'>{}</TERMINAL>\n".format(el['pos'][0],el['pos'][1],str(el['value']))

        return out
