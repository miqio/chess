#!/usr/bin/python
# -*- coding: utf-8 -*-
import re, argparse
from os import path as p, listdir, popen as execute, mkdir
from shutil import copy, rmtree

EXTMP4 = ".mpg"
EXTJPEG = ".jpg"

arg=argparse.ArgumentParser(description="Looks up jpeg files in the directory given on the command line and concatenates them into a mp4 clip")
arg.add_argument("dirname", type=str, help="Name of the directory including the jpegs")
arg.add_argument("--maxmsec", '-t', type=int, default=250, help="Max millisec between two adjacent photo shots")
dname=arg.parse_args().dirname
maxmsec=arg.parse_args().maxmsec
cmdlist=[]
files=''
pat=re.compile("IMG_(\d*_(\d*)).jpg")
dlist = [p.abspath(dname)]
wdir = p.expanduser("~/.tmp")
if not p.exists(wdir): mkdir(wdir)

for d in dlist:
  clist=listdir(d)
  dlist.extend(map(lambda k: "%s/%s" % (d,k),filter(lambda m:p.isdir("%s/%s" % (d,m)),clist)))
  l=filter(lambda f:pat.match(f),clist)
  if l:
    l.sort()
    isOn=False
    i0=l.pop(0)
    t0=int(pat.match(i0).group(2)) if pat.match(i0) else 0
    for i in l:
      t1=int(pat.match(i).group(2)) if pat.match(i) else 0
      if abs(t1-t0) < maxmsec:
        if not isOn:
          isOn = True
          bname = "VID_"+pat.search(i0).group(1)
          mdir = "%s/%s" % (wdir,bname)
          mkdir(mdir)
          copy( "%s/%s" % (d,i0), "%s/%s" % (mdir,p.basename(i0))) 
        copy( "%s/%s" % (d,i), "%s/%s" % (mdir,p.basename(i))) 
      else:
        if isOn:
          isOn = False
      i0 = i
      t0=int(pat.match(i0).group(2)) if pat.match(i0) else 0

for d in listdir(wdir):
  infiles = "mf://%s/%s/IMG_*%s" % (wdir,d,EXTJPEG)
  outfile = "%s%s" % (d,EXTMP4)
  execute('mencoder %s -mf fps=5:type=jpg -o %s -ovc lavc -ffourcc DX50 -lavcopts vcodec=mpeg4:vbitrate=900:vrc_eq=tex:naq:ilme:trell:cbp:preme=1:keyint=132:mbd=0:qns=1:vme=4:dia=2 -noskip >> %s.log'%(infiles,outfile,outfile))
  rmtree("%s/%s" % (wdir,d))
