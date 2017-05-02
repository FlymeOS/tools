'''
Created on Jun 5, 2014

@author: tangliuxiang
'''

import Smali
import utils
import re
import sys
import os
import SmaliEntry
import Replace
import SAutoCom
import tempfile
import LibUtils

from formatters.log import Paint

class reject(object):
    REJ_BEGIN = '<<<<<<<'
    REJ_SPLIT = '======='
    REJ_END = '>>>>>>>'
    
    REJ_MULTI_STR = '^%s.*$|^%s.*$|^%s.*$' % (REJ_BEGIN, REJ_SPLIT, REJ_END)
    RE_REJ = re.compile(REJ_MULTI_STR, re.M)
    
    FLAG_ENTRY_NORMAL = 0
    FLAG_ENTRY_REJECT = 1
    
    FLAG_REPLACED_TO_BOARD = 2
    
    '''
    classdocs
    '''
    def __init__(self, rejectFilePath):
        self.mASLib = LibUtils.getSmaliLib(utils.AOSP, 1)
        self.mBSLib = LibUtils.getSmaliLib(utils.BOSP, 1)
        self.mTSLib = LibUtils.getSmaliLib(utils.TARGET, 1)
        self.mRejSLib = LibUtils.getOwnLib(rejectFilePath)
                
        self.rejSmali = Smali.Smali(rejectFilePath)
        self.mClassName = self.rejSmali.getClassName()
        
        self.aospSmali = self.mASLib.getFormatSmali(self.mClassName)
        self.bospSmali = self.mBSLib.getFormatSmali(self.mClassName)
        self.targetSmali = self.mTSLib.getFormatSmali(self.mClassName)
        
        self.mFormatList = {}
        self.mCanNotReplaceEntry = []
        self.parseReject()
        
    def parseReject(self):
        for entry in self.rejSmali.getEntryList():
            if self.hasReject(entry.getContentStr()):
                entry.addFlag(reject.FLAG_ENTRY_REJECT)

    def __multiEntryReject__(self):
        lastEntry = None
        targetSmaliModified = False
        
        for entry in self.rejSmali.getEntryList():
            if self.hasReject(entry.getPreContentStr()):
                entry.setPreContentStr(self.rmRejectTagLine(entry.getPreContentStr()))
            
            if not self.targetSmali.hasEntry(entry.getType(), entry.getName()):
                if not self.isRejectEntry(entry):
                    idx = -1
                    if lastEntry is not None:
                        tEntry = self.targetSmali.getEntry(lastEntry.getType(), lastEntry.getName())
                        idx = self.targetSmali.getIndex(tEntry) + 1
                    utils.SLog.ok("\n>>>> Fix reject %s %s in %s: " % (entry.getType(), entry.getName(), self.rejSmali.getPath()))
                    utils.SLog.ok("        Add %s %s in %s from bosp" % (entry.getType(), entry.getName(), self.getRealTargetPath(self.targetSmali)))
                    self.targetSmali.addEntry(entry, idx, utils.annotation.getAddToBospPreContent(entry))
                    targetSmaliModified = True
            else:
                lastEntry = entry
        if targetSmaliModified:
            self.targetSmali.out()
        self.rejSmali.out()

    FIX_EXACT = 0
    FIX_LIGHT = 1
    FIX_MIDDLE = 2
    FIX_HEAVY = 3
    def fix(self, level=FIX_EXACT):
        if level >= reject.FIX_EXACT:
            self.__multiEntryReject__()
        
        if level >= reject.FIX_LIGHT:
#            print "replace only which can replace methods"
#            print "add missed class"
#            print "add can replace method"
            if not utils.precheck.shouldIgnore(self.rejSmali):
                self.handleLightFix()
            else:
                utils.SLog.fail(">>>> Failed on fix reject in %s" %(self.getRealTargetPath(self.targetSmali)))
            
        if level >= reject.FIX_MIDDLE:
#            print "which can not replace method: use blank"
            self.handleMiddleFix()
            
        if level >= reject.FIX_HEAVY:
            print "which missed field, replace class"
        
        self.__exit()
            
    def getRejectEntryList(self):
        rejectEntryList = []
        for entry in self.rejSmali.getEntryList():
            if self.isRejectEntry(entry):
                rejectEntryList.append(entry)
        return rejectEntryList
    
    def getRejectEntry(self, oriEntry):
        for entry in self.getRejectEntryList():
            if entry.getClassName() == oriEntry.getClassName() \
            and entry.getType() == oriEntry.getType() \
            and entry.getName() == oriEntry.getName():
                return entry
        return None

    def __exit(self):
        hasReject = self.hasReject(self.rejSmali.toString())
        if hasReject:
            self.rejSmali.out()
        if hasReject:
            self.rejSmali = Smali.Smali(self.rejSmali.getPath())
            self.rejSmali.out(self.getOutRejectFilePath())
            
    def getOutRejectFilePath(self):
        start = len(os.path.abspath(utils.REJECT))
        rejPath = self.rejSmali.getPath()
        return "%s/%s" % (utils.OUT_REJECT, rejPath[start:])
    
    def getRealTargetPath(self, tSmali):
        return "%s/smali/%s" % (utils.getJarNameFromPath(tSmali.getPath()), utils.getBaseSmaliPath(tSmali.getPath()))
        
    def replaceEntryToBosp(self, entry):
        if (entry.getFlag() & reject.FLAG_REPLACED_TO_BOARD) == 0:
            self.mTSLib.replaceEntry(self.mBSLib, entry)
        
            if self.mRejSLib.getSmali(entry.getClassName()) is not None:
                self.rejSmali = self.mRejSLib.replaceEntry(self.mBSLib, entry, False, False, True)
            rejEntry = self.getRejectEntry(entry)
            if rejEntry is not None:
                rejEntry.setFlag(reject.FLAG_ENTRY_NORMAL)
            entry.addFlag(reject.FLAG_REPLACED_TO_BOARD)
    
    def handleLightFix(self):
        target = os.path.relpath(self.rejSmali.getPath(), utils.REJECT)
        print "  "
        print "  %s %s" % (Paint.bold("FIX CONFLICTS IN"), target)
        for mEntry in self.mBSLib.getEntryList(self.getRejectEntryList()):
            (canReplaceEntry, canNotReplaceEntry) = self.mTSLib.getCanReplaceEntry(self.mBSLib, self.rejSmali.getClassName(), [mEntry], False)
            if utils.has(canReplaceEntry, mEntry):
                print "  %s %s" % (Paint.green("[PASS]"), mEntry.getName())
                utils.SLog.ok("\n>>>> Fix reject %s %s in %s: " % (mEntry.getType(), mEntry.getName(), self.rejSmali.getPath()))
                self.replaceEntryToBosp(mEntry)

            for entry in canReplaceEntry:
                if entry != mEntry:
                    self.replaceEntryToBosp(entry)
            if len(canNotReplaceEntry) > 0:
                self.mCanNotReplaceEntry.extend(canNotReplaceEntry)
                if utils.has(canNotReplaceEntry, mEntry):
                    print "  %s %s" % (Paint.red("[FAIL]"), mEntry.getName())

                    utils.SLog.fail("  %s" % target)
                    #utils.SLog.fail("  CONFLICTS: %s %s in %s" % (mEntry.getType(), mEntry.getName(), self.getRealTargetPath(self.mTSLib.getSmali(mEntry.getClassName()))))
                    #utils.SLog.fail("  Can not be replaced by bosp, because of the follows:")
                for entry in canNotReplaceEntry:
                    #utils.SLog.fail("     %s %s in %s" % (entry.getType(), entry.getName(), self.getRealTargetPath(self.mTSLib.getSmali(entry.getClassName()))))
                    pass
            
    @staticmethod
    def missMethod(sLib, entry):
        try:
            missedMethodsLen = len(sLib.getMissedMethods(entry))
        except Exception as e:
            utils.SLog.d(e)
            return True 
        return missedMethodsLen > 0
    
    @staticmethod
    def missField(sLib, entry):
        try:
            missedFieldssLen = len(sLib.getMissedFields(entry))
        except Exception as e:
            utils.SLog.d(e)
            return True 
        return missedFieldssLen > 0
    
    def handleMiddleFix(self):
        for entry in self.mCanNotReplaceEntry:
            if entry.getType() == SmaliEntry.METHOD:
                clsName = entry.getClassName()
                
                tSmali = self.mTSLib.getSmali(clsName)
                bSmali = self.mBSLib.getSmali(clsName)
                
                if not tSmali.hasEntry(entry.getType(), entry.getName()):
                    Replace.Replace.appendBlankEntry(entry, self.mTSLib.getSmali(entry.getClassName()).getPath())
                
    @staticmethod
    def isRejectEntry(entry):
        return entry.getFlag() & reject.FLAG_ENTRY_REJECT != 0
        
    @staticmethod
    def hasReject(string):
        if string is None:
            return False
        
        if bool(reject.RE_REJ.search(string)):
            return True
        else:
            return False
        
    @staticmethod
    def rmRejectTagLine(string):
        if string is None:
            return string
        outString = ""
        for line in string.splitlines():
            if not reject.hasReject(line):
                outString = "%s%s" % (outString, line)
        return outString


REJECT_ADVICE = "%s/help/reject_advice" %os.path.dirname(os.path.abspath(__file__))
REJECT_SUCCESS = "%s/help/reject_success" %os.path.dirname(os.path.abspath(__file__))

def fixReject():
    utils.annotation.setAction("make autofix")
    for rejectFile in utils.getSmaliPathList(utils.REJECT, 2):
        reject(rejectFile).fix(reject.FIX_LIGHT)

    utils.SLog.setAdviceStr(file(REJECT_ADVICE).read())
    utils.SLog.setSuccessStr(file(REJECT_SUCCESS).read())
    utils.SLog.conclude()
    LibUtils.undoFormat()

if __name__ == "__main__":
    fixReject()
