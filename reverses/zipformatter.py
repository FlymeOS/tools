#!/usr/bin/python

# Copyright 2015 Coron
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

__author__ = 'duanqz@gmail.com'


import os
import shutil, commands
import tempfile
import re

import deodex, deoat
from common import Log, Options


# Global
TAG="reverse-zipformatter"


class ZipFormatter:
    """ Abstract Model of ZIP Formatter
    """

    def __init__(self, zipModel):
        self.mZipModel = zipModel


    def format(self, zipBack=True):
        self.mZipModel.unzip()

        if not self.mZipModel.isFormatted():
            self.doFormat()

        if zipBack:
            self.mZipModel.zip()


    def doFormat(self):
        Log.e(TAG, "No implementation of ZipFormatter.doFormat() if found.")
        raise Exception("Should be implemented by sub-class!")


    def getFilesRoot(self):
        """ Get the root directory of unziped files
        """

        return self.mZipModel.getRoot();


    @staticmethod
    def genOptions(inZip):
        """ Generate options.
            Only format framework.
        """

        options = Options()
        options.inZip = inZip
        options.outZip = inZip + ".std.zip"
        options.formatFrw = True

        return options


    @staticmethod
    def create(options):
        """ Create a zip formatter for the incoming zip file
        """

        zipModel = ZipModel(options.inZip, options.outZip)
        zipType = zipModel.getZipType()

        Log.i(TAG, "process(): Creating %s ZipFormatter..." %zipType)
        if zipType == ZipModel.ART:
            deoat.OPTIONS = options
            return Deoat(zipModel)

        elif zipType == ZipModel.DVM:
            deodex.OPTIONS = options
            return Deodex(zipModel)

        else:
            raise Exception("Unknown OTA package zip. Is it an ART or DALVIKVM package?")


class Deodex(ZipFormatter):
    """ De-odex formatter
    """

    def __init__(self, zipModel):
        ZipFormatter.__init__(self, zipModel)


    def doFormat(self):
        deodex.OdexZip(self.getFilesRoot()).deodex()


class Deoat(ZipFormatter):
    """ De-oat formatter
    """

    def __init__(self, zipModel):
        ZipFormatter.__init__(self, zipModel)


    def doFormat(self):
        deoat.OatZip(self.getFilesRoot()).deoat().rebuild()



class ZipModel:
    """ Model of an OTA package zip
    """

    ART = "ART"
    DVM = "DVM"

    DAT2IMG = os.path.join(os.path.dirname(__file__), "de-dat", "dedat.sh")

    def __init__(self, inZip, outZip):
        self.mInZip  = inZip
        self.mOutZip = outZip
        self.mRoot   = None


    def unzip(self):
        # Already unziped
        if self.mRoot is not None: return

        self.mRoot = tempfile.mkdtemp()

        Log.i(TAG, "unzip %s to %s" % (self.mInZip, self.mRoot))
        cmd = "unzip -q -o %s -d %s" %(self.mInZip, self.mRoot)
        Log.d(TAG, commands.getoutput(cmd))

        self.dedatIfNeeded()

        # Format path
        if os.path.exists(os.path.join(self.mRoot, "SYSTEM")):
            shutil.move(os.path.join(self.mRoot, "SYSTEM"), os.path.join(self.mRoot, "system"))

        return self


    def zip(self):
        if self.mRoot is None: return

        origDir = os.path.abspath(os.curdir)

        Log.i(TAG, "zip from %s to %s" % (self.mRoot, self.mOutZip))

        os.chdir(self.mRoot)
        cmd = "zip -r -y -q tmp *; mv tmp.zip %s" % self.mOutZip
        Log.d(TAG, commands.getoutput(cmd))
        os.chdir(origDir)

        Log.i(TAG, "Deleting %s" % self.mRoot)
        shutil.rmtree(self.mRoot)

        Log.i(TAG, "===> %s" % self.mOutZip)


    def getRoot(self):
        """ Note: This method is not thread-safe.
        """

        if self.mRoot is None: self.unzip()
        return self.mRoot


    def isFormatted(self):
        return False


    def dedatIfNeeded(self):
        """ Android 5.0 zip structure:
            * META-INF (folder containing scripts)
            * system.new.dat (compressed /system partition)
            * system.patch.dat
            * system.transfer.list (see explanation below)
        """

        if not os.path.exists(os.path.join(self.mRoot, "system.new.dat")):
            return

        if not os.path.exists(os.path.join(self.mRoot, "system.transfer.list")):
            return

        if os.geteuid() != 0:
            raise Exception("DEDAT should be executed as root.")

        cmd = "%s %s" % (commands.mkarg(ZipModel.DAT2IMG), commands.mkarg(self.mRoot))
        Log.d(TAG, commands.getoutput(cmd))


    def getZipType(self):
        """ Retrieve the OTA package type
            The property <persist.sys.dalvik.vm.lib> defines the VM type.
            If libart.so is used, it is an ART package;
            If libdvm.so is used, it is an DVM package.
        """

        if self.mRoot is None: self.unzip()

        buildProp = os.path.join(self.mRoot, "system/build.prop")

        # Retrieve the <persist.sys.dalvik.vm.lib> in build.prop
        zipType = None
        if os.path.exists(buildProp):
            fileHandle = open(buildProp, "r")
            content = fileHandle.read()
            vmlib = re.compile("\n.*sys.dalvik.vm.lib.*=\s*(?P<lib>.*)\n")
            match = vmlib.search(content)
            if match is not None:
                libType = match.group("lib")
                Log.d(TAG, "sys.dalvik.vm.lib=%s" % libType)

            fileHandle.close()
        else:
            raise Exception("Could not find %s, unknown ota type" %buildProp)

        if libType.find("art") >= 0:
            zipType = ZipModel.ART
        elif libType.find("dvm") >= 0:
            zipType = ZipModel.DVM

        return zipType



def debug():
    inZip = "/home/duanqizhi/tmp/n5-dat/n5-dat.zip"
    outZip = "/home/duanqizhi/tmp/n5-dat/n5-dat.std.zip"
    zipModel = ZipModel(inZip, outZip)
    #zipModel.mRoot = "/home/duanqizhi/tmp/n5-dat"
    print "Zip Type: %s" % zipModel.getZipType()

if __name__ == "__main__":

    debug()
