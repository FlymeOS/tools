'''
Created on Apr 4, 2014

@author: tangliuxiang
'''
import utils
import Replace

from formatters.log import Paint 


MAX_CHECK_INVOKE_DEEP = 50

class SAutoCom(object):
    '''
    classdocs
    '''

    @staticmethod
    def autocom(vendorDir, aospDir, bospDir, mergedDir, outdir, comModuleList):
        sReplace = Replace.Replace(vendorDir, aospDir, bospDir, mergedDir)

        for module in comModuleList:
            print Paint.bold(" Complete missed method in %s") % module
            needComleteDir = '%s/%s' % (mergedDir, module)
            sDict = utils.getSmaliDict(needComleteDir)
            for clsName in sDict.keys():
                mSmali = sReplace.mMSLib.getSmali(clsName)
                if mSmali is None:
                    utils.SLog.d("can not get class: %s" % clsName)
                    continue
            
                (canReplaceEntryList, canNotReplaceEntryList) = sReplace.preReplaceCheck(mSmali)

                for entry in canReplaceEntryList:
                    sReplace.replaceEntryInFile(entry, SAutoCom.getAutocomPartPath(sReplace, entry, outdir))
                
                for entry in canNotReplaceEntryList:
                    sReplace.appendBlankEntry(entry, SAutoCom.getAutocomPartPath(sReplace, entry, outdir))
    
    @staticmethod
    def getAutocomPartPath(sCheck, entry, outdir):
        cls = entry.getClassName()
        cSmali = sCheck.mVSLib.getSmali(cls)
                
        if cSmali is None:
            utils.SLog.d("can not get class %s from: %s" % (cls, sCheck.mVSLib.getPath()))
            return
    
        jarName = cSmali.getJarName()
        pkgName = cSmali.getPackageName()
        
        return r'%s/%s/smali/%s/%s.smali.part' % (outdir, jarName, pkgName, cSmali.getClassBaseName()) 
    
