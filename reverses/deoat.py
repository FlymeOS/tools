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

# Refer to the SuperR's Kitchen for the deodex Lollipop ROMs

__author__ = 'duanqz@gmail.com'

import os
import commands
import re
import shutil
import threading

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

        self.mFrwDir     = os.path.join(self.mRoot, "system/framework")
        self.mAppDir     = os.path.join(self.mRoot, "system/app")
        self.mPrivAppDir = os.path.join(self.mRoot, "system/priv-app")
        self.mAllAppDirList = [self.mFrwDir, self.mAppDir, self.mPrivAppDir]
        self.mSystemDir = os.path.join(self.mRoot, "system")

        self.findArch()

        self.mBootOAT = os.path.join(self.mFrwDir, self.arch, "boot.oat")
        if os.path.exists(self.mBootOAT):
            Log.i(TAG, "mBootOAT : " + self.mBootOAT)
        else:
            self.mBootOAT = None
            Log.i(TAG, "boot.oat not found!")

    @staticmethod
    def testArch(frwDir, arch):
        """ Test whether arch exists
        """
        bootOATPath = os.path.join(frwDir, arch, "boot.oat")
        Log.i(TAG, "testArch : "  + bootOATPath)
        if os.path.exists(bootOATPath):
            return True
        return False


    def findArch(self):
        """ Find arch and arch2
        """
        self.arch  = ""
        self.arch2 = ""

        if OatZip.testArch(self.mFrwDir, "arm64"):
            self.arch = "arm64"
            if OatZip.testArch(self.mFrwDir, "arm"):
                self.arch2 = "arm"
        elif OatZip.testArch(self.mFrwDir, "x86_64"):
            self.arch = "x86_64"
            if OatZip.testArch(self.mFrwDir, "x86"):
                self.arch2="x86"
        elif OatZip.testArch(self.mFrwDir, "arm"):
            self.arch = "arm"
        elif OatZip.testArch(self.mFrwDir, "x86"):
            self.arch = "x86"
        else:
            Log.d(TAG, "unknow arch")


    def findBootOAT(self):
        """ Find the absolute path of boot.oat
            In Android 5.0+, all the jars of BOOTCLASSPATH are packaged into boot.oat
        """
        bootOATPath = os.path.join(self.mFrwDir, "arm64/boot.oat")
        if os.path.exists(bootOATPath):
            return bootOATPath

        bootOATPath = os.path.join(self.mFrwDir, "arm/boot.oat")
        if os.path.exists(bootOATPath):
            return bootOATPath

        bootOATPath = os.path.join(self.mFrwDir, "x86_64/boot.oat")
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

        # Phase 1: de-oat boot.oat
        OatZip.deoatBootOAT(os.path.join(self.mFrwDir, self.arch, "boot.oat"))
        if self.arch2.strip():
            OatZip.deoatBootOAT(os.path.join(self.mFrwDir, self.arch2, "boot.oat"))

        # Phase 2: de-oat all the other oat files, of which suffix is odex.
        # [Android 5.0]: All the oat jars are located in the same folder with boot.oat

        # Phase 3: de-oat app
        # de-oat app
        threadApp = threading.Thread(target = OatZip.deoatAppWithArch, args = (self.mAppDir, self.mFrwDir, self.arch, self.arch2))
        threadApp.start()

        threadPrivApp = threading.Thread(target = OatZip.deoatAppWithArch, args = (self.mPrivAppDir, self.mFrwDir, self.arch, self.arch2))
        threadPrivApp.start()

        threadApp.join()
        threadPrivApp.join()

        # Phase 4: de-oat framework
        # de-oat framework
        OatZip.deoatFrwWithArch(self.mFrwDir, self.arch)

        # de-oat framework/oat/$arch
        OatZip.deoatFrwOatWithArch(self.mFrwDir, self.arch)

        return self


    def rebuild(self):
        """ Rebuild the deoated zip
        """

        if self.mBootOAT == None:
            Log.i(TAG, "rebuild(): boot.oat not found, nothing need rebuild")
            return

        # repackage app
        OatZip.repackageAppWithArch(self.mAppDir, self.arch)
        if self.arch2.strip():
            OatZip.repackageAppWithArch(self.mAppDir, self.arch2)

        OatZip.repackageAppWithArch(self.mPrivAppDir, self.arch)
        if self.arch2.strip():
            OatZip.repackageAppWithArch(self.mPrivAppDir, self.arch2)

        # repackage framework
        #$framedir/$arch
        OatZip.repackageFrwWithArch(self.mFrwDir, os.path.join(self.mFrwDir, self.arch))

        #$framedir/$arch/dex
        if os.path.exists(os.path.join(self.mFrwDir, self.arch, "dex")):
            OatZip.repackageFrwWithArch(self.mFrwDir, os.path.join(self.mFrwDir, self.arch, "dex"))

        #$framedir/oat/$arch
        if os.path.exists(os.path.join(self.mFrwDir, "oat", self.arch)):
            OatZip.repackageFrwWithArch(self.mFrwDir, os.path.join(self.mFrwDir, "oat", self.arch))

        # deal with additional apks not in system/framework system/app system/priv-app
        OatZip.dealWithAdditionalApks(self.mSystemDir, self.mFrwDir, self.arch, self.arch2, self.mAllAppDirList)

        # Remove arch and arch2 dir
        os.chdir(self.mRoot)
        shutil.rmtree(os.path.join(self.mFrwDir, self.arch))
        if self.arch2.strip():
            shutil.rmtree(os.path.join(self.mFrwDir, self.arch2))
        if os.path.exists(os.path.join(self.mFrwDir, "oat")) :
            shutil.rmtree(os.path.join(self.mFrwDir, "oat"))


    @staticmethod
    def deoatBootOAT(bootOAT):
        """ De-oat boot.oat
        """
        bootClassFolder = os.path.dirname(bootOAT)
        bootClassFolderDex = os.path.join(bootClassFolder, "dex")
        bootClassFolderOdex = os.path.join(bootClassFolder, "odex")

        if os.path.exists(bootClassFolderDex):
            Log.d(TAG, "Delete the already exists %s" %bootClassFolderDex)
            shutil.rmtree(bootClassFolderDex)
        if os.path.exists(bootClassFolderOdex):
            Log.d(TAG, "Delete the already exists %s" %bootClassFolderOdex)
            shutil.rmtree(bootClassFolderOdex)

        Log.i(TAG, "De-oat %s" % bootOAT)
        Utils.runWithOutput([OatZip.OAT2DEX, "boot", bootOAT])

    @staticmethod
    def packageDexToAppWithArch(apkFile, arch):

        # Keep the old directory, we will change back after some operations.
        oldDir = os.path.abspath(os.curdir)

        apkPath = os.path.dirname(apkFile)
        appName = os.path.basename(apkFile)
        app = appName[0:-4]

        archPath = os.path.join(apkPath, "oat", arch)

        # chagnge to arch path
        os.chdir(archPath)

        Log.d(TAG, "Repackage %s" %(apkFile))

        dexFile = os.path.join(archPath, app + ".dex")

        # mv $appdir/$app/$arch/$app.dex $appdir/$app/$arch/classes.dex
        if os.path.exists(dexFile):
            shutil.move(dexFile, os.path.join(archPath, "classes.dex"))
            Utils.runWithOutput(["jar", "uf", apkFile, "classes.dex"])
        else:
            Log.d(TAG, "Repackage ERROR %s" %(apkFile))

        dexFile = os.path.join(archPath, app + "-classes2.dex")
        # if [[ -f "$appdir/$app/$arch/$app-classes2.dex" ]]; then
        #   mv $appdir/$app/$arch/$app-classes2.dex $appdir/$app/$arch/classes2.dex
        if os.path.exists(dexFile):
            shutil.move(dexFile, os.path.join(archPath, "classes2.dex"))
            Utils.runWithOutput(["jar", "uf", apkFile, "classes2.dex"])

        dexFile = os.path.join(archPath, app + "-classes3.dex")
        # if [[ -f "$appdir/$app/$arch/$app-classes3.dex" ]]; then
        #   mv $appdir/$app/$arch/$app-classes3.dex $appdir/$app/$arch/classes3.dex
        if os.path.exists(dexFile):
            shutil.move(dexFile, os.path.join(archPath, "classes3.dex"))
            Utils.runWithOutput(["jar", "uf", apkFile, "classes3.dex"])

        os.chdir(oldDir)

    @staticmethod
    def deoatFrwWithArch(frwDir, arch):
        """ De-oat framework
        """

        if not OPTIONS.formatFrw: return

        Log.i(TAG, "De-oat files of oat-format in %s" % frwDir)
        archDir = os.path.join(frwDir, arch)
        odexDir = os.path.join(archDir, "odex")
        for item in os.listdir(archDir):
            if item.endswith(".odex"):
                jarFile = os.path.join(frwDir, item[0:-5] + ".jar")
                if not OatZip.isDeodexed(jarFile):
                    odexFile = os.path.join(archDir, item)
                    Utils.runWithOutput([OatZip.OAT2DEX, odexFile, odexDir])

    @staticmethod
    def deoatFrwOatWithArch(frwDir, arch):
        """ De-oat framework oat
        """

        if not OPTIONS.formatFrw: return

        Log.i(TAG, "De-oat files of oat-format in %s/oat" % frwDir)
        archDir = os.path.join(frwDir, arch)
        odexDir = os.path.join(archDir, "odex")
        oatDir = os.path.join(frwDir, "oat", arch)

        if not os.path.exists(oatDir): return

        for item in os.listdir(oatDir):
            if item.endswith(".odex"):
                jarFile = os.path.join(frwDir, item[0:-5] + ".jar")
                if not OatZip.isDeodexed(jarFile):
                    odexFile = os.path.join(oatDir, item)
                    Utils.runWithOutput([OatZip.OAT2DEX, odexFile, odexDir])

    @staticmethod
    def isDeodexed(apkFile):
        """ Wheather apk/jar is deodexed
        """
        cmd = "jar tf " + apkFile + "| grep classes.dex"
        (sts, text) = commands.getstatusoutput(cmd)
        if sts == 0 and text.find('classes.dex') != -1:
            return True
        return False


    @staticmethod
    def deoatAppWithArch(appsDir, frwDir, arch, arch2):
        """ De-oat app
        """

        if OPTIONS.formatApp == False: return

        Log.i(TAG, "De-oat files of oat-format in %s" %(appsDir))

        bootClassFolderArch = os.path.join(frwDir, arch, "odex")
        bootClassFolderArch2 = os.path.join(frwDir, arch2, "odex")

        #for app in $( ls $appdir ); do
        for app in os.listdir(appsDir):
            appPath = os.path.join(appsDir, app)
            apkFile = os.path.join(appPath, app + ".apk")

            archPath = os.path.join(appPath, "oat", arch)
            #if [[ -d "$appdir/$app/$arch" ]];
            if os.path.exists(archPath):
                odexFile = os.path.join(archPath, app + ".odex")

                #java -Xmx512m -jar $oat2dex $appdir/$app/$arch/$app.odex $framedir/$arch/odex
                Utils.runWithOutput([OatZip.OAT2DEX, odexFile, bootClassFolderArch])
            else:
                # if exists arch2
                if arch2.strip():
                    arch2Path = os.path.join(appPath, "oat", arch2)
                    if os.path.exists(arch2Path):
                        odexFile2 = os.path.join(arch2Path, app + ".odex")
                        Utils.runWithOutput([OatZip.OAT2DEX, odexFile2, bootClassFolderArch2])


    @staticmethod
    def repackageFrwWithArch(frwDir, dexFolder):
        """ Repackage the classes.dex into jar of frwDir.
        """

        if OPTIONS.formatFrw == False : return

        # Keep the old directory, we will change back after some operations.
        oldDir = os.path.abspath(os.curdir)

        Log.i(TAG, "Repackage JARs of %s - %s" %(frwDir,dexFolder))

        os.chdir(dexFolder)
        for dexFile in os.listdir(dexFolder):
            if dexFile.endswith(".dex") and dexFile.find("classes") == -1:
                appName = dexFile[0:-4]
                jarFile = os.path.join(frwDir, appName + ".apk")
                if not os.path.exists(jarFile):
                    jarFile = jarFile[0:-4] + ".jar"

                if not os.path.exists(jarFile):
                    dexName = "classes.dex"
                    shutil.move(os.path.join(dexFolder, dexFile), os.path.join(dexFolder, dexName))
                    Utils.runWithOutput(["jar", "cf", jarFile, dexName])
                    os.remove(os.path.join(dexFolder, dexName))
                    continue

                Log.d(TAG, "Repackage %s" %(jarFile))
                if not OatZip.isDeodexed(jarFile):
                    # Put the dex and framework's jar in the same folder, and jar into the jarFile
                    dexName = "classes.dex"
                    shutil.move(os.path.join(dexFolder, dexFile), os.path.join(dexFolder, dexName))
                    Utils.runWithOutput(["jar", "uf", jarFile, dexName])
                    os.remove(os.path.join(dexFolder, dexName))

                    dexName = "classes2.dex"
                    dexFile = appName + "-" + dexName
                    if os.path.exists(os.path.join(dexFolder, dexFile)):
                        shutil.move(os.path.join(dexFolder, dexFile), os.path.join(dexFolder, dexName))
                        Utils.runWithOutput(["jar", "uf", jarFile, dexName])
                        os.remove(os.path.join(dexFolder, dexName))

                    dexName = "classes3.dex"
                    dexFile = appName + "-" + dexName
                    if os.path.exists(os.path.join(dexFolder, dexFile)):
                        shutil.move(os.path.join(dexFolder, dexFile), os.path.join(dexFolder, dexName))
                        Utils.runWithOutput(["jar", "uf", jarFile, dexName])
                        os.remove(os.path.join(dexFolder, dexName))

        os.chdir(oldDir)


    @staticmethod
    def repackageAppWithArch(appDir, arch):
        """ Repackage the classes.dex into apk of appDir
        """

        if OPTIONS.formatApp == False: return

        # Keep the old directory, we will change back after some operations.
        oldDir = os.path.abspath(os.curdir)

        Log.i(TAG, "Repackage APKs of %s" %(appDir))
        for app in os.listdir(appDir):
            apkPath = os.path.join(appDir, app)
            apkFile = os.path.join(apkPath, app + ".apk")
            archPath = os.path.join(apkPath, "oat", arch)
            dexFile = os.path.join(archPath, app + ".dex")
            if os.path.exists(archPath):
                if not OatZip.isDeodexed(apkFile):
                    OatZip.packageDexToAppWithArch(apkFile, arch)

                #rm -rf $appdir/$app/$arch
                shutil.rmtree(archPath)

        os.chdir(oldDir)

    @staticmethod
    def check_validate(apkFile, arch, arch2):
        '''check whether is validate apk'''
        return True

    @staticmethod
    def dealWithAdditionalApks(systemDir, frwDir, arch, arch2, allAppDirs):
        ''' deal with additional apks '''

        if OPTIONS.formatApp == False: return

        # Keep the old directory, we will change back after some operations.
        oldDir = os.path.abspath(os.curdir)

        bootClassFolderArch = os.path.join(frwDir, arch, "odex")
        bootClassFolderArch2 = os.path.join(frwDir, arch2, "odex")

        for (dirpath, dirnames, filenames) in os.walk(systemDir):

            # Exclude scanned directories
            if dirpath in allAppDirs:
                continue

            dirnames = dirnames # no use, to avoid warning

            for filename in filenames:
                if filename.endswith(".apk") or filename.endswith(".jar"):
                    apkFile = os.path.join(dirpath, filename)
                    if not OatZip.check_validate(apkFile, arch, arch2):
                        continue

                    archDir = os.path.join(dirpath, "oat", arch)
                    #app name
                    app = filename[0:-4]
                    if os.path.exists(archDir):
                        if not OatZip.isDeodexed(apkFile):
                            odexFile = os.path.join(archDir, app + ".odex")
                            if os.path.exists(odexFile):
                                Utils.runWithOutput([OatZip.OAT2DEX, odexFile, bootClassFolderArch])

                                OatZip.packageDexToAppWithArch(apkFile, arch)
                        #rm -rf $appdir/$app/$arch
                        shutil.rmtree(archDir)

                    arch2Dir = os.path.join(dirpath, "oat", arch2)
                    if os.path.exists(arch2Dir):
                        if not OatZip.isDeodexed(apkFile):
                            odexFile = os.path.join(arch2Dir, app + ".odex")
                            if os.path.exists(odexFile):
                                Utils.runWithOutput([OatZip.OAT2DEX, odexFile, bootClassFolderArch2])

                                OatZip.packageDexToAppWithArch(apkFile, arch2)
                        #rm -rf $appdir/$app/$arch
                        shutil.rmtree(arch2Dir)

                    if os.path.exists(os.path.join(dirpath, "oat")) :
                        shutil.rmtree(os.path.join(dirpath, "oat"))


def debug():

    Log.DEBUG = True
    root = "root directory the unziped files"

    OatZip(root).deoat()
    OatZip(root).rebuild()

if __name__ == "__main__":

    debug()
