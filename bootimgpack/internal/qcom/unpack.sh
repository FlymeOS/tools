#!/bin/bash

# unpack_boot.sh
# Unpack the standard boot.img or recovery.img of Android
#
# @author: duanqizhi(duanqz@gmail.com)
#

BOOTIMG=$1
OUTPUT=$2

function usage()
{
	echo "Usage unpack_boot.sh BOOTIMG [OUTPUT]"
	echo "   BOOTIMG: the file path of the boot.img to be unpack"
	echo "   OUTPUT:  the output directory. if not present, the OUT/ directory will be used"
}

function init_tools()
{
	local old_pwd=`pwd`
	TOOL_DIR=`cd $(dirname $0); pwd`
	MKBOOT=$TOOL_DIR/mkboot
	cd $old_pwd
}

function unpack_bootimg()
{
	# Unpack boot image
	$MKBOOT $BOOTIMG $OUTPUT
	[ $? != 0 ] && exit 1
}

function check_result()
{
	#[ ! -e $OUTPUT/dt.img ] && exit 1
	[ ! -e $OUTPUT/kernel ] && exit 1
	[ ! -e $OUTPUT/RAMDISK/init.rc ] && exit 1
}


### Start Script ###

# Check parameters
[ $# -eq 0 ] && usage && exit 1;
[ -z $2 ] && OUTPUT="OUT/";

init_tools;
unpack_bootimg;
check_result;
exit 0