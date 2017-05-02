'''
Created on Jun 25, 2014

@author: tangliuxiang
'''

import utils
import SmaliEntry
import Smali

MAX_CHECK_INVOKE_DEEP = 50

class Used(object):
    '''
    classdocs
    '''

    def __init__(self, sLib, aLib):
        '''
        Constructor
        '''
        self.mSLib = sLib
        self.mALib = aLib
        self.mMethodParser = MethodUsedParser(sLib, aLib)
        self.mFieldParser = FieldUsedParser(sLib, aLib)
        
    def isUsed(self, entry):
        if entry.getType() == SmaliEntry.FIELD:
            return self.mFieldParser.isUsed(entry)
        elif entry.getType() == SmaliEntry.METHOD:
            return self.mMethodParser.isUsed(entry)
        else:
            return False
    
    def checkIsUsed(self, entry, deep = 0):
        if entry is not None:
            clsName = entry.getClassName()
            entryName = entry.getName()
            aSmali = self.mALib.getSmali(entry.getClassName())
            if aSmali is not None and aSmali.getEntry(SmaliEntry.METHOD, entryName) is not None:
                return True
            
            sSmali = self.mSLib.getSmali(clsName)
            usedMethodsList = self.getUsedMethods(sSmali, [entry])
            
            if not usedMethodsList.has_key(entryName):
                for childClsName in sSmali.getChildren():
                    cSmali = self.mSLib.getSmali(childClsName)
                    if cSmali is not None and self.checkIsUsed(cSmali.getEntry(SmaliEntry.METHOD, entryName)):
                        return True
            else:
                if len(usedMethodsList) < Smali.MAX_INVOKE_LEN and deep < MAX_CHECK_INVOKE_DEEP:
                    isUsed = False
                    for invokeItem in usedMethodsList[entryName]:
                        cSmali = self.mSLib.getSmali(invokeItem.belongCls)
                        if cSmali is not None and self.checkIsUsed(cSmali.getEntry(SmaliEntry.METHOD, invokeItem.belongMethod), deep + 1):
                            isUsed = True
                            break
                    return isUsed
                else:
                    return True
        return False

class MethodUsedParser(Used):
    def checkIsUsed(self, entry):
        return False

    
class FieldUsedParser(Used):
    def checkIsUsed(self, entry):
        print ""
    