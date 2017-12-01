#!/usr/bin/python

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

__author__ = 'duanqz@gmail.com'


from os import sys

from common import Options, Log
from zipformatter import ZipFormatter


# Global
TAG="reverse-oatnormalize"
OPTIONS = Options()


if __name__ == "__main__":

    Log.DEBUG = True

    OPTIONS.handle(sys.argv)

    ZipFormatter.create(OPTIONS).format()

