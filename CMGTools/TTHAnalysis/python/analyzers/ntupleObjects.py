#!/bin/env python

class NTupleVariable:
    def __init__(self, name, function, type=float, help="", default=-99, mcOnly=False):
        self.name = name
        self.function = function
        self.type = type
        self.help = help
        self.default = default
        self.mcOnly  = mcOnly
    def __call__(self,object):
        ret = self.function(object)
        return ret
    def makeBranch(self,treeNumpy,isMC):
        if self.mcOnly and not isMC: return
        treeNumpy.var(self.name, type=self.type, default=self.default, title=self.help)
    def fillBranch(self,treeNumpy,object,isMC):
        if self.mcOnly and not isMC: return
        treeNumpy.fill(self.name, self(object))

class NTupleObjectType:
    def __init__(self,name,baseObjectTypes=[],mcOnly=[],variables=[]):
        self.name = name
        self.baseObjectTypes = baseObjectTypes
        self.mcOnly = mcOnly
        self.variables = variables
    def allVars(self,isMC):
        ret = []; names = {}
        if not isMC and self.mcOnly: return []
        for base in self.baseObjectTypes:
            if not isMC and base.mcOnly: continue
            for var in base.allVars(isMC):
                if var.name in names: raise RuntimeError, "Duplicate definition of variable %s from %s and %s" % (var.name, base.name, names[var.name])
                names[var.name] = base.name
                ret.append(var)
        for var in self.variables:
            if not isMC and var.mcOnly: continue
            if var.name in names: raise RuntimeError, "Duplicate definition of variable %s from %s and %s" % (var.name, self.name, names[var.name])
            names[var.name] = self.name
            ret.append(var)
        return ret

class NTupleObject:
    def __init__(self, name, objectType, help="", mcOnly=False):
        self.name = name
        self.objectType = objectType
        self.mcOnly = mcOnly
        self.help = ""
    def makeBranches(self,treeNumpy,isMC):
        if not isMC and self.mcOnly: return
        allvars = self.objectType.allVars(isMC)
        for v in allvars:
            h = v.help
            if self.help: h = "%s for %s" % ( h if h else v.name, self.help )
            treeNumpy.var("%s_%s" % (self.name, v.name), type=v.type, default=v.default, title=h)
    def fillBranches(self,treeNumpy,object,isMC):
        if self.mcOnly and not isMC: return
        allvars = self.objectType.allVars(isMC)
        for v in allvars:
            treeNumpy.fill("%s_%s" % (self.name, v.name), v(object))


class NTupleCollection:
    def __init__(self, name, objectType, maxlen, help="", mcOnly=False, sortAscendingBy=None, sortDescendingBy=None, filter=None):
        self.name = name
        self.objectType = objectType
        self.maxlen = maxlen
        self.help = help
        self.mcOnly = mcOnly
        if sortAscendingBy != None and sortDescendingBy != None:
            raise RuntimeError, "Cannot specify two sort conditions"
        self.filter = filter
        self.sortAscendingBy  = sortAscendingBy
        self.sortDescendingBy = sortDescendingBy
    def makeBranchesScalar(self,treeNumpy,isMC):
        if not isMC and self.objectType.mcOnly: return
        treeNumpy.var("n"+self.name, int)
        allvars = self.objectType.allVars(isMC)
        for v in allvars:
            for i in xrange(1,self.maxlen+1):
                h = v.help
                if self.help: h = "%s for %s [%d]" % ( h if h else v.name, self.help, i-1 )
                treeNumpy.var("%s%d_%s" % (self.name, i, v.name), type=v.type, default=v.default, title=h)
    def makeBranchesVector(self,treeNumpy,isMC):
        if not isMC and self.objectType.mcOnly: return
        treeNumpy.var("n"+self.name, int)
        allvars = self.objectType.allVars(isMC)
        for v in allvars:
            h = v.help
            if self.help: h = "%s for %s" % ( h if h else v.name, self.help )
            treeNumpy.vector("%s_%s" % (self.name, v.name), "n"+self.name, self.maxlen, type=v.type, default=v.default, title=h)
    def fillBranchesScalar(self,treeNumpy,collection,isMC):
        if not isMC and self.objectType.mcOnly: return
        if self.filter != None: collection = [ o for o in collection if filter(o) ]
        if self.sortAscendingBy != None: collection  = sorted(collection, key=self.sortAscendingBy)
        if self.sortDescendingBy != None: collection = sorted(collection, key=self.sortDescendingBy, reverse=True)
        num = min(self.maxlen,len(collection))
        treeNumpy.fill("n"+self.name, num)
        allvars = self.objectType.allVars(isMC)
        for i in xrange(num): 
            o = collection[i]
            for v in allvars:
                treeNumpy.fill("%s%d_%s" % (self.name, i+1, v.name), v(o))
    def fillBranchesVector(self,treeNumpy,collection,isMC):
        if not isMC and self.objectType.mcOnly: return
        if self.filter != None: collection = [ o for o in collection if filter(o) ]
        if self.sortAscendingBy != None: collection  = sorted(collection, key=self.sortAscendingBy)
        if self.sortDescendingBy != None: collection = sorted(collection, key=self.sortDescendingBy, reverse=True)
        num = min(self.maxlen,len(collection))
        treeNumpy.fill("n"+self.name, num)
        allvars = self.objectType.allVars(isMC)
        for v in allvars:
            treeNumpy.vfill("%s_%s" % (self.name, v.name), [ v(collection[i]) for i in xrange(num) ])

