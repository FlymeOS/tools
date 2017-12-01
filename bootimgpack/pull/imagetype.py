'''
Created on Aug 1, 2014

@author: tangliuxiang
'''

import tempfile
import os
import shutil

import sys

from internal import bootimg

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.andprop import andprop

BOOT = "boot"
RECOVERY = "recovery"
SYSTEM = "system"
CACHE = "cache"
DATA = "data"

class imagetype(object):
    '''
    classdocs
    '''
    STAT_NONE = 0
    STAT_UNPACKED = 1
    STAT_WRONG_IMG = -1
    
    RAMDISK = "RAMDISK"
    INIT = os.path.join(RAMDISK, "init")
    INIT_RC = os.path.join(RAMDISK, "init.rc")
    DEFAULT_PROP = os.path.join(RAMDISK, "default.prop")
    
    ETC = os.path.join(RAMDISK, "etc")
    RECOVERY_FSTAB = os.path.join(ETC, "recovery.fstab")
    
    SBIN = os.path.join(RAMDISK, "sbin")
    RECOVERY_BIN = os.path.join(SBIN, "recovery")
    
    DEVICE_PROP = "ro.product.device"
    
    def __init__(self, img):
        '''
        Constructor
        '''
        self.mImg = img
        self.mUnpackDir = None
        self.mStatus = imagetype.STAT_NONE
        
    def unpack(self):
        if self.mUnpackDir is None:
            self.mUnpackDir = tempfile.mkdtemp()
            os.removedirs(self.mUnpackDir)

            try:
                bootimg.unpack(self.mImg, self.mUnpackDir)
            except:
                self.mStatus = imagetype.STAT_WRONG_IMG
            
        return self.mUnpackDir
    
    def __getFile__(self, f):
        return os.path.join(self.mUnpackDir, f)
    
    def getunpackdir(self):
        return self.mUnpackDir
    
    def getType(self):
        if self.mStatus == imagetype.STAT_NONE:
            self.unpack()
        
        if self.mStatus < imagetype.STAT_NONE:
            return None

        iType = None
        if os.path.isdir(self.mUnpackDir):
            if os.path.isfile(self.__getFile__(imagetype.INIT)) \
                    and os.path.isfile(self.__getFile__(imagetype.INIT_RC)) \
                    and os.path.isfile(self.__getFile__(imagetype.DEFAULT_PROP)):
                if os.path.isfile(self.__getFile__(imagetype.RECOVERY_BIN)) \
                        and os.path.isfile(self.__getFile__(imagetype.RECOVERY_FSTAB)) \
                        and andprop(self.__getFile__(imagetype.DEFAULT_PROP)).get(imagetype.DEVICE_PROP) is not None:
                    iType = RECOVERY
                else:
                    iType = BOOT
        return iType

    def exit(self):
        if self.mUnpackDir is not None and os.path.isdir(self.mUnpackDir):
            shutil.rmtree(self.mUnpackDir)
