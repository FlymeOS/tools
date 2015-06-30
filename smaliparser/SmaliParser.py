'''
Created on Feb 26, 2014

@author: tangliuxiang
'''

import os
import SmaliEntryFactory
import Smali
import re
import utils
import sys

from Content import Content
from SmaliLine import SmaliLine

DEBUG = False

class SmaliParser(object):
    '''
    classdocs
    '''
    STATE_NULL = 0
    STATE_WAIT_START = 1
    STATE_WAIT_END = 2

    def __init__(self, smaliFilePath, parseNow = True):
        '''
        Constructor
        '''
        self.mSmaliFilePath = smaliFilePath
        self.mParsed = False
        self.state = SmaliParser.STATE_NULL
        self.mEntryList = []
        
        if parseNow:
            self.parse()
            
    def parse(self):
        clsName = utils.getClassFromPath(self.mSmaliFilePath)
        state = SmaliParser.STATE_WAIT_START;
        curEntryType = None
        curEntryContent = Content()
        curPreContent = Content()
        entryList = []
        
        if not os.path.isfile(self.mSmaliFilePath):
            utils.SLog.w("%s doesn't exist!" %(self.mSmaliFilePath))
            self.mParsed = True
            return
        
        sFile = file(self.mSmaliFilePath)
        fileLinesList = sFile.readlines()
        sFile.close()
        idx = 0
        while idx < len(fileLinesList):
            if fileLinesList[idx][-1] == "\n":
                sLine = SmaliLine(fileLinesList[idx][0:-1])
            else:
                sLine = SmaliLine(fileLinesList[idx])
            
            if sLine.getType() is SmaliLine.TYPE_DOT_LINE:
                if sLine.isDotEnd():
                    assert state == SmaliParser.STATE_WAIT_END, "wrong end in line: (%s:%s)" % (self.mSmaliFilePath, idx)
                    curEntryContent.append(sLine.getLine())
                    entryList.append(SmaliEntryFactory.newSmaliEntry(curEntryType, curEntryContent, clsName, curPreContent))
                    
                    curPreContent = Content()
                    curEntryContent = Content()
                    state = SmaliParser.STATE_WAIT_START
                else:
                    if state is SmaliParser.STATE_WAIT_START:
                        curEntryType = sLine.getDotType() 
                        assert curEntryType is not None, "Life is hard...."
                    
                        curEntryContent.setContentStr(sLine.getLine())
                        state = SmaliParser.STATE_WAIT_END
                    else:
                        assert state is SmaliParser.STATE_WAIT_END, "wrong state, Life is hard...."
                        assert not curEntryContent.isMultiLine(), "wrong entry start, expect .end %s (%s:%s)" % (curEntryType, self.mSmaliFilePath, idx)

                        postStr = curEntryContent.getPostContent().getContentStr()
                        curEntryContent.setContentStr(curEntryContent.getContentStr().split('\n')[0])
                        entryList.append(SmaliEntryFactory.newSmaliEntry(curEntryType, curEntryContent, clsName, curPreContent))
                        
                        curEntryType = sLine.getDotType()
                        assert curEntryType is not None, "Life is hard...."
                        
                        curPreContent = Content(postStr)
                        curEntryContent = Content(sLine.getLine())

            else:
                if state is SmaliParser.STATE_WAIT_START:
                    curPreContent.append(sLine.getLine())
                else:
                    assert state is SmaliParser.STATE_WAIT_END,  "wrong state, Life is hard...."
                    curEntryContent.append(sLine.getLine())
            idx = idx + 1
            
        if state is SmaliParser.STATE_WAIT_END \
            and curEntryType is not None \
            and curEntryContent.getContentStr() is not None:
            curEntryContent.setContentStr(curEntryContent.getContentStr().split('\n')[0])
            entryList.append(SmaliEntryFactory.newSmaliEntry(curEntryType, curEntryContent, clsName, curPreContent))
        
        self.mEntryList = entryList
        self.mParsed = True
    
    def getEntryList(self):
        if self.mParsed is False:
            self.parse()
        return self.mEntryList;
    
    def removeEntry(self, entry):
        if self.mParsed is False:
            self.parse()
            
        if entry is None:
            return False
        
        idx = 0
        while idx < len(self.mEntryList):
            if self.mEntryList[idx] == entry:
                del self.mEntryList[idx]
                return True
            idx = idx + 1
        return False
    
    def addEntry(self, entry, idx = -1):
        if self.mParsed is False:
            self.parse()
        
        if entry is None:
            return False
        
        if idx < 0 or idx >= len(self.mEntryList):
            self.mEntryList.append(entry)
        else:
            self.mEntryList.append(self.mEntryList[len(self.mEntryList) - 1])
            i = len(self.mEntryList) - 1
            while i > idx:
                self.mEntryList[i] = self.mEntryList[i - 1]
                i = i - 1
            self.mEntryList[idx] = entry
        return True
    
    def getIndex(self, entry):
        return self.mEntryList.index(entry)
    
    def replaceEntry(self, entry):
        if self.mParsed is False:
            self.parse()

        if entry is None:
            return False
        
        idx = 0
        while idx < len(self.mEntryList):
            if self.mEntryList[idx].equals(entry):
                self.mEntryList[idx] = entry
                return True
            idx = idx + 1

        self.addEntry(entry)
        return True


