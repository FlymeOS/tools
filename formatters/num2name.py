#!/usr/bin/env python

__author__ = 'zhangweiping@baiyi-mobile.com'

import re
import os
import sys

from common import Smali
from common import Java
from common import File
from common import AccessSmali
from common import Method
from common import DataFile

# method pattern
patternMethodBegin = re.compile(r'\.method static synthetic access\$(?P<accessnum>\d+)\((?P<parameterlist>.*?)\)(?P<returntype>.*?)\s', re.S)
patternMethodAnnotation = re.compile(r' *\.| *$', re.S)
patternMethodCall = re.compile(r'\s*(?P<operation>iput|iget|sput|sget|aput|aget|invoke).*? (?P<classname>L.*?);->(?P<operationobject>.*?)(:|\(.*\))', re.S)
patternMethodEnd = re.compile(r'\.end method', re.S)

class NumToName:
    def __init__(self, name, path, smaliList):
        self.name = name
        self.path = path
        self.smaliList = smaliList
        self.accessSmaliSet = {}
        self.getAccessSmaliSet()

    def getAccessSmaliSet(self):
        """ check smalilist to build access num to name map """
        for s in self.smaliList:
            sName = Smali.getSmaliName(s)
            aSmali = AccessSmali(sName)
            mode = 0
            method = ""
            for line in open(os.path.join(self.path, s), 'r'):
                if (mode == 0):
                    match = patternMethodBegin.match(line)
                    if(match):
                        method = Method(match.group("accessnum"), match.group("parameterlist"), match.group("returntype"))
                        mode = 1
                elif (mode == 1):
                    match = patternMethodEnd.match(line)
                    if(match):
                        method.endMethod()
                        mode = 0
                        aSmali.addMethod(method.accessNum, method.accessName)
                    else:
                        match = patternMethodAnnotation.match(line)
                        if(match):
                            continue
                        match = patternMethodCall.match(line)
                        if(match):
                            method.addCallLine(match.group("operation"), match.group("operationobject"), match.group(0))
                        else:
                            method.addMethodLine(line)
            if (aSmali.getMethodNumSetLen() > 0):
                aSmali.createNumMap()
                self.accessSmaliSet[sName] = aSmali

    def printAccessSmaliSet(self):
        for sName in self.accessSmaliSet.keys():
            self.accessSmaliSet[sName].printMethodNumSet()

    def doNumToName(self):
        allMethodCallNumMap = {}
        for sName in self.accessSmaliSet.keys():
            callNumMap = self.accessSmaliSet[sName].methodCallNumMap
            for callNum in callNumMap.keys():
                if callNum not in allMethodCallNumMap.keys():
                    allMethodCallNumMap[callNum] = callNumMap[callNum]
                else:
                    raise ValueError("method call num map duplicate")

        for s in self.smaliList:
            sFile = File(os.path.join(self.path, s))
            sName = Smali.getSmaliName(s)
            if sName in self.accessSmaliSet.keys():
                sFile.replaces(self.accessSmaliSet[sName].methodDefNumMap)
            sFile.replaces(allMethodCallNumMap)

    def dumpMap(self):
        """
            smalirootname.data:
    	    smaliname accessname accessnum
        """
        dumpStr = ""
        for sName in self.accessSmaliSet.keys():
            nameSet = self.accessSmaliSet[sName].methodNameSet
            for name in nameSet.keys():
                dumpStr=(dumpStr+sName+" "+name+" "+nameSet[name]+"\n")
        File(os.path.join(self.path, self.name+".data")).dump(dumpStr)
#End of NumToName


def NumToNameForOneFile(path):
    if Smali.isSmali(path):
        path = Smali.getSmaliMainPath(path)
    else:
        return
    if os.path.exists(path):
        fDir = os.path.dirname(path)
        if cmp(fDir, "") == 0:
            fDir = "."
        name = Smali.getSmaliRoot(path)
    else:
        return
    
    if os.path.exists(os.path.join(fDir, name)+".data"):
        if False: print "NumToName: "+os.path.join(fDir, name)+".data is exist, ignore!"
        return os.path.join(fDir, name) + ".data"

    java = Java(fDir, name)
    #java.printJava()
    if java.getListLen() == 0:
        if False: print "Can not find smali file: "+os.path.join(java.path, java.name)+"*.smali"
        return

    toName = NumToName(java.name, java.path, java.smaliList)
    #toName.printAccessSmaliSet()
    toName.doNumToName()

    toName.dumpMap()

    return os.path.join(java.path, java.name) + ".data"


def Usage():
    print "Usage: num2name.py  aa/bb/A.smali"
    print "       num2name.py  aa/bb/B$1.smali"
    print "       num2name.py  aa/bb"

if __name__ == '__main__':
    argLen = len(sys.argv)
    if argLen == 2:
        path = sys.argv[1]
        if Smali.isSmali(path):
            NumToNameForOneFile(path)

        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for sfile in files:
                    fPath = os.path.join(root, sfile)
                    if Smali.isRootSmali(fPath):
                        NumToNameForOneFile(fPath)

        else:
            Usage()
    else:
        Usage()






