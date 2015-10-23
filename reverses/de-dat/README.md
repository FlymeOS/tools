Android 5.0 (Lollipop) compiled roms (aosp,cm,stock) are not compressed anymore the way they
used to be on previous android versions. On previous versions all content inside /system folder
that has to be extracted within our device was either uncompressed (simple /system folder inside our flashable zip)
or compressed in a system.img file, which it is a ext4 compressed file; both of these,
anyway, were readable and we could see all system files (app,framework, etc).

Android 5.0 zip structure:
* META-INF (folder containing scripts)
* system.new.dat (compressed /system partition)
* system.patch.dat
* system.transfer.list (see explanation below)

# sdat2img
Convert sparse Android data image (.dat) to filesystem ext4 image (.img)

# img2sdat
img2sdat binary for Android

## Requirements
This binary requires Python 3.x installed on your system.

It currently supports Windows x86/x64, Linux x86/x64 & arm/arm64 architectures.



## Usage
```
sdat2img.py <transfer_list> <system_new_file> <system_ext4>
```
- `transfer_list` = input, system.transfer.list from rom zip
- `system_new_file` = input, system.new.dat from rom zip
- `system_ext4` = output ext4 raw image file



## Example
This is a simple example on a Linux system: 
```
~$ ./sdat2img.py system.transfer.list system.new.dat system.img
```


## Github
<https://github.com/xpirt>



## Info
For more information about this binary, visit <http://forum.xda-developers.com/android/software-hacking/how-to-conver-lollipop-dat-files-to-t2978952>.
