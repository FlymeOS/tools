'''
Created on Apr 3, 2014

@author: tangliuxiang
'''

from SmaliEntry import SmaliEntry

class SmaliClass(SmaliEntry):
    '''
    classdocs
    '''
    
    def getSimpleString(self):
        return  "%s %s" %(self.getType(), self.getClassName())
