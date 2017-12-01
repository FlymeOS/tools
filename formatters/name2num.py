#!/usr/bin/env python

__author__ = 'zhangweiping@baiyi-mobile.com'

import os
import sys

from common import Smali
from common import Java
from common import File
from common import DataFile
from common import AccessSmali

class NameToNum:
    def __init__(self, name, path, smaliList):
        self.name = name
        self.path = path
        self.smaliList = smaliList
        self.accessSmaliSet = {}
        self.getAccessSmaliSet()

    def getAccessSmaliSet(self):
        dFile = open(os.path.join(self.path, self.name+".data"), 'r')
        for line in dFile.readlines():
            tList = line.split()
            sName = tList[0]
            name = tList[1]
            num = tList[2]
            if (sName not in self.accessSmaliSet.keys()):
                self.accessSmaliSet[sName] = AccessSmali(sName)
            self.accessSmaliSet[sName].readMethod(name, num)
        dFile.close()

    def printAccessSmaliSet(self):
        for sName in self.accessSmaliSet.keys():
            self.accessSmaliSet[sName].printMethodNameSet()

    def doNameToNum(self):
        allMethodCallNameMap = {}
        for aSmali in self.accessSmaliSet.keys():
            self.accessSmaliSet[aSmali].createNameMap()
            callNameMap = self.accessSmaliSet[aSmali].methodCallNameMap
            for callName in callNameMap.keys():
                if callName not in allMethodCallNameMap.keys():
                    allMethodCallNameMap[callName] = callNameMap[callName]
                else:
                    raise ValueError("method call name map duplicate")

        for s in self.smaliList:
            sFile = File(os.path.join(self.path, s))
            sName = Smali.getSmaliName(s)
            if sName in self.accessSmaliSet.keys():
                sFile.replaces(self.accessSmaliSet[sName].methodDefNameMap)
            sFile.replaces(allMethodCallNameMap)
#End of NameToNum


def NameToNumForOneFile(path):
    if Smali.isSmali(path):
        path = Smali.getDataFilePath(path) #change smali path to data file path
    if DataFile.isDataFile(path) and os.path.exists(path):
        fDir = os.path.dirname(path)
        if cmp(fDir, "") == 0:
            fDir = "."
        name = DataFile.getDataFileName(path)
    else:
        return

    java = Java(fDir, name)
    #java.printJava()
    if java.getListLen() == 0:
        print "Can not find data file: "+os.path.join(java.path, java.name)+".data"
        return

    if False: print "NameToNum: "+os.path.join(java.path, java.name)+".data"
    toNum = NameToNum(java.name, java.path, java.smaliList)
    #toNum.printAccessSmaliSet()
    toNum.doNameToNum()

    os.remove(path)


def Usage():
    print "Usage: name2num.py  aa/bb/A.data"
    print "       name2num.py  aa/bb/A.smali"
    print "       name2num.py  aa/bb"

if __name__ == '__main__':
    argLen = len(sys.argv)
    if argLen == 2:
        path = sys.argv[1]
        if os.path.isfile(path) and (DataFile.isDataFile(path) or Smali.isSmali(path)):
            NameToNumForOneFile(path)

        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for sfile in files:
                    fPath = os.path.join(root, sfile)
                    if DataFile.isDataFile(fPath):
                        NameToNumForOneFile(fPath)

        else:
            Usage()
    else:
        Usage()
