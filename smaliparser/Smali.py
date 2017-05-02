'''
Created on Feb 26, 2014

@author: tangliuxiang
'''

import os
import re
import SmaliEntry
import hashlib
import SmaliParser
import utils

from Content import Content

MAX_INVOKE_LEN = 5
DEBUG = True

DEFAULT_SUPER = r'Ljava/lang/Object;'

class Smali(object):
    '''
    classdocs
    '''

    def __init__(self, smaliFilePath):
        '''
        Constructor
        '''
        self.mPath = smaliFilePath
        self.mParser = SmaliParser.SmaliParser(smaliFilePath, False)
        self.mInvokeMethods = None
        self.mAllMethods = None
        self.mImplementsClassList = None
        self.mChildrenClsNameList = []
        self.__mWasInvokedList = {}
        self.mClassName = None
        self.mSuperClassName = None
        self.mSourceName = None
        self.mPackageName = None
        self.mUsedOutsideFields = None
        self.mUsedFields = None
        self.mMemberClasses = None
        self.mIsPartSmali = utils.isPartSmaliFile(smaliFilePath)
        self.mModifed = False
        self.mDefaultOutPath = None
        self.mPreOutPath = None
        self.mFormatMapFile = "%s.fieldMap" %(self.mPath)
 
    def useField(self, name):
        pass
    
    def wasInvoke(self, invokeItem, check = False):
        if check and not self.checkInvokeType(invokeItem.method, invokeItem.type):
            utils.SLog.e("wrong invoke in class %s, method: %s, invoke method: %s, invoke type: %s" %(invokeItem.cls, invokeItem.belongMethod, invokeItem.method, invokeItem.type))
            return False
        
        if not self.__mWasInvokedList.has_key(invokeItem.method):
            self.__mWasInvokedList[invokeItem.method] = []
        if len(self.__mWasInvokedList[invokeItem.method]) < MAX_INVOKE_LEN:
                self.__mWasInvokedList[invokeItem.method].append(invokeItem)

    def getWasInvokeList(self):
        return self.__mWasInvokedList
    
    def checkInvokeType(self, methodName, invokeType):
        if invokeType is None:
            return True
        else:
            # need write function to check invoke type
            return True

    def addChild(self, childClsName):
        self.mChildrenClsNameList.append(childClsName)
    
    def getChildren(self):
        return self.mChildrenClsNameList
    
    def hasChild(self, child):
        for ch in self.mChildrenClsNameList:
            if ch == child:
                return True
        return False

    def getMemberSmaliList(self):
        if self.mMemberClasses is None:
            self.mMemberClasses = []
            clsBaseName = self.getClassBaseName()
            memberClassRe = re.compile(r'(?:^%s\$.*%s$)' % (clsBaseName, utils.SMALI_POST_SUFFIX))
            dirName = os.path.dirname(self.getPath())
            
            for root, dirs, files in os.walk(dirName):
                for fn in files:
                    if bool(memberClassRe.match(fn)):
                        self.mMemberClasses.append(Smali('%s/%s' % (dirName, fn)))
        return self.mMemberClasses

    def getEntryList(self, type = None, filterInList = None, filterOutList = None, maxSize=0):
        entryList = self.mParser.getEntryList()
        if type is None:
            return entryList
        
        outEntryList = []
        for entry in entryList:
            if entry.getType() == type:
                if filterInList is not None and not entry.hasKeyList(filterInList):
                    continue
                
                if filterOutList is not None and entry.hasKeyList(filterOutList):
                    continue
                    
                outEntryList.append(entry)
                if maxSize > 0 and len(outEntryList) >= maxSize:
                    break;

        return outEntryList
    
    def getEntry(self, type, name, filterInList = None, filterOutList = None):
        for entry in self.getEntryList(type, filterInList, filterOutList):
            if entry.getName() == name:
                return entry
        return None
    
    def hasEntry(self, type, name, filterInList = None, filterOutList = None):
        return self.getEntry(type, name, filterInList, filterInList) is not None;
    
    def hasMethod(self, name, filterInList = None, filterOutList = None):
        return self.hasEntry(SmaliEntry.METHOD, name, filterInList, filterOutList)
    
    def hasField(self, name, filterInList = None, filterOutList = None):
        return self.hasEntry(SmaliEntry.FIELD, name, filterInList, filterOutList)

    def getEntryNameList(self, type = None, filterInList = None, filterOutList = None):
        outEntryList = []
        for entry in self.getEntryList(type, filterInList, filterOutList):
            outEntryList.append(entry.getName())
        return outEntryList
    
    def getEntryListByNameList(self, type, nameList):
        outList = []
        for entry in self.getEntryList(type):
            for name in nameList:
                if name == entry.getName():
                    outList.append(entry)
                    break
        return outList
    
    def getMethodsNameList(self, filterInList = None, filterOutList = None):
        return self.getEntryNameList(SmaliEntry.METHOD, filterInList, filterOutList)
    
    def getAbstractMethodsNameList(self):
        return self.getMethodsNameList([utils.KEY_ABSTRACT])
    
    def isAbstractClass(self):
        entryList = self.getEntryList(SmaliEntry.CLASS, [utils.KEY_ABSTRACT])
        assert len(entryList) <= 1, "Error: should has only one class define"
        return len(entryList) == 1
    
    def isInterface(self):
        entryList = self.getEntryList(SmaliEntry.CLASS, [utils.KEY_INTERFACE])
        assert len(entryList) <= 1, "Error: should has only one class define"
        return len(entryList) == 1
    
    def getSuperClassName(self):
        if self.mSuperClassName is None:
            entryList = self.getEntryList(SmaliEntry.SUPER, None, None, 1)
        
            if len(entryList) == 1:
                self.mSuperClassName = entryList[0].getName()
            else:
                # java/lang/Object doesn't have super
                if utils.getClassFromPath(self.mPath) != DEFAULT_SUPER:
                    if not self.mIsPartSmali:
                        utils.SLog.w("Wrong smali, should define the super! (%s)" % (self.mPath))
                    self.mSuperClassName = DEFAULT_SUPER
                else:
                    self.mSuperClassName = None
        return self.mSuperClassName
        
    def getImplementClassList(self):
        if self.mImplementsClassList is None:
            self.mImplementsClassList = []
            for entry in self.getEntryList(SmaliEntry.IMPLEMENTS):
                self.mImplementsClassList.append(entry.getName())
        
        return self.mImplementsClassList

    def getSuperAndImplementsClassName(self):
        clsNameList = []
        superClsName = self.getSuperClassName()
        
        if superClsName is not None:
            clsNameList.append(superClsName)
            
        implementsEntryList = self.getEntryList(SmaliEntry.IMPLEMENTS)
        for entry in implementsEntryList:
            clsNameList.append(entry.getName())
        
        return clsNameList
        
    def getPath(self):
        return self.mPath
    
    def removeEntryByName(self, type, name):
        entry = self.getEntry(type, name)
        return self.mParser.removeEntry(entry)
    
    def removeEntry(self, entry):
        return self.mParser.removeEntry(entry)
    
    def addEntry(self, entry, idx = -1, preFlag = None):
        nEntry = entry.clone()
        if preFlag is not None:
            nPreContent = nEntry.getPreContent()
            if nPreContent is None:
                nPreContent = Content(preFlag)
                nEntry.setPreContent(nPreContent)
            else:
                nPreContent.append(preFlag)
        
        result = self.mParser.addEntry(nEntry, idx)
        self.mModifed = True
        return result
    
    def getIndex(self, entry):
        return self.mParser.getIndex(entry)
    
    def replaceEntry(self, entry, preFlag = None):
        nEntry = entry.clone()
        if preFlag is not None:
            nPreContent = nEntry.getPreContent()
            if nPreContent is None:
                nPreContent = Content(preFlag)
                nEntry.setPreContent(nPreContent)
            else:
                nPreContent.append(preFlag)
        
        result = self.mParser.replaceEntry(nEntry)
        self.mModifed = True
        return result

    def getClassName(self):
        if self.mClassName is None:
            entryList = self.getEntryList(SmaliEntry.CLASS, None, None, 1)

            if len(entryList) != 1:
                if not self.mIsPartSmali:
                    utils.SLog.w("should has only one class define! (%s)" %(self.mPath))
                self.mClassName = utils.getClassFromPath(self.getPath())
            else:
                self.mClassName = entryList[0].getName()
        return self.mClassName
    
    def getClassBaseName(self):
        return utils.getClassBaseNameFromPath(self.getPath())
    
    def getSourceName(self):
        if self.mSourceName is None:
            entryList = self.getEntryList(SmaliEntry.SOURCE, None, None, 1)
        
            assert len(entryList) == 1
            self.mSourceName = entryList[0].getName()
        return self.mSourceName
    
    def getJarName(self):
        return utils.getJarNameFromPath(self.getPath())
    
    def getPackageName(self):
        if self.mPackageName is None:
            self.mPackageName = utils.getPackageFromClass(self.getClassName())
            
        return self.mPackageName;
    
    def __getInvokeMethods__(self):
        invokeMethodsList = []
        for entry in self.getEntryList(SmaliEntry.METHOD):
            invokeMethodsList.extend(entry.getInvokeMethods())
        return list(set(invokeMethodsList))
    
    def getInvokeMethods(self, filterInList = None):
        if self.mInvokeMethods is None:
            self.mInvokeMethods = self.__getInvokeMethods__()
        
        if filterInList is None:
            return self.mInvokeMethods
        
        outInvokeMethodsList = []
        for invokeItem in self.mInvokeMethods:
            for k in filterInList:
                if k == invokeItem.type:
                    outInvokeMethodsList.append(invokeItem)
                    break;
        
        return outInvokeMethodsList
    
    def __getUsedFields__(self):
        usedFieldsList = []
        for entry in self.getEntryList(SmaliEntry.METHOD):
            usedFieldsList.extend(entry.getUsedFields())
        return usedFieldsList
    
    def getUsedFields(self, filterInList = None):
        if self.mUsedFields is None:
            self.mUsedFields = self.__getUsedFields__()
            
        if filterInList is None:
            return self.mUsedFields
        
        outUsedMethodsList = []
        for usedFieldItem in self.mUsedFields:
            for k in filterInList:
                if k == usedFieldItem.type:
                    outUsedMethodsList.append(usedFieldItem)
                    break;
        
        return outUsedMethodsList
    
    def getUsedOutsideFields(self):
        if self.mUsedOutsideFields is None:
            usedFileds = self.getUsedFields()
            usedOutsideFields = []
            for usedFieldItem in usedFileds:
                if not usedFieldItem.cls == self.getClassName() or not self.hasField(usedFieldItem.field):
                    usedOutsideFields.append(usedFieldItem)
            self.mUsedOutsideFields = usedOutsideFields
        return self.mUsedOutsideFields
    
    def getAllMethods(self):
        return self.mAllMethods;

    def setAllMethods(self, allMethods):
        self.mAllMethods = allMethods

    def toString(self, entryList=None):
        if entryList is None:
            entryList = self.getEntryList()
        
        outContent = Content()
        for entry in self.getEntryList(): 
            outContent.append(entry.toString())
        if outContent.getContentStr() is not None:
            outContent.append("")
        return outContent.getContentStr()
    
    def toStringByType(self, type):
        return self.toString(self.getEntryList(type))
    
    # not finish
    def split(self, outdir):
        """ Return the sorted partition list.
        """

        sName = os.path.basename(self.mPath)[:-6]

        utils.SLog.d("begin split file: %s to %s" %(self.mPath, outdir))

        partList = []

        sHeadFile = file('%s/%s.head' % (outdir, sName), 'w+')
        partList.append(sHeadFile.name)

        for entry in self.getEntryList():
            entryStr = entry.toString()
            if entryStr is None:
                continue

            if entry.getType() == SmaliEntry.METHOD:
                methodFilePath = getHashMethodPath(sName, entry, outdir)
                partList.append(methodFilePath)

                sMethodFile = file(methodFilePath, 'w+')
                sMethodFile.write("%s\n" %entryStr)
                sMethodFile.close()
            else:
                sHeadFile.write("%s\n" %entryStr)
        sHeadFile.close()

        return partList

    def formatUsingField(self, formatFieldMap):
        modified = False
            
        for entry in self.getEntryList():
            if entry.formatUsingField(formatFieldMap):
                modified = True
        #self.__saveFormatMap(formatFieldMap)
        return modified
    
    def __saveFormatMap(self, formatFieldMap):
        mapFile = file(self.mFormatMapFile, "w+")
        
        for key in formatFieldMap.keys():
            mapFile.write("%s#%s\n" %(key, formatFieldMap[key]))
        
        mapFile.close()
        
    def __getReverseFormatMap(self):
        formatFieldMap = {}
        if not os.path.isfile(self.mFormatMapFile):
            return formatFieldMap
        
        mapFile = file(self.mFormatMapFile, "r")
        for line in mapFile.readlines():
            splitArray = line[:-1].split('#')
            assert len(splitArray) >= 2, "Error: Wrong format map in %s" %(self.getPath())
            
            formatFieldMap[splitArray[1]] = splitArray[0]
        
        mapFile.close()
        return formatFieldMap
    
    def undoFormatUsingField(self):
        formatFieldMap = self.__getReverseFormatMap()
        modified = False
        for entry in self.getEntryList():
            if entry.formatUsingField(formatFieldMap):
                modified = True
        
        if os.path.isfile(self.mFormatMapFile):
            os.remove(self.mFormatMapFile)
        return modified
    
    def isModifed(self):
        return self.mModifed
    
    def modify(self):
        self.mModifed = True
        
    def cleanModify(self):
        self.mModifed = False
    
    def setDefaultOutPath(self, outPath):
        self.mDefaultOutPath = outPath
        self.modify()
        
    def getDefaultOutPath(self):
        if self.mDefaultOutPath == None:
            return self.getPath()
        else:
            return self.mDefaultOutPath

    def out(self, outPath = None):
        if outPath is None:
            outPath = self.getDefaultOutPath()
            
        if self.mPreOutPath == outPath and self.mModifed == False:
            return
        
        self.mPreOutPath = outPath
        self.mModifed = False
        utils.SLog.d("out to : %s" %outPath)
        
        dirName = os.path.dirname(outPath)
        if not os.path.isdir(dirName):
            os.makedirs(os.path.dirname(outPath))

        sFile = file(outPath, "w+")

        outStr = self.toString()
        if outStr is None:
            return
        sFile.write(outStr)
        sFile.close()

DEFAULT_HASH_LEN = 6
def getHashCode(name, len = DEFAULT_HASH_LEN):
    return hashlib.md5(name).hexdigest()[:len]

def getHashMethodPath(sName, entry, outdir):
    eName = entry.getName()
    mName = eName.split(r'(')[0]
    sMethodPath = '%s/%s.%s.%s' %(outdir, sName, mName, getHashCode(eName))
    idx=1
    while os.path.isfile(sMethodPath):
        sMethodPath = '%s/%s.%s.%s.%s' %(outdir, sName, mName, getHashCode(eName), idx)
        idx = idx + 1
    return sMethodPath
