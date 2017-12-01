#!/usr/bin/env python

'''
Created on 2012-12-11

@author: tangliuxiang
'''

import re
import sys
import os
import utils

from SmaliEntry import SmaliEntry

INVOKE_DIRECT = "invoke-direct"
INVOKE_INTERFACE = "invoke-interface"
INVOKE_STATIC = "invoke-static"
INVOKE_SUPER = "invoke-super"
INVOKE_VIRTUAL = "invoke-virtual"

INVOKE_RE = re.compile("^ *invoke-.*$", re.M)
USE_FIELD_RE = re.compile("^ *iget.*$|^ *iput.*$|^ *sget.*$|^ *sput.*$", re.M)
PUT_FIELD_RE = re.compile("iput.*|sput.*")

class Invoke(object): pass
class UsedField(object): pass

def isPutUseField(usedField):
    if PUT_FIELD_RE.match(usedField.type) is not None:
        return True
    return False

class SmaliMethod(SmaliEntry):
    '''
    classdocs
    '''
    def __init__(self, type, content, clsName, preContent=None):
        super(SmaliMethod, self).__init__(type, content, clsName, preContent)
        self.mInvokeMethods = None
        self.mUsedFields = None
    
    def __getInvokeMethods__(self):
        invokeMethodsList = []
        for line in self.getContentStr().split('\n'):
            if INVOKE_RE.match(line) is not None:
                splitArray = line.split()
                invokeItem = Invoke()
                assert len(splitArray) >= 2, "Wrong invoke: %s" %line
                invokeItem.type = splitArray[0].split(r'/')[0]
            
                splitArrayNew = splitArray[len(splitArray) - 1].split('->')
                assert len(splitArrayNew) == 2, "Wrong invoke: %s" %line
                
                if splitArrayNew[0][0] == r'[':
                    #print ">>> ignore cls: %s" % splitArrayNew[0]
                    continue
                
                invokeItem.cls = splitArrayNew[0]
                invokeItem.method = splitArrayNew[1]
                invokeItem.belongMethod = self.getName()
                invokeItem.belongCls = self.mClsName
            
                invokeMethodsList.append(invokeItem)
        return list(set(invokeMethodsList))

    def getInvokeMethods(self):
        if self.mInvokeMethods is None:
            self.mInvokeMethods = self.__getInvokeMethods__()
            
        return self.mInvokeMethods

    def __getUsedFields__(self):
        usedFieldsList = []
        for line in self.getContentStr().split('\n'):
            if USE_FIELD_RE.match(line) is not None:
                splitArray = line.split()
                usedField = UsedField()
                assert len(splitArray) >= 2, "Wrong field get or put: %s" %line
                usedField.type = splitArray[0].split(r'/')[0]
            
                splitArrayNew = splitArray[len(splitArray) - 1].split('->')
                assert len(splitArrayNew) == 2, "Wrong field get or put: %s" %line
                usedField.cls = splitArrayNew[0]
                usedField.field = splitArrayNew[1]
            
                usedFieldsList.append(usedField)
        return list(set(usedFieldsList))
    
    def getUsedFields(self):
        if self.mUsedFields is None:
            self.mUsedFields = self.__getUsedFields__()

        return self.mUsedFields

    def formatUsingField(self, formatMap):
        entryStr = self.getContentStr()
        modifed = False
        for usedFieldItem in self.getUsedFields():
            key = r'%s->%s' % (usedFieldItem.cls, usedFieldItem.field)
            if formatMap.has_key(key):
                modifed = True
                entryStr = entryStr.replace(key, formatMap[key])
        if modifed:
            self.setContentStr(entryStr)
        return modifed

    def getReturnType(self):
        return getReturnType(self.getName())
    
    def isConstructor(self):
        return self.hasKey(utils.KEY_CONSTRUCTOR)
    
    def getSimpleName(self):
        return self.getName().split('(')[0]
    
def getReturnType(methodName):
    splitArray = methodName.split(r')')
    if len(splitArray) < 2:
        utils.SLog.w("method %s return nothing!" %methodName)
        return ""
    else:
        return splitArray[-1]
