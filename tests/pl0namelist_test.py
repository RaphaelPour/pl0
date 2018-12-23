import unittest
import os

from pl0namelist import PL0NameList,NLIdent,NLConst,NLProc,NLVar

class TestPL0Parser(unittest.TestCase):

    def setUp(self):
        self.testFileFolder = "testfiles"

    # Constant Tests
    def test_addConst(self):
        nameList = PL0NameList()

        const = nameList.createConst("a",10)
        self.assertIsInstance(const,NLConst)
        
    def test_addMultipleConsts(self):
        nameList = PL0NameList()

        const1 = nameList.createConst(name="a",value=10)
        self.assertIsInstance(const1,NLConst)
        
        const2 = nameList.createConst(name="b",value=100)
        self.assertIsInstance(const2,NLConst)
        self.assertNotEqual(const1,const2)

    def test_constSetValue(self):
        nameList = PL0NameList()

        const = nameList.createConst(name="a",value=10)
        self.assertIsInstance(const,NLConst)
        self.assertEqual(const.value,10)

    def test_addAnonymConst(self):
        nameList = PL0NameList()

        const = nameList.createConst(value=10)
        self.assertIsInstance(const, NLConst)
                
    def test_addDifferentAnonymConsts(self):
        nameList = PL0NameList()

        const1 = nameList.createConst(value=1337)
        const2 = nameList.createConst(value=42)

        self.assertNotEqual(const1, const2)

    def test_addAnonymConstTwice(self):
        nameList = PL0NameList()

        const1 = nameList.createConst(value=1337)
        self.assertIsInstance(const1, NLConst)

        const2 = nameList.createConst(value=1337)
        self.assertEqual(const2, const1)

    # Variable Tests
    def test_addVar(self):
        nameList = PL0NameList()

        var = nameList.createVar("a")
        self.assertIsInstance(var,NLVar)

    def test_addMultipleVars(self):
        nameList = PL0NameList()

        var1 = nameList.createVar("a")
        self.assertIsInstance(var1,NLVar)
        
        var2 = nameList.createVar("b")
        self.assertIsInstance(var2,NLVar)
        self.assertNotEqual(var1,var2)

    def test_setVar(self):
        nameList = PL0NameList()

        var = nameList.createVar("a")
        var.value = 10
        self.assertIsInstance(var,NLVar)
        self.assertEqual(var.value, 10)   
        
    # Procedure Tests
    def test_addProcedure(self):
        n = PL0NameList()

        proc = n.createProc(name="p1")
        self.assertIsInstance(proc, NLProc)

    def test_parentProcedure(self):
        n = PL0NameList()

        proc1 = n.createProc(name="p1")
        self.assertIsInstance(proc1, NLProc)

        # Parent of our procedure must be the main procedure
        self.assertEqual(proc1.parent, n.mainProc())

    def test_addTwoNestedProcedures(self):
        n = PL0NameList()

        p1 = n.createProc("p1", parent=n.mainProc())
        p2 = n.createProc("p2", parent=p1)

        # Check if create-method gives back same object on multiple calls
        self.assertNotEqual(p1,p2)

        # Check if p1 is parent of p2
        self.assertEqual(p2.parent,p1)

        # Check if root is parent of p1
        
        self.assertEqual(p1.parent , n.mainProc())

        # Check if root is parent of p2 (should fail)
        self.assertNotEqual(p2.parent, n.mainProc())

    def test_addSequencedProcedures(self):
        n = PL0NameList()

        p1 = n.createProc("p1", parent=n.mainProc())
        p2 = n.createProc("p2", parent=n.mainProc())

        # Create-Method must return two different objects
        self.assertNotEqual(p1,p2)

        # But both of the procedures must have the same parent
        self.assertEqual(p1.parent,p2.parent)

    def test_addNestedIdenticalProcedures(self):
        n = PL0NameList()

        p1 = n.createProc("p1", n.mainProc())
        p2 = n.createProc("p2", n.mainProc())

        p13 = n.createProc("p3", p1)
        p23 = n.createProc("p3", p2)

        self.assertNotEqual(p13,p23)

    def test_resetLocalParent(self):
        pass

    # Local Search Tests
    def test_searchLocalVar(self):
        n = PL0NameList()

        ident = "A"

        varC = n.createVar(name=ident)
        self.assertIsInstance(varC, NLVar)

        varS2 = n.searchIdentNameLocal(procedure=n.mainProc(),name=ident)
        self.assertIsInstance(varS2, NLVar)
        self.assertEqual(varC, varS2)

    def test_searchLocalVarWithoutCreate(self):
        n = PL0NameList()

        ident = "A"

        # The Search must fail while the variable isn't created yet
        varS1 = n.searchIdentNameLocal(procedure=n.mainProc(),name=ident)
        self.assertIsNone(varS1)        

    def test_searchLocalConst(self):
        n = PL0NameList()

        ident = "A"

        constC = n.createVar(name=ident)
        self.assertIsInstance(constC, NLVar)

        # The search gives back our created Const
        constS = n.searchIdentNameLocal(procedure=n.mainProc(),name=ident)
        self.assertEqual(constC, constS)

    def test_searchLocalConstWithoutCreate(self):
        n = PL0NameList()

        ident = "A"

        # The Search must fail while the variable isn't created yet
        const = n.searchIdentNameLocal(procedure=n.mainProc(),name=ident)
        self.assertIsNone(const)        

    def test_searchLocalProc(self):
        n = PL0NameList()

        ident = "collatz"

        procC = n.createProc(ident, n.mainProc())
        self.assertIsInstance(procC, NLProc)

        pIdent = n.searchIdentNameLocal(procedure=n.mainProc(),name=ident)

        # TODO: Is it okay to fail or not? Has a Procedure to find
        #       idents of direct children procedures while doing 
        #       a local search?
        self.assertEqual(procC, pIdent)
        
    def test_searchLocalForeignProc(self):
        n = PL0NameList()

        proc1 = n.createProc("p1", n.mainProc())
        proc2 = n.createProc("p2", n.mainProc())
        proc3 = n.createProc("p3", proc1)

        # Look for proc3 in proc2 which must fail, cause
        # p3 is no local ident of p2
        procS = n.searchIdentNameLocal(proc2,proc3)

        self.assertIsNone(procS)
        
    # Global Search Tests
    def test_searchGlobalConst(self):
        n = PL0NameList()

        const1 = n.createConst(name="a",value=1337)
        proc1 = n.createProc("p1")

        const2 = n.searchIdentNameGlobal(procedure=proc1,name="a")
        self.assertEqual(const1,const2)

    def test_searchDeepNestedGlobalIdentSearch(self):
        n = PL0NameList()

        name = "DEBUG"

        const1 = n.createConst(name=name,value=1)
        proc1 = n.createProc("p1")
        proc2 = n.createProc("p2",proc1)
        proc3 = n.createProc("p2",proc2)
        proc4 = n.createProc("p2",proc3)
        proc5 = n.createProc("p2",proc4)

        const2 = n.searchIdentNameLocal(procedure=proc5, name=name)
        self.assertIsNone(const2)

        const3 = n.searchIdentNameGlobal(procedure=proc5,name=name)
        self.assertEqual(const1,const3)
if __name__ == '__main__':
    unittest.main()
