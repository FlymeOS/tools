#!/usr/bin/env python

__author__ = 'zhangweiping@baiyi-mobile.com'

import re
import os
import string
import hashlib

class Smali:
    """
        A set of methods for processing smali file path
    """
    @staticmethod
    def isSmali(path):
        """
            check if the path end of .smali
        """
        if re.compile(r'.*\.smali', re.S).match(path):
            return True
        return False

    @staticmethod
    def isRootSmali(path):
        """
            check if the path is a root smali
        """
        if Smali.isSmali(path) and cmp(Smali.getSmaliName(path), Smali.getSmaliRoot(path)) == 0:
            return True
        return False

    @staticmethod
    def getSmali(path):
        """
            get basename of path
            input xx/xx/A$1.smali return A$1.smali
        """
        if Smali.isSmali(path):
            return os.path.basename(path)
        raise ValueError("Not a smali path:"+path)

    @staticmethod
    def getSmaliName(path):
        """
            get smali name of path
            input xx/xx/A$1.smali  return A$1
        """
        if Smali.isSmali(path):
            basename = Smali.getSmali(path)
            return os.path.splitext(basename)[0]
        raise ValueError("Not a smali path:"+path)

    @staticmethod
    def getSmaliRoot(path):
        """
            get smali root name of path
            input xx/xx/A$1.smali  return A
        """
        if Smali.isSmali(path):
            sName = Smali.getSmaliName(path)
            return string.split(sName, "$")[0]
        raise ValueError("Not a smali path:"+path)

    @staticmethod
    def getSmaliMain(path):
        """
            get root smali of path
            input xx/xx/A$1.smali  return A.smli
        """
        if Smali.isSmali(path):
            sName = Smali.getSmaliRoot(path)
            return sName+".smali"
        raise ValueError("Not a smali path:"+path)

    @staticmethod
    def getSmaliMainPath(path):
        """
            get root smali file path of path
            input xx/xx/A$1.smali  return xx/xx/A.smali
        """
        if Smali.isSmali(path):
            sName = Smali.getSmaliRoot(path)
            return os.path.join(os.path.dirname(path), sName+".smali")
        raise ValueError("Not a smali path:"+path)

    @staticmethod
    def getDataFilePath(path):
        """
            get data file path of path
            input xx/xx/A$1.smali  return xx/xx/A.data
        """
        if Smali.isSmali(path):
            sName = Smali.getSmaliRoot(path)
            return os.path.join(os.path.dirname(path), sName+".data")
        raise ValueError("Not a smali path:"+path)
#End of Smali


class Java:
    """
        A Java include a smali file list which built from this java
    """
    def __init__(self, path, name):
        self.path = path
        self.name = name
        self.smaliList = []
        for root, dirs, files in os.walk(self.path):
            dirs[:] = []
            for f in files:
                if Smali.isSmali(f) and self.isInJava(f):
                    self.add(f)

    def add(self, sFile):
        """
            add a smali file to smali file list of this java
        """
        sName = Smali.getSmaliRoot(sFile)
        if (cmp(self.name, sName) == 0):
            self.smaliList.append(sFile)
        else:
            print sName+" not belongs java "+self.name

    def printJava(self):
        print self.path, self.name, "smaliList:"
        print self.smaliList

    def getListLen(self):
        return len(self.smaliList)

    def isInJava(self, sFile):
        """
            check if smali build from java
            input xx/xx/A.$1.smali, self.name=A  return true
        """
        if (cmp(self.name, Smali.getSmaliRoot(sFile)) == 0):
            return True
        return False
#End of Java


class File:
    def __init__(self, path):
        self.path = path

    def replaces(self, sDict):
        """
            replace the key in dict with the value of the key in this File
        """
        sFile = open(self.path, 'r+')
        fileStr = sFile.read()

        for oldStr in sDict.keys():
            fileStr = fileStr.replace(oldStr, sDict[oldStr])

        sFile.seek(0, 0)
        sFile.truncate()
        sFile.write(fileStr)

    def dump(self, dumpStr):
        """
            dump strings into File
        """
        sFile = open(self.path, 'w')
        sFile.seek(0, 0)
        sFile.truncate()
        sFile.write(dumpStr)
        sFile.close()
#End of File


class DataFile:
    @staticmethod
    def isDataFile(path):
        """
            check if the path end of .data
        """
        if re.compile(r'.*\.data', re.S).match(path):
            return True
        return False

    @staticmethod
    def getDataFile(path):
        """
            get basename of path
            input xx/xx/A.data return A.data
        """
        if DataFile.isDataFile(path):
            return os.path.basename(path)
        raise ValueError("Not a data path:"+path)

    @staticmethod
    def getDataFileName(path):
        """
            get data name of path
            input xx/xx/A.data  return A$1
        """
        if DataFile.isDataFile(path):
            basename = DataFile.getDataFile(path)
            return os.path.splitext(basename)[0]
        raise ValueError("Not a data path:"+path)
#End of DataFile


class Method:
    """
        .method static synthetic access$accessnum(parameterlist)returntype
            iput|iget|sput|sget|aput|aget|invoke {..} classname;->operationobject
        .end method

        access$accessnum  <==> access$operation-operationobject-methodlinehash
    """
    def __init__(self, accessNum, parameterList, returnType):
        self.accessNum = accessNum
        self.parameterList = parameterList
        self.returnType = returnType
        self.methodLine = self.parameterList+self.returnType

    def addCallLine(self, operation, operationObject, callLine):
        """
            operation                            {..} classname;->operationobject
            iput|iget|sput|sget|aput|aget|invoke {..} classname;->operationobject
        """
        self.operation = operation
        self.operationObject = operationObject
        self.methodLine = self.methodLine+callLine

    def addMethodLine(self, methodLine):
        self.methodLine = self.methodLine + methodLine

    def endMethod(self):
        self.createMethodName()

    def createMethodName(self):
        """
            access$accessName = access$operation-operationobject-methodlinehash
        """
        self.methodLine = string.replace(self.methodLine, ' ', '')
        self.methodLine = string.replace(self.methodLine, '\n', '')
        self.accessName = self.operation+"-"+self.operationObject+"-"+hashlib.sha1(self.methodLine).hexdigest()[0:6]

    def printMethod(self):
        print "access$"+self.accessNum, "\t", "access$"+self.accessName
#End of Method


class AccessSmali:
    """
        methodNumSet      {accessnum : accessname}
        methodDefNumMap   {.method static synthetic access$accessnum( : .method static synthetic access$accessname( }
        methodCallNumMap  {className;->access$accessnum : className;->access$accessname }

        methodNameSet      {accessname : accessnum}
        methodDefNameMap   {.method static synthetic access$accessname( : .method static synthetic access$accessnum( }
        methodCallNameMap  {className;->access$accessname : className;->access$accessnum }
    """
    def __init__(self, className):
        self.className = className
        self.methodDefBegin = ".method static synthetic access$"
        self.methodDefEnd = "("
        self.methodCallBegin = className+";->access$"
        self.methodCallEnd = "("

        self.methodNumSet = {}
        self.methodDefNumMap = {}
        self.methodCallNumMap = {}

        self.methodNameSet = {}
        self.methodDefNameMap = {}
        self.methodCallNameMap = {}

    def addMethod(self, num, name):
        if num in self.methodNumSet.keys():
            return
        else:
            self.methodNumSet[num] = name
        if name not in self.methodNameSet.keys():
            self.methodNameSet[name] = num

    def readMethod(self, name, num):
        if name not in self.methodNameSet.keys():
            self.methodNameSet[name] = num
        else:
            return

    def createNumMap(self):
        for num in self.methodNumSet.keys():
            self.methodDefNumMap[self.methodDefBegin+num+self.methodDefEnd] = self.methodDefBegin+self.methodNumSet[num]+self.methodDefEnd
            self.methodCallNumMap[self.methodCallBegin+num+self.methodCallEnd] = self.methodCallBegin+self.methodNumSet[num]+self.methodCallEnd

    def createNameMap(self):
        for name in self.methodNameSet.keys():
            self.methodDefNameMap[self.methodDefBegin+name+self.methodDefEnd] = self.methodDefBegin+self.methodNameSet[name]+self.methodDefEnd
            self.methodCallNameMap[self.methodCallBegin+name+self.methodCallEnd] = self.methodCallBegin+self.methodNameSet[name]+self.methodCallEnd

    def getMethodNumSetLen(self):
        return len(self.methodNumSet)

    def getMethodNameSetLen(self):
        return len(self.methodNameSet)

    def printMethodNumSet(self):
        for k in self.methodNumSet.keys():
            print self.className+": access$"+k+"\t"+" access$"+self.methodNumSet[k]

    def printMethodNameSet(self):
        for k in self.methodNameSet.keys():
            print self.className+": access$"+k+"\t"+" access$"+self.methodNameSet[k]

#End of AccessSmali
