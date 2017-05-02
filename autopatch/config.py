#!/usr/bin/python

"""
Configuration
"""

__author__ = 'duanqz@gmail.com'


import os
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

class Config:
    """ Configuration.
    """

### Root directory   
    # Root directory of current project
    PRJ_ROOT = os.curdir

### AUTOPATCH Directory
    # We need to hold three directory because diff3
    # incorporate changes from newer to older into target.

    AUTOPATCH = os.path.join(PRJ_ROOT, "autopatch/")

    # AOSP root directory
    AOSP_ROOT = os.path.join(AUTOPATCH, "aosp/")

    # BOSP root directory
    BOSP_ROOT = os.path.join(AUTOPATCH, "bosp/")

    # Last BOSP root directory
    LAST_BOSP_ROOT = os.path.join(AUTOPATCH, "last_bosp/")

    # Vendor original root directory
    VENDOR_ORIGINAL_ROOT = os.path.join(AUTOPATCH, "vendor_original")

    # Vendor patched root directory
    VENDOR_PATCHED_ROOT = os.path.join(AUTOPATCH, "vendor_patched")

    # Root directory of reject files
    REJ_ROOT = os.path.join(AUTOPATCH, "reject/")

### Patch XML
    PATCHALL_XML = os.path.join(AUTOPATCH, "patchall.xml")

    UPGRADE_XML  = os.path.join(AUTOPATCH, "upgrade.xml")

    PORTING_XML  = os.path.join(AUTOPATCH, "porting.xml")

    @staticmethod
    def toString():
        print "-----------------------------------------------------------"
        print "PRJ_ROOT:\t" + Config.PRJ_ROOT
        print "AOSP_DIR:\t" + Config.AOSP_ROOT
        print "BOSP_DIR:\t" + Config.BOSP_ROOT
        print "---"
        print "PATCHALL_XML:\t" + Config.PATCHALL_XML
        print "-----------------------------------------------------------"

# End of class Config

if __name__ == "__main__":
    Config.toString()
