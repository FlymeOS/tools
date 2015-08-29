#!/usr/bin/env python

# Copyright 2015 duanqz(duanqz@gmail.com)
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
Unpack and pack boot.img Intelligently.
"""

__author__ = 'duanqz@gmail.com'


import os
import subprocess
import commands
import tempfile
import time
import signal
import shutil

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

DEBUG = False


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
            boot_type = tool.attrib["type"]
            description = tool.attrib["description"]

            unpack_tool = tool.find("unpack").text
            pack_tool = tool.find("pack").text
            self.allTools[boot_type] =  { "UNPACK" : os.path.join(Toolkit.TOOLS_ROOT, unpack_tool),
                                          "PACK"   : os.path.join(Toolkit.TOOLS_ROOT, pack_tool) }
            self.sequence[seq] = (boot_type, description)

    def parse_boot_img_type(self, boot_img):
        """ Match appropriate tools for the boot image file.
        """

        remain_seqs = sorted(self.sequence.keys())
        # Try to unpack boot image for each type,
        # choose the appropriate one.
        print "Trying to unpack:"
        for seq in sorted(self.sequence.keys()):

            # Delete from remain_seqs
            remain_seqs.remove(seq)

            # Try to unpack the boot image by unpack tool
            (boot_type, description) = self.sequence.get(seq)
            unpack_tool = self.get_tools(boot_type, "UNPACK")
            if Utils.try_unpack(unpack_tool, boot_img):
                print " Succeed trying with %s(%s) " % (boot_type, description)
                break
            else:
                print " Failed trying with %s(%s)" % (boot_type, description)

        if len(remain_seqs) > 0:
            print " "
            print "You might manually try unpacking with the remaining if %s does not actually work:" % boot_type
            for seq in remain_seqs:
                (remain_boot_type, description) = self.sequence.get(seq)
                print "  %s(%s)" % (remain_boot_type, description)

        return boot_type

    def get_tools(self, boot_type, attrib=None):
        """ Get tools by type of boot.img
        """

        tools = self.allTools.get(boot_type)
        if attrib is None:
            return tools
        else:
            return tools[attrib]


class Utils:

    def __init__(self):
        pass

    @staticmethod
    def try_unpack(unpack_tool, boot_img):
        """ Try to unpack the boot image into TEMP_DIR.
            Return True: unpack successfully. False: otherwise.
        """

        tmp_dir = tempfile.mkdtemp()

        cmd = "%s %s %s" % (unpack_tool, boot_img, tmp_dir)
        p = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        timeout = 10
        while True:
            if p.poll() is not None:
                status = p.poll()
                break
            timeout -= 1
            time.sleep(0.5)
            if timeout <= 0:
                status = -1
                os.killpg(p.pid, signal.SIGTERM)
                break

        (output, err) = p.communicate()

        # Debug code. Useless for release version
        Utils.__debug("\nTry: %s" % cmd)
        Utils.__debug(output)

        shutil.rmtree(tmp_dir)

        return status == 0


    @staticmethod
    def format(boot_img):
        """ Format boot_img
        """

        f = open(boot_img, "r+")
        hstr = f.read(len("ANDROID"))

        if hstr == "ANDROID":
            return

        f.seek(0)
        content = f.read()

        idx = content.find("ANDROID")
        if idx >= 0:
            f.seek(0)
            f.truncate()
            f.write(content[idx:])

        f.close()

    @staticmethod
    def write_boot_img_type(boot_type, boot_dir):
        """ Write boot_type into a type.config in boot_dir
        """

        f = open(os.path.join(boot_dir, Toolkit.TYPE_CONFIG), "w")
        f.write(boot_type)
        f.close()


    @staticmethod
    def read_boot_img_type(boot_dir):
        """ Read boot_type from type.config in boot_dir
        """

        try:
            f = open(os.path.join(boot_dir, Toolkit.TYPE_CONFIG), "r")
            boot_type = f.read().rstrip()
            f.close()
        except IOError:
            print "Can not find type.config, use COMMON as image type by default"
            boot_type = "COMMON-V1"

        return boot_type


    @staticmethod
    def __debug(msg):
        if DEBUG:
            print msg


def unpack(boot_img, output):
    """ Unpack the boot image into the output directory.
    """

    Utils.format(boot_img)

    tool_kit = Toolkit()

    # Try unpack tool set to find the suitable one
    boot_type = tool_kit.parse_boot_img_type(boot_img)

    # Check whether the tools exists
    if boot_type is None:
        raise ValueError("Unknown boot image type: " + boot_img)

    # Execute the unpack command
    unpack_tool = tool_kit.get_tools(boot_type, "UNPACK")
    cmd = "%s %s %s" % (commands.mkarg(unpack_tool), commands.mkarg(boot_img), commands.mkarg(output))
    (status, result) = commands.getstatusoutput(cmd)

    if status != 0:
        print "\n* Unpack failed"
        print result
    else:
        print "\n* Unpack %s %s --> %s" % (boot_type, boot_img, output)

    # Store the used tools to output
    Utils.write_boot_img_type(boot_type, output)


def pack(boot_dir, output):
    """ Pack the BOOT directory into the output image
    """

    # Retrieve the last used tools from boot directory
    boot_type = Utils.read_boot_img_type(boot_dir)

    # Check whether the tools exists
    if boot_type is None:
        raise ValueError("Unknown boot image type.")

    # Execute the pack command
    pack_tool = Toolkit().get_tools(boot_type, "PACK")
    cmd = "%s %s %s" % (commands.mkarg(pack_tool), commands.mkarg(boot_dir), commands.mkarg(output))
    (status, result) = commands.getstatusoutput(cmd)

    if status != 0:
        print "Pack failed"
        print result
    else:
        print "Pack %s %s --> %s" % (boot_type, boot_dir, output)


if __name__ == '__main__':
    pass