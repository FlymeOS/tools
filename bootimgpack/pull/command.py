'''
Created on Jul 31, 2014

@author: tangliuxiang
'''

import subprocess
import tempfile
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from formatters.log import Log

DEBUG = False
DD_BLOCK_SIZE = 512

class Shell(object):
    
    """ Subprocess to run shell command
    """
    
    def run(self, cmd, out=None, printout=DEBUG):
        """ Run command in shell.
        """
        if printout is False:
            cmd = "%s 2>&1 > /dev/null" % cmd
        
        subp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        while True:
            buff = subp.stdout.readline().strip('\n')
            if printout:
                print buff
            if out is not None:
                out.write(buff)
            if buff == '' and subp.poll() != None:
                break
        
        if subp.returncode > 0:
            return False

        return True

class AdbShell(Shell):
    """ Subprocess to run shell command
    """
    ANDROID_TMP = "/data/local/tmp"
    TAG = "adb"
    def run(self, cmd, out=None, printout=DEBUG):
        """ Run command in shell.
        """
        outTmp = None
        if out is not None:
            outTmp = tempfile.mktemp(dir=AdbShell.ANDROID_TMP)
            cmd = 'echo \'%s > %s && chmod 777 %s; exit $?\'| adb shell' % (cmd, outTmp, outTmp)
        else:
            cmd = 'echo \'%s; exit $?\' | adb shell' % cmd
        ret = self.__superrun__(cmd, None, printout)
        
        if outTmp is not None and out is not None:
            self.pull(outTmp, out, False)
            self.__superrun__("rm -r %s" % outTmp, None, False)
        
        return ret
    
    def __superrun__(self, cmd, out=None, printout=DEBUG):
        self.waitdevices()
        return super(AdbShell, self).run(cmd, out, printout)
    
    def push(self, inFile, outFile, printout=DEBUG):
        cmd = "adb push %s %s" % (inFile, outFile)
        return self.__superrun__(cmd)
    
    def pull(self, inFile, outFile, printout=DEBUG):
        cmd = "adb pull %s %s" % (inFile, outFile)
        return self.__superrun__(cmd)
    
    def waitdevices(self, printout=DEBUG):
        if printout:
            Log.i(AdbShell.TAG, "waiting for devices....")
        return super(AdbShell, self).run("adb wait-for-device", None, printout)

class SuShell(AdbShell):
    '''
    classdocs
    '''
    
    def run(self, cmd, out=None, printout=DEBUG):
        """ Run command in shell.
        """
        cmd = "su -c \"%s\"" % (cmd)
        return super(SuShell, self).run(cmd, out, printout)

class ShellFactory(object):
    mShell = None

    @staticmethod
    def __getRootShell__():
        subp = subprocess.Popen(["check-su"], stdout=subprocess.PIPE)
        subp.communicate()
        if subp.returncode == 0:
            Log.i("AdbShell", "use su to root")
            return SuShell()
        else:
            Log.i("AdbShell", "Can not use su to root, assume your phone has already been root with modify default.prop in boot!")
            Log.i("AdbShell", "Try adb root, it may be blocked!")
            subp = subprocess.Popen(["adb", "root"], stdout=subprocess.PIPE)
            subp.communicate()
            Log.i("AdbShell", "Root successfull")
            return AdbShell()

    @staticmethod
    def getDefaultShell():
        if ShellFactory.mShell is None:
            ShellFactory.mShell = ShellFactory.__getRootShell__()
        return ShellFactory.mShell

class AndroidFile():
    
    def __init__(self, path, shell=None):
        self.mPath = path
        if shell is None:
            self.mShell = ShellFactory.getDefaultShell()
        else:
            self.mShell = shell
        
    def getPath(self):
        return self.mPath
        
    def read(self, start=0, size= -DD_BLOCK_SIZE):
        outStr = None
        
        skip = start / DD_BLOCK_SIZE
        count = size / DD_BLOCK_SIZE + 1
        
        phoneTmp = self.__readToPhoneTmp__(skip, count)
        if phoneTmp is not None:
            pcTmp = self.__pullToPc__(phoneTmp)
            
            if pcTmp is not None and os.path.isfile(pcTmp):
                pcTmpFile = file(pcTmp)
                
                if size > 0:
                    pcStart = start % DD_BLOCK_SIZE
                    pcEnd = (size % DD_BLOCK_SIZE - DD_BLOCK_SIZE) % DD_BLOCK_SIZE
                    
                    pcTmpFile.seek(pcStart)
                    outStr = file(pcTmp).read()[:pcEnd]
                    
                else:
                    outStr = file(pcTmp).read()
                
                os.remove(pcTmp)
            AndroidFile(phoneTmp).remove()
        
        return outStr
    
    def pull(self, dst, start=0, size= -DD_BLOCK_SIZE):
        skip = start / DD_BLOCK_SIZE
        count = size / DD_BLOCK_SIZE + 1
        
        phoneTmp = self.__readToPhoneTmp__(skip, count)
        if phoneTmp is not None:
            self.__pullToPc__(phoneTmp, dst)
            
            AndroidFile(phoneTmp).remove()
            if os.path.isfile(dst):
                return True
        
        return False
    
    def remove(self):
        return self.mShell.run("rm -r %s" % (self.mPath))

    def append(self, fstr):
        return self.__writeinternal__(fstr, True)
    
    def write(self, fstr):
        return self.__writeinternal__(fstr, False)
    
    def dd_write(self, pcFile, start=0, size= -DD_BLOCK_SIZE):
        if size > os.path.getsize(pcFile):
            size = -DD_BLOCK_SIZE

        skip = start / DD_BLOCK_SIZE
        count = size / DD_BLOCK_SIZE + 1
        inFile = self.__pushToPhoneTmp__(pcFile)

        if count <= 0:
            cmd = "dd if=%s of=%s seek=%s; chmod 777 %s" % (inFile, self.mPath, skip, self.mPath)
        else:
            cmd = "dd if=%s of=%s seek=%s count=%s; chmod 777 %s" % (inFile, self.mPath, skip, count, self.mPath)
        
        print cmd
        return self.mShell.run(cmd)

    def __writeToPcTmp__(self, fstr):
        inFilePath = tempfile.mktemp()
        inFile = file(inFilePath, "w+")
        inFile.write(fstr)
        inFile.close()
        
        return inFilePath
    
    def exist(self):
        outTmp = tempfile.mktemp()
        ret = False
        if self.mShell.run(r'if [ -e %s ]; then echo True; else echo False; fi' % (self.mPath), outTmp):
            if os.path.isfile(outTmp) and file(outTmp).read().strip("\n") == "True":
                ret = True
        os.remove(outTmp)
        return True
    
    def __readToPhoneTmp__(self, skip, count):
        outFile = tempfile.mktemp(dir=AdbShell.ANDROID_TMP)
        if count <= 0:
            cmd = "dd if=%s of=%s skip=%s; chmod 777 %s" % (self.mPath, outFile, skip, outFile)
        else:
            cmd = "dd if=%s of=%s skip=%s count=%s; chmod 777 %s" % (self.mPath, outFile, skip, count, outFile)
        
        if self.mShell.run(cmd):
            return outFile
        else:
            return None
    
    def __pullToPc__(self, phoneTmp, pcOut=None):
        if pcOut is None:
            pcOut = tempfile.mktemp()
        self.mShell.pull(phoneTmp, pcOut)
        
        return pcOut
    
    def __pushToPhoneTmp__(self, inFilePath):
        outFile = tempfile.mktemp(dir=AdbShell.ANDROID_TMP)
        if self.mShell.push(inFilePath, outFile):
            return outFile
        else:
            return None
    
    def __writeinternal__(self, fstr, append=True):
        inFilePath = self.__writeToPcTmp__(fstr)
        outFile = self.__pushToPhoneTmp__(inFilePath)
        
        if append:
            ret = self.mShell.run("cat %s >> %s" % (outFile, self.mPath), str)
        else:
            ret = self.mShell.run("cat %s > %s" % (outFile, self.mPath), str)
        
        AndroidFile(outFile).remove()
        os.remove(inFilePath)
        return ret
        
