#!/bin/bash

# pack_boot_mtk.sh
# Pack the directory to boot.img

BOOTDIR=$1
OUTPUT=$2

function usage()
{
	echo "Usage pack_boot_mtk.sh BOOTDIR [OUTPUT]"
	echo "   BOOTDIR: the directory containing boot files to be pack"
	echo "   OUTPUT:  the output directory. if not present, the out.img will be used"
}

function init_tools()
{
	local old_pwd=`pwd`
	TOOL_DIR=`cd $(dirname $0); pwd`
	MKMTKBOOTIMG=$TOOL_DIR/mkmtkbootimg
	MKIMAGE=$TOOL_DIR/mkimage

	local common_dir=`cd $TOOL_DIR; cd ../common; pwd`
	MKBOOTFS=$common_dir/mkbootfs
	MINIGZIP=$common_dir/minigzip
	MKBOOTIMG=$common_dir/mkbootimg

	cd $old_pwd
}

function pack_bootimg()
{
	local old_pwd=`pwd`

	cd $BOOTDIR
	$MKBOOTFS ./RAMDISK | $MINIGZIP > ramdisk.img
	[ $? != 0 ] && exit 1

	if [ -f ./RAMDISK/etc/recovery.fstab ];then
		$MKIMAGE ./ramdisk.img  RECOVERY > ramdisk_root.img
		[ $? != 0 ] && exit 1
	else
		$MKIMAGE ./ramdisk.img  ROOTFS > ramdisk_root.img
		[ $? != 0 ] && exit 1
	fi

	$MKMTKBOOTIMG --kernel ./kernel --ramdisk ./ramdisk_root.img  --output pack.img
	[ $? != 0 ] && exit 1

	rm ramdisk.img ramdisk_root.img
	cd $old_pwd
	mv $BOOTDIR/pack.img $OUTPUT
}

# Check parameters
[ $# -eq 0 ] && usage && exit 1;
[ -z $2 ] && OUTPUT=out.img;

init_tools;
pack_bootimg;
