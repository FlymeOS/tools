#!/usr/bin/python
'''
USAGE: flash device recovery.fstab device.img [fstab_version]
    device: [boot|recovery]
    device.img: [boot.img|recovery.img]
    fstab_version: [1|2]
                1 for android 4.0 - 4.2 (DEFAULT)
                2 for android 4.3 - *

Created on Jul 31, 2014

@author: tangliuxiang
'''
import sys
import os
import traceback
from pull import utils

if __name__ == '__main__':

    try:
        if len(sys.argv) == 4:
            utils.PushUtils.push(sys.argv[1], sys.argv[2], sys.argv[3])
        elif len(sys.argv) >= 5:
            utils.PushUtils.push(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
        else:
            print __doc__
    except Exception as e:
        traceback.print_exc()
        # See help.xml ERR_PULL_BOOT_RECOVERY_FAILED
        sys.exit(156)