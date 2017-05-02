'''
Created on Sep 3, 2014

@author: tangliuxiang
'''
import re
import os
import sys

NAME = "name"
CERTIFICATE = "certificate"
PRIVATE_KEY = "private_key"
PRESIGNED = "PRESIGNED"

class certentry(object):
    def __init__(self, line):
        self.mLine = re.sub("^[ \t]*|[ \t]*$", "", line)
        self.mDict = {}
        self.__parse__()
        
    def __parse__(self):
        if len(self.mLine) > 0:
            splitArray = self.mLine.replace("=", " ").split()
            assert len(splitArray) % 2 == 0, "Wrong apkcerts in line: %s" %(self.mLine)
            
            i = 0
            while (i + 1) < len(splitArray):
                self.mDict[splitArray[i]] = splitArray[i + 1].replace('"','')
                i = i + 2
                
    def get(self, key, defValue = None):
        if self.mDict.has_key(key):
            return self.mDict[key]
        else:
            return defValue

class cert(object):
    '''
    classdocs
    '''

    def __init__(self, cf):
        '''
        Constructor
        '''
        self.mApkCerts = cf
        self.mEntryDict = {}
        self.__parse__()
    
    def __parse__(self):
        for line in file(self.mApkCerts, 'r').readlines():
            entry = certentry(line)
            entryName = entry.get(NAME)
            if entryName is not None:
                self.mEntryDict[entryName] = entry
            else:
                print "Warning: Wrong apkcerts in line: %s" %(line)
            assert entryName is not None, "Wrong apkcerts in line: %s" %(line)
    
    def getApps(self, tag, value):
        appList = []
        for appName in self.mEntryDict.keys():
            if self.mEntryDict[appName].get(tag) == value:
                appList.append(appName)
        return appList

    def getPresignedApps(self):
        return self.getApps(CERTIFICATE, PRESIGNED)
    
    def getAppCertificate(self, appName):
        appName = formatAppName(appName)
        if self.mEntryDict.has_key(appName):
            return self.mEntryDict[appName].get(CERTIFICATE)
        else:
            return None
        
    def getAppPrivateKey(self, appName):
        appName = formatAppName(appName)
        if self.mEntryDict.has_key(appName):
            return self.mEntryDict[appName].get(PRIVATE_KEY)
        else:
            return None
    
    def getAppCertType(self, appName):
        ct = self.getAppCertificate(appName)
        return formatCertType(ct)

def formatAppName(appName):
    if appName is not None:
        (root, ext) = os.path.splitext(os.path.basename(appName))
        return "%s.apk" %root 
    else:
        print "Warning: Wrong parameters, appName is None"
        return None
    
def formatCertType(ct):
    if ct is not None:
        return re.sub("\..*$", "", os.path.basename(ct))
    else:
        return None

def getPresignedApps(cf):
    return cert(cf).getPresignedApps()

def main(argv):
    if len(argv) >= 1:
        ct = cert(argv[0])
        print ct.getPresignedApps()
        print ct.getAppCertType("BaiduGallery3D")
        print ct.getAppCertType("BaiduGallery3D.apk")
        print ct.getAppCertType("what/app/BaiduGallery3D.apk")
        print ct.getAppCertType("BaiduBrowser.apk")

if __name__ == '__main__':
    main(sys.argv[1:])
