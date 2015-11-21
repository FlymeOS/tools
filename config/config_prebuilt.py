#!/usr/bin/env python

'''
Created on Sep 2, 2014

@author: tangliuxiang
'''

import os
import sys
import time
import cert
import re

PORT_ROOT = os.getenv("PORT_ROOT", os.path.dirname(os.path.dirname(__file__)))
DEFAULT_CERT_FILE = os.path.join(PORT_ROOT, "flyme", "release", "META", "apkcerts.txt")

class andprop(object):
    def __init__(self, prop):
        self.mProp = prop
        self.mParsed = False
        self.mPropDict = {}
        self.__parsed__()
    
    def __parsed__(self):
        if self.mParsed is False:
            propfile = file(self.mProp)
            for line in propfile.readlines():
                stripline = line.strip()
                if len(stripline) > 0 and stripline[0] != "#":
                    try:
                        idx = stripline.index('=')
                        self.mPropDict[stripline[:idx].strip()] = stripline[idx + 1:].strip()
                    except:
                        raise "Wrong properties: %s" % (stripline)
            
            self.mParsed = True
            
    def get(self, key, defValue = None):
        if self.mPropDict.has_key(key):
            return self.mPropDict[key]
        else:
            return defValue
        
    def set(self, key, value):
        self.mPropDict[key] = value
        
    def out(self, outPath=None):
        if outPath == None:
            outPath = self.mProp
        
        outFile = file(outPath, "w+")
        for key in self.mPropDict.keys():
            outFile.write("%s=%s" % (key, self.mPropDict[key]))
        outFile.close()



class prebuilt(object):
    '''
    classdocs
    '''

    def __init__(self, out="prebuilt.mk", bsys=None, vsys=None):
        '''
        Constructor
        '''
        if bsys is None:
            bsys = os.path.join(PORT_ROOT, "flyme/release/arm/system")

        if vsys is None:
            vsys = os.path.join(PORT_ROOT, "devices/base/vendor/system")

        self.mBsys = bsys
        self.mVsys = vsys;
        self.mOut = out;

        self.mBbuildprop = andprop(os.path.join(self.mBsys, "build.prop"))
        self.mVbuildprop = andprop(os.path.join(self.mVsys, "build.prop"))
        
        self.mPresignedAppArr = []
        self.mPbDirArr = []
        self.mPbFileArr = []
        self.mOutStr = ""

    def __getVersion__(self, bprop):
        return bprop.get("ro.build.version.incremental", bprop.get("ro.build.display.id"))

    def __getModel__(self, bprop):
        return bprop.get("ro.product.model", bprop.get("ro.product.device"))

    def do(self):
        for root, dirs, files in os.walk(self.mBsys):
            relRoot = os.path.relpath(root, self.mBsys)

            if self.__alreadyInPrebuiltDir__(relRoot):
                continue

            for d in dirs:
                if not os.path.exists(os.path.join(self.mVsys, relRoot, d)):
                    Log.d("ADD dir: %s" % (os.path.relpath(os.path.join(root, d), self.mBsys)))
                    self.mPbDirArr.append(os.path.relpath(os.path.join(root, d), self.mBsys))

            for f in files:
                if not os.path.exists(os.path.join(self.mVsys, relRoot, f)):
                    Log.d("ADD file: %s" % (os.path.relpath(os.path.join(root, f), self.mBsys)))
                    self.mPbFileArr.append(os.path.relpath(os.path.join(root, f), self.mBsys))

        self.mPresignedAppArr = self.__getPresignedApps__()
        self.__out__()

    def __getPresignedApps__(self):
        certFile = os.path.join(os.path.dirname(self.mBsys), "META", "apkcerts.txt")
        if not os.path.isfile(certFile):
            certFile = DEFAULT_CERT_FILE
        if not os.path.isfile(certFile):
            print  "Warning: %s doesn't exist! Can not generate the %s" % (certFile, self.mOut)
            return []
        return cert.getPresignedApps(certFile)

    def __alreadyInPrebuiltDir__(self, d):
        while len(d) > 0:
            for item in self.mPbDirArr:
                if item == d:
                    return True
            d = os.path.dirname(d)
        return False

    def __appendMk__(self, arr):
        for item in sorted(set(arr)):
            self.mOutStr = self.mOutStr + "    %s \\\n" % item

    @staticmethod
    def __equals__(str1, str2):
        return re.sub("^#.*$", "", str1, 0, re.M) == re.sub("^#.*$", "", str2, 0, re.M)

    def __out__(self):
        self.mOutStr = self.mOutStr + "# This file is auto generate by %s\n" % os.path.relpath(__file__, PORT_ROOT)

        self.mOutStr = self.mOutStr + "# version: from %s(%s) ==> %s(%s)\n" % \
                    (self.__getVersion__(self.mVbuildprop),
                    self.__getModel__(self.mVbuildprop),
                    self.__getVersion__(self.mBbuildprop),
                    self.__getModel__(self.mBbuildprop))
        self.mOutStr = self.mOutStr + "# Date: %s\n\n" % (time.strftime("%Y/%m/%d %H:%M"))

        self.mOutStr = self.mOutStr + "BOARD_PREBUILT_DIRS += \\\n"
        self.__appendMk__(self.mPbDirArr)

        self.mOutStr = self.mOutStr + "\n\nBOARD_PREBUILT += \\\n"
        self.__appendMk__(self.mPbFileArr)

        self.mOutStr = self.mOutStr + "\n\nBOARD_PRESIGNED_APPS += \\\n"
        self.__appendMk__(self.mPresignedAppArr)
        self.mOutStr = self.mOutStr + "\n\n # This is the end.\n"

        if not os.path.isfile(self.mOut) or not prebuilt.__equals__(self.mOutStr, file(self.mOut, 'r').read()):
            outF = file(self.mOut, 'w+')
            outF.write(self.mOutStr)
            outF.close()
        else:
            print "Already the newest prebuilt.mk, ignore....."

class Log():
    DEBUG = False
    @staticmethod
    def d(message):
        if Log.DEBUG is True:
            print message

def configPrebuilt(out="prebuilt.mk", bsys=None, vsys=None):
    prebuilt(out, bsys, vsys).do()

def main(argv):
    out = "prebuilt.mk"
    bsys = None
    vsys = None
    if len(argv) >= 1:
        out = argv[0]
    if len(argv) >= 2:
        bsys = argv[1]
    if len(argv) >= 3:
        vsys = argv[2]
    configPrebuilt(out, bsys, vsys)

if __name__ == '__main__':
    main(sys.argv[1:])
