#!/bin/bash

# pack_boot.sh
# Pack the directory to boot.img

BOOTDIR=$1
OUTPUT=$2

function usage()
{
	echo "Usage pack_boot.sh BOOTDIR [OUTPUT]"
	echo "   BOOTDIR: the directory containing boot files to be pack"
	echo "   OUTPUT:  the output directory. if not present, the out.img will be used"
}

function init_tools()
{
	local old_pwd=`pwd`
	TOOL_DIR=`cd $(dirname $0); pwd`
	MKBOOTFS=$TOOL_DIR/mkbootfs
	MINIGZIP=$TOOL_DIR/minigzip
	MKBOOTIMG=$TOOL_DIR/mkbootimg
	cd $old_pwd
}

function pack_bootimg()
{
	local old_pwd=`pwd`

	cd $BOOTDIR
	$MKBOOTFS ./RAMDISK | $MINIGZIP > ramdisk.img
	[ $? != 0 ] && exit 1

	BOOTBASE=$(cat ./base)
	BOOTCMDLINE=$(cat ./cmdline)
	BOOTPAGESIZE=$(cat ./pagesize)
	$MKBOOTIMG --kernel ./kernel --cmdline "$BOOTCMDLINE" --pagesize "$BOOTPAGESIZE"  --base "$BOOTBASE" --ramdisk ./ramdisk.img --output pack.img
	[ $? != 0 ] && exit 1

	rm ramdisk.img
	cd $old_pwd
	mv $BOOTDIR/pack.img $OUTPUT
}

# Check parameters
[ $# -eq 0 ] && usage && exit 1;
[ -z $2 ] && OUTPUT=out.img;

init_tools;
pack_bootimg;
