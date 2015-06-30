#!/bin/bash
#
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

ROOT=$1
SYS_TRANS_LIST=$ROOT/system.transfer.list
SYS_NEW_DAT=$ROOT/system.new.dat
SYS_EXT4_IMG=$ROOT/system.img
SYS_DIR=$ROOT/system

function usage()
{
    echo "Usage: $0 ROOT_DIRECTORY_OF_UNZIPED_OTA_PACKAGE"
}


function convert_dat_to_img()
{

    [ ! -e $SYS_TRANS_LIST ] && return
    [ ! -e $SYS_NEW_DAT ] && return

    $SDAT2IMG $SYS_TRANS_LIST $SYS_NEW_DAT $SYS_EXT4_IMG
}


function unpack_sys_ext4_img()
{
    [ ! -e $SYS_EXT4_IMG ] && return

    local name=`whoami`
    local outdir=`mktemp -d /tmp/dedat.mount.XXXXX`
    sudo mount -t ext4 -o loop $SYS_EXT4_IMG $outdir
    sudo cp -r $outdir $SYS_DIR
    sudo chown -R $name:$name $SYS_DIR
    sudo umount $outdir
    rm -rf $outdir

    echo "DEDAT ===> $SYS_DIR"
}

prog="$0"
while [ -h "${prog}" ]; do
    newProg=`/bin/ls -ld "${prog}"`

    newProg=`expr "${newProg}" : ".* -> \(.*\)$"`
    if expr "x${newProg}" : 'x/' >/dev/null; then
        prog="${newProg}"
    else
        progdir=`dirname "${prog}"`
        prog="${progdir}/${newProg}"
    fi
done
oldwd=`pwd`
progdir=`dirname "${prog}"`
cd "${progdir}"
progdir=`pwd`
prog="${progdir}"/`basename "${prog}"`
cd "${oldwd}"

SDAT2IMG=sdat2img.py
if [ ! -r "$progdir/$SDAT2IMG" ]
then
    echo `basename "$prog"`": can't find $SDAT2IMG"
    exit 1
fi

if [ "$OSTYPE" = "cygwin" ] ; then
	SDAT2IMG=`cygpath -w  "$progdir/$SDAT2IMG"`
else
	SDAT2IMG="$progdir/$SDAT2IMG"
fi

[ ! -d "$ROOT" ] && usage && exit 1

convert_dat_to_img
unpack_sys_ext4_img

