#!/usr/bin/python3

from py_irsend import irsend
import time

while True:
    irsend.send_once("AKB", ["powerOn"])
    time.sleep(2)
    irsend.send_once("AKB", ["powerOff"])
    time.sleep(2)
