'''
Created on Aug 26, 2014

@author: tangliuxiang
'''
from xml.dom import minidom
import sys
import re
import os

reload(sys)
sys.setdefaultencoding("utf-8")

def getPackageName(androidManifest):
    manDom = minidom.parse(androidManifest)
    return manDom.documentElement.getAttribute("package")

def getPackageNameFromPublicXml(publicXml):
    androidManifest = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(publicXml))), "AndroidManifest.xml")
    if os.path.isfile(androidManifest):
        pkgName = getPackageName(androidManifest)
    else:
        publicXml = minidom.parse(publicXml)
        root = publicXml.documentElement
        pkgName = ""
        for item in root.childNodes:
            if item.nodeType == minidom.Node.ELEMENT_NODE:
                itemId = item.getAttribute("id").replace(r'0x0', r'')
                if len(itemId) == 7 and itemId[0] == '1':
                    pkgName = 'android'
                break
    assert pkgName is not None and len(pkgName) > 0, "Wrong package name in %s, make sure %s is exist and correct!" % (publicXml, androidManifest)
    return pkgName
