'''
Created on Jun 3, 2014

@author: tangliuxiang
'''

import Smali
import SmaliEntry
import SAutoCom
import os
import utils
import LibUtils
import Content
import FormatSmaliLib

class FileReplace(utils.precheck):
    mASLib = LibUtils.getSmaliLib(utils.AOSP)
    
    def __init__(self, withCheck):
        self.outMap = {}
        self.curSuccess = True
        self.curAction = ""
        self.mWithCheck = withCheck
        self.curClassName = ""
        self.init()
        self.curSrcLib = None
        self.curDstLib = None
        
        
    def fail(self, dstLib, entry, failEntryList, tobosp = False):
        if self.curSuccess:
            utils.SLog.fail(">>>> Failed on %s" %(self.curAction))
            utils.SLog.fail("")
            if tobosp:
                utils.SLog.fail("        >> Failed to replace %s %s in %s to bosp...." %(entry.getType(), entry.getName(), entry.getClassName()))
            else:
                utils.SLog.fail("        >> Failed to keep the %s %s in %s which was added by vendor!" %(entry.getType(), entry.getName(), entry.getClassName()))
            self.curSuccess = False
        utils.SLog.fail("")
        utils.SLog.fail("            >> can not replace %s %s in %s" %(entry.getType(), entry.getName(), dstLib.getSmali(entry.getClassName()).getPath()))
        for fEntry in failEntryList:
            utils.SLog.fail("                %s %s in %s" %(fEntry.getType(), fEntry.getName(), dstLib.getSmali(fEntry.getClassName()).getPath()))

    def __replaceOneFile__(self, srcSmali, dstSmali):
        utils.SLog.i("\n>>>> Try replace %s to %s" %(dstSmali.getPath(), srcSmali.getPath()))
        #dstLib = LibUtils.getOwnLib(dstSmali.getPath())
        #srcLib = LibUtils.getOwnLib(srcSmali.getPath())
         
        clsName = srcSmali.getClassName()
        self.curClassName = clsName
        srcSmali = self.curSrcLib.getFormatSmali(clsName)
        dstSmali = self.curDstLib.getFormatSmali(clsName)
        
        for entry in srcSmali.getEntryList(SmaliEntry.FIELD):
            if not dstSmali.hasField(entry.getName()):
                dstSmali.addEntry(entry)
        
        for entry in srcSmali.getEntryList(SmaliEntry.METHOD):
            (canReplaceEntry, canNotReplaceEntry) = self.curDstLib.getCanReplaceEntry(self.curSrcLib, clsName, [entry], False)
            if len(canNotReplaceEntry) > 0:
                self.fail(self.curDstLib, entry, canNotReplaceEntry, True)
                return False
        
        utils.annotation.disable()
        for entry in dstSmali.getEntryList(SmaliEntry.FIELD):
            if not srcSmali.hasField(entry.getName()) and utils.precheck.canAddField(entry):
                self.curSrcLib.replaceEntry(self.curDstLib, entry, True, False)
            
        self.curDstLib.setSmali(clsName, srcSmali)
        nDstLib = FormatSmaliLib.FormatSmaliLib(LibUtils.getLibPath(dstSmali.getPath()))
        noError = True
        for dEntry in dstSmali.getEntryList():
            if not srcSmali.hasEntry(dEntry.getType(), dEntry.getName()):
                if dEntry.getType() == SmaliEntry.METHOD:
                    if not self.mWithCheck:
                        self.curDstLib.replaceEntry(nDstLib, dEntry, True, False)
                        continue
                    
                    (canReplaceEntry, canNotReplaceEntry) = self.curDstLib.getCanReplaceEntry(nDstLib, clsName, [dEntry], False)
                    if len(canNotReplaceEntry) > 0:
                        self.fail(self.curDstLib, dEntry, canNotReplaceEntry)
                        noError = False
                    else:
                        for entry in canReplaceEntry:
                            self.curDstLib.replaceEntry(nDstLib, entry, True, False)
        
        utils.annotation.enable()
        
        # add precontent
        if noError:
            nDstSmali = Smali.Smali(dstSmali.getPath())
            for entry in Smali.Smali(srcSmali.getPath()).getEntryList():
                if nDstSmali.hasEntry(entry.getType(), entry.getName()):
                    dEntry = dstSmali.getEntry(entry.getType(), entry.getName())
                    if dEntry.getContentStr() != entry.getContentStr():
                        self.__setPreContent__(srcSmali, entry, utils.annotation.getReplaceToBospPreContent(entry))
                else:
                    self.__setPreContent__(srcSmali, entry, utils.annotation.getAddToBospPreContent(entry))
            srcSmali.setDefaultOutPath(dstSmali.getPath())
            self.outMap[srcSmali] = dstSmali

        return noError

    @staticmethod
    def __setPreContent__(smali, entry, nPreContentStr):
        nPreContent = Content.Content(entry.getPreContentStr())
        nPreContent.append(nPreContentStr)
        
        nEntry = smali.getEntry(entry.getType(), entry.getName())
        nEntry.setPreContent(nPreContent)
        
        smali.modify()
        
    def replace(self, src, dst):
        srcSmali = Smali.Smali(src)
        dstSmali = Smali.Smali(dst)
        
        if utils.precheck.shouldIgnore(srcSmali):
            utils.SLog.fail(">>>> Failed to replace %s to %s" %(dst, src))
            return False
        
        self.curSrcLib = LibUtils.getOwnLib(src)
        self.curDstLib = LibUtils.getOwnLib(dst)
        
        self.curSrcLib.cleanModify()
        self.curDstLib.cleanModify()

        srcSmali = self.curSrcLib.getFormatSmali(srcSmali.getClassName())
        dstSmali = self.curDstLib.getFormatSmali(dstSmali.getClassName())

        srcMemberSmaliList = srcSmali.getMemberSmaliList()
        dstMemberSmaliList = dstSmali.getMemberSmaliList()
    
        success = True
        self.outMap.clear()
        self.curSuccess = True
        self.curAction = "replace %s to %s" %(dst, src)
        
        nDstLib = FormatSmaliLib.FormatSmaliLib(LibUtils.getLibPath(dstSmali.getPath()))
        
        srcMemberSmaliList.append(srcSmali)
        dstMemberSmaliList.append(dstSmali)
        
        for sMem in srcMemberSmaliList:
            dstPath = '%s/%s' %(os.path.dirname(dst), os.path.basename(sMem.getPath()))
            utils.SLog.d("DSTPATH: %s" %dstPath)
            self.curDstLib.setSmali(sMem.getClassName(), sMem)
            sMem.setDefaultOutPath(dstPath)
        
        utils.annotation.disable()
        for sMem in srcMemberSmaliList:
            for dMem in dstMemberSmaliList:
                if dMem.getClassName() == sMem.getClassName():
                    for dEntry in dMem.getEntryList():
                        if not sMem.hasEntry(dEntry.getType(), dEntry.getName()):
                            if self.mWithCheck:
                                if dEntry.getType() == SmaliEntry.METHOD:
                                    utils.SLog.d("Try to replace method %s in %s" %(dEntry.getName(), dEntry.getClassName()))
                                    if not dEntry.hasKey(utils.KEY_PRIVATE) and self.curDstLib.isMethodUsed(FileReplace.mASLib, sMem, dEntry.getName()):
                                        (canReplaceEntry, canNotReplaceEntry) = self.curDstLib.getCanReplaceEntry(nDstLib, dMem.getClassName(), [dEntry], False)
                                        if len(canNotReplaceEntry) > 0:
                                            self.fail(self.curDstLib, dEntry, canNotReplaceEntry)
                                            return False
                                        else:
                                            for entry in canReplaceEntry:
                                                self.curDstLib.replaceEntry(nDstLib, entry, True, False)
                                elif dEntry.getType() == SmaliEntry.FIELD:
                                    if utils.precheck.canAddField(dEntry):
                                        self.curDstLib.replaceEntry(nDstLib, dEntry, True, False)
                                    elif dEntry.hasKey(utils.KEY_PUBLIC):
                                        self.fail(self.curDstLib, dEntry, canNotReplaceEntry)
                                        return False
                            else:
                                self.curDstLib.replaceEntry(nDstLib, dEntry, True, False)
                        else:
                            sEntry = sMem.getEntry(dEntry.getType(), dEntry.getName())
                            if self.mWithCheck and sEntry.getType() == SmaliEntry.METHOD:
                                (canReplaceEntry, canNotReplaceEntry) = self.curDstLib.getCanReplaceEntry(self.curDstLib, dMem.getClassName(), [sEntry], False)
                                if len(canNotReplaceEntry) > 0:
                                    self.fail(self.curDstLib, sEntry, canNotReplaceEntry)
                                    return False

        utils.annotation.enable()
        if success:
            for sMem in srcMemberSmaliList:
                for dMem in dstMemberSmaliList:
                    if dMem.getClassName() == sMem.getClassName():
                        nDstSmali = Smali.Smali(dMem.getPath())
                        for sEntry in Smali.Smali(sMem.getPath()).getEntryList():
                            if nDstSmali.hasEntry(sEntry.getType(), sEntry.getName()):
                                dEntry = nDstSmali.getEntry(sEntry.getType(), sEntry.getName())
                                if dEntry.getContentStr() != sEntry.getContentStr():
                                    self.__setPreContent__(sMem, sMem.getEntry(sEntry.getType(), sEntry.getName()), utils.annotation.getReplaceToBospPreContent(sEntry))
                            else:
                                self.__setPreContent__(sMem, sMem.getEntry(sEntry.getType(), sEntry.getName()), utils.annotation.getAddToBospPreContent(sEntry))
            
            self.curDstLib.out()
            utils.SLog.ok(">>>> SUCCESS: replace %s to %s" %(dst, src))
        else:
            utils.SLog.fail(">>>> Failed to replace %s to %s" %(dst, src))
        return success

    def precheck(self, tSmali, bSmali, entry):
        if tSmali is not None:
            if tSmali.getClassName() == self.curClassName:
                return True
        
        if tSmali is not None \
            and bSmali is not None \
            and entry.getType() == SmaliEntry.METHOD:
                if entry.isConstructor():            
                    for field in tSmali.getEntryList(SmaliEntry.FIELD):
                        if not bSmali.hasEntry(SmaliEntry.FIELD, field.getName()):
                            return False
                elif entry.getSimpleName() == "onTransact":
                    utils.SLog.e(">>> onTransact is an binder interface, it shouldn't be replace, if you want to replace, find the stub and proxy, replace them all!")
                    utils.SLog.e("       such as if you want replace method in IAlarmManager$Stub.smali")
                    utils.SLog.e("       you better use smalitobosp to replace the IAlarmManager$Stub.smali and IAlarmManager$Stub$Proxy.smali both!")
                    return False
        return True
    
    def init(self):
        utils.precheck.setInstance(self)
        
    def __exit__(self):
        LibUtils.undoFormat()

    @staticmethod
    def stb_withoutcheck(src, dst):
        srcSmali = Smali.Smali(src)
        dstSmali = Smali.Smali(dst)

        if utils.precheck.shouldIgnore(srcSmali):
            utils.SLog.fail(">>>> Failed to replace %s to %s" % (dst, src))
            return False

        curSrcLib = LibUtils.getOwnLib(src)
        curDstLib = LibUtils.getOwnLib(dst)

        srcSmali = curSrcLib.getFormatSmali(srcSmali.getClassName())
        dstSmali = curDstLib.getFormatSmali(dstSmali.getClassName())

        srcMemberSmaliList = srcSmali.getMemberSmaliList()
        dstMemberSmaliList = dstSmali.getMemberSmaliList()

        srcMemberSmaliList.append(srcSmali)
        dstMemberSmaliList.append(dstSmali)

        for dMem in dstMemberSmaliList:
            os.remove(dMem.getPath())

        for sMem in srcMemberSmaliList:
            sMem = curSrcLib.getFormatSmali(sMem.getClassName())
            sMem.out(os.path.join(os.path.dirname(dst), os.path.basename(sMem.getPath())))

SMALITOBOSP_ADVICE = "%s/help/smalitobosp_advice" %os.path.dirname(os.path.abspath(__file__))
SMALITOBOSP_SUCCESS = "%s/help/smalitobosp_success" %os.path.dirname(os.path.abspath(__file__))

def smalitobosp(args, withCheck = True):
    fReplace = FileReplace(withCheck)

    for smaliFile in args:
        src = utils.getMatchFile(smaliFile, utils.BOSP)
        dst = utils.getMatchFile(smaliFile, utils.TARGET)
        
        if withCheck:
            if fReplace.replace(src, dst) is False:
                raise
        else:
            fReplace.stb_withoutcheck(src, dst)
    utils.SLog.setAdviceStr(file(SMALITOBOSP_ADVICE).read())
    utils.SLog.setSuccessStr(file(SMALITOBOSP_SUCCESS).read())
    #utils.SLog.conclude()
    fReplace.__exit__()
        
