'''
Created on Feb 26, 2014

@author: tangliuxiang
'''
import string
from Content import *

CLASS = "class"
SUPER = "super"
SOURCE = "source"
IMPLEMENTS = "implements"
ANNOTATION = "annotation"
FIELD = "field"
METHOD = "method"

class SmaliEntry(object):
    '''
    classdocs
    '''
    
    def __init__(self, type, content, clsName=None, preContent=None):
        '''
        Constructor
        '''
        self.mContent = content
        self.mType = type
        self.mPreContent = preContent
        
        self.mFirstLine = None
        self.mKeyList = None
        self.mName = None
        self.mClsName = clsName
        
        self.mFlag = 0
        
    def clone(self):
        nPreContent = None
        if self.getPreContent() is not None:
            nPreContent = self.getPreContent().clone() 
        return SmaliEntry(self.getType(), self.getContent().clone(), self.getClassName(), nPreContent)
        
    def addFlag(self, flag):
        self.mFlag = self.mFlag | flag
    
    def rmFlag(self, flag):
        self.mFlag = self.mFlag & (~flag)

    def setFlag(self, flag):
        self.mFlag = flag
        
    def getFlag(self):
        return self.mFlag
        
    def setClassName(self, clsName):
        self.mClsName = clsName
        
    def getClassName(self):
        return self.mClsName
        
    def getEntry(self):
        return self.mEntry;
    
    def setEntry(self, entry):
        self.mEntry = entry;
    
    def getType(self):
        return self.mType;
    
    def setType(self, type):
        self.mType = type;

    def getContent(self):
        return self.mContent;
    
    def getContentStr(self):
        if self.mContent is not None:
            return self.mContent.getContentStr()
        else:
            return None
    
    def setContent(self, content):
        self.mContent = content
        
    def setContentStr(self, contentStr):
        if self.mContent is not None:
            self.mContent.setContentStr(contentStr)
        else:
            self.mContent = Content(contentStr)
            
    def getPreContent(self):
        return self.mPreContent;
    
    def getPreContentStr(self):
        if self.mPreContent is not None:
            return self.mPreContent.getContentStr()
        else:
            return None
    
    def setPreContent(self, preContent):
        self.mPreContent = preContent
        
    def setPreContentStr(self, preContentStr):
        if self.mPreContent is not None:
            self.mPreContent.setContentStr(preContentStr)
        else:
            self.mPreContent = Content(preContentStr)
    
    def equals(self, sEntry):
        if sEntry.mType is not None \
        and sEntry.mType == self.mType \
        and sEntry.getName() == self.getName():
            return True
        return False

    def formatUsingField(self, formatMap):
        return False
    
    def undoFormatUsingField(self, formatMap):
        return False

    def getFirstLine(self):
        if self.mFirstLine is None: 
            self.mFirstLine = self.getContent().getFirstLine()
            
        return self.mFirstLine
    
    def getName(self):
        if self.mName is None:
            if self.getFirstLine() is None:
                return ""

            splitArray = self.getFirstLine().split()
            self.mName = splitArray[len(splitArray) - 1]
        return self.mName

    def getKeyList(self):
        if self.mKeyList is None:
            splitArray = self.getFirstLine().split()
            if len(splitArray) >= 3:
                self.mKeyList = splitArray[1:len(splitArray) - 1]
            else:
                self.mKeyList = []
            
        # print "keyList: %s" %self.mKeyList
        return self.mKeyList
        
    def hasKey(self, key):
        if key is None:
            return False
        
        for k in self.getKeyList():
            if k == key:
                return True
            
        return False
    
    def hasKeyList(self, keyList):
        if keyList is None:
            return False
        
        for k in keyList:
            if self.hasKey(k):
                return True
            
        return False
    
    def getAttributeList(self):
        firstLine = self.getContent().getFirstLine()
        splitArray = firstLine.split()
        return splitArray[1:(len(splitArray) - 1)]
    
    def getAttributes(self):
        return string.join(self.getAttributeList())

    def getSimpleString(self):
        return  "%s %s->%s" % (self.getType(), self.getClassName(), self.getName())

    def toString(self):
        if self.getPreContentStr() is not None: 
            if self.getContentStr() is not None:
                return "%s\n%s" % (self.getPreContentStr(), self.getContentStr())
            else:
                return self.getPreContentStr()
        else:
            if self.getContentStr() is not None:
                return self.getContentStr()
            else:
                return None

    def out(self, outdir, sName):
        entryStr = self.toString()
        if entryStr is not None:
            sFile = file("%s/%s.%s" % (outdir, sName, self.getType()), 'a')
            sFile.write("%s\n" % entryStr)
            sFile.close()
