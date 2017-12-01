#!/usr/bin/python

'''
Workflow
'''


import os, sys
import subprocess
import shutil
import re


try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpdoc import help
from formatters.log import Log, Paint

TAG="workflow"

class Phase:
    """ The model of phase in workflow
    """

    def __init__(self, tag):
        """ Initialize the Phase model.
            The input tag is <phase> in workflow
        """

        self.tag = tag
        self.action = tag.get('action')
        self.next = None
        self.cmds = []

        for child in tag.getchildren():
            if  child.tag == "state":
                self.state = child.text
            elif child.tag == "prev":
                self.prev = child.get('action')
            elif child.tag == "next":
                self.next = child.get('action')
            elif child.tag == "sequence":
                for cmd in child.getchildren():
                    self.cmds.append(cmd.text)

    def equals(self, otherPhase):
        return self.action == otherPhase.action

    def updateState(self):
        """ Publish the state to XML
        """

        self.tag.find('state').text = self.state

# End of class Phase


class Workflow:

    def __init__(self, xmlPath):
        self.xmlPath = xmlPath
        self.xmlDom = ET.parse(xmlPath)

        self.phases = {}
        for tag in self.xmlDom.findall('phase'):
            phase = Phase(tag)
            self.phases[phase.action] = phase

    def getAllActions(self):
        return self.phases.keys()

    def getPhase(self, action):
        try:
            return self.phases[action]
        except KeyError:
            return None

    def publish(self):
        """ Publish the workflow to XML
        """

        self.xmlDom.write(self.xmlPath)



class State:
    INACTIVE = "inactive"
    ACTIVING = "activing"
    ACTIVED = "actived"


class StateMachine:

    def __init__(self, workflow):
        self.workflow = workflow

    def start(self):
        self.transit(self.workflow.getPhase("init"))

    def transit(self, phase):
        if   phase.state == State.INACTIVE:
            self.activate(phase)
        elif phase.state == State.ACTIVING:
            self.reActivate(phase)
        elif phase.state == State.ACTIVED:
            if phase.next == None: return
            self.transit(self.workflow.getPhase(phase.next))


    def activate(self, phase):
        """ Activate phase
        """

        phase.state = State.ACTIVING

        if self.doAction(phase.action):
            phase.state = State.ACTIVED
            self.publish(phase)
            self.transit(phase)
        else:
            self.publish(phase)


    def reActivate(self, phase):
        """ Re-activate phase
        """

        self.activate(phase)

    def publish(self, phase):
        """ Publish the phase state to XML
        """

        phase.updateState()
        self.workflow.publish()


    def doAction(self, action):
        """ Return True: do action succeed. Otherwise return false
        """

        raise Exception("Should be implemented by subclass")

# End of class StateMachine


class CoronStateMachine(StateMachine):
    """ Coron State Machine
    """

    XML = os.path.join(os.curdir, "workflow.xml")


    def __init__(self):
        self.createXMLIfNotExist()
        StateMachine.__init__(self, Workflow(CoronStateMachine.XML))

    def createXMLIfNotExist(self):
        if os.path.exists(CoronStateMachine.XML): return

        source = os.path.join(os.path.dirname(os.path.realpath(__file__)), "workflow.xml")
        shutil.copy(source, CoronStateMachine.XML)

    def doAction(self, action):
        action = " ".join(action)
        print Paint.blue(">>> %s" % action)

        status = 0

        phase = self.workflow.getPhase(action)
        if phase != None:
            for cmd in phase.cmds:
                status = Shell.run(cmd)
                if status != 0: break
        else:
            cmd = "make %s" % action
            status = Shell.run(cmd)

        help.show(status, action)

        if status == 0:
            print Paint.blue("<<< %s succeed" % action)
            return True
        else:
            print Paint.red("<<< %s failed" % action)
            return False


# End of CoronStateMachine


class Shell:
    """ Subprocess to run shell command
    """

    @staticmethod
    def run(cmd):
        """ Run command in shell.
            Set `isMakeCommand` to True if command is a `make` command
        """

        subp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        output = None
        while True:
            buff = subp.stdout.readline().strip('\n')
            print buff
            if buff == '' and subp.poll() != None:
                break

            output = buff

        Log.d(TAG, "Shell.run() %s return %s" %(cmd, subp.returncode))
        status = Shell.parseHelpStatus(subp.returncode, "%s" %output)

        return status


    @staticmethod
    def parseHelpStatus(status, output):
        """ Parse the error number in `make` command output
        """

        # GNU make exits with a status of zero if all makefiles were successfully parsed and no targets that were built failed.
        # A status of one will be returned if the -q flag was used and make  determines that a target needs to be rebuilt.
        # A status of two will be returned if any errors were encountered.
        errRegex = re.compile("^make: .* Error (?P<errNo>(?!.*(ignored)).*)")
        match = errRegex.search(output)
        if match != None:
            Log.d(TAG, "Shell.parseHelpStatus() Target in GNU make")
            status = int(match.group("errNo"))

        Log.d(TAG, "Shell.parseHelpStatus() Output is %s" % output)
        Log.d(TAG, "Shell.parseHelpStatus() Status is %d" % status)

        return status


    @staticmethod
    def isMakeCommand(cmd):
        """ Whether is a make command or not
        """

        makeRegex = re.compile("^make")
        return makeRegex.match(cmd) != None

# End of class Shell



if __name__ == "__main__":
    CoronStateMachine().start()






