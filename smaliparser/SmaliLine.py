'''
Created on Feb 26, 2014

@author: tangliuxiang
'''
import re

blankLineRule = re.compile(r'^ *#.*$|^ *$')
entryStartRule = re.compile(r'^\..*$')

def getLineType(line):
    lineType = SmaliLine.TYPE_NORMAL_LINE
    if blankLineRule.match(line) is not None:
        lineType = SmaliLine.TYPE_BLANK_LINE
    elif entryStartRule.match(line) is not None:
        lineType = SmaliLine.TYPE_DOT_LINE

    return lineType

class SmaliLine(object):
    '''
    classdocs
    '''

    TYPE_NORMAL_LINE = 0    
    TYPE_BLANK_LINE = 1
    TYPE_DOT_LINE = 2

    def __init__(self, line):
        '''
        Constructor
        '''
        self.setLine(line)
    
    def setLine(self, line):
        self.mLineType = getLineType(line)
        self.mLine = line
        
    def getLine(self):
        return self.mLine
        
    def getType(self):
        return self.mLineType
    
    def isBlank(self):
        return self.mLineType is SmaliLine.TYPE_BLANK_LINE
        
    def getDotType(self):
        if self.mLine is None and self.mLineType is not SmaliLine.TYPE_DOT_LINE:
            return None
        lstr = re.sub(r'^\.end *', '', self.mLine)
        lstr = re.sub(r'^\.', '', lstr)
        arr = lstr.split()
        return arr[0]

    def isDotEnd(self):
        if self.mLine is None and self.mLineType is not SmaliLine.TYPE_DOT_LINE:
            return False
        if re.compile(r'^\.end.*$').match(self.mLine) is None:
            return False
        else:
            return True
