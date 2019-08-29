#!/usr/bin/env python
""" Measure and report temperature of Raspberry Pi"""
from __future__ import print_function
import os
import time

PROG_VER = 'ver 1.5'

SLEEP_SECONDS = 5   # seconds between readings

def measure_temp():
    """ Read vcgencmd file and get temperature reading into variable"""
    temp_reading = os.popen("vcgencmd measure_temp").readline()
    return float(temp_reading.replace("temp=", "").replace("'C\n", ""))

def report_temp():
    """ print cpu temperature then sleep"""
    while True:
        print("CPU at %s'C" % measure_temp())
        time.sleep(SLEEP_SECONDS)

print("Measuring CPU temperature every %i seconds" % SLEEP_SECONDS)
print("Press cntrl-c to Exit")
try:
    report_temp()
except KeyboardInterrupt:
    print("")
    print("User Exited with Control-C")
