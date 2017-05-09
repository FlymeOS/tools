#!/usr/bin/python
# Filename: autopatch.py

"""
Patch the files automatically based on the autopatch.xsd.

Usage: $autopatch.py [OPTIONS]
              OPTIONS:
                --patchall, -p : Patch all the changes
                --upgrade,  -u : Patch the upgrade changes
                --porting,  -t : Porting changes from the other device

                Loosely, make sure you have prepared the autopatch directory by your self
                --loosely,  -l : Not prepare autopatch/
"""

__author__ = 'duanqz@gmail.com'



import shutil
import os, sys
import fnmatch
import traceback
import precondition
import rejector

from diff_patch import DiffPatch
from target_finder import TargetFinder
from config import Config
from error import Error

from formatters.format import Format
from formatters.log import Paint


try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


TAG="autopatch"


class AutoPatch:

    def __init__(self, targetRoot, olderRoot, newerRoot, patchXML):
        AutoPatch.TARGET_ROOT = targetRoot
        AutoPatch.OLDER_ROOT  = olderRoot
        AutoPatch.NEWER_ROOT  = newerRoot
        AutoPatch.PATCH_XML   = patchXML


    def run(self):
        # Parse out the PATCH_XML
        AutoPatchXML().parse()

        Error.report()

# End of class AutoPatch


class AutoPatchXML:
    """ Represent the tree model of the patch XML.
    """

    def parse(self):
        """ Parse the XML with the schema defined in autopatch.xsd
        """

        XMLDom = ET.parse(AutoPatch.PATCH_XML)

        for feature in XMLDom.findall('feature'):
            self.handleRevise(feature)


    def handleRevise(self, feature):
        """ Parse the revise node to handle the revise action.
        """

        description = feature.attrib['description']

        if len(feature.getchildren()) == 0:
            print "\n No changes between %s and %s, nothing to patch." % (AutoPatch.OLDER_ROOT, AutoPatch.NEWER_ROOT)
        else:
            print "\n [%s]" % description
            for revise in feature:
                ReviseExecutor(revise).run()

# End of class AutoPatchXML


class ReviseExecutor:
    """ Execute revise action to a unique file.
        Actions including ADD, MERGE, REPLACE. 
    """

    ADD     = "ADD"
    MERGE   = "MERGE"
    DELETE  = "DELETE"
    REPLACE = "REPLACE"

    TARGET_FINDER = TargetFinder()

    def __init__(self, revise):
        """ @args revise: the revise XML node.
        """

        self.action = revise.attrib['action']

        # Compose the source and target file path
        target = revise.attrib['target']
        self.mTarget = target
        self.mOlder  = os.path.join(AutoPatch.OLDER_ROOT,  target)
        self.mNewer  = os.path.join(AutoPatch.NEWER_ROOT,  target)


    def run(self):
        if   os.path.isfile(self.mNewer) or os.path.isfile(self.mOlder):
            self.singleAction(self.mTarget, self.mOlder, self.mNewer)

        elif os.path.isdir(self.mNewer): self.handleDirectory(self.mNewer)
        elif os.path.isdir(self.mOlder): self.handleDirectory(self.mOlder)

        elif self.mNewer.endswith("*"): self.handleRegex(self.mNewer)
        elif self.mOlder.endswith("*"): self.handleRegex(self.mOlder)

        else:
            print Paint.red("  Can not handle: %s" % self.mTarget)


    def handleDirectory(self, directory):
        """ Handle target is a directory
        """

        if   directory.startswith(AutoPatch.OLDER_ROOT):
            relpathStart = AutoPatch.OLDER_ROOT
        elif directory.startswith(AutoPatch.NEWER_ROOT):
            relpathStart = AutoPatch.NEWER_ROOT

        for (dirpath, dirnames, filenames) in os.walk(directory):

            dirnames = dirnames # No use, just avoid of warning

            for filename in filenames:
                path =  os.path.join(dirpath, filename)

                target = os.path.relpath(path, relpathStart)
                older  = os.path.join(AutoPatch.OLDER_ROOT,  target)
                newer  = os.path.join(AutoPatch.NEWER_ROOT,  target)

                self.singleAction(target, older, newer)


    def handleRegex(self, regex):
        """ Handle target ends with *
        """

        targetdir = os.path.dirname(self.mTarget)
        olderdir  = os.path.dirname(self.mOlder)
        newerdir  = os.path.dirname(self.mNewer)

        regexdir = os.path.dirname(regex)
        regexbase = os.path.basename(regex)

        # Match the filename in the directory
        for filename in os.listdir(regexdir):
            if fnmatch.fnmatch(filename, regexbase):
                target = os.path.join(targetdir, filename)
                older  = os.path.join(olderdir,  filename)
                newer  = os.path.join(newerdir,  filename)

                self.singleAction(target, older, newer)


    @staticmethod
    def bakupTarget(target, dst):

        # Find out the actual target
        target = ReviseExecutor.TARGET_FINDER.find(target)

        if not os.path.exists(target):
            return

        dstTarget = os.path.join(dst, target)
        if os.path.exists(dstTarget):
            os.remove(dstTarget)

        dirname = os.path.dirname(dstTarget)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        shutil.copy(target, dstTarget)


    def singleAction(self, target, older, newer):
        """ action for a single file
        """

        ReviseExecutor.bakupTarget(target, Config.VENDOR_ORIGINAL_ROOT)

        try:
            if   self.action == ReviseExecutor.ADD:     result = ReviseExecutor.singleReplaceOrAdd(target, newer)
            elif self.action == ReviseExecutor.MERGE:   result = ReviseExecutor.singleMerge(target, older, newer)
            elif self.action == ReviseExecutor.DELETE:  result = ReviseExecutor.singleDelete(target)
            elif self.action == ReviseExecutor.REPLACE: result = ReviseExecutor.singleReplaceOrAdd(target, newer)

            print result
        except:
            Error.fail("  * Failed to %s  %s" % (self.action, target))
            traceback.print_exc()

        ReviseExecutor.bakupTarget(target, Config.VENDOR_PATCHED_ROOT)


    @staticmethod
    def singleReplaceOrAdd(target, source):
        """ Add a file from source to target.
            Replace the target if exist.
        """

        # Find out the actual target
        target = ReviseExecutor.TARGET_FINDER.find(target)

        if os.path.exists(target):
            execute = "REPLACE  " + target
        else:
            execute = "    ADD  " + target
            ReviseExecutor.createIfNotExist(os.path.dirname(target))

        if not os.path.exists(source):
            Error.fileNotFound(source)

            return "%s %s" % (Paint.red("  [FAIL]"), execute)

        # Only format access method and res id
        action = Format.RESID_TO_NAME
        formatSource = Format(AutoPatch.NEWER_ROOT, source).do(action)
        formatTarget = Format(AutoPatch.TARGET_ROOT, target).do(action)

        shutil.copy(source, target)

        # Would not change res name back
        formatSource.undo(action)
        formatTarget.undo(action)

        return "%s %s" % (Paint.green("  [PASS]"), execute)


    @staticmethod
    def singleMerge(target, older, newer):
        """ Incorporate changes from older to newer into target
        """

        # Find out the actual target loosely
        target = ReviseExecutor.TARGET_FINDER.find(target, loosely=True)

        execute = "  MERGE  " + target

        if not os.path.exists(target):
            Error.fileNotFound(target)
            return "%s %s" % (Paint.red("  [FAIL]"), execute)

        action = Format.REMOVE_LINE | Format.RESID_TO_NAME
        formatTarget = Format(AutoPatch.TARGET_ROOT, target).do(action)
        formatOlder  = Format(AutoPatch.OLDER_ROOT,  older).do(action)
        formatNewer  = Format(AutoPatch.NEWER_ROOT,  newer).do(action)

        DiffPatch(target, older, newer).run()

        # Would not change res name back
        action = Format.REMOVE_LINE
        formatTarget.undo(action)
        formatOlder.undo(action)
        formatNewer.undo(action)

        conflictNum = rejector.process_conflicts(target)

        if conflictNum > 0 :
            Error.conflict(conflictNum, target)
            return "%s %s" % (Paint.yellow("  [CFLT]"), execute)
        else:
            return "%s %s" % (Paint.green("  [PASS]"), execute)


    @staticmethod
    def singleDelete(target):
        """ delete the target
        """

        # Find out the actual target
        target = ReviseExecutor.TARGET_FINDER.find(target)

        execute = " DELETE  " + target

        if os.path.exists(target):
            os.remove(target)
            return "%s %s" % (Paint.green("  [PASS]"), execute)

        return "%s %s" % (Paint.red("  [FAIL]"), execute)


    @staticmethod
    def createIfNotExist(dirname):
        if not os.path.exists(dirname):
            os.makedirs(dirname)


# End of class ReviseExecutor


def main(argv):
    argc = len(argv)
    if argc <= 1:
        print __doc__
        sys.exit(1)

    options = precondition.OPTIONS.handle(argv)

    if options.prepare: precondition.Prepare()

    AutoPatch(Config.PRJ_ROOT, options.olderRoot, options.newerRoot, options.patchXml).run()

if __name__ == "__main__":
    main(sys.argv)

