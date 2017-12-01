                                                                 
###  An open source project for Android ROM porting.
                                                                 
Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0).
                                                                 
COMMANDs are:
                                                                 
    * flyme help [ACTION]
                                                                 
      Type `help name` to find out more about the `name`.
                                                                 
    * flyme ACTION
                                                                 
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
                                                                 
###  Error Codes
                                                                 
***ERR_USB_NOT_CONNECTED(151)***
                                                              

		Please make sure your device has been connected.
		
                                                          
***ERR_DEVICE_NOT_ROOTED(152)***
                                                              
***ERR_UNPACK_BOOTIMG_FAILED(153)***
                                                              

		Using the following command to check whether your image can be unpacked:
		  $ unpack_bootimg recovery.img

		If unpack failed, use another recovery.img.
		
                                                          
***ERR_PACK_BOOTIMG_FAILED(154)***
                                                              

		Using the following command to check whether your image can be unpacked:
		  $ pack_bootimg image_out/

		If pack failed, unpack your boot image again.
		
                                                          
***ERR_DEVICE_BASE_NOT_FOUND(155)***
                                                              

		Make sure you have synced the base from coron, and the path is devices/base.
		If devices/base not exists, try to use "repo sync" to sync coron again.
		
                                                          
***ERR_PULL_BOOT_RECOVERY_FAILED(156)***
                                                              

		Check adb devices is fine and your phone is su root!
		
                                                          
***ERR_WRONG_PARAMETERS(157)***
                                                              
***ERR_AUTOCOM_FAILED(158)***
                                                              

		Please check you have Phone.apk and in vendor/system/app and it can be decode correctly. Try:
          $ apktool d vendor/system/app/Phone.apk
		If you don't have Phone.apk, it must be renamed to someoneelse, find it and rename to Phone.apk.
		if the decode of Phone.apk is failed, just remove the Phone.apk in vendor/system/app, then go on!
		
                                                          
***ERR_METHODTOBOSP_FAILED(159)***
                                                              

		Make sure both of the vendor and bosp have this smali file!
		And the method name is fine, such as 
		  $ methodtobosp services.jar.out/smali/com/android/server/am/ActivityManagerService.smali 'moveTaskToFront(IILandroid/os/Bundle;)V'
		
                                                          
***ERR_SMALITOBOSP_FAILED(160)***
                                                              

		Make sure both of the vendor and bosp have this smali file!
		
                                                          
***ERR_APKTOOL_BUILD_FAILED(161)***
                                                              

		Make sure you don't install any framework resource after you decode the apk,
		otherwise you should install the framework resource which match your apk, then build again
		  $ ifdir xxx/system/framework

		Example: 
		If you want build out's apk, you better install out's framework first! 
		  $ ifdir out/merged_target_files/SYSTEM/framework/
		
                                                          
***ERR_APKTOOL_DECODE_FAILED(162)***
                                                              

		Make sure the destination directory doesn't exist! 
		And install framework resource first 
		  $ ifdir xxx/system/framework

		Example: 
		If you want decode board's apk, you better install board's framework first! 
		  $ ifdir board/system/framework
		
                                                          
***ERR_DEODEX_FAILED(163)***
                                                              

		You can try to update the smali.jar and baksmali.jar in tools, which can be download from http://code.google.com
		If it doesn't work, you better find some other tools to deodex.
		
---------------------------------------------------------------------------------------------------------------------------------
      
###  Flyme开源项目致力于为开发者提供业界一流的ROM适配工具.
                                                                 
Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0).
                                                                 
提供的命令:
                                                                 
    * flyme help [ACTION]
                                                                 
      输入 `help [ACTION]` 去获取更多关于[ACTION]的帮助文档.
                                                                 
    * flyme ACTION
                                                                 
       config 	为新设备生成一个Makefile，这个Makefile将会包含所有的配置.
                                                                 
       newproject 	为新设备建立一个新项目，只能用在为设备建立新项目上.
                                                                 
       patchall 	应用所有的Flyme的修改(插桩).
		将AOSP和BOSP产生的修改合并到原厂代码上.
		 BOSP  : Flyme开源代码
		 AOSP  : 安卓开源代码
		 VENDOR: 设备原厂代码

		原厂代码位于你的机型根目录.
		AOSP和BOSP位于机型根目录的autopatch目录里.
                                                                 
       fullota 	制作一个完整的刷机包.
		一个完整的刷机包将会在out目录下生成，你应该把它刷入你的手机.
                                                                 
       upgrade 	应用所有的更新修改，你可以升级你的设备到最新.
                                                                 
       porting 	从现有的设备参考制作FlymeOS.
		 使用语法： "COMMIT1=xx COMMIT2=xx" 应用修改从COMMIT1到COMMIT2
                                                                 
       clean 	清理项目输出的文件.
                                                                 
       cleanall 	清理项目不需要的文件，包括机型目录下的board目录和out目录.
                                                                 
###  错误号
                                                                 
***ERR_USB_NOT_CONNECTED(151)***
                                                              

		请确认你的设备已经连接.
		
                                                          
***ERR_DEVICE_NOT_ROOTED(152)***
                                                              
***ERR_UNPACK_BOOTIMG_FAILED(153)***
                                                              

                建议解决方案:
                ----------------
		使用以下命令来确认镜像是否能被CORON解包:
		  $ unpack_bootimg recovery.img

		如果解包失败，请使用其他镜像或者上网搜索解包方式.
		
                                                          
***ERR_PACK_BOOTIMG_FAILED(154)***
                                                              

                建议解决方案:
                ----------------
		使用以下命令来确认镜像是否能被打包:
		  $ pack_bootimg image_out/

		如果打包失败，请重新解包你的boot.img或者recovery.img.
		
                                                          
***ERR_DEVICE_BASE_NOT_FOUND(155)***
                                                              

                建议解决方案:
                ----------------
		请确认devices/base有一个coron base.
		如果没有devices/base not, 请尝试使用 "repo sync" 去重新同步源码.
		Make sure you have synced the base from coron, and the path is devices/base.
		If devices/base not exists, try to use "repo sync" to sync coron again.
		
                                                          
***ERR_PULL_BOOT_RECOVERY_FAILED(156)***
                                                              

		请确保adb正常工作并让你的设备获取root权限!
		
                                                          
***ERR_WRONG_PARAMETERS(157)***
                                                              
***ERR_AUTOCOM_FAILED(158)***
                                                              

		请检查是否有 Phone.apk 在 vendor/system/app 里，还要确认其是否能被反编译.
			尝试输入 $ apktool d vendor/system/app/Phone.apk
		如果你没有 Phone.apk, 那么它一定是被某人或者厂商修改了，请找到它并改名为 Phone.apk.
		如果反编译失败，请删除它，然后继续.
		
                                                          
***ERR_METHODTOBOSP_FAILED(159)***
                                                              

		请确认原厂代码和BOSP中都含有这个smali文件!
		如果函数方法是正确的, 就像这样
		$ methodtobosp services.jar.out/smali/com/android/server/am/ActivityManagerService.smali 'moveTaskToFront(IILandroid/os/Bundle;)V'
		
                                                          
***ERR_SMALITOBOSP_FAILED(160)***
                                                              

		请确认原厂代码和BOSP中都含有这个smali文件!
		
                                                          
***ERR_APKTOOL_BUILD_FAILED(161)***
                                                              

		请确认你在反编译这个apk后没有再安装过任何资源框架,
		你可以使用以下命令重新安装资源框架
			$ ifdir xxx/system/framework
		例子:
		如果你想回编译原厂apk，那么你必须使用以下命令安装原厂的资源框架!
			$ ifdir out/merged_target_files/SYSTEM/framework/
		
                                                          
***ERR_APKTOOL_DECODE_FAILED(162)***
                                                              

		请确认目标文件夹不存在!
		还有，在反编译之前，你必须先安装资源框架.
			$ ifdir xxx/system/framework
		例子:
		如果你想反编译Flyme的apk，那么你必须先使用以下命令安装Flyme的资源框架!
			$ ifdir board/system/framework
		
                                                          
***ERR_DEODEX_FAILED(163)***
                                                              

		请更新在tools/apktools/里的smali.jar和baksmali.jar, 可以在这里下载 http://code.google.com
		如果它无法工作 那么你可以寻找其他合并odex的工具.

