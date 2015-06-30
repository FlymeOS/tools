#!/usr/bin/python
# Filename test.py

__author__ = 'duanqz@gmail.com'


import os
import pickle
import shutil
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from internal.bootimg import Bootimg


def assertTypeEquals(bootfile, bootType):

    # Unpack
    Bootimg(bootfile).unpack("OUT/")

    # Load type
    fileHandle = open("OUT/type.config", "r")

    # Assert
    assert bootType == fileHandle.read()

    # Clear
    fileHandle.close()
    shutil.rmtree("OUT/")


def assetPackSucc(bootfile):
    Bootimg(bootfile).pack("out.img")

    assert os.path.exists("out.img")

    os.remove("out.img")

### Start
if __name__ == '__main__':

    testDir = path.dirname(path.abspath(__file__)) + "/"

    print ">>> Test unpack common boot.img"
    bootfile = os.path.join(testDir, "common-boot.img")
    assertTypeEquals(bootfile, "COMMON-V1")
    print "<<< Pass\n"

    print ">>> Test unpack common v1 boot.img"
    bootfile = os.path.join(testDir, "common-v1-boot.img")
    assertTypeEquals(bootfile, "COMMON-V1")
    print "<<< Pass\n"

    print ">>> Test unpack qcom boot.img"
    bootfile = os.path.join(testDir, "qcom-boot.img")
    assertTypeEquals(bootfile, "QCOM")
    print "<<< Pass\n"

    print ">>> Test unpack mtk boot.img"
    bootfile = os.path.join(testDir, "mtk-boot.img")
    assertTypeEquals(bootfile, "MTK")
    print "<<< Pass\n"

    print ">>> Test unpack sony boot.img"
    bootfile = os.path.join(testDir, "sony-boot.img")
    assertTypeEquals(bootfile, "SONY")
    print "<<< Pass\n"

    print ">>> Test pack common boot.img"
    bootfile = os.path.join(testDir, "common-boot")
    assetPackSucc(bootfile)
    print "<<< Pass\n"

    print ">>> Test pack common v1 boot.img"
    bootfile = os.path.join(testDir, "common-v1-boot")
    assetPackSucc(bootfile)
    print "<<< Pass\n"

    print ">>> Test pack qcom boot.img"
    bootfile = os.path.join(testDir, "qcom-boot")
    assetPackSucc(bootfile)
    print "<<< Pass\n"

    print ">>> Test pack mtk boot.img"
    bootfile = os.path.join(testDir, "mtk-boot")
    assetPackSucc(bootfile)
    print "<<< Pass\n"

    print ">>> Test pack sony boot.img"
    bootfile = os.path.join(testDir, "sony-boot")
    assetPackSucc(bootfile)
    print "<<< Pass\n"

