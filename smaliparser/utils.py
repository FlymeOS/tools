'''
Created on Mar 26, 2014

@author: tangliuxiang
'''

import os, sys
import re
import Smali
import SmaliEntry
import time
import getpass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from formatters.log import Log, Paint

KEY_PUBLIC = "public"
KEY_PRIVATE = "private"
KEY_PROTECTED = "protected"
KEY_STATIC = "static"
KEY_FINAL = "final"
KEY_SYNTHETIC = "synthetic"

# only use in methods
KEY_ABSTRACT = "abstract"
KEY_CONSTRUCTOR = "constructor"
KEY_BRIDGE = "bridge"
KEY_DECLARED_SYNCHRONIZED = "declared-synchronized"
KEY_NATIVE = "native"
KEY_SYNCHRONIZED = "synchronized"
KEY_VARARGS = "varargs"

# only use in field
KEY_ENUM = "enum"
KEY_TRANSIENT = "transient"
KEY_VOLATILE = "volatile"

KEY_INTERFACE = "interface"

class SLog():
    TAG = "smali-parser"
    DEBUG = False
    FAILED_LIST = []
    SUCCESS_LIST = []
    
    ADVICE = ""
    SUCCESS = ""
    @staticmethod
    def e(s):
        Log.e(SLog.TAG, s)
    @staticmethod
    def w(s):
        Log.w(SLog.TAG, s)
    @staticmethod
    def d(s):
        if SLog.DEBUG:
            Log.i(SLog.TAG, s)
        else:
            Log.d(SLog.TAG, s)
    @staticmethod
    def i(s):
        Log.i(SLog.TAG, s)
    @staticmethod
    def fail(s):
        SLog.FAILED_LIST.append(s)
    @staticmethod
    def ok(s):
        SLog.SUCCESS_LIST.append(s)
        #Log.i(SLog.TAG, s)

    @staticmethod
    def conclude():

        print Paint.red("  ____________________________________________________________________________________")
        print "                                                                                                "
        print Paint.red("  Go through 'autopatch/still-reject' to find out the rest of conflicts after autofix:")
        print "                                                                                                "

        if len(SLog.FAILED_LIST) > 0:
            for failed in set(SLog.FAILED_LIST): print Paint.red(failed)
            #Log.i(SLog.TAG, SLog.ADVICE)
        else:
            #Log.i(SLog.TAG, SLog.SUCCESS)
            pass

        
    @staticmethod
    def setAdviceStr(str):
        SLog.ADVICE = str
    
    @staticmethod
    def setSuccessStr(str):
        SLog.SUCCESS = str
        
PRJ_ROOT = os.getcwd()
REJECT = '%s/autopatch/reject' %(PRJ_ROOT)
BOSP = '%s/autopatch/bosp' %(PRJ_ROOT)
AOSP = '%s/autopatch/aosp' %(PRJ_ROOT)
TARGET = "%s/out/obj/autofix/target" %(PRJ_ROOT)
OUT_REJECT = '%s/autopatch/still-reject' %(PRJ_ROOT)

SMALI_POST_SUFFIX = r'\.smali'
PART_SMALI_POST_SUFFIX = r'\.smali\.part'
SMALI_POST_SUFFIX_LEN = 6

smaliFileRe = re.compile(r'(?:^.*%s$)|(?:^.*%s$)' % (SMALI_POST_SUFFIX, PART_SMALI_POST_SUFFIX))
partSmaliFileRe = re.compile(r'(?:^.*%s$)' %(PART_SMALI_POST_SUFFIX))

def has(list, item):
    for i in list:
        if i == item:
            return True
    return False

def isSmaliFile(smaliPath):
    return bool(smaliFileRe.match(smaliPath))

def isPartSmaliFile(smaliPath):
    return bool(partSmaliFileRe.match(smaliPath))

def getSmaliPathList(source, smaliDirMaxDepth = 0):
    filelist = []
    
    source = os.path.abspath(source)
    if os.path.isfile(source):
        if isSmaliFile(source):
            filelist.append(source)
        return filelist
    
    for root, dirs, files in os.walk(source):
        if smaliDirMaxDepth > 0:
            rootWithSuffix = "%s/" %root
            try:
                idx = rootWithSuffix.rindex('/smali/')
            except:
                idx = -1
            if idx < len(source) \
            or (idx > len(source) \
            and len(rootWithSuffix[len(source) + 1: idx].split('/')) > smaliDirMaxDepth):
                continue
        for fn in files:
            if isSmaliFile(fn):
                filelist.append("%s/%s" % (root, fn))

    return filelist

def getPackageFromClass(className):
    try:
        idx = className.rindex(r'/')
    except:
        SLog.e("wrong className: %s" %className)
        return None
    return className[1:idx]

def getSmaliDict(smaliDir, smaliDirMaxDepth = 0):
    sFileList = getSmaliPathList(smaliDir, smaliDirMaxDepth)
    smaliDict = {}
    
    for sPath in sFileList:
        smali = Smali.Smali(sPath)
        sClass = getClassFromPath(sPath)
        smaliDict[sClass] = smali
       
    return smaliDict

def getJarNameFromPath(smaliPath):
    assert isSmaliFile(smaliPath), "This file is not smali file: %s" % smaliPath

    absSmaliPath = os.path.abspath(smaliPath)
    #splitArray = absSmaliPath.split("/smali/")
    splitArray = re.split("/smali/|/smali_classes\\d*/", absSmaliPath)

    assert len(splitArray) >= 2, "This smali is not decode by apktool, doesn't hava /smali/ directory"
    return os.path.basename(splitArray[len(splitArray) - 2])

def getBaseSmaliPath(smaliPath):
    assert isSmaliFile(smaliPath), "This file is not smali file: %s" % smaliPath
    
    absSmaliPath = os.path.abspath(smaliPath)
    #splitArray = absSmaliPath.split("/smali/")
    splitArray = re.split("/smali/|/smali_classes\\d*/", absSmaliPath)
    
    assert len(splitArray) >= 2, "This smali is not decode by apktool, doesn't hava /smali/ directory"
    return splitArray[len(splitArray) - 1]

def getClassBaseNameFromPath(smaliPath):
    assert isSmaliFile(smaliPath), "This file is not smali file: %s" % smaliPath
    sBaseName = os.path.basename(smaliPath)
    return sBaseName[:sBaseName.rindex('.smali')]
        
def getClassFromPath(smaliPath):
    assert isSmaliFile(smaliPath), "This file is not smali file: %s" % smaliPath
    
    absSmaliPath = os.path.abspath(smaliPath)
    #splitArray = absSmaliPath.split("/smali/")
    splitArray = re.split("/smali/|/smali_classes\\d*/", absSmaliPath)
    
    assert len(splitArray) >= 2, "This smali is not decode by apktool, doesn't hava /smali/ directory"
    clsNameWithPost = splitArray[len(splitArray) - 1]
    return 'L%s;' % clsNameWithPost[:clsNameWithPost.rindex('.smali')]

def getReturnType(methodName):
    splitArray = methodName.split(r')')
    if len(splitArray) < 2:
        SLog.w("method %s return nothing!" %methodName)
        return ""
    else:
        return splitArray[-1]

def getMatchFile(smaliFile, targetDir = BOSP):
    assert isSmaliFile(smaliFile), "%s is not an smali file" %(smaliFile)
    assert os.path.isdir(targetDir), "%s directory is not exist!" %(targetDir)
    assert os.path.isfile(smaliFile), "%s is not exist!" %(smaliFile)
    
    baseSmaliFile = getBaseSmaliPath(smaliFile)
    jarName = getJarNameFromPath(smaliFile)
    
    filePath = '%s/smali/%s' %(jarName, baseSmaliFile)
    if os.path.isfile('%s/%s' %(targetDir, filePath)):
        return '%s/%s' %(targetDir, filePath)
    else:
        cmd = 'find %s -path "*/smali/%s"' %(targetDir, baseSmaliFile)
        
        matchFiles = os.popen(cmd).readlines()
        assert len(matchFiles) >= 1, "Error: Can not find match files in %s for %s" % (targetDir, smaliFile)
        if len(matchFiles) > 1:
            minLen = len(matchFiles[0].split('/'))
            minDepthFile = matchFiles[0]
            for f in matchFiles[1:]:
                sLen = len(f.split('/'))
                if sLen < minLen:
                    minDepthFile = f
                    minLen = sLen
            
            SLog.w("         there are not only one file for %s in %s" % (baseSmaliFile, targetDir))
            SLog.i("         used: %s" % (minDepthFile))
            SLog.i("         You can run %s to check it out!" % cmd)
        return matchFiles[0][:-1]


def getSimpleMethodName(methodName):
    return methodName.split('(')[0]

class precheck():
    mPreCheck = None
    
    @staticmethod
    def getInstance():
        if precheck.mPreCheck is None:
            precheck.mPreCheck = precheck()
        return precheck.mPreCheck
    
    @staticmethod
    def setInstance(nInstance):
        precheck.mPreCheck = nInstance
    
    @staticmethod
    def canAddField(field):
        firstLine = field.getFirstLine()
        try:
            if firstLine.index('=') > 0 and field.hasKeyList([KEY_FINAL, KEY_STATIC]):
                return True
        except:
            return False
        return False
    
    @staticmethod
    def shouldIgnore(smali):
        if smali.getClassName() == 'Lcom/android/server/ServerThread;' or smali.getSuperClassName() == 'Landroid/os/Binder;':
            return True
        return False
    
    def precheck(self, tSmali, bSmali, entry):
        if tSmali is not None \
            and bSmali is not None \
            and entry.getType() == SmaliEntry.METHOD:
                if entry.isConstructor():            
                    for field in tSmali.getEntryList(SmaliEntry.FIELD):
                        if not bSmali.hasEntry(SmaliEntry.FIELD, field.getName()) and not self.canAddField(field):
                            return False
                elif entry.getSimpleName() == "onTransact":
                    SLog.e(">>> onTransact is an binder interface, it shouldn't be replace, if you want to replace, find the stub and proxy, replace them all!")
                    SLog.e("       such as if you want replace method in IAlarmManager$Stub.smali")
                    SLog.e("       you better use smalitobosp to replace the IAlarmManager$Stub.smali and IAlarmManager$Stub$Proxy.smali both!")
                    return False
        return True

def preCheck(tSmali, bSmali, entry):
    return precheck.getInstance().precheck(tSmali, bSmali, entry)

class annotation():
    CUR_ACTION = None
    ATTENTION = None
    
    ENABLE = True
    @staticmethod 
    def disable():
        annotation.ENABLE = False
        
    @staticmethod 
    def enable():
        annotation.ENABLE = True
    
    @staticmethod
    def setAction(action):
        annotation.CUR_ACTION = action
    
    @staticmethod
    def setAttention(attention):
        annotation.ATTENTION = attention
    
    @staticmethod
    def getAppendStr():
        appendStr = ""
        if annotation.CUR_ACTION is not None:
            appendStr = "\n# @action: %s" %(annotation.CUR_ACTION)
    
        if annotation.ATTENTION is not None:
            appendStr = "%s\n# @attention: %s" %(annotation.ATTENTION)
        return appendStr

    @staticmethod
    def getReplaceToBospPreContent(entry):
        if annotation.ENABLE:
            return "# REPLACE:\n# This %s is replaced to bosp at %s\n#%s\n# @author: %s" %(entry.getType(), time.strftime('%Y-%m-%d %H:%M'), annotation.getAppendStr(), getpass.getuser())
        else:
            return None
    
    @staticmethod
    def getAddToBospPreContent(entry):
        if annotation.ENABLE:
            return "# ADD:\n# This %s is replaced to bosp at %s\n#%s\n# @author: %s" %(entry.getType(), time.strftime('%Y-%m-%d %H:%M'), annotation.getAppendStr(), getpass.getuser())
        else:
            return None
