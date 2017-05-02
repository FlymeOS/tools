'''
Created on Jul 31, 2014

@author: tangliuxiang
'''

from xml.dom import minidom
import os
from command import AndroidFile
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from formatters.log import Log

class entry(object):
    ERROR_VALUE = -1
    
    def __init__(self, strline, fsconfig):
        self.mFsconfig = fsconfig
        self.mSplitArr = strline.split()
        
    def length(self):
        return len(self.mSplitArr)
    
    def getByKey(self, key):
        return self.get(self.mFsconfig.position(key))
        
    def get(self, idx=None):
        if idx < 0 or idx >= len(self.mSplitArr):
            return None
        return self.mSplitArr[idx]
    
class fstabconfig(object):
    ARRAY_TAG = "array"
    ITEM_TAG = "item"
    BLOCK_TAG = "block"
    
    ATTR_NAME = "attr"
    NAME = "name"
    ERROR_VALUE = -1
        
    ATTR_BLOCK = "block"
    ATTR_FSTYPE = "fstype"
    ATTR_MP = "mp"
    ATTR_LENGTH = "length"
    ATTR_SIZE = "size"
    ATTR_START = "start"
    ATTR_PROP = "prop"
    ATTR_STAT = "stat"

    def __init__(self, config):
        self.mConfig = config
        self.mParsed = False
        self.mAttrArray = []
        self.mBlockDict = {}
        self.__parse__()
    
    def __parse__(self):
        if self.mParsed is True:
            return
        
        root = minidom.parse(self.mConfig).documentElement
        for array in root.getElementsByTagName(fstabconfig.ARRAY_TAG):
            if array.nodeType == minidom.Node.ELEMENT_NODE:
                if array.getAttribute(fstabconfig.NAME) == fstabconfig.ATTR_NAME:
                    for item in array.getElementsByTagName(fstabconfig.ITEM_TAG):
                        if item.nodeType == minidom.Node.ELEMENT_NODE:
                            self.mAttrArray.append(item.childNodes[0].nodeValue)
                            
        for block in root.getElementsByTagName(fstabconfig.BLOCK_TAG):
            if block.nodeType == minidom.Node.ELEMENT_NODE:
                self.mBlockDict[block.getAttribute(fstabconfig.NAME)] = block.childNodes[0].nodeValue.strip('"')

        self.mParsed = True
        
    def position(self, name):
        if self.mAttrArray is None or name is None:
            return fstabconfig.ERROR_VALUE
        
        idx = 0
        while idx < len(self.mAttrArray):
            if self.mAttrArray[idx] == name:
                return idx
            idx = idx + 1
        return fstabconfig.ERROR_VALUE
    
    def getRealName(self, block):
        if self.mBlockDict.has_key(block):
            return self.mBlockDict[block]
        else:
            return None
        
    def getBlockByRealName(self, realName):
        for bn in self.mBlockDict.keys():
            if self.mBlockDict[bn] == realName:
                return bn
        return None
        

class fstab(object):
    '''
    classdocs
    '''

    def __init__(self, fsfile, fsconfig):
        '''
        Constructor
        '''
        self.mFsconfig = fsconfig
        self.mFile = fsfile
        self.mEntryDict = {}
        self.mParsed = False
        self.parse()
    
    def parse(self):
        if self.mParsed:
            return
        
        for line in self.mFile.read().splitlines():
            strpLine = line.strip()
            if len(strpLine) > 0 and strpLine[0] != "#":
                etr = entry(strpLine, self.mFsconfig)
                realName = etr.getByKey(fstabconfig.ATTR_BLOCK)
                if realName is not None:
                    block = self.mFsconfig.getBlockByRealName(realName)
                    if block is not None:
                        self.mEntryDict[block] = etr
        
        self.mParsed = True
        
    def getEntry(self, block):
        if self.mEntryDict.has_key(block):
            return self.mEntryDict[block]
        else:
            return None
    
    def getMp(self, block):
        return self.get(block, fstabconfig.ATTR_MP)
    
    def get(self, block, attr):
        etr = self.getEntry(block)
        if etr is not None:
            return etr.getByKey(attr)
        else:
            return None

if __name__ == "__main__":
    fsconfig = fstabconfig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mtk_fstab.xml"))
    fs = fstab(AndroidFile("/proc/dumchar_info"), fsconfig)
    print fs.getMp("boot")
    print fs.getMp("recovery")
    print fs.getMp("system") 