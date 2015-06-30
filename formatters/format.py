#!/usr/bin/python

### File Information ###
"""
Format the smali files, include following actions:
    1, remove the lines
    2, turn all resouces id to the name
    3, format all access method
    4, and so on....
    
Usage:  format.py [flags] -l smali_lib_dir [format_dir|format_files]

    -l (--library) <smali_lib_dir>
        make sure there is a decoded framework-res directory in smali_lib_dir

    -r (--rollback)
        rollback the format's before

    -e (--rmline)
        remove the lines

    -i (--idtoname)
        turn resouce id to name

    -a (--accesstoname)
        turn the access method to name
    
    -u (--unifyfield)
        unify the get/put field
    
"""

__author__ = 'duanqz@gmail.com'



import commands
import shutil
import os, sys
import getopt

from name2num import NameToNumForOneFile
from num2name import NumToNameForOneFile

from idtoname import idtoname
from nametoid import nametoid


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smaliparser import utils
from smaliparser import SmaliLib
from smaliparser import Smali


class Format():

    DEBUG = False

    RELATIVE_PUBLIC_XML = "framework-res/res/values/public.xml"
    
    DO = 0x01
    UNDO_DO = 0x02

    NONE           = 0x00000000
    REMOVE_LINE    = 0x00000001
    RESID_TO_NAME  = 0x00000010
    ACCESS_TO_NAME = 0x00000100
    UNIFY_FIELD    = 0x00001000
    XX             = 0x00010000
    XXX            = 0x00100000
    XXXX           = 0x01000000
    XXXXX          = 0x10000000
    
    ALL_ACTION     = REMOVE_LINE | RESID_TO_NAME | ACCESS_TO_NAME | UNIFY_FIELD
    mLibDict = {}
    
    @staticmethod
    def getLib(libPath):
        absPath = os.path.abspath(libPath)
        if not Format.mLibDict.has_key(absPath):
            Format.mLibDict[absPath] = SmaliLib.SmaliLib(libPath, 1)
        return Format.mLibDict[absPath]

    def __init__(self, root, smaliFile):
        self.mRoot = root
        self.mSmaliFile = smaliFile
        
        self.mPublicXML = os.path.join(self.mRoot, Format.RELATIVE_PUBLIC_XML)
        self.mAction = None
        self.mLinePatch = None
        self.mSmaliLib = Format.getLib(self.mRoot)

    def setPublicXML(self, publicXML):
        self.mPublicXML = publicXML
        return self

    def do(self, action = ALL_ACTION):
        self.mAction = action

        Format.log("DO")

        # REMOVE_LINE ->  ACCESS_TO_NAME -> RESID_TO_NAME
        if self.mAction & Format.REMOVE_LINE:
            Format.log("  REMOVE_LINE")
            self.mLinePatch = Format.remLines(self.mSmaliFile)

        if self.mAction & Format.ACCESS_TO_NAME:
            Format.log("  ACCESS_TO_NAME")
            NumToNameForOneFile(self.mSmaliFile)

        if self.mAction & Format.RESID_TO_NAME:
            Format.log("  RESID_TO_NAME")
            if os.path.exists(self.mPublicXML):
                idtoname(self.mPublicXML, self.mSmaliFile).idtoname()
            else:
                Format.log("  No such file or directory: %s" % self.mPublicXML)

        if self.mAction & Format.UNIFY_FIELD:
            Format.log("  UNIFY_FIELD")
            Format.formatUsingField(self.mSmaliLib, self.mSmaliFile)

        return self

    def undo(self, action = None):
        if action is None:
            if self.mAction is not None:
                action = self.mAction
            else:
                action = Format.ALL_ACTION

        Format.log("UNDO")

        # RESID_TO_NAME ->  ACCESS_TO_NAME -> REMOVE_LINE 
        if action & Format.RESID_TO_NAME:
            Format.log("  RESID_TO_NAME")
            if os.path.exists(self.mPublicXML):
                nametoid(self.mPublicXML, self.mSmaliFile).nametoid()
            else:
                Format.log("  No such file or directory: %s" % self.mPublicXML)

        if action & Format.ACCESS_TO_NAME:
            Format.log("  ACCESS_TO_NAME")
            NameToNumForOneFile(self.mSmaliFile)

        if action & Format.REMOVE_LINE:
            Format.log("  REMOVE_LINE")
            Format.addLines(self.mSmaliFile, self.mLinePatch)
            
        if action & Format.UNIFY_FIELD:
            Format.log("  UNIFY_FIELD")
            # Can not undo now.....
            #Format.undoFormatUsingField(self.mSmaliLib, self.mSmaliFile)

        return self
    
    @staticmethod
    # format the replace methods
    def formRepMethod(smaliFile):
        return NumToNameForOneFile(smaliFile)

    @staticmethod
    # format the used fields
    def formatUsingField(sLib, smaliFile):
        cSmali = Smali.Smali(smaliFile)
        sLib.setSmali(cSmali.getClassName(), cSmali)
        sLib.formatUsingField(cSmali)

    @staticmethod
    # undo format the used fields
    def undoFormatUsingField(sLib, smaliFile):
        cSmali = Smali.Smali(smaliFile)
        sLib.setSmali(cSmali.getClassName(), cSmali)
        sLib.undoFormatUsingField(cSmali)

    @staticmethod
    def remLines(origFile):
        """ Remove lines in original file
        """

        noLineFile = origFile + ".noline"

        # Generate no line file
        cmd = "cat %s | sed -e '/^\s*\.line.*$/d' | sed -e 's/\/jumbo//' > %s" % \
                (commands.mkarg(origFile), commands.mkarg(noLineFile))
        commands.getstatusoutput(cmd)

        if not os.path.exists(noLineFile):
            return None

        # Generate line patch
        linesPatch = origFile + ".linepatch"
        cmd = "diff -B -u %s %s > %s" % \
                (commands.mkarg(noLineFile), commands.mkarg(origFile), commands.mkarg(linesPatch))
        commands.getstatusoutput(cmd)

        shutil.move(noLineFile, origFile)

        return linesPatch

    @staticmethod
    def addLines(smaliFile, linesPatch = None):
        """ Add the lines back to no line file
        """
        if linesPatch is None:
            linesPatch = '%s.linepatch' %(smaliFile)
        
        if not os.path.isfile(linesPatch):
            return

        # Patch the lines to no line file
        cmd = "patch -f %s -r /dev/null < %s > /dev/null" % \
                (commands.mkarg(smaliFile), commands.mkarg(linesPatch))
        commands.getstatusoutput(cmd)

        os.remove(linesPatch)
        origFile = smaliFile + ".orig"
        if os.path.exists(origFile): os.remove(origFile)

        return smaliFile

    @staticmethod
    def log(message):
        if Format.DEBUG: print message

    @staticmethod
    def __doJob__(f, job, action):
        if job == Format.DO:
            f.do(action)
        elif job == Format.UNDO_DO:
            f.undo()
        else:
            Format.log("Error Action %s" % action)

    @staticmethod
    def format(job, libPath, smaliFileList = None, action = ALL_ACTION):
        if smaliFileList is None:
            smaliFileList = utils.getSmaliPathList(libPath)

        idx = 0
        while idx < len(smaliFileList):
            if os.path.isdir(smaliFileList[idx]):
                Format.format(job, libPath, utils.getSmaliPathList(libPath), action)
                continue
            
            f = Format(libPath, smaliFileList[idx])
            Format.__doJob__(f, job, action)
            idx = idx + 1

def usage():
    print __doc__

class Options(object): pass
OPTIONS = Options()
OPTIONS.Job = Format.DO
OPTIONS.Action = Format.NONE
OPTIONS.LibPath = None
DEFAULT_ACTION = Format.ALL_ACTION

def main(argv):
    options,args = getopt.getopt(argv[1:], "hrl:eiau", [ "help", "rollback", "library", "rmline", "idtoname", "accesstoname", "unifyfield"])
    for name,value in options:
        if name in ("-h", "--help"):
            usage()
        elif name in ("-r", "--rollback"):
            OPTIONS.Job = Format.UNDO_DO
        elif name in ("-l", "--library"):
            OPTIONS.LibPath = value
        elif name in ("-e", "--rmline"):
            OPTIONS.Action = OPTIONS.Action | Format.REMOVE_LINE
        elif name in ("-i", "--idtoname"):
            OPTIONS.Action = OPTIONS.Action | Format.RESID_TO_NAME
        elif name in ("-a", "--accesstoname"):
            OPTIONS.Action = OPTIONS.Action | Format.ACCESS_TO_NAME
        elif name in ("-u", "--unifyfield"):
            OPTIONS.Action = OPTIONS.Action | Format.UNIFY_FIELD
        else:
            Format.log("Wrong parameters, see the usage....")
            usage()
            exit(1)
    if OPTIONS.Action == Format.NONE:
        OPTIONS.Action = DEFAULT_ACTION

    if OPTIONS.LibPath is None:
        if len(args) > 0:
            OPTIONS.LibPath = args[0]
            args = args[1:]
        else:
            usage()
            exit(1)
    if args is not None and len(args) <= 0:
        args = None

    Format.format(OPTIONS.Job, OPTIONS.LibPath, args, OPTIONS.Action)
    
def test():
    root = "/media/source/smali/smali-4.2/devices/demo/autopatch/vendor"
    smaliFile = "/media/source/smali/smali-4.2/devices/demo/framework.jar.out/smali/android/widget/TextView.smali"
    publicXML = "/media/source/smali/smali-4.2/devices/demo/framework-res/res/values/public.xml"

    action = Format.REMOVE_LINE | Format.ACCESS_TO_NAME | Format.RESID_TO_NAME | Format.UNIFY_FIELD
    Format(root, smaliFile).setPublicXML(publicXML).do(action).undo()

if __name__ == "__main__":
    main(sys.argv)
