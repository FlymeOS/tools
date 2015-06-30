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

"""
Convert the OAT format on ART to DEX format on DALVIKVM.
 Usage: deoat.py [OPTIONS] <otapackage.zip> [<otapackage.deoat.zip>]
        OPTIONS:
        --app, -a:         only de-oat the apk in system.
        --framework, -f:   only de-oat the jar in system.
"""


__author__ = 'duanqz@gmail.com'

import os
import commands
import re
import shutil

from common import Utils, Log

# Global
TAG="reverse-deoat"
OPTIONS = None

class OatZip:
    """ Model of OAT ZIP file
    """

    OAT2DEX = os.path.join(os.path.dirname(__file__), "de-oat", "oat2dex.sh")

    def __init__(self, unzipRoot):
        self.mRoot = unzipRoot

        self.mFrwDir = os.path.join(self.mRoot, "system/framework")
        self.mAppDir = os.path.join(self.mRoot, "system/app")
        self.mPrivAppDir = os.path.join(self.mRoot, "system/priv-app")

        # boot.oat
        self.mBootOAT = self.findBootOAT()
        if self.mBootOAT != None:
            self.mBootOATDir = os.path.dirname(self.mBootOAT)
            self.mBootClassFolder = os.path.join(self.mBootOATDir, "dex")


    def findBootOAT(self):
        """ Find the absolute path of boot.oat
            In Android 5.0+, all the jars of BOOTCLASSPATH are packaged into boot.oat
        """

        bootOATPath = os.path.join(self.mFrwDir, "arm/boot.oat")
        if os.path.exists(bootOATPath):
            return bootOATPath

        bootOATPath = os.path.join(self.mFrwDir, "x86/boot.oat")
        if os.path.exists(bootOATPath):
            return bootOATPath

        bootOATPath = None
        cmd = "find %s -name boot.oat" % (commands.mkarg(self.mFrwDir))
        (sts, text) = commands.getstatusoutput(cmd)
        try:
            if sts == 0:
                text = text.split("\n")[0]
                if len(text) > 0:
                    return text
        except:
            bootOATPath = None

        return bootOATPath


    def deoat(self):
        """ De-oat the OTA package.
        """

        if self.mBootOAT == None:
            Log.i(TAG, "deoat(): boot.oat not found in %s, nothing need deoat" % self.mRoot)
            return self

        if os.path.exists(self.mBootClassFolder):
            Log.d(TAG, "Delete the already exists %s" %self.mBootClassFolder)
            shutil.rmtree(self.mBootClassFolder)

        # Phase 1: de-oat boot.oat
        OatZip.deoatBootOAT(self.mBootOAT)

        # Phase 2: de-oat all the other oat files, of which suffix is odex.
        # [Android 5.0]: All the oat jars are located in the same folder with boot.oat
        OatZip.deoatFrw(self.mBootOATDir)

        # Phase 3: de-oat app
        OatZip.deoatApp(self.mFrwDir, self.mBootClassFolder)
        OatZip.deoatApp(self.mAppDir, self.mBootClassFolder)
        OatZip.deoatApp(self.mPrivAppDir, self.mBootClassFolder)

        return self


    def rebuild(self):
        """ Rebuild the deoated zip
        """

        if self.mBootOAT == None:
            Log.i(TAG, "rebuild(): boot.oat not found, nothing need rebuild")
            return

        OatZip.repackageFrw(self.mFrwDir, self.mBootClassFolder)
        OatZip.repackageApp(self.mFrwDir)
        OatZip.repackageApp(self.mAppDir)
        OatZip.repackageApp(self.mPrivAppDir)

        # Remove the whole OAT directory
        if os.path.exists(self.mBootOATDir):
            shutil.rmtree(self.mBootOATDir)

    @staticmethod
    def deoatBootOAT(bootOAT):
        """ De-oat boot.oat
        """

        Log.i(TAG, "De-oat %s" % bootOAT)
        Utils.runWithOutput([OatZip.OAT2DEX, "boot", bootOAT])


    @staticmethod
    def deoatFrw(oatJarDir):
        """ De-oat framework
        """

        if not OPTIONS.formatFrw: return

        Log.i(TAG, "De-oat files of oat-format in %s" % oatJarDir)
        for item in os.listdir(oatJarDir):
            if item.endswith(".odex"):
                # COMMANDS: oat2dex boot <jar-of-oat-format>
                oatJar = os.path.join(oatJarDir, item)
                Utils.runWithOutput([OatZip.OAT2DEX, "boot", oatJar])


    @staticmethod
    def deoatApp(oatApkDir, bootClassFolder):
        """ De-oat app
        """

        if OPTIONS.formatApp == False: return

        Log.i(TAG, "De-oat files of oat-format in %s, with BOOTCLASSFOLDER=%s" %(oatApkDir, bootClassFolder))
        for (dirpath, dirnames, filenames) in os.walk(oatApkDir):

            dirnames = dirnames # no use, to avoid warning

            for filename in filenames:
                if filename.endswith(".odex"):
                    # no need to de-oat if original apk does not exist
                    apkFile = filename[0:-5] + ".apk"
                    apkPath = os.path.dirname(dirpath)
                    if not os.path.exists(os.path.join(apkPath, apkFile)):
                        continue

                    oatApk = os.path.join(dirpath, filename)
                    deoatApk = oatApk[0:-5] + ".dex"
                    if os.path.exists(deoatApk):
                        Log.d(TAG, "Delete the already exists %s" % deoatApk)
                        os.remove(deoatApk)

                    Utils.runWithOutput([OatZip.OAT2DEX, oatApk, bootClassFolder])


    @staticmethod
    def repackageFrw(frwDir, bootClassFolder):
        """ Repackage the classes.dex into jar of frwDir.
        """

        if OPTIONS.formatFrw == False : return

        # Keep the old directory, we will change back after some operations.
        oldDir = os.path.abspath(os.curdir)

        # Some dexFiles are parted, such as framework-classes2.dex
        regex = re.compile("(.*)-(classes\d?).dex")

        Log.i(TAG, "Repackage JARs of %s" %(frwDir))
        os.chdir(frwDir)
        for dexFile in os.listdir(bootClassFolder):
            if dexFile.endswith(".dex"):
                jarFile = dexFile[0:-4] + ".jar"
                dexName = "classes.dex"

                if not os.path.exists(jarFile):
                    # Match out the jar file with regex
                    matcher = regex.match(dexFile)
                    if matcher != None:
                        jarFile = matcher.group(1) + ".jar"
                        dexName = matcher.group(2) + ".dex"
 
                Log.d(TAG, "Repackage %s" %(jarFile))
                # Put the dex and framework's jar in the same folder, and jar into the jarFile
                shutil.move(os.path.join(bootClassFolder, dexFile), os.path.join(frwDir, dexName))
                Utils.runWithOutput(["jar", "uf", jarFile, dexName])

                if os.path.exists(dexName):
                    os.remove(dexName)

        os.chdir(oldDir)


    @staticmethod
    def repackageApp(appDir):
        """ Repackage the classes.dex into apk of appDir
        """

        if OPTIONS.formatApp == False: return

        # Keep the old directory, we will change back after some operations.
        oldDir = os.path.abspath(os.curdir)

        Log.i(TAG, "Repackage APKs of %s" %(appDir))
        for (dirpath, dirnames, filenames) in os.walk(appDir):

            dirnames = dirnames # no use, to avoid warning

            for dexFile in filenames:
                if dexFile.endswith(".dex"):
                    apkFile = dexFile[0:-4] + ".apk"
                    apkPath  = os.path.dirname(dirpath)

                    if not os.path.exists(os.path.join(apkPath, apkFile)):
                        Log.d(TAG, "No apk matched with %s, Ignore" %dexFile)
                        continue

                    dexName = "classes.dex"

                    Log.d(TAG, "Repackage %s" %(apkPath))
                    # Put the dex and apk in the same folder, and jar into the apk
                    shutil.move(os.path.join(dirpath, dexFile), os.path.join(apkPath, dexName))

                    os.chdir(apkPath)
                    Utils.runWithOutput(["jar", "uf", apkFile, dexName])
                    if os.path.exists(dexName):
                        os.remove(dexName)

                    shutil.rmtree(dirpath)


        os.chdir(oldDir)



def debug():

    Log.DEBUG = True
    root = "root directory the unziped files"
    #root = "/w/code/smali-5.0/devices/sony/out/tmp"

    OatZip(root).deoat()

if __name__ == "__main__":

    debug()
