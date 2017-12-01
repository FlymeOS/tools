'''
Created on Jul 22, 2014

@author: tangliuxiang
'''

import os, sys
from os import path
import Smali
from SmaliLib import SmaliLib

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from formatters.format import Format


class FormatSmaliLib(SmaliLib):
    '''
    classdocs
    '''
    
    mFormatList = {}
    def __init__(self, libPath, smaliDirMaxDepth=0):
        '''
        Constructor
        '''
        self.mFieldFormatMap = {}
        SmaliLib.__init__(self, libPath, smaliDirMaxDepth)
        
    def __format(self, root, sPath):
        sPath = os.path.abspath(sPath)
        if not FormatSmaliLib.mFormatList.has_key(sPath):
            sFormat = Format(root, sPath)
            sFormat.do(Format.ACCESS_TO_NAME | Format.RESID_TO_NAME | Format.REMOVE_LINE)
            FormatSmaliLib.mFormatList[sPath] = sFormat
            return True
        return False
    
    def getFormatSmali(self, clsName):
        oldSmali = self.getSmali(clsName)
        if oldSmali is None:
            print "Can not get class: %s in %s" %(clsName, self.getPath())
            return None
        if self.__format(self.getPath(), oldSmali.getPath()):
            self.setSmali(clsName, Smali.Smali(oldSmali.getPath()))
        return self.getSmali(clsName)
    
    @staticmethod
    def undoFormat():
        for fKey in FormatSmaliLib.mFormatList.keys():
            FormatSmaliLib.mFormatList[fKey].undo()