#!/usr/bin/env python
# vim:fileencoding=utf-8
 
import sys
import os
import struct
import shutil

outName = ("kernel","ramdisk.img","RPM.bin")

def getSegNum(f):
  f.seek(44)
  d = f.read(2)
  return struct.unpack('<H', d)[0]
 
def readSegInfo(f):
  d = f.read(32)
  info = struct.unpack('<LLLLLLLL', d)
  return info[4], info[1], info[2] # size, offset
 
def main(fname, output=None):
  if output is not None:
    if os.path.isdir(output):
      shutil.rmtree(output)
    os.makedirs(output)
  else:
    output = os.getcwd()

  f = open(fname, 'rb')
  os.chdir(output)
  n = getSegNum(f)
  if n > 100:
    return -1 # not a sony img, just return
  f.seek(52)

  fBaseName = os.path.split(fname)[1]
  segs = [readSegInfo(f) for i in range(n)]
  for i, seg in enumerate(segs):
    f.seek(seg[1])
    data = f.read(seg[0])

    if i < 3:
      outFileName = "%s" %(outName[i])
    else:
      outFileName = "%s-%s" %(fBaseName,i)

    with open(outFileName, 'wb') as wf:
      wf.write(data)
    
    addrFileName="addr_%s" %(outFileName)
    with open(addrFileName, 'wb') as wfaddr:
      wfaddr.write(hex(seg[2]))
  
    if i == 1:
      ramdiskDir = "RAMDISK"
      os.mkdir(ramdiskDir)
      os.system("cd %s && gunzip < ../%s | cpio -i" %(ramdiskDir, outFileName))
      os.remove(outFileName)

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print('Which boot.img need to be unpack')
  else:
    main(*sys.argv[1:])
