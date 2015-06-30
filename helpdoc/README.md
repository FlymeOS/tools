### Introduction
                                                                 
***Coron - an open source project for Android ROM porting***
                                                                 
Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)  
                                                                 
***COMMANDs*** are:                                              
                                                                 
    * coron help [NAME]
                                                                 
      Type `help name' to find out more about the `name'.
                                                                 
    * coron ACTION
      Run the action separately.
      ACTION 	Description
                                                                 
       config 	Genearate the configuration for a new device.
		A Makefile containing all the configurations will be generated.
                                                                 
       newproject 	Generate the new project for a new device.
		Only used when setup your device project.
                                                                 
       patchall 	Patch all the changes.
		Incorpate all the changes from BOSP to AOSP into VENDOR.
		 BOSP  : Code of Board Open Source Project
		 AOSP  : Code Android Open Source Project
		 VENDOR: Code pulled out from the device

		The codes of VENDOR are located in the root directory of your device.
		The codes of AOSP and BOSP are located in the autopatch directory of your device.
                                                                 
       fullota 	Fully make out the ota package.
		An OTA package will be generated, you could flash it into your device.
                                                                 
       upgrade 	Patch the upgrade changes. You could upgrade your device to the latest.
		 Using parameter "LAST_COMMIT=xx" to patch changes from LAST_COMMIT
                                                                 
       porting 	Porting changes from an existing device to another.
		 Using parameter "COMMIT1=xx COMMIT2=xx" to patch changes from COMMIT1 to COMMIT2
                                                                 
       clean 	Clean the project output.
                                                                 
       cleanall 	Clean all the project unneccessary files, inluding board/ and out/.
                                                                 
    * coron fire
      Porting ROM in one step. All the progress of ROM porting will be concentrated in to one step.
                                                                 
### Error Codes
                                                                 
You might confront with the following error while porting        
                                                                 
***ERR_USB_NOT_CONNECTED(151)***
                                                               

		Can not find device
		

		Please make sure your device has been connected.
		
                                                               
***ERR_DEVICE_NOT_ROOTED(152)***
                                                               

		Can not acquire ROOT permission
		
***ERR_UNPACK_BOOTIMG_FAILED(153)***
                                                               

		Unpack bootimg failed. Your boot.img or recovery.img might be imformal that could not be unpacked out.
		

		Using the following command to check whether your image can be unpacked:
		  $ unpack_bootimg recovery.img

		If unpack failed, use another recovery.img.
		
                                                               
***ERR_PACK_BOOTIMG_FAILED(154)***
                                                               

		Pack bootimg failed. Your boot.img or recovery.img might be informal that could not be packed back.
		

		Using the following command to check whether your image can be unpacked:
		  $ pack_bootimg image_out/

		If pack failed, unpack your boot image again.
		
                                                               
***ERR_DEVICE_BASE_NOT_FOUND(155)***
                                                               

		devices/base not found!
		

		Make sure you have synced the base from coron, and the path is devices/base.
		If devices/base not exists, try to use "repo sync" to sync coron again.
		
                                                               
***ERR_PULL_BOOT_RECOVERY_FAILED(156)***
                                                               

		Failed to pull boot.img and recovery.img from your phone.
		

		Check adb devices is fine and your phone is su root!
		
                                                               
***ERR_WRONG_PARAMETERS(157)***
                                                               

		Wrong parameters for this command....
		
***ERR_AUTOCOM_FAILED(158)***
                                                               

		Failed to autocomplete missed method in android.policy and Phone.
		

		Please check you have Phone.apk and in vendor/system/app and it can be decode correctly. Try:
          $ apktool d vendor/system/app/Phone.apk
		If you don't have Phone.apk, it must be renamed to someoneelse, find it and rename to Phone.apk.
		if the decode of Phone.apk is failed, just remove the Phone.apk in vendor/system/app, then go on!
		
                                                               
***ERR_METHODTOBOSP_FAILED(159)***
                                                               

		Failed to replace method to bosp.
		

		Make sure both of the vendor and bosp have this smali file!
		And the method name is fine, such as 
		  $ methodtobosp services.jar.out/smali/com/android/server/am/ActivityManagerService.smali 'moveTaskToFront(IILandroid/os/Bundle;)V'
		
                                                               
***ERR_SMALITOBOSP_FAILED(160)***
                                                               

		Failed to replace smali file to bosp.
		

		Make sure both of the vendor and bosp have this smali file!
		
                                                               
***ERR_APKTOOL_BUILD_FAILED(161)***
                                                               

		Failed to use apktool build apk back.
		

		Make sure you don't install any framework resource after you decode the apk,
		otherwise you should install the framework resource which match your apk, then build again
		  $ ifdir xxx/system/framework

		Example: 
		If you want build out's apk, you better install out's framework first! 
		  $ ifdir out/merged_target_files/SYSTEM/framework/
		
                                                               
***ERR_APKTOOL_DECODE_FAILED(162)***
                                                               

		Failed to use apktool d xxx.apk.
		

		Make sure the destination directory doesn't exist! 
		And install framework resource first 
		  $ ifdir xxx/system/framework

		Example: 
		If you want decode board's apk, you better install board's framework first! 
		  $ ifdir board/system/framework
		
                                                               
***ERR_DEODEX_FAILED(163)***
                                                               

		Failed to deodex ota.zip/target-files.zip.
		

		You can try to update the smali.jar and baksmali.jar in tools, which can be download from http://code.google.com
		If it doesn't work, you better find some other tools to deodex.
		
                                                               
***tale(255)***
                                                               
