#!/usr/bin/env python

'''
Created on 2012-12-25

@author: jock
'''
from xml.dom import minidom
import sys
import re
import os
import android_manifest

reload(sys)
sys.setdefaultencoding("utf-8")

class idtoname(object):
    '''
    classdocs
    '''
    mIdToNameDict = {}

    def __init__(self, xmlPath, inDir):
        '''
        Constructor
        '''
        self.smaliFileList = self.getInFileList(inDir)
        self.idToNameMap = idtoname.getMap(xmlPath)

    @staticmethod
    def getMap(xmlPath):
        absPath = os.path.abspath(xmlPath)
        if not idtoname.mIdToNameDict.has_key(absPath):
            idtoname.mIdToNameDict[absPath] = idtoname.getIdToNameMap(absPath)
        return idtoname.mIdToNameDict[absPath]

    def getInFileList(self, inDir):
        if os.path.isfile(inDir):
            return [inDir]

        filelist = []
        smaliRe = re.compile(r'(?:.*\.smali)')
        for root, dirs, files in os.walk(inDir):
            for fn in files:
                if bool(smaliRe.match(fn)) is True:
                    filelist.append("%s/%s" % (root, fn))

        return filelist

    @staticmethod
    def getIdToNameMap(xmlPath):
        publicXml = minidom.parse(xmlPath)
        root = publicXml.documentElement
        idList = {}

        pkgName = android_manifest.getPackageNameFromPublicXml(xmlPath)
        Log.d("package name: %s" %pkgName)
        pkgName = pkgName + ':'
        for item in root.childNodes:
            if item.nodeType == minidom.Node.ELEMENT_NODE:
                itemType = item.getAttribute("type")
                itemName = item.getAttribute("name")
                itemId = item.getAttribute("id").replace(r'0x0', r'0x')
                idList[itemId] = "%s%s@%s" % (pkgName, itemType, itemName)

        return idList

    def getArrayId(self, arrayIdStr):
        idList = arrayIdStr.split()
        arrayId = "%s%s%s%s" % (idList[3][-3:-1], idList[2][-3:-1], idList[1][-3:-1], idList[0][-3:-1])
        arrayId = "0x%s" % (arrayId.replace('x', '0'))
        return arrayId.replace('0x0', '0x')

    def getIdByHigh16(self, high16Str):
        idx = high16Str.index('0x')
        rId = '%s%s' % (high16Str[idx:], '0000')
        return (rId,high16Str[0:idx])

    def getIdByApktool2High16(self, high16Str):
        idx = high16Str.index('0x')
        rId = high16Str[idx:]
        return (rId,high16Str[0:idx])

    def idtoname(self):
        normalIdRule = re.compile(r'0x(?:[1-9a-f]|7f)[0-1][0-9a-f]{5}$', re.M)
        arrayIdRule = re.compile(r'(?:0x[0-9a-f]{1,2}t ){3}0x(?:[1-9a-f]|7f)t')
        high16IdRule = re.compile(r'const/high16[ ]*v[0-9][0-9]*,[ ]*0x(?:[1-9a-f]|7f)[0-1][0-9a-f]$', re.M)
        apktool2High16IdRule = re.compile(r'const/high16[ ]*v[0-9][0-9]*,[ ]*0x(?:[1-9a-f]|7f)[0-1][0-9a-f]0000$', re.M)

        for smaliFile in self.smaliFileList:
            #print "start modify: %s" % smaliFile
            sf = file(smaliFile, 'r+')
            fileStr = sf.read()
            modify = False

            for matchApktool2Hight16IdStr in list(set(apktool2High16IdRule.findall(fileStr))):
                (rId, preStr) = self.getIdByApktool2High16(matchApktool2Hight16IdStr)
                name = self.idToNameMap.get(rId, None)
                if name is not None:
                    fileStr = fileStr.replace(matchApktool2Hight16IdStr, r'%s#%s#i' % (preStr, name))
                    modify = True
                    Log.d("change id from %s to name %s" % (matchApktool2Hight16IdStr, name))

            for matchId in list(set(normalIdRule.findall(fileStr))):
                name = self.idToNameMap.get(matchId, None)
                if name is not None:
                    fileStr = fileStr.replace(matchId, r'#%s#t' % name)
                    modify = True
                    Log.d("change id from %s to name %s" % (matchId, name))

            for matchArrIdStr in  list(set(arrayIdRule.findall(fileStr))):
                matchArrId = self.getArrayId(matchArrIdStr)
                arrName = self.idToNameMap.get(matchArrId, None)
                if arrName is not None:
                    fileStr = fileStr.replace(matchArrIdStr, r'#%s#a' % arrName)
                    modify = True
                    Log.d("change array id from %s to name %s" % (matchArrIdStr, arrName))

            for matchHigh16IdStr in list(set(high16IdRule.findall(fileStr))):
                (rId, preStr) = self.getIdByHigh16(matchHigh16IdStr)
                name = self.idToNameMap.get(rId, None)
                if name is not None:
                    fileStr = fileStr.replace(matchHigh16IdStr, r'%s#%s#h' % (preStr, name))
                    modify = True
                    Log.d("change id from %s to name %s" % (matchHigh16IdStr, name))

            if modify is True:
                sf.seek(0, 0)
                sf.truncate()
                sf.write(fileStr)
            sf.close()

class Log:
    DEBUG = False

    @staticmethod
    def d(message):
        if Log.DEBUG: print message

    @staticmethod
    def i(message):
        print message

def main():
    print "start change id to name...."
    if len(sys.argv) == 3:
        idtoname(sys.argv[1], sys.argv[2]).idtoname()
    else:
        print "USAGE: idtoname public.xml DIRECTORY"
        print "eg: idtoname public.xml framework.jar.out"
        print "change all of the id in framework.jar.out to type@name"
        sys.exit(1)

    print "change id to name done"

if __name__ == '__main__':
    main()
