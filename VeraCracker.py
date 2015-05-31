#!/usr/bin/env python3.3
# -*- coding: utf8 -*-
#
# VeraCrypt volume password cracker

# Copyright (c) 2015	NorthernSec
# Copyright (c) 2015	Pieter-Jan Moreels
# This software is licensed under the Original BSD License

# Imports
import argparse
import os
import platform
import sys
import time
from datetime import datetime

# Constants
VeraPath = '"c:\\Program Files\\VeraCrypt\\"'

# Version check (to be removed)
if platform.system() != "Windows":
  sys.exit("This script is currently only written for Windows")


# Set variables based on platform
if platform.system() == "Windows":
  veraCMD = 'VeraCrypt.exe /v "%s" /q /p "%s" /s /l %s'
  processCMD = "query process"
  veraProcessName = "veracrypt.exe"
else:
  print("TODO: Linux version")

# Functions
def isVeraRunning():
  return True if ''.join(os.popen(processCMD).readlines()).find(veraProcessName) >= 0 else False

def printResults(startTime, tried):
  print("Cracking duration: %s"%str(datetime.now()-startTime))
  print("Passwords tried:   %s"%tried)
if __name__ == '__main__':
  # Parse arguments
  description='''VeraCrypt volume cracker'''

  parser = argparse.ArgumentParser(description=description)
  parser.add_argument('-v', metavar='volume',     type=str, required=True, help='Path to volume')
  parser.add_argument('-p', metavar='list',       type=str, nargs="?",     help='Password list')
  parser.add_argument('-m', metavar='mountpoint', type=str, required=True, help='Mountpoint for the volume to be mounted')
  parser.add_argument('-d', action='store_true',                           help='Debug mode')
  parser.add_argument('-o', metavar='file',       type=str,                help='Output file for untried passwords on quit')
  args = parser.parse_args()

  # Check script requirements
  if isVeraRunning():
    sys.exit("Please close VeraCrypt before running this script")
  try:
    os.chdir("%s:"%args.m)
    sys.exit("Please specify an unused mountpoint")
  except Exception as e:
    pass
  # Get wordlist
  wordlist=[x.strip() for x in open(args.p, 'r')] if args.p else [line.strip() for line in fileinput.input()]
  
  # Time to test
  wlCopy = list(wordlist)
  tried=0
  startTime=datetime.now()
  try:
    for p in wordlist:
      wlCopy.pop(0)
      tried+=1
      if args.d:
        print("[-] Trying %s"%p)
      os.popen(VeraPath + veraCMD%(args.v, p, args.m))
      while True:
        if isVeraRunning():
          time.sleep(0.1)
        else:
	        break
      try:
        os.chdir("%s:"%args.m)
        print("[+] Password found! --> %s <--"%p)
        printResults(startTime, tried)
        sys.exit(0)
      except:
        pass
    print("Password not found")
    printResults(startTime, tried)
  except KeyboardInterrupt:
    print("[!]Cracker interrupted")
    if args.o:
      if args.d:
        print("[-] Saving leftover passwords to %s"%args.o)
      f=open(args.o,'w')
      f.write("\n".join(wlCopy))