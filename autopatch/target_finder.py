#!/usr/bin/python
# Filename: target_finder.py

"""
Fast search the target out.

Usage: target_finder.py TARGET
        - TARGET target path relative to current directory.
"""

__author__ = 'duanqz@gmail.com'


import sys
import re
import os
import fnmatch
import commands

class TargetFinder:

    # The framework partitions
    PARTITIONS = []

    def __init__(self):
        self.__initPartitions()

        # Path Regex to match out useful parts
        # Using named group match with "(?P<group_name>)", using minimum match end with "?"
        self.pathRegex = re.compile("(?P<part1>.*?)/(?P<part2>smali/.*?)(?P<part3>.*)")

    def __initPartitions(self):
        """ Parse out the framework partitions.
        """

        makefile = None
        for filename in os.listdir(os.curdir):
            if fnmatch.fnmatch(filename.lower(), "makefile"):
                makefile = filename

        if makefile == None:
            return

        fileHandle = open(makefile, "r")
        content = fileHandle.read()
        modifyJars = re.compile("\n\s*vendor_modify_jars\s*:=\s*(?P<jars>.*)\n")
        match = modifyJars.search(content)
        if match != None:
            TargetFinder.PARTITIONS = match.group("jars").split(" ")

        fileHandle.close()


    def __findInDexPartitions(self, target):
            """ Find the target in dex partition.
                On Android 5.0, Files might be split to different dex-partitions
            """

            if os.path.exists(target):
                return target


            (outClass, innerClass) = TargetFinder.__extractInnerClass(target)
            match = self.pathRegex.search(outClass)
            if match != None:
                # Part 1: top directory of framework
                # Part 2: smali or smali_classes2 ...
                # Part 3: the remains of the path
                part1 = match.group("part1")
                part2 = match.group("part2")
                part3 = match.group("part3")

                if not os.path.exists(part1):
                    return target

                for subDir in os.listdir(part1):
                    if subDir.startswith("smali") and subDir != part2:
                        newTarget = os.path.join(part1, subDir, part3)
                        if os.path.exists(newTarget):
                            return TargetFinder.__concatInnerClass(newTarget, innerClass)

            # Not found
            return target



    def __findInFrwPartitions(self, target):
        """ Find the target in the partitions.
            Files might be split to different framework-partition
        """

        (outClass, innerClass) = TargetFinder.__extractInnerClass(target)

        match = self.pathRegex.search(outClass)
        if match != None:
            # Part 1: top directory of framework
            # Part 2: smali or smali_classes2 ...
            # Part 3: the remains of the path
            part1 = match.group("part1")
            part2 = match.group("part2")
            part3 = match.group("part3")

            for partition in TargetFinder.PARTITIONS:
                if not partition.endswith(".jar.out"):
                    partition += ".jar.out"

                newTarget = os.path.join(partition, part2, part3)
                if os.path.exists(newTarget):
                    return TargetFinder.__concatInnerClass(outClass, innerClass)


        # Not found
        return target


    @staticmethod
    def __extractInnerClass(target):
        """ Extract the inner class file from target
        """

        pos = target.find("$")
        if pos >= 0:
            # Inner class, set outer class as new target to find
            outClass = target[:pos] + ".smali"
            innerClass = target[pos:]
            return (outClass, innerClass)
        else:
            return (target, None)


    @staticmethod
    def __concatInnerClass(outClass, innerClass):
        if innerClass != None:
            return outClass.replace(".smali", innerClass)
        else:
            return outClass



    def __findInAll(self, target):
        """ Find the target in all project root
        """

        basename = os.path.basename(target)
        searchPath = []
        for partition in TargetFinder.PARTITIONS:
            if not partition.endswith(".jar.out"):
                partition += ".jar.out"
            searchPath.append(partition)

        cmd = "find %s -name %s" % (" ".join(searchPath), commands.mkarg(basename))
        (sts, text) = commands.getstatusoutput(cmd)
        try:
            if sts == 0:
                text = text.split("\n")[0]
                if len(text) > 0:
                    return text
        except:
            pass

        return target


    def find(self, target, loosely=False):
        """ Find the target out in the current directory.
            Set loosely to be True to find file base name in all directory
        """

        # Firstly, check whether target exists in dex partitions
        target = self.__findInDexPartitions(target)
        if os.path.exists(target):
            return target

        # Secondly, check whether target exists in framework partitions
        # It is more efficiently than find in all files
        target = self.__findInFrwPartitions(target)
        if os.path.exists(target):
            return target

        # Thirdly, still not find the target, search in all sub directories
        if loosely:
            return self.__findInAll(target)
        else:
            return target


# End of class TargetFinder

if __name__ == "__main__":
    argc = len(sys.argv)
    if argc != 2 :
        print __doc__
        sys.exit()

    target = sys.argv[1]
    print TargetFinder().find(target)
