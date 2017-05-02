'''
Created on Jul 26, 2014

@author: tangliuxiang
'''

import getopt
import sys

class Options(object): pass
OPTIONS = Options()

OPTIONS.quiet = False

def ParseOptions(argv,
                 extra_opts="", extra_long_opts=(),
                 extra_option_handler=None):
    try:
        opts, args = getopt.getopt(
                                   argv, "q" + extra_opts,
                                   ["quiet"] + 
                                   list(extra_long_opts))
    except getopt.GetoptError, err:
        print "**", str(err), "**"
        sys.exit(2)
    
    for o, a in opts:
        if o in ("-q", "--quiet"):
            OPTIONS.quiet = True
        else:
            if extra_option_handler is None or not extra_option_handler(o, a):
                assert False, "unknown option \"%s\"" % (o,)
    return args