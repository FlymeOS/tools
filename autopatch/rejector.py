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

"""
rejector.

"""

__author__ = 'duanqz@gmail.com'


import os
import fnmatch
from config import Config


class Collector:
    """ Collect the conflicts
    """

    CONFILCT_START = "<<<<<<<"
    CONFLICT_MID   = "======="
    CONFILCT_END   = ">>>>>>>"

    def __init__(self, target):
        self.mTarget = target
        self.mConflictNum = 0

    def get_conflict_num(self):
        return self.mConflictNum

    def collect_conflict(self):
        """ Check whether conflict happen or not in the target
        """

        self.mConflictNum = 0

        top = 0

        # delLinesNumbers record the lines of conflicts
        del_line_numbers = []
        need_to_del = False

        target_file = open(self.mTarget, "r+")

        line_num = 0
        lines = target_file.readlines()

        for line in lines:
            size = self.mConflictNum
            if line.startswith(Collector.CONFILCT_START):

                top += 1

                # Modify the conflict in the original
                lines[line_num] = "%s #Conflict %d\n" % (line.rstrip(), size)
                self.mConflictNum += 1

                del_line_numbers.append(line_num)

            elif line.startswith(Collector.CONFILCT_END):

                # Modify the conflict in the original
                lines[line_num] = "%s #Conflict %d\n" % (line.rstrip(), size-top)

                del_line_numbers.append(line_num)
                need_to_del = False

                if top == 0:
                    break

                top -= 1

            else:
                if top > 0:

                    if line.startswith(Collector.CONFLICT_MID):
                        need_to_del = True

                    if need_to_del:
                        del_line_numbers.append(line_num)

            line_num += 1

        # Create a reject file if conflict happen
        if self.mConflictNum > 0:
            rej_file_path = create_reject_file(self.mTarget)
            f = open(rej_file_path, "wb")
            f.writelines(lines)
            f.close()

        # Remove conflict blocks, and write back target.
        for line_num in del_line_numbers[::-1]:
            del lines[line_num]

        target_file.seek(0)
        target_file.truncate()
        target_file.writelines(lines)
        target_file.close()

        return self

    # Deprecated
    def resolve_conflict(self):

        f = open(self.mTarget, "r+")

        top = 0
        line_num = 0

        del_line_numbers = []
        need_to_del = True

        lines = f.readlines()
        for line in lines:
            if line.startswith(Collector.CONFILCT_START):
                top += 1
                del_line_numbers.append(line_num)

            elif line.startswith(Collector.CONFILCT_END):
                top -= 1
                del_line_numbers.append(line_num)
                need_to_del = True

                if top < 0: break;
            else:
                if top > 0:
                    if need_to_del:
                        del_line_numbers.append(line_num)

                    if line.startswith(Collector.CONFLICT_MID):
                        need_to_del = False

            line_num += 1

        for line_num in del_line_numbers[::-1]:
            del lines[line_num]

        f.seek(0)
        f.truncate()
        f.writelines(lines)
        f.close()


def create_reject_file(target):
    """ create a reject file
    :param target: the target might have conflicts
    :return: reject file path
    """
    rel_target = os.path.relpath(target, Config.PRJ_ROOT)
    rej_file_path = os.path.join(Config.REJ_ROOT, rel_target)
    d = os.path.dirname(rej_file_path)
    if not os.path.exists(d):
        os.makedirs(d)

    return rej_file_path


def process_conflicts(target):
    """ process conflicts of the target
    :param target: the target might have conflicts
    :return: number of conflicts
    """

    return Collector(target).collect_conflict().get_conflict_num()