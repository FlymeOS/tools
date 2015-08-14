#!/usr/bin/python

__author__ = 'duanqz@gmail.com'


import os
import sys

import shutil
import unittest
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from internal import bootimg


class TestUnpack(unittest.TestCase):

    def setUp(self):
        self.dir = path.dirname(path.abspath(__file__))

    def test_unpack_common(self):
        boot_img = path.join(self.dir, "common-boot.img")
        Utils.assert_type_equals(boot_img, "QCOM")

    def test_unpack_common_v1(self):
        boot_img = path.join(self.dir, "common-v1-boot.img")
        Utils.assert_type_equals(boot_img, "QCOM")

    def test_unpack_qcom(self):
        boot_img = path.join(self.dir, "qcom-boot.img")
        Utils.assert_type_equals(boot_img, "QCOM")

    def test_unpack_mtk(self):
        boot_img = path.join(self.dir, "mtk-boot.img")
        Utils.assert_type_equals(boot_img, "MTK")

    def test_unpack_sony(self):
        boot_img = path.join(self.dir, "sony-boot.img")
        Utils.assert_type_equals(boot_img, "SONY")


class TestPack(unittest.TestCase):

    def setUp(self):
        self.dir = path.dirname(path.abspath(__file__))

    def test_pack_common(self):
        boot_dir = path.join(self.dir, "common-boot")
        Utils.asset_pack_succ(boot_dir)

    def test_pack_common_v1(self):
        boot_dir = path.join(self.dir, "common-v1-boot")
        Utils.asset_pack_succ(boot_dir)

    def test_pack_mtk(self):
        boot_dir = path.join(self.dir, "mtk-boot")
        Utils.asset_pack_succ(boot_dir)

    def test_pack_qcom(self):
        boot_dir = path.join(self.dir, "qcom-boot")
        Utils.asset_pack_succ(boot_dir)

    def test_pack_sony(self):
        boot_dir = path.join(self.dir, "sony-boot")
        Utils.asset_pack_succ(boot_dir)


class TestToolKit(unittest.TestCase):

    def test_existing(self):
        assert path.exists(bootimg.Toolkit.TOOLKIT_XML)

    def test_content_valid(self):
        all_tools = {}
        sequence = {}

        tree = ET.parse(bootimg.Toolkit.TOOLKIT_XML)
        for tool in tree.findall("tool"):
            seq = tool.attrib["seq"]
            boot_type = tool.attrib["type"]
            description = tool.attrib["description"]

            unpack_tool = tool.find("unpack").text
            pack_tool = tool.find("pack").text
            all_tools[boot_type] =  { "UNPACK" : path.join(bootimg.Toolkit.TOOLS_ROOT, unpack_tool),
                                      "PACK"   : path.join(bootimg.Toolkit.TOOLS_ROOT, pack_tool) }
            sequence[seq] = (boot_type, description)

        assert len(sequence) == 5

        assert "MTK" in all_tools
        assert "SONY" in all_tools
        assert "COMMON" in all_tools
        assert "COMMON-V1" in all_tools
        assert "QCOM" in all_tools


class Utils:

    def __init__(self):
        pass

    @staticmethod
    def assert_type_equals(boot_img, boot_type):

        bootimg.unpack(boot_img, "OUT/")

        f = open("OUT/type.config", "r")

        f_boot_type = f.read()

        f.close()
        shutil.rmtree("OUT/")

        assert boot_type == f_boot_type

    @staticmethod
    def asset_pack_succ(boot_dir):
        bootimg.pack(boot_dir, "out.img")

        assert path.exists("out.img")

        os.remove("out.img")


if __name__ == '__main__':
    unittest.main()