#!/usr/bin/env python
# Filename tools.py

__author__ = 'duanqz@gmail.com'


### Import blocks

import os
import shutil
import tempfile
import signal
import subprocess
import time


try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET



### Class blocks

class Toolkit:
    """ Toolkit including all tools
    """

    TOOLS_ROOT = os.path.dirname(os.path.abspath(__file__))
    TOOLKIT_XML = os.path.join(TOOLS_ROOT, "toolkit.xml")
    TYPE_CONFIG = "type.config"
 
    def __init__(self):
        """ Initialize tools factory from config.xml
        """

        self.allTools = {}
        self.sequence = {}

        tree = ET.parse(Toolkit.TOOLKIT_XML)
        for tool in tree.findall("tool"):
            seq = tool.attrib["seq"]
            bootType = tool.attrib["type"]
            description = tool.attrib["description"]

            unpackTool = tool.find("unpack").text
            packTool = tool.find("pack").text
            self.allTools[bootType] =  { "UNPACK" : os.path.join(Toolkit.TOOLS_ROOT, unpackTool),
                                         "PACK"   : os.path.join(Toolkit.TOOLS_ROOT, packTool) }
            self.sequence[seq] = (bootType, description)

    def parseType(self, bootfile):
        """ Match appropriate tools for the boot image file.
        """

        tryType = None

        unTryedSeqs = sorted(self.sequence.keys())
        # Try to unpack boot image for each type,
        # choose the appropriate one.
        for seq in sorted(self.sequence.keys()):

            # Delete from unTryedSeqs
            unTryedSeqs.remove(seq)

            # Try to unpack the boot image by unpack tool
            (bootType, description) = self.sequence.get(seq)
            unpackTool = self.getTools(bootType, "UNPACK")
            if BootimgParser.tryUnpack(unpackTool, bootfile) == True:
                tryType = bootType
                print "Succeed trying with %s(%s) " % (bootType, description)
                break
            else:
                print "Failed trying with %s(%s)" % (bootType, description)

        if len(unTryedSeqs) > 0:
            print "You might manually try unpacking with the following if %s does not actually work:" % bootType
            for seq in unTryedSeqs:
                (bootType, description) = self.sequence.get(seq)
                print "  %s(%s)" % (bootType, description)

        BootimgParser.clearTempDir()

        return tryType

    def getTools(self, bootType, attrib=None):
        """ Get tools by type of boot.img
        """

        tools = self.allTools.get(bootType)
        if attrib == None :
            return tools
        else:
            return tools[attrib]

    @staticmethod
    def storeType(bootType, bootout):
        # Serialize
        fileHandle = open(os.path.join(bootout, Toolkit.TYPE_CONFIG), "w")
        fileHandle.write(bootType)
        fileHandle.close()

    @staticmethod
    def retrieveType(bootout):
        # De-serialize
        try:
            fileHandle = open(os.path.join(bootout, Toolkit.TYPE_CONFIG), "r")
            bootType = fileHandle.read().rstrip()
            fileHandle.close()
        except:
            print "Can not find type.config, use COMMON as image type by default"
            bootType = "COMMON"
        return bootType

### End of class Toolkit


class BootimgParser:
    """ Match out appropriate tools
    """

    # Directory for temporary data storage.
    TEMP_DIR = tempfile.mkdtemp()
    TIME_OUT = 10 # 5.0 seconds

    @staticmethod
    def tryUnpack(unpackTool, bootimg):
        """ Try to unpack the boot image into TEMP_DIR.
            Return True: unpack successfully. False: otherwise.
        """

        BootimgParser.clearTempDir()

        cmd = "%s %s %s" %(unpackTool, bootimg, BootimgParser.TEMP_DIR)
        p = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        timeout = BootimgParser.TIME_OUT
        while True:
            if p.poll() != None:
                status = p.poll()
                break
            timeout -= 1
            time.sleep(0.5)
            if timeout <= 0:
                status = -1
                os.killpg(p.pid, signal.SIGTERM)
                break

        (output, erroutput) = p.communicate()

        # Debug code. Useless for release version
        BootimgParser.__debug("\nTry: %s" % cmd)
        BootimgParser.__debug(output)

        return status == 0

    @staticmethod
    def clearTempDir():
        """ Clear the temporary directory
        """

        if os.path.exists(BootimgParser.TEMP_DIR) == True:
            shutil.rmtree(BootimgParser.TEMP_DIR)

    @staticmethod
    def __debug(msg):
        if False: print msg
### End of class ToolsMatcher

