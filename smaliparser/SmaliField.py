'''
Created on Feb 26, 2014

@author: tangliuxiang
'''
import SmaliEntry

class SmaliField(SmaliEntry.SmaliEntry): 
    '''
    classdocs
    '''
    
    def getName(self):
        if self.mName is None:
            firstLine = self.getContent().getFirstLine()
            splitArray = firstLine.split(r'=')[0].split()
            #self.mName = splitArray[len(splitArray) - 1].split(r':')[0]
            self.mName = splitArray[len(splitArray) - 1]
        return self.mName