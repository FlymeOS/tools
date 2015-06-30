'''
Created on Jun 3, 2014

@author: tangliuxiang
'''

import SCheck
import SmaliEntry
import SmaliFileReplace
import os
import utils
import Replace

def usage():
    print ""
    
def tobosp(args):
    if len(args) <= 0:
        usage()
    elif len(args) == 2:
        Replace.replace(utils.getMatchFile(args[0], utils.BOSP), args[0], SmaliEntry.METHOD, SmaliEntry, args[1])
    else:
        for smaliFile in args:
            SmaliFileReplace.replace(utils.getMatchFile(smaliFile, utils.BOSP), smaliFile)
