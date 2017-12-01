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
Deodex
TODO
"""

__author__ = 'duanqz@gmail.com'


import os
import tempfile
import commands
import shutil

from common import Options, Log

# Global
TAG="reverse-deodex"
OPTIONS = Options()

class OdexZip:

    CLASSPATH="core.jar:ext.jar:framework.jar:android.policy.jar:services.jar"

    def __init__(self, unzipRoot):
        self.mRoot = unzipRoot

        self.mFrwDir = os.path.join(self.mRoot, "system/framework")
        self.mAppDir = os.path.join(self.mRoot, "system/app")
        self.mPrivAppDir = os.path.join(self.mRoot, "system/priv-app")

        if OPTIONS.classpath == None:
            OPTIONS.classpath = OdexZip.CLASSPATH


    def deodex(self):
        OdexZip.deodexFrw(self.mFrwDir)

        #OdexZip.deodexApp(self.mAppDir)
        #OdexZip.deodexApp(self.mPrivAppDir)


    @staticmethod
    def deodexFrw(odexJarDir):
        """ De-odex framework
        """

        if OPTIONS.formatFrw == False: return

        coreOdex = os.path.join(odexJarDir, "core.odex")
        if os.path.exists(coreOdex):
            Log.i(TAG, "De-odex core.odex")
            deodexFile = os.path.join(odexJarDir, "core.jar")
            OdexZip.deodexOneFile(coreOdex, deodexFile)

        Log.i(TAG, "De-odex files of odex-format in %s" % odexJarDir)
        for item in os.listdir(odexJarDir):
            if item.endswith(".odex"):
                odexJar = os.path.join(odexJarDir, item)
                deodexJar = odexJar[0:-4] + ".jar"
                OdexZip.deodexOneFile(odexJar, deodexJar)
                break


    @staticmethod
    def deodexApp(odexApkDir):
        """ De-oat app
        """

        if OPTIONS.formatApp == False: return

        for item in os.listdir(odexApkDir):
            if item.endswith(".odex"):
                odexApk = os.path.join(odexApkDir, item)
                deodexApk = odexApk[0:-4] + ".apk"
                OdexZip.deodexOneFile(odexApk, deodexApk)


    @staticmethod
    def deodexOneFile(odexFile, deodexFile):
        """ De-odex one file.
        """

        if not odexFile.endswith(".odex"): return

        temp = tempfile.mktemp()

        # Phase 1: Baksmali the odex file
        cmd = ["baksmali", "-x", odexFile, "-d", "framework", "-I", "-o", os.path.join(temp, "out")]
        if OPTIONS.apiLevel  != None: cmd.extend(["-a", OPTIONS.apiLevel])
        if OPTIONS.classpath != None: cmd.extend(["-c", OPTIONS.classpath])

        cmd = " ".join(cmd)
        Log.d(TAG, cmd)
        Log.d(TAG, commands.getoutput(cmd))

        # Phase 2: Smali the files into dex
        oldDir = os.path.abspath(os.curdir)
        os.chdir(temp)

        cmd = "smali out/ -o classes.dex"
        Log.d(TAG, commands.getoutput(cmd))
        #Utils.runWithOutput(["smali", "out", "-o", "classes.dex"])

        # Phase 3: Package
        if os.path.exists(deodexFile):
            #cmd = ["jar", "uf", deodexFile, "classes.dex"]
            cmd = "jar uf %s classes.dex" % deodexFile
        else:
            #cmd = ["jar", "cf", deodexFile, "classes.dex"]
            cmd = "jar cf %s classes.dex" % deodexFile

        Log.d(TAG, commands.getoutput(cmd))
        #Utils.runWithOutput(cmd)
        os.chdir(oldDir)

        if os.path.exists(odexFile): os.remove(odexFile)

        Log.i(TAG, "Delete %s" %temp)
        shutil.rmtree(temp)

        # Phase 4: zipalign
        #Utils.runWithOutput(["zipalign", "4", deodexFile, deodexFile+".aligned"])
        #Utils.runWithOutput(["mv", deodexFile+".aligned", deodexFile])

        cmd = "zipalign 4 %s %s" %(deodexFile, deodexFile+".aligned")
        Log.d(TAG, commands.getoutput(cmd))

        cmd = "mv %s %s" %(deodexFile+".aligned", deodexFile)
        Log.d(TAG, cmd)


def debug():

    Log.DEBUG = True
    root = "root directory the unziped files"
    OdexZip(root).deodex()


if __name__ == "__main__":

    debug()

