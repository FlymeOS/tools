'''
Created on Aug 1, 2014

@author: tangliuxiang
'''

class andprop(object):
    def __init__(self, prop):
        self.mProp = prop
        self.mParsed = False
        self.mPropDict = {}
        self.__parsed__()
    
    def __parsed__(self):
        if self.mParsed is False:
            propfile = file(self.mProp)
            for line in propfile.readlines():
                stripline = line.strip()
                if len(stripline) > 0 and stripline[0] != "#":
                    try:
                        idx = stripline.index('=')
                        self.mPropDict[stripline[:idx].strip()] = stripline[idx + 1:].strip()
                    except:
                        raise "Wrong properties: %s" % (stripline)
            
            self.mParsed = True
            
    def get(self, key, defValue = None):
        if self.mPropDict.has_key(key):
            return self.mPropDict[key]
        else:
            return defValue
        
    def set(self, key, value):
        self.mPropDict[key] = value
        
    def out(self, outPath=None):
        if outPath == None:
            outPath = self.mProp
        
        outFile = file(outPath, "w+")
        for key in self.mPropDict.keys():
            outFile.write("%s=%s" % (key, self.mPropDict[key]))
        outFile.close()
