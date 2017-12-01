'''
Created on Jul 31, 2014

@author: tangliuxiang
'''
import os
import sys
import imagetype

from fstab import fstabconfig
from fstab import fstab
from command import AndroidFile
from fstab import entry
from pull import pull

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from formatters.log import Log

LOG_TAG = "mtkpull"

class mtkEntry(entry):
    def __init__(self, name, etr):
        self.mName = name
        self.mEntry = etr
        
        assert self.mEntry is not None, "Wrong block mount info ....."
        
        self.mBlockName = self.getByKey(fstabconfig.ATTR_BLOCK)
        self.mMp = self.getByKey(fstabconfig.ATTR_MP)
        self.mSize = int(self.getByKey(fstabconfig.ATTR_SIZE), 16)
        self.mStart = int(self.getByKey(fstabconfig.ATTR_START), 16)
        self.mFstype = self.getByKey(fstabconfig.ATTR_FSTYPE)
        
    def length(self):
        return self.mEntry.length()
    
    def getByKey(self, key):
        return self.mEntry.getByKey(key)
        
    def get(self, idx=None):
        return self.mEntry.get(idx)
        
class mtkpull(pull):
    '''
    classdocs
    '''
    MTK_DUMCHAR_INFO = "/proc/dumchar_info"
    MTK_FSTAB_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mtk_fstab.xml")
    mPull = None

    def __init__(self):
        '''
        Constructor
        '''
        super(mtkpull, self).__init__()
        self.mFstabConfig = fstabconfig(mtkpull.getFstabconfigFile())
        self.mFstab = fstab(AndroidFile(mtkpull.MTK_DUMCHAR_INFO), self.mFstabConfig)
        
        Log.d(LOG_TAG, "work dir: %s" %(self.mWorkdir))
        
        self.mBootImg = os.path.join(self.mWorkdir, "boot.img")
        self.mRecoveryImg = os.path.join(self.mWorkdir, "recovery.img")
    
    @staticmethod
    def getFstabconfigFile():
        return mtkpull.MTK_FSTAB_CONFIG 
    
    @staticmethod
    def getInstance():
        if mtkpull.mPull is None:
            mtkpull.mPull = mtkpull()
        return mtkpull.mPull
    
    @staticmethod
    def do(outDir=None):
        p = mtkpull.getInstance()
        p.__pull__()
        
        if os.path.isfile(p.mBootImg):
            bootimg = imagetype.imagetype(p.mBootImg)
            assert bootimg.getType() == imagetype.BOOT, "Wrong boot.img....."
            p.mImgDict[imagetype.BOOT] = p.mBootImg
            bootimg.exit()
        
        if os.path.isfile(p.mRecoveryImg):
            recoveryimg = imagetype.imagetype(p.mRecoveryImg)
            assert recoveryimg.getType() == imagetype.RECOVERY, "Wrong recovery.img....."
            p.mImgDict[imagetype.RECOVERY] = p.mRecoveryImg
            recoveryimg.exit()
        p.out(outDir)
        if os.path.isfile(os.path.join(outDir, "boot.img")) \
        and os.path.isfile(os.path.join(outDir, "recovery.img")):
            return True
        return False

    def __pull__(self):
        bootEntry = mtkEntry(imagetype.BOOT, self.mFstab.getEntry(imagetype.BOOT))
        Log.i(LOG_TAG, "Try to pull boot partition from device ...")
        adBoot = AndroidFile(bootEntry.mMp)
        adBoot.pull(self.mBootImg, bootEntry.mStart, bootEntry.mSize)
        
        recoveryEntry = mtkEntry(imagetype.RECOVERY, self.mFstab.getEntry(imagetype.RECOVERY))
        Log.i(LOG_TAG, "Try to pull recovery partition from device ...")
        adRecovery = AndroidFile(recoveryEntry.mMp)
        adRecovery.pull(self.mRecoveryImg, recoveryEntry.mStart, recoveryEntry.mSize)
        
    @staticmethod
    def isMtkDevice():
        return AndroidFile(mtkpull.MTK_DUMCHAR_INFO).exist()
