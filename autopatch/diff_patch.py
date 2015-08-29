#!/usr/bin/python

### File Information ###
"""
Incorporate changes from older to newer into target.
"""

__author__ = 'duanqz@gmail.com'


TAG="diff_patch"

import os
import commands
import shutil
import fnmatch
import tempfile

from config import Config
from smaliparser.Smali import Smali
from formatters.log import Log


class DiffPatch():

    def __init__(self, target, older, newer):
        self.mTarget = target
        self.mOlder  = older
        self.mNewer  = newer

    def run(self):
        if fnmatch.fnmatch(self.mTarget, "*.smali"):
            self.diff3_smali()
        else:
            self.diff3_non_smali()

    def diff3_non_smali(self):
        """ diff3 for non SMALI file
        """

        DiffPatch.__diff3(self.mTarget, self.mOlder, self.mNewer)

    def diff3_smali(self):
        """ diff3 for SMALI file
            Each file will be split to lots of parts, then using diff3 by each part,
            at last, all the parts will be joined again.
        """

        # Acquire splitters
        splitters = Splitters()
        (target, older, newer) = splitters.aquire(self.mTarget, self.mOlder, self.mNewer)

        # Delete the unnecessary part
        # Here should use deep copy of the list, otherwise will cause leak deleting
        for targetPart in target.getAllParts()[:]:
            olderPart = older.match(targetPart)
            newerPart = newer.match(targetPart)

            # Case
            # target older newer  action
            #   o      o     x    delete
            #   x      o     x    ignore
            #   o      x     x    ignore
            #   x      x     x    ignore

            olderExists = os.path.exists(olderPart)
            newerExists = os.path.exists(newerPart)
            if olderExists and (not newerExists):
                target.deletePart(targetPart)


        # Patch partitions one by one
        for newerPart in newer.getAllParts():
            targetPart = target.match(newerPart)
            olderPart  = older.match(newerPart)

            # Case
            # target older newer  action
            #   o      o     o    merge
            #   o      x     o    replace
            #   x      o     o    conflict
            #   x      x     o    append

            targetExists = os.path.exists(targetPart)
            olderExists  = os.path.exists(olderPart)
            if targetExists and olderExists:
                # all of items exist. (merge)
                DiffPatch.__diff3(targetPart, olderPart, newerPart)
            elif targetExists:
                # newer already exist in target. (replace)
                target.replacePart(targetPart, newerPart)
                pass
            elif olderExists:
                # target might be removed by vendor. (conflict)
                target.conflictPart(olderPart, newerPart)
                pass
            else:
                # newer not exist in older and target. (append)
                target.appendPart(newerPart)

        # Release splitters
        splitters.release()


    @staticmethod
    def __diff3(target, older, newer):
        """ Incorporate changes from older to newer into target.
            Return True if no conflicts, otherwise return False.
        """

        # Exit status is 0 if successful, 1 if conflicts, 2 if trouble
        cmd = "diff3 -E -m -L VENDOR %s -L AOSP %s -L BOSP %s" % \
                (commands.mkarg(target), commands.mkarg(older), commands.mkarg(newer))
        (status, output) = commands.getstatusoutput(cmd)

        # Append "\n" to output for shell invoking result will miss it
        output += "\n"
 
        if status != 2:
            # Write back the patched file
            targetFile = open(target, "wb")
            if status != 0:
                output = DiffPatch.__markConflictMethod(output)
            targetFile.write(output)
            targetFile.close()

        # status is 0 if successful
        return status == 0


    @staticmethod
    def __markConflictMethod(output):
        """ Mark out the method name in conflict part.
        """

        subStart   = output.find(".method")
        subEnd     = output.find("(")
        if subStart >= 0:
            methodName = output[subStart:subEnd]
            output = output.replace("=======", "======= #@%s@" %methodName)

        return output


###
### SMALI Splitter
###

class Splitters:
    """ Holder of all the SMALI splitters.
    """

    TMP = tempfile.mktemp()
    TARGET_OUT = os.path.join(TMP, "target")
    OLDER_OUT  = os.path.join(TMP, "older")
    NEWER_OUT  = os.path.join(TMP, "newer")

    def aquire(self, target, older, newer):

        # Prepare temporary directory
        for tmpDir in (Splitters.TARGET_OUT, Splitters.OLDER_OUT, Splitters.NEWER_OUT):
            if not os.path.exists(tmpDir): os.makedirs(tmpDir)

        # Split the target, older and newer
        self.targetSplitter = SmaliSplitter().split(target, Splitters.TARGET_OUT)
        self.olderSplitter  = SmaliSplitter().split(older,  Splitters.OLDER_OUT)
        self.newerSplitter  = SmaliSplitter().split(newer,  Splitters.NEWER_OUT)

        return (self.targetSplitter, self.olderSplitter, self.newerSplitter)

    def release(self):
        # Join the partitions
        self.targetSplitter.join()

        # Remove temporary directory
        shutil.rmtree(Splitters.TMP)


class SmaliSplitter:
    """ Independent splitter of SMALI file
    """

    def split(self, origSmali, output=None):
        """ Split the original SMALI file into partitions
        """

        if output == None: output = os.path.dirname(origSmali)

        self.mOrigSmali = origSmali
        self.mOutput    = output
        self.mPartList  = Smali(origSmali).split(self.mOutput)

        return self

    def match(self, part):
        basename = os.path.basename(part)
        return os.path.join(self.mOutput, basename)

    def getAllParts(self):
        return self.mPartList

    def appendPart(self, part):
        """ Append a part to list if not exist
        """

        try:
            self.mPartList.index(part)
        except:
            Log.d(TAG, "  [Add new part %s ] " % part)
            self.mPartList.append(part)

    def deletePart(self, part):
        """ Delete a part
        """

        try:
            self.mPartList.remove(part)
            Log.d(TAG, "  [Delete part %s ] " % part)
        except:
            Log.e(TAG, "SmaliSpliiter.deltePart(): can not find part %s" % part)

    def replacePart(self, targetPart, newerPart):
        """ Replace the target with the newer.
        """

        try:
            index = self.mPartList.index(targetPart)
            self.mPartList[index] = newerPart
            Log.d(TAG, "  [Replace %s by %s] " % (targetPart, newerPart))
        except:
            Log.e(TAG, "SmaliSplitter.replacePart() can not find part %s" % targetPart)

    def conflictPart(self, olderPart, newerPart):
        """ If older and newer are the same content, no conflict happen. Otherwise, mark out conflict.
        """

        # Get older part content
        olderHandle = open(olderPart, "rb")
        olderContent = olderHandle.read()
        olderHandle.close()

        # Get newer part content
        newerHandle = open(newerPart, "r+")
        newerContent = newerHandle.read()

        # Compare older and newer content
        if olderContent == newerContent:
            # No need to handle access any more
            # # BOSP has no change on AOSP.
            # # Still handle this case: "access$" method
            # if newerPart.find("access$") >= 0:
            #     Log.d(TAG, "  [Might useful access part %s ] " % newerPart)
            #
            #     lines = []
            #     lines.append("\n# Remove the first '#' if you want to enable this method. It might be invoked from codes of BOSP.\n")
            #     for line in newerContent.splitlines():
            #         if len(line) > 0: line = "#%s\n" % line
            #         lines.append(line)
            #
            #     newerHandle.seek(0)
            #     newerHandle.truncate()
            #     newerHandle.writelines(lines)
            #     newerHandle.close()
            #     self.mPartList.append(newerPart)
            # else:
            #     newerHandle.close()
            newerHandle.close()
        else:
            # BOSP has changes on AOSP.

            # Conflict happened
            Log.d(TAG, "  [Conflict part %s ] " % newerPart)

            # Mark out the conflict
            newerContent = "\n<<<<<<< VENDOR\n=======%s\n>>>>>>> BOSP\n" % newerContent
            newerHandle.seek(0)
            newerHandle.truncate()
            newerHandle.write(newerContent)
            newerHandle.close()
            self.mPartList.append(newerPart)


    def join(self):
        """ Join all the partitions.
        """

        newSmali = open(self.mOrigSmali, "wb")

        # Write back the part by sequence
        for part in self.mPartList:
            if not os.path.exists(part):
                continue

            partHandle = open(part ,"rb")
            newSmali.write(partHandle.read())
            partHandle.close()

        newSmali.close()

        return self



def test():
    print "Result\t%s" % Config.PRJ_ROOT
    print "------  ---------------------------------------------------"

    # Test for XML
    f = "framework-res/AndroidManifest.xml"
    target = os.path.join(Config.PRJ_ROOT,  f)
    older  = os.path.join(Config.AOSP_ROOT, f)
    newer  = os.path.join(Config.BOSP_ROOT, f)

    print DiffPatch(target, older, newer).run(),
    print "\t" + f

    # Test for SMALI
    f = "framework.jar.out/smali/android/content/res/AssetManager.smali"
    target = os.path.join(Config.PRJ_ROOT,  f)
    older  = os.path.join(Config.AOSP_ROOT, f)
    newer  = os.path.join(Config.BOSP_ROOT, f)

    print DiffPatch(target, older, newer).run(),
    print "\t" + f



if __name__ == "__main__":
    test()
