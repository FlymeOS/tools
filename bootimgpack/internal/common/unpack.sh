#!/bin/bash

# unpack_boot.sh
# Unpack the standard boot.img or recovery.img of Android
#
# @author: duanqz@gmail.com
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
	UNPACKBOOTIMG=$TOOL_DIR/unpackbootimg
	UNPACKBOOTIMGPL=$TOOL_DIR/unpack-bootimg.pl
	cd $old_pwd
}

function unpack_bootimg()
{
	local old_pwd=`pwd`
	mkdir -p $OUTPUT
	cp $BOOTIMG $OUTPUT/boot.img
	cd $OUTPUT

	# Open the macro variable to filter " *** glibc detected *** " error
	local tmp_stderr=$LIBC_FATAL_STDERR_
	export LIBC_FATAL_STDERR_=1

	# Unpack boot image
	$UNPACKBOOTIMG -i boot.img -o ./
	[ $? != 0 ] && exit 1

	$UNPACKBOOTIMGPL boot.img
	[ $? != 0 ] && exit 1

	mv boot.img-ramdisk   RAMDISK
	mv boot.img-zImage    kernel
	mv boot.img-cmdline   cmdline
	mv boot.img-base      base
	mv boot.img-pagesize  pagesize
	rm -rf boot.img*

	export LIBC_FATAL_STDERR_=$tmp_stderr

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
