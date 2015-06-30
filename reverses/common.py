#!/usr/bin/python

# Copyright 2015 Coron
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

__author__ = 'duanqz@gmail.com'


"""
Android has different VMs, each might has its own format.
From 2.3 to 4.3, DALVIK VM is used, and the format ODEX is introduced for efficiency.
From 4.4, ART comes out, the format ELF is designed for ART.

For easy use, CORON only treat standard OTA package, so we need to convert different OTA
package to the unified format.

Usage: $shell [-a|-f|-l|-c] -i input.zip -o output.zip
            --app, -a:        only format the system apps
            --framework, -f:  only format the framework jars
            --apiLevel,  -l:  set the API Level to deodex
            --classpath, -c:  set the classpath to deodex     
"""


import os
import sys
import getopt
import subprocess

TAG="reverse"

class Options(object):

    def usage(self):
        print __doc__

    def __init__(self):
        self.apiLevel  = None
        self.classpath = None

        # Only handle system APKs
        self.formatApp = False

        # Only handle framework JARS
        self.formatFrw = False

        self.inZip  = None
        self.outZip = None


    def handle(self, argv):
        """ Handle input arguments.
        """

        if len(argv) <= 1:
            self.usage()
            sys.exit(1)

        try:
            (opts, args) = getopt.getopt(argv[1:], "hafl:c:i:o:", \
                            [ "help", "app", "framework", "apilevel=", "classpath=", "input=", "output=" ])
            Log.d(TAG, "Program args = %s" %args)
        except getopt.GetoptError:
            Options.usage()

        for name, value in opts:
            if name in ("--help", "-h"):
                self.usage()
                sys.exit(0)

            elif name in ("--app", "-a"):
                self.formatApp = True

            elif name in ("--framework", "-f"):
                self.formatFrw = True

            elif name in ("--apilevel",  "-l"):
                self.apiLevel = value

            elif name in ("--classpath",  "-c"):
                self.classpath = value

            elif name in ("--input", "-i"):
                self.inZip = os.path.abspath(value)
            
            elif name in ("--output", "-o"):
                self.outZip = os.path.abspath(value)

        if self.inZip == None:
            Log.e(TAG, "No ota package is presented, nothing to be normalized.")
            self.usage
            sys.exit(1)

        if self.outZip == None:
            self.outZip = self.inZip + ".std.zip"

        if self.formatApp == False and self.formatFrw == False:
            self.formatApp = self.formatFrw = True

    def dump(self):
        Log.d(TAG, "input=%s, output=%s, apiLevel=%s" % (self.inZip, self.outZip, self.apiLevel))



class Utils:

    @staticmethod
    def runWithOutput(args):
        subp = Utils.run(args, stdout=subprocess.PIPE)
        Utils.printSubprocessOut(subp)


    @staticmethod
    def run(args, **kwargs):
        """Create and return a subprocess.Popen object, printing the command
           line on the terminal
        """

        return subprocess.Popen(args, **kwargs)


    @staticmethod
    def printSubprocessOut(subp):
        while True:
            buff = subp.stdout.readline().strip('\n')
            if buff == '' and subp.poll() != None:
                break

            Log.d(TAG, buff)



class Log:

    DEBUG = False

    @staticmethod
    def d(tag, message):
        if Log.DEBUG: print "D/%s: %s" %(tag, message)

    @staticmethod
    def i(tag, message):
        print "I/%s: %s" %(tag, message)

    @staticmethod
    def w(tag, message):
        print "W/%s: %s" %(tag, message)

    @staticmethod
    def e(tag, message):
        print "E/%s: %s" %(tag, message)