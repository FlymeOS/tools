'''
Created on Jul 31, 2014

@author: tangliuxiang
'''
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from bootimgpack.pull.push import push
from bootimgpack.pull.mtkpush import mtkpush
from command import AdbShell, SuShell
from formatters.log import Log
from mtkpull import mtkpull
from pull import pull

import tempfile

LOG_TAG = "pull_boot_recovery"

def check():
    AdbShell().waitdevices(True)
    
class PullUtils():

    @staticmethod
    def pull(outDir):
        ret = False
        Log.i(LOG_TAG, "Begin pull boot and recovery, make sure your phone was connected and adb devices is fine!")
        Log.i(LOG_TAG, "It may take a few minutes, please wait....")
        check()
        Log.i(LOG_TAG, "adb connect success.")
        #if mtkpull.isMtkDevice() and mtkpull.do(outDir):
        #    Log.d("pull_boot_recovery", "Success use mtkpull to pull images....")
        #    ret = True
        #else:
        if pull.do(outDir):
            Log.d("pull_boot_recovery", "Success to pull images....")
            ret = True
        assert ret == True, "Failed to pull images....."

class PushUtils():

    @staticmethod
    def push(device, fstabFile, inFile, fstab_version = 1):
        ret = False
        Log.i("flash boot or recovery", "It may take a few minutes, please wait....")
        check()
        if mtkpull.isMtkDevice() and mtkpush(device, fstabFile, inFile, fstab_version).do():
            Log.d("flash boot or recovery", "Success use mtkpush to flash images....")
            ret = True
        else:
            if push(device, fstabFile, inFile, fstab_version).do():
                Log.d("flash boot or recovery", "Success to flash images....")
                ret = True
        assert ret == True, "Failed to flash image %s for %s" %(inFile, device)

        return ret
            
        
        
        
        

