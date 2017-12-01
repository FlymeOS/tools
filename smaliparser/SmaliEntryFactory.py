'''
Created on Feb 27, 2014

@author: tangliuxiang
'''

import SmaliEntry
import SmaliMethod
import SmaliField
import SmaliClass

def newSmaliEntry(type, content, clsName = None, preContent = None):
    #return SmaliEntry.SmaliEntry(type, content, preContent)
    
    if type is None:
        return None 
    elif type == SmaliEntry.METHOD:
        return SmaliMethod.SmaliMethod(type, content, clsName, preContent)
    elif type == SmaliEntry.FIELD:
        return SmaliField.SmaliField(type, content, clsName, preContent)
#    elif type is SmaliEntry.ANNOTATION:
    elif type is SmaliEntry.CLASS:
        return SmaliClass.SmaliClass(type, content, clsName, preContent)
#    elif type is SmaliEntry.SOURCE:
#    elif type is SmaliEntry.SUPER:
#    elif type is SmaliEntry.IMPLEMENTS:
    else:
        return SmaliEntry.SmaliEntry(type, content, clsName, preContent)