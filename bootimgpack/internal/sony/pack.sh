#!/bin/bash
#**************************************************#
# Make sony's boot.img
# Xperia
#**************************************************#

BOOTDIR=$1
OUTPUT=$2

function usage()
{
	echo "Usage pack_boot_sony.sh BOOTDIR [OUTPUT]"
	echo "   BOOTDIR: the directory containing boot files to be pack"
	echo "   OUTPUT:  the output directory. if not present, the out.img will be used"
}

function init_tools()
{
	local old_pwd=`pwd`
	TOOL_DIR=`cd $(dirname $0); pwd`
	TOOL_MKELF=$TOOL_DIR/mkelf.py
	cd $old_pwd
}

function pack_bootimg()
{
	local old_pwd=`pwd`
	cd $BOOTDIR

	# Files
	ADDR_TAG='addr'

	ls kernel 2>&1 > /dev/null
	if [ "$?" != "0" ];then
		echo ">>> ERROR, kernel doesn't exist!"
		exit 1
	fi

	FILE_KERNEL="kernel"
	FILE_KERNEL_ADDR=$(cat "$ADDR_TAG"_"$FILE_KERNEL")

	DIR_RAMDISK="RAMDISK"
	FILE_RAMDISK="ramdisk.img"
	FILE_RAMDISK_ADDR=$(cat "$ADDR_TAG"_"ramdisk.img")

	FILE_RPM="RPM.bin"
	FILE_RPM_ADDR=$(cat "$ADDR_TAG"_"$FILE_RPM")

	OTHER_PARAM=""
	for file in `ls *-[0-9]*`
	do
		addrValue=$(cat "$ADDR_TAG"_"$file")
		OTHER_PARAM="$OTHER_PARAM $file\@$addrValue"
	done

	# Generate ramdisk file
	cd $DIR_RAMDISK && find . | cpio -o -H newc | gzip > ../$FILE_RAMDISK && cd ..

	# Make kernel-updated.elf
	python $TOOL_MKELF -o pack.img \
	       $FILE_KERNEL@$FILE_KERNEL_ADDR \
	       $FILE_RAMDISK@$FILE_RAMDISK_ADDR,ramdisk \
	       $FILE_RPM@$FILE_RPM_ADDR,rpm \
	       $OTHER_PARAM
	[ $? != 0 ] && exit 1

	# Clear temporary files
	rm $FILE_RAMDISK
	cd $old_pwd
	mv $BOOTDIR/pack.img $OUTPUT
}

# Check parameters
[ $# -eq 0 ] && usage && exit 1;
[ -z $2 ] && OUTPUT=out.img;

init_tools;
pack_bootimg;
