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
