#!/usr/bin/python
'''
Created on Jul 31, 2014

@author: tangliuxiang
'''
import sys
import os
import traceback
from pull import utils

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        outDir = sys.argv[1]
    else:
        outDir = os.getcwd()
    
    try:
        utils.PullUtils.pull(outDir)
    except Exception as e:
        traceback.print_exc()
        # See help.xml ERR_PULL_BOOT_RECOVERY_FAILED
        sys.exit(156)