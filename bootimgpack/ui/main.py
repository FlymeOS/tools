#!/usr/bin/python
# Filename main.py
# Main UI of bootimgpack
#

__author__ = 'duanqz@gmail.com'

import os
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from internal import bootimg

from Tkinter import *
import tkFileDialog


class Main:

    def __init__(self):
        root = Tk()
        self.__layout(root)
        root.mainloop()

    def __layout(self, root):
        root.title("BootimgPack")
        root.geometry("500x220+400+400")
        root.resizable(width=False, height=False)

        self.__layoutBootImgFrame(root)
        self.__layoutPackBtnFrame(root)
        self.__layoutBootDirFrame(root)
        self.__layoutResultFrame(root)
        pass

    def __layoutBootImgFrame(self, root):
        frame = Frame(root)

        Label(frame, width=12, text="Boot Image: ", anchor=W).pack(side=LEFT)

        self.__bootImgText = StringVar()
        Entry(frame, width=40, textvariable=self.__bootImgText).pack(side=LEFT)

        self.__bootImgSelect = Button(frame, text="...")
        self.__bindButtonAction(self.__bootImgSelect, self.onClick)
        self.__bootImgSelect.pack(padx=5, side=LEFT)

        frame.pack(padx=5, pady=15)

    def __layoutPackBtnFrame(self, root):
        frame = Frame(root)

        self.__packBtn = Button(frame, text="PACK ^", width=7, height=1)
        self.__bindButtonAction(self.__packBtn, self.onClick)
        self.__packBtn.pack(padx=30, side=LEFT)

        self.__unpackBtn = Button(frame, text ="UNPACK v", width=7, height=1)
        self.__bindButtonAction(self.__unpackBtn, self.onClick)
        self.__unpackBtn.pack(side=LEFT)

        frame.pack(padx=5, pady=5)

    def __layoutBootDirFrame(self, root):
        frame = Frame(root)

        Label(frame, width=12, text="Files Directory: ", anchor=W).pack(side=LEFT)

        self.__bootDirText = StringVar()
        Entry(frame, width=40, textvariable=self.__bootDirText).pack(side=LEFT)

        self.__bootDirSelect = Button(frame, text="...")
        self.__bindButtonAction(self.__bootDirSelect, self.onClick)
        self.__bootDirSelect.pack(padx=5, side=LEFT)

        frame.pack(padx=5, pady=5)

    def __layoutResultFrame(self, root):
        frame = Frame(root, relief=SUNKEN, borderwidth=1)

        self.__resultText = StringVar()
        Label(frame, height=3, textvariable=self.__resultText, wraplength=400, anchor=NW).pack(padx=10, side=LEFT)
        self.__resultText.set("Result")

        frame.pack(padx=10, pady=20, fill=X, expand=1)

    def __bindButtonAction(self, btn, command):
        btn.bind("<Button-1>", command)
        btn.bind("<Return>", command)

    def onClick(self, event):
        if event.widget == self.__bootImgSelect:
            filename = tkFileDialog.askopenfilename(initialdir=os.path.expanduser("~"))
            if len(filename) > 0 :
                self.__bootImgText.set(filename)

        elif event.widget == self.__bootDirSelect:
            directory = tkFileDialog.askdirectory(initialdir=os.path.expanduser("~"))
            if len(directory) > 0 :
                self.__bootDirText.set(directory) 

        elif event.widget == self.__unpackBtn:
            bootfile = self.__bootImgText.get()
            output =  self.__bootDirText.get()

            if len(bootfile) > 0 :
                bootimg.unpack(bootfile, output)
                result = "Unpack " + bootfile + " --> " + output
                self.__resultText.set(result)

        elif event.widget == self.__packBtn:
            bootfile = self.__bootDirText.get()
            output = self.__bootImgText.get()

            if len(bootfile) > 0 :
                bootimg.pack(bootfile, output)
                result = "Pack " + bootfile + " --> " + output
                self.__resultText.set(result)

# End of class Main

### Start
if __name__ == '__main__':
    Main()