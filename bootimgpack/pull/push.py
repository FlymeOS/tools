'''
Created on Sep 17, 2014

@author: tangliuxiang
'''
from bootimgpack.pull.fstab import fstab
from bootimgpack.pull.command import AndroidFile
from bootimgpack.pull.fstab import fstabconfig, entry
import os

class push(object):
    '''
    classdocs
    '''
    NORMAL_FSTAB_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "normal_fstab.xml")
    KK_FSTAB_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kk_fstab.xml")

    def __init__(self, device, fstabFile, inFile, fstab_version=1):
        '''
        Constructor
        '''
        self.mDevice = device
        
        if fstab_version == 1:
            self.mFstab = fstab(file(fstabFile), fstabconfig(push.NORMAL_FSTAB_CONFIG))
        else:
            self.mFstab = fstab(file(fstabFile), fstabconfig(push.KK_FSTAB_CONFIG))
        
        self.mEntry = self.mFstab.getEntry(self.mDevice)
        self.mInFile = inFile
        
    
    def do(self):
        mp = self.mEntry.getByKey(fstabconfig.ATTR_MP)
        print ">>> start flash %s from %s to %s" %(self.mDevice, self.mInFile, mp)
        adImage = AndroidFile(mp)
        return adImage.dd_write(self.mInFile)
