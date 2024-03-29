#!/usr/bin/env python
"""
demo of "gpio_function()" port test
script by Alex Eames https://raspi.tv/?p=6805
Modified by Claude Pageau
"""
from __future__ import print_function
import RPi.GPIO as GPIO
import os
import sys

PROG_VER = '1.5'
PROG_NAME = os.path.basename(__file__)

# Offer the user a choice of Boare Pin
# or BCM Port numbers and set numbering scheme accordingly
print('{} ver {}'.format(PROG_NAME, PROG_VER))
print("GPIO Port Status Listing")
print("------------------------")
print("1 - by Board Pin Number")
print("2 - by BCM GPIO Pin Number")
MENU_CHOICE = raw_input("Choice: ")
print(' ')

if MENU_CHOICE == "1":
    GPIO.setmode(GPIO.BOARD)
    PORTS = [3, 5, 7, 8, 10, 11, 12, 13, 15, 16, 18, 19, 21, 22,
             23, 24, 26, 29, 31, 32, 33, 35, 36, 37, 38, 40]
    PIN_TYPE = "Board Pin"
else:
    GPIO.setmode(GPIO.BCM)
    PORTS = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26,
             14, 15, 18, 23, 24, 25, 8, 7, 12, 16, 20, 21]
    PIN_TYPE = "BCM GPIO"

# Using a dictionary as a lookup table to give a name to gpio_function() return code
PORT_USE = {0:"GPIO.OUT", 1:"GPIO.IN", 40:"GPIO.SERIAL", 41:"GPIO.SPI",
            42:"GPIO.I2C", 43:"GPIO.HARD_PWM", -1:"GPIO.UNKNOWN"}

# loop through the list of ports/pins querying and displaying the status of each
for port in PORTS:
    pin_usage = GPIO.gpio_function(port)
    print("%s %2d status: %s" % (PIN_TYPE, port, PORT_USE[pin_usage]))

print('')
print('{} ver {}'.format(PROG_NAME, PROG_VER))
print('Bye ...')
sys.exit(0)