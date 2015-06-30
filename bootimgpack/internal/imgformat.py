'''
Created on Jul 25, 2014

@author: tangliuxiang
'''

import sys

class ImgFormat(object):
    '''
    classdocs
    '''

    IMAGE_HEAD_STR = "ANDROID"

    def __init__(self, bootfile):
        '''
        Constructor
        '''
        self.bootfile = bootfile
        
    def format(self):
        f = open(self.bootfile, "r+")
        hstr = f.read(len(ImgFormat.IMAGE_HEAD_STR))
        
        if hstr == ImgFormat.IMAGE_HEAD_STR:
            return
        
        f.seek(0)
        fstr = f.read()
        
        try:
            idx = fstr.index(ImgFormat.IMAGE_HEAD_STR)
            if idx < 0:
                return
        except:
            #print "Unknown boot image type: " + self.bootfile
            return
        
        f.seek(0)
        f.truncate()
        f.write(fstr[idx:])
        f.close()

if __name__ == '__main__':
    ImgFormat("/home/tangliuxiang/tmp/boot-sign-test/boot.img").format()