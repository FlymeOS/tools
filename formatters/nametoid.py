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

class nametoid(object):
    '''
    classdocs
    '''
    mIdToNameDict = {}
    CONST_LEN = len('const/high16')

    def __init__(self, xmlPath, inDir):
        '''
        Constructor
        '''
        self.smaliFileList = self.getInFileList(inDir)
        self.nameToIdMap = nametoid.getMap(xmlPath)

    @staticmethod
    def getMap(xmlPath):
        absPath = os.path.abspath(xmlPath)
        if not nametoid.mIdToNameDict.has_key(absPath):
            nametoid.mIdToNameDict[absPath] = nametoid.getIdToNameMap(absPath)
        return nametoid.mIdToNameDict[absPath]

    def getInFileList(self, inDir):
        if os.path.isfile(inDir):
            return [inDir]

        filelist = []
        smaliRe = re.compile(r'.*\.smali')
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
                idList["%s%s@%s" % (pkgName, itemType, itemName)] = itemId
                if pkgName == "android:":
                    idList["%s@%s" % (itemType, itemName)] = itemId

        return idList

    def getArrayId(self, arrayIdStr):
        idList = arrayIdStr.split()
        arrayId = "%s%s%s%s" % (idList[3][-3:-1], idList[2][-3:-1], idList[1][-3:-1], idList[0][-3:-1])
        arrayId = "0x%s" % (arrayId.replace('x', '0'))
        return arrayId.replace('0x0', '0x')

    def getArrayStr(self, arrayId):
        if cmp(arrayId[-8], "x") == 0:
            arrayStr = '0x%st 0x%st 0x%st 0x%st' % (arrayId[-2:], arrayId[-4:-2], arrayId[-6:-4], arrayId[-7:-6])
        else:
            arrayStr = '0x%st 0x%st 0x%st 0x%st' % (arrayId[-2:], arrayId[-4:-2], arrayId[-6:-4], arrayId[-8:-6])
        return arrayStr.replace('0x0', '0x')

    def getHigh16Name(self, high16Str):
        idx = high16Str.index('#')
        hName = high16Str[idx:]
        return (hName,high16Str[0:idx])

    def getApktool2High16Name(self, high16Str):
        idx = high16Str.index('#')
        hName = high16Str[idx:]
        return (hName,high16Str[0:idx])

    def nametoid(self):
        normalNameRule = re.compile(r'#[^ \t\n]*@[^ \t\n]*#t')
        arrayNameRule = re.compile(r'#[^ \t\n]*@[^ \t\n]*#a')
        high16NameRule = re.compile(r'const/high16[ ]*v[0-9][0-9]*,[ ]*#[^ \t\n]*@[^ \t\n]*#h')
        apktool2High16IdRule = re.compile(r'const/high16[ ]*v[0-9][0-9]*,[ ]*#[^ \t\n]*@[^ \t\n]*#i')

        for smaliFile in self.smaliFileList:
#           print "start modify: %s" % smaliFile
            sf = file(smaliFile, 'r+')
            fileStr = sf.read()
            modify = False

            for matchApktool2HightName in list(set(apktool2High16IdRule.findall(fileStr))):
                (hName, preStr) = self.getApktool2High16Name(matchApktool2HightName)
                newId = self.nameToIdMap.get(hName[1:-2], None)
                if newId is not None:
                    if newId[-4:] != '0000':
                        newStr = r'const%s%s' % (preStr[nametoid.CONST_LEN:], newId)
                    else:
                        newStr = r'%s%s' % (preStr, newId)
                    fileStr = fileStr.replace(matchApktool2HightName, newStr)
                    modify = True
                    Log.d(">>> change name from %s to id %s" % (matchApktool2HightName, newStr))

            for matchArrName in  list(set(arrayNameRule.findall(fileStr))):
                arrId = self.nameToIdMap.get(matchArrName[1:-2], None)
                if arrId is not None:
                    newArrIdStr = self.getArrayStr(arrId)
                    fileStr = fileStr.replace(matchArrName, newArrIdStr)
                    modify = True
                    Log.d(">>> change array name from %s to id %s" % (matchArrName[1:-2], newArrIdStr))

            for matchName in list(set(normalNameRule.findall(fileStr))):
                newId = self.nameToIdMap.get(matchName[1:-2], None)
                if newId is not None:
                    fileStr = fileStr.replace(matchName, newId)
                    modify = True
                    Log.d(">>> change name from %s to id %s" % (matchName[1:-2], newId))

            for matchHighName in list(set(high16NameRule.findall(fileStr))):
                (hName, preStr) = self.getHigh16Name(matchHighName)
                newId = self.nameToIdMap.get(hName[1:-2], None)
                if newId is not None:
                    if newId[-4:] != '0000':
                        newStr = r'const%s%s' % (preStr[nametoid.CONST_LEN:], newId)
                    else:
                        newStr = r'%s%s' % (preStr, newId[:-4])
                    fileStr = fileStr.replace(matchHighName, newStr)
                    Log.d(">>> change name from %s to id %s" % (matchHighName, newStr))
                    modify = True

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
    if len(sys.argv) == 3:
        nametoid(sys.argv[1], sys.argv[2]).nametoid()
    else:
        print "USAGE: nametoid public.xml DIRECTORY"
        print "eg: nametoid public.xml framework.jar.out"
        print "change all of type@name in framework.jar.out to resource id"
        sys.exit(1)

    print ">>> change the name to id done"

if __name__ == '__main__':
    main()
