'''
Created on Sep 17, 2014

@author: tangliuxiang
'''
from bootimgpack.pull.fstab import fstab
from bootimgpack.pull.command import AndroidFile
from bootimgpack.pull.fstab import fstabconfig
from bootimgpack.pull.mtkpull import mtkpull, mtkEntry

class mtkpush(object):
    '''
    classdocs
    '''
    def __init__(self, device, fstabFile, inFile, fstab_version=1):
        '''
        Constructor
        '''
        self.mDevice = device
        self.mFstab = fstab(AndroidFile(mtkpull.MTK_DUMCHAR_INFO), fstabconfig(mtkpull.getFstabconfigFile()))

        self.mEntry = mtkEntry(self.mDevice, self.mFstab.getEntry(self.mDevice))
        self.mInFile = inFile
        
    
    def do(self):
        mp = self.mEntry.mMp
        adImage = AndroidFile(mp)
        print ">>> start flash %s from %s to %s, start: %s, size: %s" %(self.mDevice, self.mInFile, mp, self.mEntry.mStart, self.mEntry.mSize)
        return adImage.dd_write(self.mInFile, self.mEntry.mStart, self.mEntry.mSize)
