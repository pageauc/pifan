#!/usr/bin/env python

"""
pifand.py written by Claude Pageau:

Controls Raspberry Pi 5v case fan via GPIO control pin to NPN transistor.
Turns fan on at setpoint_high and turns fan off at setpoint_low
For details see https://github.com/pageauc/pifan
"""

# Import python libraries ...
import os
from time import sleep
import RPi.GPIO as GPIO

# User Variable Settings
# ----------------------

fan_GPIO = 25       # connect npn transistor center lead + resistor to this pin
setpoint_high = 65  # deg C of fan os off turn it on at this temperature
setpoint_low  = 55  # deg C if fan is on turn it off at this temperature
sleep_sec = 10      # seconds to wait between readings
# ----------------------

vcgencmd_path = '/usr/bin/vcgencmd' # Path to command to retrieve temperature data
vcgen_cmd = vcgencmd_path + ' measure_temp'

# Setup pin designated by fan_GPIO variable above
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)   # set mode for GPIO numbering scheme
GPIO.setup(fan_GPIO, GPIO.OUT)  # sends signal to npn transistor center lead

fan_on = False  # initialize fan status boolean
GPIO.output(fan_GPIO, fan_on)  # make sure fan is off. overrides and previous setting

while True:     # Loop forever
    """
    The /usr/bin/vcgencmd command reads current RPI temperature.
    The command requires a path to the vcgencmd file location. If there
    are problems, find path using command below then edit vcgen_cmd variable above

        which vcgencmd

    """
    res = os.popen(vcgen_cmd).readline()  # read the latest temperature from file
    temp = float((res.replace("temp=","").replace("'C\n","")))

    if fan_on and temp <= setpoint_low:
        GPIO.output(fan_GPIO, False)  # send signal to NPN transistor to turn fan OFF
        fan_on = False
    elif not fan_on and temp >= setpoint_high:
        GPIO.output(fan_GPIO, True)  # send signal to NPN transistor to turn fan ON
        fan_on = True

    try:
       sleep(sleep_sec)   # Wait before the next reading
    except KeyboardInterrupt:
        print(' ')
        break

GPIO.cleanup()
print('Bye ...')
