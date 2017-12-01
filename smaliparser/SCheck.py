'''
Created on Mar 12, 2014

@author: tangliuxiang

'''
import SmaliEntry
import Smali
import string
import SmaliMethod
import sys
import os
import getopt
import SAutoCom
import SmaliFileReplace
import tobosp
import utils
import Replace
import LibUtils
import traceback


class Options(object): pass
OPTIONS = Options()
OPTIONS.autoComplete = False

OPTIONS.replaceWithCheck = False
OPTIONS.methodToBosp = False
OPTIONS.smaliToBosp = False

def formatSmali(smaliLib, smaliFileList = None):
    utils.SLog.i("    begin format smali files, please wait....")
    if smaliFileList is not None:
        idx = 0
        while idx < len(smaliFileList):
            clsName = utils.getClassFromPath(smaliFileList[idx])
            cSmali = smaliLib.getSmali(clsName)
            smaliLib.formatUsingField(cSmali)
            idx = idx + 1
    else:
        for clsName in smaliLib.mSDict.keys():
            cSmali = smaliLib.getSmali(clsName)
            smaliLib.formatUsingField(cSmali)
    utils.SLog.i("    format done")

def usage():
    print __doc__

def main(argv):
    options,args = getopt.getopt(argv[1:], "hams", [ "help", "autocomplete", "methodtobosp", "smalitobosp"])
    for name,value in options:
        if name in ("-h", "--help"):
            usage()
        elif name in ("-a", "--autocomplete"):
            OPTIONS.autoComplete = True
        elif name in ("-m", "--methodtobosp"):
            OPTIONS.replaceWithCheck = False
            OPTIONS.methodToBosp = True
        elif name in ("-s", "--smalitobosp"):
            OPTIONS.smaliToBosp = True
        else:
            utils.SLog.w("Wrong parameters, see the usage....")
            usage()

    if OPTIONS.autoComplete:
        if len(args) >= 6:
            try:
                SAutoCom.SAutoCom.autocom(args[0], args[1], args[2], args[3], args[4], args[5:])
            except:
                traceback.print_exc()
                # see error info in help.xml for ERR_AUTOCOM_FAILED
                sys.exit(158)
        else:
            # see error info in help.xml for ERR_WRONG_PARAMETERS
            sys.exit(157)
    elif OPTIONS.methodToBosp:
        if len(args) >= 2:
            try:
                Replace.methodtobosp(args[0], args[1], OPTIONS.replaceWithCheck)
            except:
                traceback.print_exc()
                # see error info in help.xml for ERR_METHODTOBOSP_FAILED
                sys.exit(159)
        else:
            # see error info in help.xml for ERR_WRONG_PARAMETERS
            sys.exit(157)
    elif OPTIONS.smaliToBosp:
        if len(args) >= 1:
            try:
                SmaliFileReplace.smalitobosp(args, False)
            except:
                traceback.print_exc()
                # see error info in help.xml for ERR_SMALITOBOSP_FAILED
                sys.exit(160)
        else:
            # see error info in help.xml for ERR_WRONG_PARAMETERS
            sys.exit(157)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        main(sys.argv)
    else:
        usage()
