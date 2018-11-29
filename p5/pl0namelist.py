
class NLProcedure:

    def __init__(self, parent, name, root=False):
        self.parent = parent
        self.relativeAddressCounter = 0
        self.constants = []
        self.variables = []
        self.root = root
        self.ident = NLIdent(name, mutable=False)

    def identAlreadyExisting(self,ident):
        return self.getVariable(ident) or self.getConstant(ident) or self.ident.name == ident

    def getVariable(self, ident):
        for v in self.variables:
            if v.name == ident:
                return v

        return None

    def getConstant(self, ident):
        for c in self.constants:
            if c.name == ident:
                return c

        return None
      
    def addAnonymConstant(self,value):
        for c in self.constants:
            if c.isAnonym() and c.value == value:
                return c

        const = NLConstant(value=value)
        self.constants.append(const)
        return const

    def addConstant(self, ident):
        if self.identAlreadyExisting(ident) :
            return None

        const = NLConstant(ident) 
        self.constants.append(const)
        return const

    def addVariable(self,ident):
        if self.identAlreadyExisting(ident):
            return None

        var = NLVariable(ident,self.getNewRelativeAddress())
        
        self.variables.append(var)
        return var

    def getNewRelativeAddress(self):
        addr = self.relativeAddressCounter
        
        # We only have 4-byte (32 bit) values
        self.relativeAddressCounter += 4
        return addr


class NLIdent:
    def __init__(self, name=None,value=None,mutable=True):
        self.name = name
        self.value = value
        self.mutable = mutable

    def getValue(self):
        return self.value

    def setValue(self,value):
        self.value = value
        return True

    def isConstant(self):
        return not self.mutable

    def isVariable(self):
        return self.mutable

    def isAnonym(self):
        return self.name == None

class NLVariable(NLIdent):

    def __init__(self,name,relativeAddress,value=None):
        NLIdent.__init__(self,name,value)
        self.relativeAddress = relativeAddress

class NLConstant(NLIdent):

    def __init__(self,name=None,value=None):
        NLIdent.__init__(self,name,value)
    
    def setValue(self,value):
        # Constants can onle be set once
        if self.value is not None:
            return False

        self.value = value
        return True

class PL0NameList:

    def __init__(self):
        self.procedures = []

        # Main Programm will be the first procedure without
        # parent and root-flag set to true
        self.procedures.append(NLProcedure(parent=None,name=None,root=True))

    def getMainProcedure(self):
        return self.procedures[0]

    def getCurrentProcedure(self):
        return self.procedures[-1]
    
    def createAnonymConst(self,value):
        return self.getCurrentProcedure().addAnonymConstant(value=value)

    def createConst(self,ident):
        return self.getCurrentProcedure().addConstant(ident=ident)

    def searchConst(self,ident):
        p = self.getCurrentProcedure()

        while 1:
            c = p.getConstant(ident)
            if c is not None:
                return c
            if p.root:
                break
            p = p.parent
            
    def createVar(self,ident):
        return self.procedures[-1].addVariable(ident=ident)

    def createProc(self,name,parent):
        if parent is None:
            return None

        proc = NLProcedure(parent=parent,name=name)
        self.procedures.append(proc)
        return proc

    def searchIdentLocal(self, procedure, ident):
        if procedure.ident.name == ident:
            return procedure.ident

        id = procedure.getConstant(ident=ident)
        if id:
            return id

        id = procedure.getVariable(ident=ident)
        if id:
            return id

        return None

    def searchIdentGlobal(self, ident):
        p = self.getCurrentProcedure()

        while 1:
            id = self.searchIdentLocal(procedure=p,ident=ident)

            if id is not None:
                return id

            if p.root:
                return None
            
            p = p.parent