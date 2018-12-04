import unittest
import os

from pl0parser import PL0Parser, EdgeType, Edge
from pl0lexer import Symbol


class TestPL0Parser(unittest.TestCase):

    def setUp(self):
        self.testFileFolder = "../testfiles"

    def test_instance(self):
        p = PL0Parser(os.path.join(self.testFileFolder, "tx.pl0"))

        self.assertIsInstance(p, PL0Parser)

    def test_parse_test_pl0(self):
        p = PL0Parser(os.path.join(self.testFileFolder, "test.pl0"))

        path = p.parse()

        self.assertNotEqual(path, False)

        self.assertEqual(path,
                         [
                             {'value': 'PROGRAM', 'type': EdgeType.SUBGRAPH_, 'pos': (1, 3), 'sub':
                              [
                                 {'value': 'BLOCK', 'type': EdgeType.SUBGRAPH_, 'pos': (1, 3), 'sub':
                                  [
                                     {'value': 'PROCEDURE_DECLARATION', 'type': EdgeType.SUBGRAPH_, 'pos': (1, 3), 'sub':
                                      [
                                         {'value': Symbol.PROCEDURE,
                                             'type': EdgeType.SYMBOL___, 'pos': (1, 3)},
                                         {'value': 'P1', 'type': EdgeType.MORPHEM__, 'pos': (
                                             1, 13)},
                                         {'value': ';', 'type': EdgeType.SYMBOL___, 'pos': (
                                             1, 15)},
                                         {'value': 'BLOCK', 'type': EdgeType.SUBGRAPH_, 'pos': (2, 3), 'sub':
                                          [
                                             {'value': 'STATEMENT', 'type': EdgeType.SUBGRAPH_, 'pos': (2, 3), 'sub':
                                              [
                                                 {'value': 'COMPOUND_STATEMENT', 'type': EdgeType.SUBGRAPH_, 'pos': (2, 3), 'sub':
                                                  [
                                                     {'value': Symbol.BEGIN, 'type': EdgeType.SYMBOL___, 'pos': (
                                                         2, 3)},
                                                     {'value': 'STATEMENT', 'type': EdgeType.SUBGRAPH_, 'pos': (3, 5), 'sub':
                                                      [
                                                         {'value': 'ASSIGNMENT_STATEMENT', 'type': EdgeType.SUBGRAPH_, 'pos': (3, 5), 'sub':
                                                          [
                                                             {'value': 'I', 'type': EdgeType.MORPHEM__, 'pos': (
                                                                 3, 5)},
                                                             {'value': Symbol.ASSIGN, 'type': EdgeType.SYMBOL___, 'pos': (
                                                                 3, 6)},
                                                             {'value': 'EXPRESSION', 'type': EdgeType.SUBGRAPH_, 'pos': (3, 8), 'sub':
                                                              [
                                                                 {'value': 'TERM', 'type': EdgeType.SUBGRAPH_, 'pos': (3, 8), 'sub':
                                                                  [
                                                                     {'value': 'FACTOR', 'type': EdgeType.SUBGRAPH_, 'pos': (3, 8), 'sub':
                                                                      [
                                                                         {'value': 0.0, 'type': EdgeType.MORPHEM__, 'pos': (
                                                                             3, 8)}
                                                                     ]
                                                                     }
                                                                 ]
                                                                 }
                                                             ]
                                                             }
                                                         ]
                                                         }
                                                     ]
                                                     },
                                                     {'value': Symbol.END, 'type': EdgeType.SYMBOL___, 'pos': (
                                                         4, 3)}
                                                 ]
                                                 }
                                             ]
                                             }
                                         ]
                                         },
                                         {'value': ';', 'type': EdgeType.SYMBOL___, 'pos': (
                                             4, 6)}
                                     ]
                                     },
                                     {'value': 'STATEMENT', 'type': EdgeType.SUBGRAPH_, 'pos': (6, 1), 'sub':
                                      [
                                         {'value': 'PROCEDURE_CALL', 'type': EdgeType.SUBGRAPH_, 'pos': (6, 1), 'sub':
                                          [
                                             {'value': Symbol.CALL, 'type': EdgeType.SYMBOL___, 'pos': (
                                                 6, 1)},
                                             {'value': 'P1', 'type': EdgeType.MORPHEM__, 'pos': (
                                                 6, 6)}
                                         ]
                                         }
                                     ]
                                     }
                                 ]
                                 },
                                 {'value': '.', 'type': EdgeType.SYMBOL___,
                                     'pos': (6, 8)}
                             ]
                             }
                         ])


if __name__ == '__main__':
    unittest.main()
