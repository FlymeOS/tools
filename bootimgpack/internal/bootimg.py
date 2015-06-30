#!/usr/bin/env python
# Filename bootimg.py

__author__ = 'duanqz@gmail.com'


import commands
from toolkit import Toolkit

import imgformat

class Bootimg:
    """
    Model of boot image. With the property of type.
    """

    TOOLKIT = Toolkit()
    FORMAT_BEFORE_UNPACK = True

    def __init__(self, bootfile):
        """ bootfile could be a boot.img or an already unpacked boot directory
        """

        self.bootfile = bootfile
        self.imgFormat = imgformat.ImgFormat(self.bootfile)

    def unpack(self, output):
        """ Unpack the boot image into the output directory.
        """
        if Bootimg.FORMAT_BEFORE_UNPACK:
            self.imgFormat.format()

        # Try unpack tool set to find the suitable one
        self.bootType = self.TOOLKIT.parseType(self.bootfile)

        # Check whether the tools exists
        if self.bootType == None: raise ValueError("Unknown boot image type: " + self.bootfile)

        # Execute the unpack command
        unpackTool = self.TOOLKIT.getTools(self.bootType, "UNPACK")
        cmd = "%s %s %s" %(commands.mkarg(unpackTool), commands.mkarg(self.bootfile), commands.mkarg(output))
        (status, result) = commands.getstatusoutput(cmd)

        if status != 0:
            print "Unpack failed"
            print result
        else:
            print "Unpack %s %s --> %s" %(self.bootType, self.bootfile, output)

        # Store the used tools to output
        Toolkit.storeType(self.bootType, output)

    def pack(self, output):
        """ Pack the BOOT directory into the output image
        """

        # Retrieve the last used tools from boot directory
        self.bootType = Toolkit.retrieveType(self.bootfile)

        # Check whether the tools exists
        if self.bootType == None: raise ValueError("Unknown boot image type.")

        # Execute the pack command
        packTool = self.TOOLKIT.getTools(self.bootType, "PACK")
        cmd = "%s %s %s" %(commands.mkarg(packTool), commands.mkarg(self.bootfile), commands.mkarg(output))
        (status, result) = commands.getstatusoutput(cmd)

        if status != 0:
            print "Pack failed"
            print result
        else:
            print "Pack %s %s --> %s" %(self.bootType, self.bootfile, output)

### End of class Bootimg


