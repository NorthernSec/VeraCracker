#!/usr/bin/env python3.3
# -*- coding: utf8 -*-
#
# VeraCrypt volume password cracker
#
# Copyright (c) 2015	NorthernSec
# Copyright (c) 2015	Pieter-Jan Moreels
# This software is licensed under the Original BSD License

# Imports
import argparse
import os
import platform
import subprocess
import sys
import time
from datetime import datetime

# Constants
VeraWinPath = '"c:\\Program Files\\VeraCrypt\\VeraCrypt.exe"'
VeraWinAttributes = ' /v "%s" /q /p "%s" /s /l %s'
VeraWinProcList = "query process"
VeraWinProcName = "veracrypt.exe"
VeraMacPath = '/Applications/VeraCrypt.app/Contents/MacOS/VeraCrypt'
VeraLinuxPath = 'veracrypt'
VeraLinuxAttributes = ' -t %s -p %s --non-interactive'

# Functions


def isVeraRunning():
    return True if ''.join(os.popen(VeraWinProcList).readlines()).find(VeraWinProcName) >= 0 else False


def progressbar(it, prefix="Cracking ", size=50):
    count = len(it)

    def _show(_i):
        if count != 0 and sys.stdout.isatty():
            x = int(size * _i / count)
            sys.stdout.write("%s[%s%s] %i/%i\r" %
                             (prefix, "#" * x, " " * (size - x), _i, count))
            sys.stdout.flush()
    _show(0)
    for i, item in enumerate(it):
        yield item
        _show(i + 1)
    sys.stdout.write("\n")
    sys.stdout.flush()


def checkRequirements():
    if platform.system() == "Windows":
        print("TODO: Is veracrypt installed")
        if isVeraRunning():
            sys.exit("Please close VeraCrypt before running this script")
        try:
            os.chdir("%s:" % args.m)
            sys.exit("Please specify an unused mountpoint")
        except Exception as e:
            pass


def windowsCrack(p, veracryptPath):
    os.popen(veracryptPath + VeraWinAttributes % (args.v, p, args.m))
    while True:
        if isVeraRunning():
            time.sleep(0.1)
        else:
            break
    try:
        os.chdir("%s:" % args.m)
        return True
    except:
        return False


def linuxCrack(p, veracryptPath):
    cmd = veracryptPath + VeraLinuxAttributes % (args.v, p)
    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()

    procreturn = str(
        out, "utf-8").strip() if out else str(err, "utf-8").strip()
    if procreturn.find("Error: Operation failed due to one or more of the following:") != -1:
        return False
    elif procreturn == "Error: Failed to obtain administrator privileges.":
        sys.exit("This script requires root previleges")
    elif procreturn.find("No such file or directory") != -1:
        sys.exit(
            "VeraCrypt cannot be found: Install VeraCrypt or use the -b argument")
    elif procreturn == "Error: The volume you are trying to mount is already mounted.":
        sys.exit("This volume is already mounted")
    else:
        print(procreturn)
        return True


def printResults(startTime, tried):
    print("Cracking duration: %s" % str(datetime.now() - startTime))
    print("Averange time per try: %s" %
          str((datetime.now() - startTime) / tried))
    print("Passwords tried:   %s" % tried)


if __name__ == '__main__':
    # Parse arguments
    description = '''VeraCrypt volume cracker'''

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-v', metavar='volume', type=str,
                        required=True, help='Path to volume')
    parser.add_argument('-p', metavar='list', type=str,
                        nargs="?", help='Password list')
    if platform.system() == "Windows":
        parser.add_argument('-m', metavar='mountpoint', type=str,
                            required=True, help='Mountpoint for the volume to be mounted')
    parser.add_argument('-d', action='store_true',
                        help='Debug mode')
    parser.add_argument('-o', metavar='file', type=str,
                        help='Output file for untried passwords on quit')
    parser.add_argument('-b', metavar='file', type=str,
                        help='Path to the VeraCrypt binary')
    args = parser.parse_args()

    # Get VeraCypt binary path
    if platform.system() == "Linux":
        veracryptPath = VeraLinuxPath
        crack = linuxCrack
    elif platform.system() == "Windows":
        veracryptPath = VeraWinPath
        crack = windowsCrack
    elif platform.system() == "Darwin":
        veracryptPath = VeraMacPath
        crack = linuxCrack
    else:
        sys.exit("This script is not written for your platform")

    if args.b:
        veracryptPath = args.b

    # Check script requirements
    checkRequirements()

    # Get wordlist
    wordlist = [x.strip() for x in open(args.p, 'r')] if args.p else [
        line.strip() for line in fileinput.input()]

    # Time to test
    wlCopy = list(wordlist)
    tried = 0
    startTime = datetime.now()
    try:
        for p in progressbar(wordlist):
            if args.d:
                print("[-] Trying %s" % p)
            if crack(p, veracryptPath):
                print("[+] Password found! --> %s <--" % p)
                printResults(startTime, tried)
                sys.exit(0)
            wlCopy.pop(0)
            tried += 1
        print("Password not found")
        printResults(startTime, tried)
    except KeyboardInterrupt:
        print("[!]Cracker interrupted")
        if args.o:
            if args.d:
                print("[-] Saving leftover passwords to %s" % args.o)
            f = open(args.o, 'w')
            f.write("\n".join(wlCopy))
