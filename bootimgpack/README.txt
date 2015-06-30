# Encoding: UTF-8

-------------------------------------------------------------------------------
bootimgpack 是一个智能解包和打包 Android boot.img 的工具,
采用 Python 和 Shell 语言实现, 目前仅支持类 Unix 系统.

特点
===
  * 自适应不同手机厂商的 boot.img 格式,智能完成解包
  * 提供命令和图形界面两种操作方式

使用
===
 * 命令方式
   解包 unpack_bootimg.py boot.img output/
   打包 pack_bootimg.py   BOOT/ boot.img

 * 图形界面
   运行 ui/main.py 将会启动操作界面

版本
===
v1.0

-------------------------------------------------------------------------------
bootimgpack is a smart tool for unpack or pack boot.img of Android,
implemented in Python and Shell, now only for Unix-like OS.

Features
===
 * Hide format differences of boot.img of different manufactors
 * Both command and graphic mode are provided

Usage
===
 * Command Mode
   Unpack : unpack_bootimg.py boot.img output/
   Pack   : pack_bootimg.py BOOT/ boot.img

 * Graphic Mode
   Run ui/main.py to launch the UI

Version
===
V1.0
