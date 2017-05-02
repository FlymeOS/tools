#!/usr/bin/python

"""
Usage: log LEVEL TAG MESSAGE
        LEVEL   : d(debug), i(info), w(warning), e(error)
        TAG     : log tag
        MESSAGE : log message
"""


import sys

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


class Paint:

    @staticmethod
    def bold(s):
        return "%s[01m%s%s[0m" % (chr(27), s.rstrip(), chr(27))

    @staticmethod
    def red(s):
        return "%s[33;31m%s%s[0m" % (chr(27), s.rstrip(), chr(27))

    @staticmethod
    def green(s):
        return "%s[31;32m%s%s[0m" % (chr(27), s.rstrip(), chr(27))

    @staticmethod
    def blue(s):
        return "%s[34;01m%s%s[0m" % (chr(27), s.rstrip(), chr(27))

    @staticmethod
    def yellow(s):
        return "%s[31;33m%s%s[0m" % (chr(27), s.rstrip(), chr(27))


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print __doc__
        sys.exit()

    level   = sys.argv[1]
    tag     = sys.argv[2]
    message = sys.argv[3]

    if   level in ("d", "debug"): Log.d(tag, message)
    elif level in ("i", "info") : Log.i(tag, message)
    elif level in ("w", "warn") : Log.w(tag, message)
    elif level in ("e", "error"): Log.e(tag, message)
