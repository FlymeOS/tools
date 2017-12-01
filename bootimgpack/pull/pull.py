'''
Created on Jul 31, 2014

@author: tangliuxiang
'''
from command import AndroidFile
import tempfile
import os
import imagetype
import shutil
import string
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from formatters.log import Log

LOG_TAG = "pull"

class pull(object):
    '''
    classdocs
    '''
    mPull = None
    PROC_PARTITIONS = "/proc/partitions"
    BLOCK_DIR = "/dev/block"
    
    MIN_SIZE = 4096
    MAX_SIZE = 51200
    
    def __init__(self):
        '''
        Constructor
        '''
        self.mWorkdir = tempfile.mkdtemp()
        self.mImgDict = {}
        self.mOutDir = os.getcwd()
    
    @staticmethod
    def getInstance():
        if pull.mPull is None:
            pull.mPull = pull()
        return pull.mPull
    
    def getAdPartitions(self, minsize, maxsize):
        adPt = AndroidFile(pull.PROC_PARTITIONS)
        assert adPt.exist(), "File %s is not exist in phone!" %(pull.PROC_PARTITIONS)
        
        outAdDict = {}
        Log.i(LOG_TAG, "Try to create block of partitions ...")
        for etr in adPt.read().splitlines():
            stripEtr = etr.strip("\n")
            if len(stripEtr) > 0 and stripEtr[0] != "#":
                splitArray = stripEtr.split()
                if len(splitArray) == 4:
                    try:
                        blkSize = string.atoi(splitArray[2])
                    except:
                        continue
                    blkName = splitArray[3]
                    adBlk = AndroidFile("%s/%s" %(pull.BLOCK_DIR, blkName))
                    if blkSize >= minsize and blkSize <= maxsize and adBlk.exist():
                        outAdDict[blkName] = adBlk
        Log.i(LOG_TAG, "Create block of partitions done!")
        return outAdDict
    
    def __pull__(self, adDict):
        Log.i(LOG_TAG, "Pull blocks from device ...")
        for blkName in adDict.keys():
            pcOut = os.path.join(self.mWorkdir, blkName)
            Log.i(LOG_TAG, "Pull %s to %s" %(blkName, pcOut))
            if adDict[blkName].pull(pcOut):
                Log.i(LOG_TAG, "...")
                img = imagetype.imagetype(pcOut)
                itype = img.getType()
                if itype is not None:
                    self.mImgDict[itype] = pcOut
                img.exit()
            if len(self.mImgDict.keys()) >= 2: # both boot and rec had found
                return
                
    def out(self, outDir = None):
        if outDir is None:
            outDir = self.mOutDir
        for itype in self.mImgDict.keys():
            outFile = os.path.join(outDir, "%s.img" %(itype))
            shutil.copyfile(self.mImgDict[itype], outFile)
            Log.i(LOG_TAG, "Out: %s" %(outFile))
        shutil.rmtree(self.mWorkdir)

    @staticmethod
    def do(outDir=None):
        p = pull.getInstance()
        adDict = p.getAdPartitions(pull.MIN_SIZE, pull.MAX_SIZE)
        p.__pull__(adDict)
        p.out(outDir)
        if os.path.isfile(os.path.join(outDir, "boot.img")) \
                and os.path.isfile(os.path.join(outDir, "recovery.img")):
            return True
        return False
