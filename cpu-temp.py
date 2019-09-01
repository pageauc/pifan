#!/usr/bin/env python
""" Measure and report temperature of Raspberry Pi"""

from __future__ import print_function
import os
import sys
import time

PROG_VER = '1.5'
PROG_NAME = os.path.basename(__file__)

SLEEP_SECONDS = 5   # seconds between readings

def measure_temp():
    """ Read vcgencmd file and get temperature reading into variable"""
    temp_reading = os.popen("vcgencmd measure_temp").readline()
    return float(temp_reading.replace("temp=", "").replace("'C\n", ""))

def report_temp():
    """ print cpu temperature then sleep"""
    timer = SLEEP_SECONDS
    while True:
        for sec in reversed(range(1, SLEEP_SECONDS + 1)):
            print("CPU at %s'C  Wait %i/%i sec ..." %
                  (measure_temp(), sec, SLEEP_SECONDS))
            time.sleep(1)

print('{} ver {}'.format(PROG_NAME, PROG_VER))
print("Measuring RPI CPU Temperature Every %i seconds" % SLEEP_SECONDS)
print("Press cntrl-c to Exit")
try:
    report_temp()
except KeyboardInterrupt:
    print("")
    print("User Exited with Control-C")
    print('{} ver {}'.format(PROG_NAME, PROG_VER))
    print('Bye ...')
    sys.exit(0)