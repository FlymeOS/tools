#!/usr/bin/python

"""
Usage: $decode_ota.py ota.zip output
        decode ota.zip to output
"""

__author__ = 'duanqz@gmail.com'


import sys
from precondition import Utils

if __name__ == "__main__":

    argc = len(sys.argv)

    if argc < 3:
        print __doc__

    Utils.decode(sys.argv[1], sys.argv[2])