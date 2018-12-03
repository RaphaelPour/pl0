import unittest
import os

from pl0namelist import PL0NameList,NLIdent,NLConstant,NLProcedure,NLVariable

class TestPL0Parser(unittest.TestCase):

    def setUp(self):
        self.testFileFolder = "../testfiles"

    # Constant Tests
    def test_addConst(self):
        nameList = PL0NameList()

        const = nameList.createConst("a")
        self.assertIsInstance(const,NLConstant)
        
    def test_addConstTwice(self):
        nameList = PL0NameList()

        const = nameList.createConst("a")
        self.assertIsInstance(const,NLConstant)
        
        # Creating the constant again must fail
        const = nameList.createConst("a")
        self.assertIsNone(const)

    def test_addMultipleConsts(self):
        nameList = PL0NameList()

        const1 = nameList.createConst("a")
        self.assertIsInstance(const1,NLConstant)
        
        const2 = nameList.createConst("b")
        self.assertIsInstance(const2,NLConstant)
        self.assertNotEqual(const1,const2)

    def test_constSetValue(self):
        nameList = PL0NameList()

        const = nameList.createConst("a")
        self.assertIsInstance(const,NLConstant)
        self.assertTrue(const.setValue(10))
        self.assertEqual(const.value, 10)
        self.assertFalse(const.setValue(11))

    def test_constSetAndGetValue(self):
        nameList = PL0NameList()

        const = nameList.createConst("a")
        self.assertIsInstance(const,NLConstant)
        self.assertTrue(const.setValue(10))
        self.assertEqual(const.value, 10)
        self.assertFalse(const.setValue(11))
        
    def test_constSetTwiceValue(self):
        nameList = PL0NameList()

        const = nameList.createConst("a")
        self.assertIsInstance(const,NLConstant)
        self.assertTrue(const.setValue(10))
        # Second time must fail
        self.assertFalse(const.setValue(11))

    def test_addAnonymConst(self):
        nameList = PL0NameList()

        const = nameList.createAnonymConst(1337)
        self.assertIsInstance(const, NLConstant)
                
    def test_addDifferentAnonymConsts(self):
        nameList = PL0NameList()

        const1 = nameList.createAnonymConst(1337)
        const2 = nameList.createAnonymConst(42)

        self.assertNotEqual(const1, const2)

    def test_addAnonymConstTwice(self):
        nameList = PL0NameList()

        const1 = nameList.createAnonymConst(1337)
        self.assertIsInstance(const1, NLConstant)

        const2 = nameList.createAnonymConst(1337)
        self.assertEqual(const2, const1)

    # Variable Tests
    def test_addVar(self):
        nameList = PL0NameList()

        var = nameList.createVar("a")
        self.assertIsInstance(var,NLVariable)
        
    def test_addVarTwice(self):
        nameList = PL0NameList()

        var = nameList.createVar("a")
        self.assertIsInstance(var,NLVariable)
        
        var = nameList.createVar("a")
        self.assertIsNone(var)

    def test_addMultipleVars(self):
        nameList = PL0NameList()

        var1 = nameList.createVar("a")
        self.assertIsInstance(var1,NLVariable)
        
        var2 = nameList.createVar("b")
        self.assertIsInstance(var2,NLVariable)
        self.assertNotEqual(var1,var2)

    def test_setVar(self):
        nameList = PL0NameList()

        var = nameList.createVar("a")
        self.assertIsInstance(var,NLVariable)
        self.assertTrue(var.setValue(10))   
        
    def test_setGetVar(self):
        nameList = PL0NameList()

        var = nameList.createVar("a")
        self.assertIsInstance(var,NLVariable)
        self.assertTrue(var.setValue(10))   
        self.assertEqual(var.getValue(), 10)   

    def test_setVarTwice(self):
        nameList = PL0NameList()

        var = nameList.createVar("a")
        self.assertIsInstance(var,NLVariable)
        self.assertTrue(var.setValue(10))
        self.assertEqual(var.getValue(),10)   
        self.assertTrue(var.setValue(11))    
        self.assertEqual(var.getValue(),11)

    # Variable/Const Mixed Tests
    def test_addVarAndConstWithSameIdent(self):
        n = PL0NameList()

        var1 = n.createVar('a')
        self.assertIsInstance(var1,NLVariable)

        const1 = n.createConst('a')
        self.assertFalse(const1)

        # test the other way arround

        const2 = n.createConst('b')
        self.assertIsInstance(const2,NLConstant)

        var2 = n.createVar('b')
        self.assertFalse(var2)

    # Procedure Tests
    def test_addProcedure(self):
        n = PL0NameList()

        proc = n.createProc(name="p1",parent=n.getCurrentProcedure())
        self.assertIsInstance(proc, NLProcedure)

    def test_parentProcedure(self):
        n = PL0NameList()

        proc1 = n.createProc(name="p1", parent=None)
        self.assertIsNone(proc1)

        proc2 = n.createProc(name="p2", parent=n.getMainProcedure())
        self.assertIsInstance(proc2, NLProcedure)

        # Parent of our procedure must be the main procedure
        self.assertEqual(proc2.parent, n.getMainProcedure())

    def test_addTwoNestedProcedures(self):
        n = PL0NameList()

        p1 = n.createProc("p1", parent=n.getMainProcedure())
        p2 = n.createProc("p2", parent=p1)

        # Check if create-method gives back same object on multiple calls
        self.assertNotEqual(p1,p2)

        # Check if p1 is parent of p2
        self.assertEqual(p2.parent,p1)

        # Check if root is parent of p1
        
        self.assertEqual(p1.parent , n.getMainProcedure())

        # Check if root is parent of p2 (should fail)
        self.assertNotEqual(p2.parent, n.getMainProcedure())

    def test_addSequencedProcedures(self):
        n = PL0NameList()

        p1 = n.createProc("p1", parent=n.getMainProcedure())
        p2 = n.createProc("p2", parent=n.getMainProcedure())

        # Create-Method must return two different objects
        self.assertNotEqual(p1,p2)

        # But both of the procedures must have the same parent
        self.assertEqual(p1.parent,p2.parent)

    def test_addNestedIdenticalProcedures(self):
        n = PL0NameList()

        p1 = n.createProc("p1", n.getMainProcedure())
        p2 = n.createProc("p2", n.getMainProcedure())

        p13 = n.createProc("p3", p1)
        p23 = n.createProc("p3", p2)

        self.assertNotEqual(p13,p23)

    # Local Search Tests
    def test_searchLocalVar(self):
        n = PL0NameList()

        ident = "A"

        varC = n.createVar(ident)
        self.assertIsInstance(varC, NLVariable)

        varS2 = n.searchIdentLocal(n.getMainProcedure(),ident)
        self.assertIsInstance(varS2, NLVariable)
        self.assertEqual(varC, varS2)

    def test_searchLocalVarWithoutCreate(self):
        n = PL0NameList()

        ident = "A"

        # The Search must fail while the variable isn't created yet
        varS1 = n.searchIdentLocal(n.getMainProcedure(),ident)
        self.assertIsNone(varS1)        

    def test_searchLocalConst(self):
        n = PL0NameList()

        ident = "A"

        constC = n.createVar(ident)
        self.assertIsInstance(constC, NLVariable)

        # The search gives back our created Const
        constS = n.searchIdentLocal(n.getMainProcedure(),ident)
        self.assertEqual(constC, constS)

    def test_searchLocalConstWithoutCreate(self):
        n = PL0NameList()

        ident = "A"

        # The Search must fail while the variable isn't created yet
        const = n.searchIdentLocal(n.getMainProcedure(),ident)
        self.assertIsNone(const)        

    def test_searchLocalProc(self):
        n = PL0NameList()

        ident = "collatz"

        procC = n.createProc(ident, n.getMainProcedure())
        self.assertIsInstance(procC, NLProcedure)

        pIdent = n.searchIdentLocal(n.getMainProcedure(), ident)

        # TODO: Is it okay to fail or not? Has a Procedure to find
        #       idents of direct children procedures while doing 
        #       a local search?
        self.assertEqual(procC.ident, pIdent)
        
    def test_searchLocalForeignProc(self):
        n = PL0NameList()

        proc1 = n.createProc("p1", n.getMainProcedure())
        proc2 = n.createProc("p2", n.getMainProcedure())
        proc3 = n.createProc("p3", proc1)

        # Look for proc3 in proc2 which must fail, cause
        # p3 is no local ident of p2
        procS = n.searchIdentLocal(proc2,proc3.ident)

        self.assertIsNone(procS)
        
    # Global Search Tests
    def test_searchGlobalConst(self):
        n = PL0NameList()

        const1 = n.createConst("a")
        proc1 = n.createProc("p1", n.getMainProcedure())

        const2 = n.searchIdentGlobal(proc1,"a")
        self.assertEqual(const1,const2)

if __name__ == '__main__':
    unittest.main()
