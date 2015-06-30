#!/usr/bin/python
# Filename pack_bootimg.py

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
        print "Usage: pack_bootimg.py BOOT_IMG_DIR [OUTPUT_IMG]"
        print "       - BOOT_IMG_DIR : the directory of boot image files."
        print "       - OUTPUT_IMG   : the output image after pack. If not present, out.img will be used"
        exit(1);
    elif argLen == 1:
        bootfile = args[0]
        output = bootfile + ".img" 
    elif argLen >= 2:
        bootfile = args[0]
        output = args[1]

    try:
        Bootimg(bootfile).pack(output)
    except ValueError as ve:
        if param.OPTIONS.quiet is False:
            traceback.print_exc()
        # See help.xml ERR_PACK_BOOTIMG_FAILED
        sys.exit(154)
