'''
Created on Feb 26, 2014

@author: tangliuxiang
'''
from SmaliLine import SmaliLine

class Content(object):
    def __init__(self, contentStr = None):
        self.ContentStr = contentStr
        
    def append(self, contentStr):
        if self.ContentStr is not None:
            self.ContentStr = "%s\n%s" %(self.ContentStr, contentStr)
        else:
            self.ContentStr = contentStr
    
    def clone(self):
        return Content(self.getContentStr())
            
    def getContentStr(self):
        return self.ContentStr
    
    def setContentStr(self, contentStr):
        self.ContentStr = contentStr
        
    def isMultiLine(self):
        firstLine = True
        for line in self.ContentStr.split('\n'):
            if firstLine is False:
                if not SmaliLine(line).isBlank():
                    return True
            else:
                firstLine = True
    
        return False
    
    def getFirstLine(self):
        if self.ContentStr is not None:
            return self.ContentStr.split('\n')[0]
        else:
            return None
        
    def getPostContent(self):
        postContent = Content()
        firstLine = True
        for line in self.ContentStr.split('\n'):
            if firstLine is False:
                postContent.append(line)
            else:
                firstLine = False
    
        return postContent