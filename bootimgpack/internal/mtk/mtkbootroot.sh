#/bin/sh
ramdisk="$1-ramdisk"
bootheader="$1-bootheader"
bootkernel="$1-kernel"
cpio="$1-ramdisk.cpio.gz"

defaultprop="$ramdisk/default.prop"
kernelnotroot="ro.secure=1"
kernelroot="ro.secure=0"
startline="5"
rpath="`dirname $0`"

if [ $# -lt "1" ];then
	echo "usage:$0 bootimage"
	exit 0
fi
$rpath/unpack-mtk-bootimg.pl $1
if [ -f $defaultprop ];then
	sed -i "/$kernelnotroot/d" $defaultprop
	sed -i "/$kernelroot/d" $defaultprop
	echo "$kernelroot" >> $defaultprop
fi

$rpath/mkbootfs $ramdisk | minigzip > .ramdisk.ori
$rpath/mkimage .ramdisk.ori ROOTFS > .ramdisk.img
rm .ramdisk.ori
echo "generate the root bootimage to $1.boot"
cat $bootheader $bootkernel .ramdisk.img > $1.boot
rm $bootheader $bootkernel .ramdisk.img $cpio
rm -rf $ramdisk
