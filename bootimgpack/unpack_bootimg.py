#!/usr/bin/python
# Filename unpack_bootimg.py

__author__ = 'duanqz@gmail.com'


from internal import param
from internal.bootimg import Bootimg
import sys
import traceback

### Start
if __name__ == '__main__':
    args = param.ParseOptions(sys.argv[1:])
    argLen = len(args)
    if argLen <= 0:
        print "Usage: unpack_bootimg.py BOOT_IMG [OUTPUT]"
        print "       - BOOT_IMG : the boot image to be unpack"
        print "       - OUTPUT   : the output directory after unpack. if not present OUT/ directory will be used."
        exit(1);
    elif argLen == 1:
        bootfile = args[0]
        output = bootfile + ".out"
    elif argLen >= 2:
        bootfile = args[0]
        output = args[1]

    try:
        Bootimg(bootfile).unpack(output)
    except ValueError as ve:
        if param.OPTIONS.quiet is False:
            traceback.print_exc()
        # See help.xml ERR_UNPACK_BOOTIMG_FAILED
        sys.exit(153)
