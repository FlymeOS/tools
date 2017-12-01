#!/bin/bash

#####################################################
#
#  use to decode all of the apk and jar in the system
#  note: unzip the zip first
#
#####################################################

CUR_DIR=$(dirname $0)
APKTOOL=$CUR_DIR/apktool
THREAD_NUM=4

IN_DIR=""
OUT_DIR=""

# echo the usage of decode_all
function usage
{
	echo "usage: decode_all [OPTIONS] SYSTEM_DIR [OUT_DIR]"
	echo "       OPTIONS: -j[0-9]* jobs number"
	echo "       SYSTEM_DIR: the apk/jar's directory which will be decoded"
	echo "       OUT_DIR: output directory for decoded, current directory is default."
	echo "eg: decode_all system/framework ."
}

# setup the parameters
function setParam
{
    if [ $# -eq 0 ]
    then
	    usage
        exit 1
    fi

    set -- `getopt "j:" "$@"`

    while :
    do
        case "$1" in
            -j) shift; THREAD_NUM=$1 ;;
            --) break ;;
        esac
        shift
    done
    shift

    IN_DIR=$1

    if [ $# -eq 1 ]
    then
	    OUT_DIR="."
    else
	    OUT_DIR=$2
	    if [ ! -d $OUT_DIR ]
        then
	        mkdir -p $OUT_DIR
        fi
    fi
}

# init multi build jobs through fifo
function initMultiJobs
{
    tmp_fifofile="/tmp/$$.fifo"

    mkfifo "$tmp_fifofile"
    exec 6<>"$tmp_fifofile"
    rm $tmp_fifofile

    for ((i=0;i<$THREAD_NUM;i++));do
        echo
    done >&6
}

# decode all apks
function decodeApks
{
    for line in `find $IN_DIR -name "*.apk"`
    do
        read -u6
        {
            echo ">>> begin decode $line"
    	    out_file=${line:${#IN_DIR}:${#line}}
    	    let "len=${#out_file}-4"
    	    out_file=${out_file:0:$len}
    	    $APKTOOL d $line -o $OUT_DIR"/"$out_file
            echo "<<< decode $line done"
	        echo >&6
        } &
    done
}

# decode all jars
function decodeJars
{
    for line in `find $IN_DIR -name "*.jar"`
    do
        read -u6
        {
            echo ">>> begin decode $line"
    	    out_file=${line:${#IN_DIR}:${#line}}
    	    let "len=${#out_file}"
            #out_file=${line:${#file_path}:${#line}}
    	    out_file=${out_file:0:$len}
            $APKTOOL d $line -o $OUT_DIR"/"$out_file".out"
            echo "<<< decode $line done"
            echo >&6
        } &
    done
}

# wait for the end
function waitToEnd
{
    # wait it for done
    for ((i=0;i<$THREAD_NUM;i++));do
        read -u6
    done
}

function main
{
    setParam $@
    initMultiJobs
    decodeApks
    decodeJars
    waitToEnd
}

main $@
