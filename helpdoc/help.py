#!/usr/bin/python
# -*- coding: utf-8 -*-

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

"""
Type `help name' to find out more about the `name'.

   e.g.  help "config"
   e.g.  help "newproject"
   e.g.  help "patchall"

"""


import os
import sys
import types
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from formatters.log import Paint

reload(sys)
sys.setdefaultencoding( "utf-8" )

class Item:
    """ Help Item Model
    """

    name = None
    code = None
    detail = None
    solution = None

    def __init__(self, code, name):
        self.code = code
        self.name = name


class HelpModel:
    """ Help Model
    """

    CODE_TO_NAME = {}
    NAME_TO_CODE = {}
    ITEM_TAGS = {}

    def __init__(self):

        self.help_xml = HelpModel.retrieve_xml_by_locale()
        self.help_xml_dir = os.path.dirname(self.help_xml)

        xml_dom = ET.parse(self.help_xml)

        for tag in xml_dom.findall('item'):
            name = tag.get('name')
            code = int(tag.get('code'))

            self.CODE_TO_NAME[code] = name
            self.NAME_TO_CODE[name] = code
            self.ITEM_TAGS[code] = tag

    def get_help_xml_dir(self):
        return self.help_xml_dir

    @staticmethod
    def retrieve_xml_by_locale():
        d = os.path.dirname(os.path.realpath(__file__))
        if "zh" in os.popen('echo $LANG').read():
            f = open(os.path.join(d, "locale_cn"), "r")
        else:
            f = open(os.path.join(d, "locale"), "r")
        locale = f.read().rstrip()
        f.close()

        return os.path.join(d, locale, "help.xml")

    def get(self, key):
        """ Get the help item by either code or name.
            See the Help Item Model @Item
        """

        if key is None:
            return None
        elif type(key) is types.IntType:
            code = key
            name = self.CODE_TO_NAME.get(code)
        elif key.isdigit():
            code = int(key)
            name = self.CODE_TO_NAME.get(code)
        else:
            name = key
            code = self.NAME_TO_CODE.get(name)

        tag = self.ITEM_TAGS.get(code)
        if tag is None:
            return None

        item = Item(code, name)
        for child in tag.getchildren():
            if child.tag == "solution":
                item.solution = child.text
            elif child.tag == "detail":
                item.detail = child.text

        return item


class HelpModelOverride(HelpModel):
    """ Derived class of Help.
        Override items if defined in Help
    """

    def __init__(self, xml):
        HelpModel.__init__(self)

        xml_dom = ET.parse(xml)

        for tag in xml_dom.findall('item'):
            name = tag.get('name')
            code = int(tag.get('code'))

            self.CODE_TO_NAME[code] = name
            self.NAME_TO_CODE[name] = code
            self.ITEM_TAGS[code] = tag

# End of class HelpOverride


def __get_help_xml(category):
    help_xml = os.path.join(os.path.dirname(HelpModel.retrieve_xml_by_locale()), "help_%s.xml" % category)
    if os.path.exists(help_xml):
        return help_xml
    else:
        return None


def __create(category=None):
    """ Create a help model
    :param category: help category, like config, newproject etc.
    :return: HelpModel
    """

    help_xml = __get_help_xml(category)
    if help_xml is not None:
        return HelpModelOverride(help_xml)
    else:
        return HelpModel()


def __get_item(key, category):
    """
    Get item by key in category
    :param key: code or name of item
    :param category: help category, like config, newproject
    :return: Item
    """

    help_model = __create(category)
    item = help_model.get(key)

    if item is None and category is None:
        all_help_xml = os.listdir(help_model.get_help_xml_dir())
        for help_xml in all_help_xml:
            if help_xml.startswith("help_") and help_xml.endswith(".xml"):
                category = help_xml[5:-4]
                help_model = __create(category)
                item = help_model.get(key)

    return item


def show(key, category=None):
    """ Show the help item
    :param key: name or code of the help item
    :param category: help category, like config, newproject
    """

    item = __get_item(key, category)
    if item is None:
        return

    if item.detail is not None:
        print "%s: %s" % (Paint.bold(item.name), item.detail.replace("\t", "").strip())

    if item.solution is not None:
        print Paint.green(item.solution.replace("\t", "").lstrip())

    print ""


def show_all():
    """ Show all the help items
    """

    help_model = __create()
    for code in sorted(help_model.CODE_TO_NAME.keys()):
        if code >= 220:
            continue

        show(code)


def main(argv):
    """ Parse input arguments.
    @:param argv[1]: name or code of the help item
    @:param argv[2]: category
    """

    key = None
    category = None
    size = len(argv)

    if size == 1:
        show_all()

    if size > 1:
        key = argv[1]

    if size > 2:
        category = argv[2]

    show(key, category)


def usage():
    help_model = __create()

    print "                                                                 "
    print Paint.bold(help_model.get("help_usage").detail.strip())
    print "                                                                 "
    print help_model.get("help_license").detail.strip()
    print "                                                                 "
    print help_model.get("help_cmds").detail.strip()

    # help
    print Paint.bold("* flyme help [ACTION]")
    print "                                                                 "
    print " ", help_model.get("help").detail.strip()
    print "                                                                 "

    # action
    print Paint.bold("* flyme [ACTION]")
    print "                                                                 "

    actions = ("config", "newproject", "patchall", "fullota", "upgrade", "porting", "clean", "cleanall")
    for action in actions:
        print Paint.bold(action).rjust(20), "\t", help_model.get(action).detail.strip()
        print "                                                             "

    # fire
    #print Paint.bold("* flyme fire")
    #print " ", help_model.get("fire").detail.strip()
    print ""

def readme():

    help_model = __create()

    f = open("README.md", "w")
    print >>f, "                                                                 "
    print >>f, "### ", help_model.get("help_usage").detail.strip()
    print >>f, "                                                                 "
    print >>f, help_model.get("help_license").detail.strip()
    print >>f, "                                                                 "
    print >>f, help_model.get("help_cmds").detail.strip()
    print >>f, "                                                                 "
    print >>f, "    * flyme help [ACTION]"
    print >>f, "                                                                 "
    print >>f, "     ", help_model.get("help").detail.strip()
    print >>f, "                                                                 "

    # action
    print >>f, "    * flyme ACTION"
    print >>f, "                                                                 "

    actions = ("config", "newproject", "patchall", "fullota", "upgrade", "porting", "clean", "cleanall")
    for action in actions:
        print >>f, "      ", action, "\t", help_model.get(action).detail.strip()
        print >>f, "                                                                 "

    # fire
    #print >>f, "    * flyme fire"
    #print >>f, "     ", help_model.get("fire").detail.strip()
    #print >>f, "                                                                 "

    print >>f, "### ", help_model.get("err_code").detail.strip()
    print >>f, "                                                                 "
    for code in sorted(help_model.CODE_TO_NAME.keys()):
        if code < 150 or code > 220:
            continue

        item = help_model.get(code)
        print >>f, "***%s(%d)***" % (item.name, item.code)
        print >>f, "                                                              "
        if item.solution is not None:
            print >>f, "%s" % item.solution
            print >>f, "                                                          "

    f.close()

if __name__ == "__main__":
    readme()

