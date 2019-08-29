#!/usr/bin/env python
import os
import time

"""
 Measure and report temperature of Raspberry Pi
"""
prog_ver = 'ver 1.3'

sleep_seconds = 5   # seconds between readings

def measure_temp():
    res = os.popen("vcgencmd measure_temp").readline()
    return float((res.replace("temp=","").replace("'C\n","")))

def report_temp():
    while True:
        print("CPU at %s'C" % measure_temp())
        time.sleep(sleep_seconds)

print("Measuring CPU temperature every %i seconds" % sleep_seconds)
print("Press cntrl-c to Exit")
try:
    report_temp()
except KeyboardInterrupt:
    print("")
    print("User Exited with Control-C")

