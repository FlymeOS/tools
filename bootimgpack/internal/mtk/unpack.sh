#!/bin/bash

# unpack_boot_mtk.sh
# Unpack the boot.img or recovery.img of MTK format
#
# @author: duanqz@gmail.com
#

BOOTIMG=$1
OUTPUT=$2

function usage()
{
	echo "Usage unpack_boot_mtk.sh BOOTIMG [OUTPUT]"
	echo "   BOOTIMG: the file path of the boot.img to be unpack"
	echo "   OUTPUT:  the output directory. if not present, the OUT/ directory will be used"
}

function init_tools()
{
	local old_pwd=`pwd`
	TOOL_DIR=`cd $(dirname $0); pwd`
	UNPACKBOOTIMG=$TOOL_DIR/unpack-mtk-bootimg.pl
	cd $old_pwd
}

function unpack_bootimg()
{
	local old_pwd=`pwd`
	mkdir -p $OUTPUT
	cp $BOOTIMG $OUTPUT/boot.img
	cd $OUTPUT

	# Unpack boot image
	$UNPACKBOOTIMG boot.img
	[ $? != 0 ] && exit 1

	mv boot.img-ramdisk  RAMDISK
	mv boot.img-kernel   kernel
	rm -rf boot.img*

	cd $old_pwd
}

function check_result()
{
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
