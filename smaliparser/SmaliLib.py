'''
Created on Feb 28, 2014

@author: tangliuxiang
'''

import Smali
import SmaliEntry
import string
import os
import utils
import sys
import SmaliMethod
import traceback

MAX_CHECK_INVOKE_DEEP = 50

class SmaliLib(object):
    '''
    classdocs
    '''
    def __init__(self, libPath, smaliDirMaxDepth=0):
        '''
        Constructor
        '''
        self.mSDict = utils.getSmaliDict(libPath, smaliDirMaxDepth)
        self.mCalledMethods = None
        self.mSmaliRoot = None
        self.mAlreadyParsedInvoke = False
        self.mPath = libPath
        self.mFieldFormatMap = {}
        self.mSmaliFileList = None
        self.mSmaliDirMaxDepth = smaliDirMaxDepth

    def cleanModify(self):
        for cls in self.mSDict.keys():
            self.mSDict[cls].cleanModify()
    
    def replaceEntry(self, srcLib, entry, printOut=True, out=True, noAdd=False):
        clsName = entry.getClassName()
        type = entry.getType()
        name = entry.getName()
        
        srcSmali = srcLib.getFormatSmali(clsName)
        dstSmali = self.getFormatSmali(clsName)
        
        srcEntry = srcSmali.getEntry(type, name)
        if dstSmali.hasEntry(type, name):
            dstEntry = dstSmali.getEntry(type, name)
            if not dstEntry.getContentStr() == srcEntry.getContentStr():
                if (srcEntry.getName() == 'needNewResources(II)Z'):
                    print srcEntry.getPreContentStr()
                dstSmali.replaceEntry(srcEntry, utils.annotation.getReplaceToBospPreContent(entry))
                if (srcEntry.getName() == 'needNewResources(II)Z'):
                    print srcEntry.getPreContentStr()
                #if printOut:
                if True:
                    utils.SLog.ok("        Replace %s %s from %s to %s" % (type, name, srcSmali.getPath(), dstSmali.getPath()))
        elif not noAdd:
            idx = srcSmali.getIndex(srcEntry) - 1
            bospEntryList = srcSmali.getEntryList()
            while idx >= 0 and not dstSmali.hasEntry(bospEntryList[idx].getType(), bospEntryList[idx].getName()) :
                idx = idx - 1
            
            if idx >= 0:
                idx = dstSmali.getIndex(dstSmali.getEntry(bospEntryList[idx].getType(), bospEntryList[idx].getName())) + 1
            
            if printOut:
                utils.SLog.ok("        Add %s %s from %s to %s" % (type, name, srcSmali.getPath(), dstSmali.getPath()))
            dstSmali.addEntry(srcEntry, idx, utils.annotation.getAddToBospPreContent(entry))
        if out:
            dstSmali.out()
        return dstSmali
    
    def out(self):
        for cls in self.mSDict.keys():
            smali = self.mSDict.get(cls)
            if smali.isModifed():
                smali.out()
    
    def getSmaliFileList(self):
        if self.mSmaliFileList is None:
            self.mSmaliFileList = []
            for clsName in self.mSDict.keys():
                self.mSmaliFileList.append(self.getSmali(clsName).getPath())
        return self.mSmaliFileList
    
    def getPath(self):
        return self.mPath
        
    def getSmali(self, className):
        if self.mSDict.has_key(className):
            return self.mSDict[className]
        
        return None
    
    def setSmali(self, className, smali):
        self.mSDict[className] = smali
    
    def getSuperSmali(self, child):
        return self.getSmali(child.getSuperClassName())
    
    def generateSmaliTree(self):
        if self.mSmaliRoot is None:
            self.mSmaliRoot = self.getSmali("Ljava/lang/Object;")
            for clsName in self.mSDict.keys():
                smali = self.getSmali(clsName)
                superClsName = smali.getSuperClassName()
                superSmali = self.getSmali(superClsName)
                if superSmali is not None:
                    superSmali.addChild(smali.getClassName())
    
    def getInheritMethods(self, child, filterInList=None, filterOutList=None):
        methodsList = []
        
        for clsName in child.getSuperAndImplementsClassName():
            superSmali = self.getSmali(clsName)
            if superSmali is None:
                utils.SLog.d("can not get %s's super class: %s" % (child.getClassName(), clsName))
                continue
            
            methodsList.extend(self.getInheritMethods(superSmali, filterInList, filterOutList))
            methodsList.extend(superSmali.getEntryList(SmaliEntry.METHOD, filterInList, filterOutList))
        
        return methodsList

    def getAllMethods(self, smali):
        superFilterOutList = [utils.KEY_PRIVATE]
        if not smali.isInterface() and not smali.isAbstractClass():
            superFilterOutList.append(utils.KEY_ABSTRACT)
        methodsList = self.getInheritMethods(smali, None, superFilterOutList)
        methodsList.extend(smali.getEntryList(SmaliEntry.METHOD))
        
        return methodsList

    def getAllFields(self, smali):
        fieldsList = smali.getEntryList(SmaliEntry.FIELD)
        for clsName in self.getAllFathers(smali):
            cSmali = self.getSmali(clsName)
            if cSmali is not None and not cSmali.isInterface():
                fieldsList.extend(cSmali.getEntryList(SmaliEntry.FIELD, None, [utils.KEY_PRIVATE]))
        return fieldsList
    
    def getNeedOverrideMethods(self, smali):
        overrideMethodsList = []
        
        superClsNameList = smali.getEntryNameList(SmaliEntry.IMPLEMENTS)
        superClsName = smali.getSuperClassName()
        
        if superClsName is not None:
            superClsNameList.append(superClsName)
        
        for clsName in superClsNameList:
            superSmali = self.getSmali(clsName)
            assert superSmali is not None, "Error: can not find class: %s" % (clsName)
            
            overrideMethodsList.extend(self.getNeedOverrideMethods(superSmali))
            overrideMethodsList.extend(superSmali.getAbstractMethodsNameList())
            
        return overrideMethodsList

    def __parseAllInvoke(self):
        if self.mAlreadyParsedInvoke:
            return

        self.generateSmaliTree()
        for clsName in self.mSDict.keys():
            smali = self.mSDict[clsName]
            for invokeItem in smali.getInvokeMethods():
                cSmali = self.getSmali(invokeItem.cls)
                if cSmali is not None:
                    cSmali.wasInvoke(invokeItem)
        self.mAlreadyParsedInvoke = True
    
    def getCalledMethod(self, smali):
        self.__parseAllInvoke()
        cSmali = self.getSmali(smali.getClassName())
        if cSmali is not None:
            return cSmali.getWasInvokeList()
        else:
            utils.SLog.d("can not get class %s from smali lib" % (smali.getClassName()))
            return []
        
    def getAllFathers(self, smali, allowDuplicate = False):
        if smali is None:
            return []
        allFathersList = []
        for clsName in smali.getSuperAndImplementsClassName():
            cSmali = self.getSmali(clsName)
            if cSmali is not None:
                allFathersList.append(clsName)
        
        for clsName in smali.getSuperAndImplementsClassName():
            cSmali = self.getSmali(clsName)
            if cSmali is not None:
                allFathersList.extend(self.getAllFathers(cSmali))
        
        if allowDuplicate:
            return allFathersList
        else:
            return list(set(allFathersList))
        
    def getAbstractMethodsNameList(self, smali):
        absMethodsNameList = smali.getAbstractMethodsNameList()
        for clsName in self.getAllFathers(smali):
            cSmali = self.getSmali(clsName)
            absMethodsNameList.append(cSmali.getAbstractMethodsNameList())
        return list(set(absMethodsNameList))
    
    def __getSuperCalledMethods__new(self, smali):
        superCalledMethods = {}
        for clsName in self.getAllFathers(smali):
            cSmali = self.getSmali(clsName)
            if cSmali.isInterface():
                if superCalledMethods.has_key(clsName):
                    superCalledMethods[clsName] = dict(superCalledMethods[clsName], **self.getCalledMethod(cSmali))
                else:
                    superCalledMethods[clsName] = self.getCalledMethod(cSmali)
            elif cSmali.isAbstractClass():
                absMethodsNameList = cSmali.getAbstractMethodsNameList()
                sCalledMethods = self.getCalledMethod(cSmali)
                
                for method in sCalledMethods.keys():
                    for absMethodName in absMethodsNameList:
                        if method == absMethodName:
                            if not superCalledMethods.has_key(cSmali):
                                superCalledMethods[cSmali] = {}
                            superCalledMethods[cSmali][method] = sCalledMethods[method]
                            break
        return superCalledMethods
        
    def __getSuperCalledMethods__(self, smali):
        superCalledMethods = {}
        
        superClsName = smali.getSuperClassName()
        if superClsName is not None and self.getSmali(superClsName) is not None:
            superSmali = self.getSmali(superClsName)
            sCalledMethods = self.getCalledMethod(superSmali)
            absMethodsNameList = superSmali.getAbstractMethodsNameList()
            superCalledMethods = self.__getSuperCalledMethods__(superSmali)
            
            for method in sCalledMethods.keys():
                for absMethodName in absMethodsNameList:
                    if method == absMethodName:
                        if not superCalledMethods.has_key(superClsName):
                            superCalledMethods[superClsName] = {}
                        superCalledMethods[superClsName][method] = sCalledMethods[method]
                        break
        
        for clsName in smali.getImplementClassList():
            superSmali = self.getSmali(clsName)
            if superSmali is not None:
                assert superSmali.isAbstractClass() and superSmali.isInterface(), "Error: class %s was implement by %s, it should be interface!" % (clsName, smali.getClassName())
                if superCalledMethods.has_key(clsName):
                    superCalledMethods[clsName] = dict(superCalledMethods[clsName], **self.getCalledMethod(superSmali))
                else:
                    superCalledMethods[clsName] = self.getCalledMethod(superSmali)
        return superCalledMethods
    
    def __dict(self, dict1, dict2):
        newDict = dict1.copy()
        for key in dict2.keys():
            if newDict.has_key(key):
                newDict[key].extend(dict2[key])
            else:
                newDict[key] = dict2[key]
        return newDict
    
    def __getSelfAndSuperCalledMethods__(self, smali):
        allCalledMethods = {}
        allCalledMethods[smali.getClassName()] = self.getCalledMethod(smali)
        if not smali.isInterface() and not smali.isAbstractClass():
            allCalledMethods = self.__dict(allCalledMethods, self.__getSuperCalledMethods__new(smali))
        return allCalledMethods
    
    def __getUnImplementMethods__(self, smali, selfMethods):
        usedMethodsList = {}
        allCalledMethodDict = self.__getSelfAndSuperCalledMethods__(smali)
        
        for clsName in allCalledMethodDict.keys():
            for method in allCalledMethodDict[clsName]:
                hasMethod = False
                for sMethod in selfMethods:
                    if method == sMethod.getName():
                        hasMethod = True
                        break;
                if hasMethod is False:
                    if not usedMethodsList.has_key(method):
                        usedMethodsList[method] = []
                    usedMethodsList[method].extend(allCalledMethodDict[clsName][method])

        return usedMethodsList
    
    def getUsedMethods(self, smali, selfMethods=None):
        if selfMethods is None:
            selfMethods = self.getAllMethods(smali)
        usedMethodsList = {}
        allCalledMethodDict = self.__getSelfAndSuperCalledMethods__(smali)
        for method in selfMethods:
            for clsName in allCalledMethodDict.keys():
                for methodName in allCalledMethodDict[clsName]:
                    if methodName == method.getName():
                        if not usedMethodsList.has_key(methodName):
                            usedMethodsList[methodName] = []
                        usedMethodsList[methodName].extend(allCalledMethodDict[clsName][methodName])
                        break
                    
                if usedMethodsList.has_key(method.getName()) and \
                len(usedMethodsList[method.getName()]) >= Smali.MAX_INVOKE_LEN:
                    break

        return usedMethodsList

    def getBelongClass(self, smali, type, name):
        if type != SmaliEntry.FIELD:
            utils.SLog.e("not support getBelongClass for type: %s" % type)
            return None

        if smali.hasEntry(type, name):
            return smali.getClassName()

        allClsName = self.getAllFathers(smali, True)
        for clsName in allClsName:
            cSmali = self.getSmali(clsName)
            assert cSmali is not None, "Error: can not get class from: %s" % (self.getPath())
            if cSmali.hasEntry(type, name):
                return cSmali.getClassName()
        return None

    def checkMethods(self, smali):
#        if smali.isAbstractClass() or smali.isInterface():
#            return
        
        allCalledMethods = self.getCalledMethod(smali)
        if not smali.isInterface() and not smali.isAbstractClass():
            mergedDict = self.__dict(allCalledMethods, self.__getSuperCalledMethods__(smali))
            allCalledMethods = mergedDict
        
        for key in allCalledMethods.keys():
            splitArray = key.split(':')
            assert len(splitArray) == 2, "Life is hard...."
            type = splitArray[0]
            method = splitArray[1]
            
            hasMethod = False
            for sMethod in self.getAllMethods(smali):
                if method == sMethod.getName():
                    hasMethod = True
                    break;
            if hasMethod is False:
                utils.SLog.e("%s doesn't has method %s, was called by: %s" % (smali.getClassName(), method, string.join(allCalledMethods[key])))

    def formatUsingField(self, smali):
        if smali is None:
            return

        usedOutsideFields = smali.getUsedOutsideFields()

        if usedOutsideFields is not None and len(usedOutsideFields) > 0:
            for usedFieldsItem in usedOutsideFields:
                key = r'%s->%s' % (usedFieldsItem.cls, usedFieldsItem.field)
                uSmali = self.getSmali(usedFieldsItem.cls)
                if uSmali is not None and not self.mFieldFormatMap.has_key(key):
                    belongCls = self.getBelongClass(uSmali, SmaliEntry.FIELD, usedFieldsItem.field)
                    if belongCls is not None and belongCls != uSmali.getClassName():
                        targetKey = r'%s->%s' % (belongCls, usedFieldsItem.field)
                        utils.SLog.d("change %s to %s" % (key, targetKey))
                        self.mFieldFormatMap[key] = targetKey
            if smali.formatUsingField(self.mFieldFormatMap):
                smali.out()
                
    def undoFormatUsingField(self, smali):
        if smali is None:
            return
        
        if smali.undoFormatUsingField():
            smali.out()
        
    def getEntryList(self, oriEntryList):
        outEntryList = []
        for entry in oriEntryList:
            clsName = entry.getClassName()
            smali = self.getSmali(clsName)
            
            if smali is not None:
                nEntry = smali.getEntry(entry.getType(), entry.getName())
                if nEntry is not None:
                    outEntryList.append(nEntry)
        return outEntryList

    def getMissedMethods(self, invokeMethods):
        missedMethods = []
        for invokeItem in invokeMethods:
            cSmali = self.getSmali(invokeItem.cls)
            assert cSmali is not None, "Error: doesn't have class: %s" % invokeItem.cls

            hasMethod = False
            for mEntry in self.getAllMethods(cSmali):
                if invokeItem.method == mEntry.getName():
                    hasMethod = True
                    break
            if not hasMethod:
                utils.SLog.d("class: %s doesn't have method: %s" % (invokeItem.cls, invokeItem.method))
                missedMethods.append(invokeItem)
        return missedMethods

    def getMissedFields(self, usedFields):
        missedFields = []
        for usedFieldItem in usedFields:
            cSmali = self.getSmali(usedFieldItem.cls)
            assert cSmali is not None, "Error: doesn't have class: %s" % usedFieldItem.cls

            hasField = False
            for mEntry in self.getAllFields(cSmali):
                if usedFieldItem.field == mEntry.getName():
                    hasField = True
                    break
            if not hasField:
                utils.SLog.d("class: %s doesn't have field: %s" % (usedFieldItem.cls, usedFieldItem.field))
                missedFields.append(usedFieldItem)
        return missedFields

    def isMethodUsed(self, asLib, smali, methodName, deep = 0):
        sMethodEntry = smali.getEntry(SmaliEntry.METHOD, methodName)
        if sMethodEntry is not None:
            aSmali = asLib.getSmali(smali.getClassName())
            if aSmali is not None and aSmali.getEntry(SmaliEntry.METHOD, methodName) is not None:
                return True
            
            usedMethodsList = self.getUsedMethods(smali, [sMethodEntry])
            
            if not usedMethodsList.has_key(methodName):
                for childClsName in smali.getChildren():
                    cSmali = self.getSmali(childClsName)
                    if cSmali is not None and self.isMethodUsed(asLib, cSmali, methodName):
                        return True
            else:
                if len(usedMethodsList) < Smali.MAX_INVOKE_LEN and deep < MAX_CHECK_INVOKE_DEEP:
                    isUsed = False
                    for invokeItem in usedMethodsList[methodName]:
                        cSmali = self.getSmali(invokeItem.belongCls)
                        if cSmali is not None and self.isMethodUsed(asLib, cSmali, invokeItem.belongMethod, deep + 1):
                            isUsed = True
                            break
                    return isUsed
                else:
                    return True
        return False

    def getUnImplementMethods(self, asLib, smali):
        unImplementMethods = []
        methodsList = self.__getUnImplementMethods__(smali, self.getAllMethods(smali))
        for key in methodsList.keys():
            if len(methodsList[key]) >= Smali.MAX_INVOKE_LEN:
                unImplementMethods.append(key)
                continue

            for invokeItem in methodsList[key]:
                cSmali = self.getSmali(invokeItem.belongCls)
                if cSmali is None:
                    continue
                
                if self.isMethodUsed(asLib, cSmali, invokeItem.belongMethod):
                    unImplementMethods.append(key)
                    break
        return unImplementMethods

    # targetLib is which you already merged 
    # sourceLib is which you want get the replace method
    def getCanReplaceEntry(self, sourceLib, clsName, methodEntryList, allowBlank = True):
        canReplaceEntryList = []
        canNotReplaceEntryList = []
        for mEntry in methodEntryList:
            methodName = mEntry.getName()
            utils.SLog.d("Check if can replace method: %s in class: %s" %(methodName, clsName))
    
            if mEntry is None:
                utils.SLog.e("Baidu doesn't have this Method: %s" %clsName)
                continue
            
            tSmali = self.getSmali(mEntry.getClassName())
            sSmali = sourceLib.getSmali(mEntry.getClassName())
            if not utils.preCheck(tSmali, sSmali, mEntry):
                canNotReplaceEntryList.append(mEntry)
                continue
            
            try:
                missedFields = self.getMissedFields(mEntry.getUsedFields())
                canIgnore = True
                outMissedFieldsList = []
                for usedField in missedFields:
                    cSmali = sourceLib.getSmali(usedField.cls)
                    if cSmali is None:
                        canIgnore = False
                        break
                    
                    fieldEntry = cSmali.getEntry(SmaliEntry.FIELD, usedField.field)
                    if fieldEntry is None or (not SmaliMethod.isPutUseField(usedField) and not utils.precheck.canAddField(fieldEntry)):
                        canIgnore = False
                        break
                    else:
                        outMissedFieldsList.append(fieldEntry)
                if canIgnore:
                    canReplaceEntryList.extend(outMissedFieldsList)
                else:
                    canNotReplaceEntryList.append(mEntry)
                    continue
            except Exception as e:
                utils.SLog.d(e)
                canNotReplaceEntryList.append(mEntry)
                utils.SLog.d("can not replace method: %s in class: %s" %(methodName, clsName))
                continue
            
            try:
                missedMethods = self.getMissedMethods(mEntry.getInvokeMethods())
                missedMethodDict = {}
                for invokeItem in missedMethods:
                    if not missedMethodDict.has_key(invokeItem.cls):
                        missedMethodDict[invokeItem.cls] = []
                    missedMethodDict[invokeItem.cls].append(invokeItem.method)
                    
                missedClass = False
                for cls in missedMethodDict.keys():
                    cSmali = sourceLib.getSmali(cls)
                    if cSmali is None:
                        canIgnore = False
                        missedClass = True
                        canNotReplaceEntryList.append(mEntry)
                        break
    
                    entryList = cSmali.getEntryListByNameList(SmaliEntry.METHOD, missedMethodDict[cls])
                    (cEntryList, nEntryList) = self.getCanReplaceEntry(sourceLib, cls, entryList, allowBlank)
                    if len(nEntryList) > 0:
                        canIgnore = False
                    canReplaceEntryList.extend(cEntryList)
                    canNotReplaceEntryList.extend(nEntryList)
                if not missedClass and (canIgnore or allowBlank):
                    canReplaceEntryList.append(mEntry)
                else:
                    canNotReplaceEntryList.append(mEntry)
                missedMethodDict.clear()
            except Exception as e:
                utils.SLog.d(e)
                canNotReplaceEntryList.append(mEntry)
                utils.SLog.d("can not replace method: %s in class: %s" %(methodName, clsName))
                continue
    
        return list(set(canReplaceEntryList)), list(set(canNotReplaceEntryList))
def __getSplitItem__(string, sep, idx=0):
    splitArray = string.split(sep)
    assert len(splitArray) > idx, "Life is hard...."
    return splitArray[idx]
        
