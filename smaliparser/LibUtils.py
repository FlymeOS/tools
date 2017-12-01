'''
Created on Jul 22, 2014

@author: tangliuxiang
'''

from FormatSmaliLib import FormatSmaliLib
from SmaliLib import SmaliLib
import os

mSmaliLibDict = {}

LIBTYPE_FORMAT = 1
LIBTYPE_SMALILIB = 0

def getSmaliLib(libPath, smaliDirMaxDepth = 0, libType = LIBTYPE_FORMAT):
    absRoot = os.path.abspath(libPath)
    if not mSmaliLibDict.has_key(absRoot) or mSmaliLibDict[absRoot].mSmaliDirMaxDepth != smaliDirMaxDepth:
        if libType == LIBTYPE_FORMAT:
            mSmaliLibDict[absRoot] = FormatSmaliLib(libPath, smaliDirMaxDepth)
        elif libType == LIBTYPE_SMALILIB:
            mSmaliLibDict[absRoot] = SmaliLib(libPath, smaliDirMaxDepth)
    return mSmaliLibDict[absRoot]
    
def getLibPath(path):
    if os.path.isdir(path):
        children = os.listdir(path)
        for child in children:
            if os.path.isdir("%s/smali" % child):
                return path
    while not os.path.isdir("%s/smali" % path):
        path = os.path.dirname(path)
        if path == "/":
            return None
    return os.path.dirname(path)
    
def getOwnLib(smaliFile):
    libPath = getLibPath(smaliFile)
    if libPath is not None:
        return getSmaliLib(libPath, 1)
    return None

def undoFormat():
    FormatSmaliLib.undoFormat()