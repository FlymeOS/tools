#!/usr/bin/env python
'''
Created on 2012-12-11

@author: jock
'''
import SmaliParser
import os
import re
import shutil
import Smali
import SmaliLib
import string
import SCheck
import SmaliEntry
import utils

class SmaliTest(object):
    '''
    classdocs
    '''

    def __init__(self, smaliDir):
        '''
        Constructor
        '''
        if os.path.isdir("/tmp/what-smali"):
            shutil.rmtree("/tmp/what-smali")
        #smaliLib = SmaliLib.SmaliLib(smaliDir)
        #self.testSmaliLibGetUnImplementMethods("/home/tangliuxiang/work/smali/smali-4.0/devices/t328t/temp/test3/app/Phone/smali/com/android/phone/PhoneInterfaceManager.smali", smaliLib)
        for smaliFilePath in self.getSmaliFiles(smaliDir, "/tmp/what-smali/"):
            #self.testSmaliGetSuperClassName(smaliFilePath, "/tmp/what-smali/%s" %(smaliFilePath.replace(smaliDir, '',1)))
            
            #self.testSmaliLibGetOverrideMethods(smaliFilePath, smaliLib)
            #self.testSmaliGetInvokeMethods(smaliFilePath, smaliLib)
            #self.testSamliGetCalledMethod(smaliFilePath, smaliLib)
            #self.testSmaliLibGetUnImplementMethods(smaliFilePath, smaliLib)
            self.testSmaliSplit(smaliFilePath, "/tmp/what-smali/%s" %(os.path.dirname(smaliFilePath.replace(smaliDir, '',1))))
            
        
    def getSmaliFiles(self, inDir, outDir):
        filelist = []
        smaliRe = re.compile(r'(?:^.*\.smali$)')
        os.mkdir(outDir)
        for root, dirs, files in os.walk(inDir):
            for fn in files:
                if bool(smaliRe.match(fn)) is True:
                    filelist.append("%s/%s" % (root, fn))
            for dir in dirs:
                absDir = "%s/%s" %(root, dir)
                odir = "%s/%s" %(outDir, absDir.replace(inDir, '', 1))
                if os.path.isdir(odir) is False:
                    os.mkdir(odir)

        return filelist
        
    def testEntryToString(self, smaliFilePath, outFilePath):
        '''
        new a smali class from smali file
        '''
        print "testEntryToString: %s" %(smaliFilePath)

        entries = SmaliParser.SmaliParser(smaliFilePath).getEntryList()
        outFile = file(outFilePath, 'w+')
        
        for entry in entries: 
            #outFile.write("# entry start: type: %s\n%s\n"%(entry.getType(), entry.toString()))
            outFile.write("%s\n"%(entry.toString()))
        outFile.close()

        
    def TestSmaliToString(self, smaliFilePath, outFilePath):
        '''
        new a smali class from smali file
        '''
        print "TestSmaliToString: %s" %(smaliFilePath)

        outFile = file(outFilePath, 'w+')
        smaliFile = Smali.Smali(smaliFilePath)
        outFile.write(smaliFile.toString())
        outFile.close()
        
    def getAllEntryType(self, smaliFilePath, outFilePath):
        '''
        new a smali class from smali file
        '''
        print "getAllEntryType: %s" %(smaliFilePath)

        outFile1 = file("/tmp/what-smali/smali-entry-type", 'a')
        smaliFile = Smali.Smali(smaliFilePath)
        
        for entry in smaliFile.getEntryList():
            outFile1.write("%s\n" %entry.getType())
        outFile1.close()
        
        outFile = file(outFilePath, 'w+')
        outFile.write(smaliFile.toString())
        outFile.close()
        
    def testEntryOut(self, smaliFilePath, outFilePath):
        '''
        new a smali class from smali file
        '''
        print "testEntryOut: %s" %(smaliFilePath)

        smaliFile = Smali.Smali(smaliFilePath)
        
        for entry in smaliFile.getEntryList():
            entry.out("/tmp/what-smali/", "")
            
    def testEntryGetName(self, smaliFilePath, outFilePath):
        print "testSmaliGetName: %s" %(smaliFilePath)

        smaliFile = Smali.Smali(smaliFilePath)
        outFile = file(outFilePath, 'w+')
        
        for entry in smaliFile.getEntryList(): 
            outFile.write("# entry name: type: %s name:%s\n"%(entry.getType(), entry.getName()))
            outFile.write("%s\n"%(entry.toString()))
        outFile.close()
        
    def testSmaliGetSuperClassName(self, smaliFilePath, outFilePath):
        smaliFile = Smali.Smali(smaliFilePath)
        print "testSmaliGetSuper: %s, super: %s" %(smaliFilePath, smaliFile.getSuperClassName())
        
    def testSmaliLibGetOverrideMethods(self, smaliFilePath, smaliLib):
        smali = Smali.Smali(smaliFilePath)
        
        if smali.isAbstractClass() or smali.isInterface():
            return
        #print "Overrides in: %s" %smaliFilePath
        
        sMethods = smaliLib.getAllMethods(smali)
        
        for overMethod in smaliLib.getNeedOverrideMethods(smali):
            #print "\t\tMethod: %s" %overMethod
            hasMethod = False
            for method in sMethods:
                if overMethod == method:
                    hasMethod = True
                    break
            if hasMethod == False:
                print "%s doesn't implements method: %s" %(smaliFilePath, overMethod)
                
    def testSmaliGetInvokeMethods(self, smaliFilePath, smaliLib):
        smali = Smali.Smali(smaliFilePath)
        for method in smali.getInvokeMethods():
            print "Invoke methods: type: %s, cls: %s, method: %s" %(method.type, method.cls, method.method)
            
    def testSamliGetCalledMethod(self, smaliFilePath, smaliLib):
        smali = Smali.Smali(smaliFilePath)
        
        print "Smali: %s" %smaliFilePath
        for method in smaliLib.getCalledMethod(smali):
            print "method was called: type: %s, cls: %s, method: %s" %(method.type, method.cls, method.method)
            
    def testSmaliLibCheckMethod(self, smaliFilePath, smaliLib):
        smali = Smali.Smali(smaliFilePath)
        #print "Smali: %s" %smaliFilePath
        smaliLib.checkMethods(smali)
        
    def testSmaliLibGetUnImplementMethods(self, smaliFilePath, smaliLib):
        smali = Smali.Smali(smaliFilePath)
        methodsList = smaliLib.getUnImplementMethods(smali)
        for method in methodsList:
            print "%s: %s" %(smali.getClassName(), method)
            
    def testSmaliSplit(self, smaliFilePath, outFilePath):
        smali = Smali.Smali(smaliFilePath)
        smali.split(outFilePath)
        
def testSCheckGetCanReplaceMethods(vendorDir, aosp, bosp):
    sCheck = SCheck.SCheck(vendorDir, aosp, bosp)
    for key in sCheck.mBSLib.mSDict.keys():
        smali = sCheck.mBSLib.getSmali(key)
        methodsList = sCheck.getCanReplaceToBoardMethods(smali, smali.getEntryList(SmaliEntry.METHOD))
        if methodsList is None:
            continue
        for method in methodsList:
            print "%s: %s" %(smali.getClassName(), method.getName())
            
def testSCheckAutoComplete(vendorDir, aosp, bosp, mergedDir):
    sCheck = SCheck.SCheck(vendorDir, aosp, bosp, mergedDir)
    
    for key in sCheck.mMSLib.mSDict.keys():
        smali = sCheck.mMSLib.getSmali(key)
        if smali.getPackageName() == r'Lcom/baidu/internal/telephony/sip':
            continue
        
#        print "packageName: %s, clsName: %s" %(smali.getPackageName(), smali.getClassName())
        methodsList = sCheck.autoComplete(smali)
        for method in methodsList:
            print "%s: %s" %(method.getClassName(), method.getName())
    
def testSCheckGetUnImplementMethods(vendorDir, aosp, bosp, mergedDir):
    sCheck = SCheck.SCheck(vendorDir, aosp, bosp, mergedDir)
    
    for key in sCheck.mMSLib.mSDict.keys():
        smali = sCheck.mMSLib.getSmali(key)
        if smali.getPackageName() == r'Lcom/baidu/internal/telephony/sip':
            continue
        
#        print "packageName: %s, clsName: %s" %(smali.getPackageName(), smali.getClassName())
        methodsList = sCheck.getUnImplementMethods(smali)
        for method in methodsList:
            print "%s: %s" %(smali.getClassName(), method)
    
#    smali = Smali.Smali("/home/tangliuxiang/work/smali/smali-4.0/devices/t328t/temp/test3/app/Phone/smali/com/android/phone/PhoneInterfaceManager.smali")
#    methodsList = sCheck.getUnImplementMethods(smali)
#    for method in methodsList:
#        print "%s: %s" %(smali.getClassName(), method)
    
            
def testSmaliGetSmaliPathList(smaliDir):
    smaliDict = utils.getSmaliDict(smaliDir)
    for key in smaliDict.keys():
        print "key: %s, file: %s" %(key, smaliDict[key].mPath)
        
if __name__ == "__main__":
    print ""
    smali = SmaliTest("/home/tangliuxiang/work/smali/smali-mtk-4.2/devices/h30_t00/framework.jar.out/")
    #smali = SmaliTest("/home/tangliuxiang/work/smali/smali-4.0/devices/t328t/temp/test-telephony")
    #testSmaliGetSmaliPathList("/home/tangliuxiang/work/smali/smali-mtk-4.2/devices/h30_t00/temp/ori/framework/")
    # main()
    
    #testSCheckGetCanReplaceMethods("/home/tangliuxiang/work/smali/smali-4.0/devices/t328t/temp/ori/framework", "/home/tangliuxiang/work/smali/smali-4.0/reference/aosp", "/home/tangliuxiang/work/smali/smali-4.0/devices/t328t/temp/baidu")
    #testSCheckGetUnImplementMethods("/home/tangliuxiang/work/smali/smali-4.0/devices/t328t/temp/test-telephony/ori", "/home/tangliuxiang/work/smali/smali-4.0/reference/aosp", "/home/tangliuxiang/work/smali/smali-4.0/reference/bosp")
    #testSCheckGetUnImplementMethods("/home/tangliuxiang/work/smali/smali-4.0/devices/t328t/temp/ori/framework",  "/home/tangliuxiang/work/smali/smali-4.0/reference/aosp", "/home/tangliuxiang/work/smali/smali-4.0/reference/bosp", "/home/tangliuxiang/work/smali/smali-4.0/devices/t328t/temp/test3")
    #testSCheckAutoComplete("/home/tangliuxiang/work/smali/smali-4.2/devices/p6/temp/ori",  "/home/tangliuxiang/work/smali/smali-4.2/reference/aosp", "/home/tangliuxiang/work/smali/smali-4.2/devices/p6/temp/baidu", "/home/tangliuxiang/work/smali/smali-4.2/devices/p6/temp/test-1")
