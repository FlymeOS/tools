#!/usr/bin/python


__author__ = 'duanqz@gmail.com'


import os
from config import Config
from formatters.log import Paint

class Error:

    FAILED_LIST = []

    TOTAL_FILENOTFOUND = 0
    FILENOTFOUND_STATISTIC = {}

    TOTAL_CONFLICTS = 0
    CONFLICT_FILE_NUM  = 0
    CONFLICT_STATISTIC = {}


    @staticmethod
    def fileNotFound(target):
        # Add to FAILED_LIST
        Error.fail("  * File not found: %s" % target)

        # Increment total file not found
        Error.TOTAL_FILENOTFOUND += 1

        # Increment file not found of each part
        key = Error.getStatisticKey(target)
        if not Error.FILENOTFOUND_STATISTIC.has_key(key):
            Error.FILENOTFOUND_STATISTIC[key] = 0

        Error.FILENOTFOUND_STATISTIC[key] += 1


    @staticmethod
    def conflict(conflictNum, target):
        # Add to FAILED_LIST
        Error.fail("  %3d conflicts in: %s" %(conflictNum, target))

        # Increment total conflicts        
        Error.TOTAL_CONFLICTS += conflictNum;
        Error.CONFLICT_FILE_NUM += 1

        # Increment conflicts of each part
        key = Error.getStatisticKey(target)
        if not Error.CONFLICT_STATISTIC.has_key(key):
            Error.CONFLICT_STATISTIC[key] = 0

        Error.CONFLICT_STATISTIC[key] += conflictNum

    @staticmethod
    def getStatisticKey(target):
        relpath = os.path.relpath(target, Config.PRJ_ROOT)
        key = relpath[0:relpath.find("/")]

        return key        

    @staticmethod
    def fail(message):
        Error.FAILED_LIST.append(message)


    @staticmethod
    def showStatistic():
        for key in Error.FILENOTFOUND_STATISTIC.keys():
            print "%3d files not found in %s" % (Error.FILENOTFOUND_STATISTIC[key], key)

        if Error.TOTAL_FILENOTFOUND > 0:
            print Paint.bold("%3d files not found totally, they might be removed or moved to other place by vendor?" % Error.TOTAL_FILENOTFOUND)
            print " "

        for key in Error.CONFLICT_STATISTIC.keys():
            print "%3d conflicts in %s " % (Error.CONFLICT_STATISTIC[key], key)

        if Error.TOTAL_CONFLICTS > 0:
            print Paint.bold("%3d conflicts in %d files, go through the reject files in 'autopatch/reject' to find them out" % (Error.TOTAL_CONFLICTS, Error.CONFLICT_FILE_NUM))
            print Paint.red("\n  Ask for advice? Please type 'flyme help CONFLICTS_HAPPENED' \n")


    @staticmethod
    def report():

        if len(Error.FAILED_LIST) == 0:
            print Paint.green("\n  Ask for advice? Please type 'flyme help NO_CONFLICT' \n")
        else:
            Error.createAllRejects()

            Error.printDivide()
            for failed in Error.FAILED_LIST: print failed

            Error.printDivide()
            Error.showStatistic()


    @staticmethod
    def printDivide():
        print "  ____________________________________________________________________________________"
        print "                                                                                      "       


    @staticmethod
    def createAllRejects():
        if not os.path.exists(Config.REJ_ROOT):
            os.makedirs(Config.REJ_ROOT)
        allrejects = os.path.join(Config.REJ_ROOT, "allrejects.txt")
        handle = open(allrejects, "w")
        handle.write("\n".join(Error.FAILED_LIST))
        handle.close()


