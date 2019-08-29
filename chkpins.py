#!/usr/bin/env python
# demo of "gpio_function()" port test
# script by Alex Eames https://raspi.tv/?p=6805

import RPi.GPIO as GPIO

# Offer the user a choice of Pin or Port numbers and set numbering scheme accordingly
print("GPIO Port Status Listing")
print("------------------------")
print("1 - Display by Port Number")
print("2 - Display by BCM Port Numbering")
choice = raw_input("Choice: ")
print(' ')

if choice == "1":
    GPIO.setmode(GPIO.BOARD)
    ports = [3,5,7,8,10,11,12,13,15,16,18,19,21,22,23,24,26,29,31,32,33,35,36,37,38,40]
    pin_type = "Port Number"
else:
    GPIO.setmode(GPIO.BCM)
    ports = [2,3,4,17,27,22,10,9,11,5,6,13,19,26,14,15,18,23,24,25,8,7,12,16,20,21]
    pin_type = "BCM Port"

# Using a dictionary as a lookup table to give a name to gpio_function() return code
port_use = {0:"GPIO.OUT", 1:"GPIO.IN",40:"GPIO.SERIAL",41:"GPIO.SPI",42:"GPIO.I2C",
           43:"GPIO.HARD_PWM", -1:"GPIO.UNKNOWN"}

# loop through the list of ports/pins querying and displaying the status of each
for port in ports:
    usage = GPIO.gpio_function(port)
    print("%s %2d status: %s" % (pin_type, port, port_use[usage]))
