'''
Created on Jun 4, 2014

@author: tangliuxiang
'''
from xml.dom import minidom
import Content
import LibUtils
import Smali
import SmaliEntry
import SmaliEntryFactory
import SmaliFileReplace
import SmaliMethod
import os
import re
import string
import utils
import sys


class Replace(object):
    '''
    classdocs
    '''
    BLANK_CONTENT_XML = r'%s/autocomplete.xml' %(os.path.dirname(os.path.abspath(__file__)))
    BLANK_ENTRY = None
        
    def __init__(self, vendorDir, aospDir, bospDir, mergedDir):
        '''
        Constructor
        '''
        self.mVSLib = LibUtils.getSmaliLib(vendorDir)
        self.mASLib = LibUtils.getSmaliLib(aospDir)
        self.mBSLib = LibUtils.getSmaliLib(bospDir)
        self.mMSLib = LibUtils.getSmaliLib(mergedDir)
    
    def preReplaceCheck(self, smali):
        unImplementMethods = self.getUnImplementMethods(smali)
        canReplaceEntryList = []
        canNotReplaceEntryList = []
        if unImplementMethods is not None and len(unImplementMethods) > 0:
            vSmali = self.mVSLib.getSmali(smali.getClassName())
            if vSmali is None:
                utils.SLog.d("Can't get smali %s from vendor: %s"  %(smali.getClassName(), string.join(unImplementMethods)))
                return (canReplaceEntryList, canNotReplaceEntryList)
            
            unImplMethodEntryList = vSmali.getEntryListByNameList(SmaliEntry.METHOD, unImplementMethods)
            (canReplaceEntryList, canNotReplaceEntryList) = self.mMSLib.getCanReplaceEntry(self.mVSLib, smali.getClassName(), unImplMethodEntryList)
        
            for entry in canReplaceEntryList:
                utils.SLog.d("   Can Replace: %s" %(entry.getSimpleString()))

            for entry in canNotReplaceEntryList:
                utils.SLog.d("   Can not Replace: %s" %(entry.getSimpleString()))

        return (canReplaceEntryList, canNotReplaceEntryList)
    
    @staticmethod
    def replaceEntryInFile(entry, outFilePath):
        utils.SLog.d(" REPLACE %s" % (entry.getSimpleString()))

        dirName = os.path.dirname(outFilePath)
        if not os.path.isdir(dirName):
            os.makedirs(os.path.dirname(outFilePath))

        outSmali = Smali.Smali(outFilePath)
        outSmali.replaceEntry(entry)
        outSmali.out()

        print "  ADD %s %s --> %s" % (entry.getType(), entry.getName(), os.path.basename(outFilePath))

    @staticmethod
    def replaceEntry(src, dst, type, name, withCheck = True):
        srcSmali = Smali.Smali(src)
        dstSmali = Smali.Smali(dst)

        if srcSmali is None:
            utils.SLog.d("%s doesn't exist or is not smali file!" %src)
            return False

        if dstSmali is None:
            utils.SLog.d("%s doesn't exist or is not smali file!" %dst)
            return False

        name = name.split()[-1]
        srcEntry = srcSmali.getEntry(type, name)
        returnValue = False
        if srcEntry is not None:
            srcLib = LibUtils.getOwnLib(src)
            dstLib = LibUtils.getOwnLib(dst)
            if withCheck:
                (canReplaceEntry, canNotReplaceEntry) = dstLib.getCanReplaceEntry(srcLib, dstSmali.getClassName(), [srcEntry], False)
            
                if len(canNotReplaceEntry) > 0:
                    utils.SLog.fail("Failed to replace %s %s from %s to %s" % (type, name, src, dst))
                    for entry in canNotReplaceEntry:
                        if entry != srcEntry:
                            utils.SLog.fail("    Can not replace %s %s in %s" %(entry.getType(), entry.getName(), entry.getClassName()))
                    returnValue = False
                else:
                    for entry in canReplaceEntry:
                        dstLib.replaceEntry(srcLib, entry)
                    returnValue = True
            else:
                dstLib.replaceEntry(srcLib, srcEntry)
                returnValue = True
        else:
            utils.SLog.d("Can not get %s:%s from %s" %(type, name, src))
            returnValue = False
        return returnValue

    @staticmethod
    def parseAutoComXml():
        assert os.path.isfile(Replace.BLANK_CONTENT_XML), "%s doesn't exist! Are you remove it?" %(Replace.BLANK_CONTENT_XML)
        root = minidom.parse(Replace.BLANK_CONTENT_XML).documentElement
        
        Replace.BLANK_ENTRY = {}

        for item in root.childNodes:
            if item.nodeType == minidom.Node.ELEMENT_NODE:
                if not Replace.BLANK_ENTRY.has_key(item.nodeName):
                    Replace.BLANK_ENTRY[item.nodeName] = {}
                
                if item.nodeName == SmaliEntry.METHOD:
                    returnType = item.getAttribute("return")
                    contentStr = item.getAttribute("content")
                    outStr = re.sub(r'^ ', '', contentStr, 0, re.M)
                    Replace.BLANK_ENTRY[item.nodeName][returnType] = outStr
                else:
                    utils.SLog.d("Doesn't support %s in %s" %(item.nodeName, Replace.BLANK_CONTENT_XML))
    
    @staticmethod    
    def __getBlankContentStr__(entry):
        returnType = entry.getReturnType()
        if Replace.BLANK_ENTRY is None:
            Replace.parseAutoComXml()
        if Replace.BLANK_ENTRY[entry.getType()].has_key(returnType):
            return Replace.BLANK_ENTRY[entry.getType()][returnType]
        else:
            for key in Replace.BLANK_ENTRY[entry.getType()].keys():
                if re.match(key, returnType) is not None:
                    return Replace.BLANK_ENTRY[entry.getType()][key]
        return None

    @staticmethod
    def getBlankContent(entry):
        content = Content.Content()
        if entry.getType() == SmaliEntry.METHOD:
            contentStr = Replace.__getBlankContentStr__(entry)

            if contentStr is not None:
                content.append(entry.getFirstLine())
                content.append(contentStr)

        return content
    
    @staticmethod
    def getBlankEntry(entry):
        return SmaliEntryFactory.newSmaliEntry(entry.getType(), Replace.getBlankContent(entry), entry.getClassName(), entry.getPreContent())

    @staticmethod
    def appendBlankEntry(entry, outFilePath):
        utils.SLog.d(" ADD BLANK %s" % (entry.getSimpleString()))

        if Replace.BLANK_ENTRY is None:
            Replace.parseAutoComXml()
        
        if not Replace.BLANK_ENTRY.has_key(entry.getType()) or entry.getType() != SmaliEntry.METHOD:
            utils.SLog.d("Doesn't support add blank %s in autocomplete")
            return

        dirName = os.path.dirname(outFilePath)
        if not os.path.isdir(dirName):
            os.makedirs(os.path.dirname(outFilePath))

        partSmali = Smali.Smali(outFilePath)
        nEntry = Replace.getBlankEntry(entry)
        partSmali.replaceEntry(nEntry)
        partSmali.out()

        print "  ADD %s %s --> %s" % (entry.getType(), entry.getName(), os.path.basename(outFilePath))

    def getUnImplementMethods(self, smali):
        return self.mMSLib.getUnImplementMethods(self.mASLib, smali)
        
    def getCanReplaceToBoardMethods(self, smali, methodEntryList):
        return self.mMSLib.getCanReplaceEntry(self.mBSLib, smali.getClassName(), methodEntryList)
    
def replaceMethod(src, dst, methodName, withCheck = False):
    ret = Replace.replaceEntry(src, dst, SmaliEntry.METHOD, methodName, withCheck)
    if ret:
        utils.SLog.i("\n>>>> SUCCESS: replaced method %s from %s to %s" %(methodName, src, dst))
    else:
        utils.SLog.i("\n>>>> FAILED: Can not replace method %s from %s to %s" %(methodName, src, dst))
    LibUtils.undoFormat()
    return ret
    
def methodtobosp(smaliFile, methodName, withCheck = True):
    utils.annotation.setAction("methodtosmali")
    src = utils.getMatchFile(smaliFile, utils.BOSP)
    dst = utils.getMatchFile(smaliFile, utils.TARGET)
    if replaceMethod(src, dst, methodName, withCheck) is False:
        raise
