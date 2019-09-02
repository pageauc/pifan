#!/usr/bin/env python
# Import python libraries ...
"""
pifand.py written by Claude Pageau:

Controls Raspberry Pi 5v case fan via GPIO control pin to NPN transistor.
Turns fan on at SETPOINT_HIGH and turns fan off at setpoint_low
For details see https://github.com/pageauc/pifan
"""

from __future__ import print_function
import os
import sys
import signal
from time import sleep
import RPi.GPIO as GPIO

PROG_VER = 'ver 1.5'
PROG_NAME = os.path.basename(__file__)

# User Variable Settings
# ----------------------
FAN_GPIO = 25       # connect npn transistor center lead + resistor to this pin
SETPOINT_HIGH = 65  # deg C of fan os off turn it on at this temperature
SETPOINT_LOW = 55  # deg C if fan is on turn it off at this temperature
SLEEP_SEC = 10      # seconds to wait between readings
# ----------------------

VCGENCMD_PATH = '/usr/bin/vcgencmd' # Path to command to retrieve temperature data
VCGEN_CMD = VCGENCMD_PATH + ' measure_temp'

# Setup pin designated by FAN_GPIO variable above
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)   # set mode for GPIO numbering scheme
GPIO.setup(FAN_GPIO, GPIO.OUT)  # sends signal to npn transistor center lead

FAN_ON = False  # initialize fan status boolean
GPIO.output(FAN_GPIO, FAN_ON)  # make sure fan is off. overrides and previous setting

def sigterm_handler(signal, frame):
    """ Exit Gracefully on kill """
    GPIO.cleanup()
    print('WARN  : %s Received Kill' % PROG_NAME)
    print('INFO  : Performed GPIO.cleanup.  Bye ...')
    sys.exit(0)
    
# Setup signal to exit gracefully if a kill is send to this script
signal.signal(signal.SIGTERM, sigterm_handler)

while True:     # Loop forever
    """
    The /usr/bin/vcgencmd command reads current RPI temperature.
    The command requires a path to the vcgencmd file location. If there
    are problems, find path using command below then edit vcgen_cmd variable above

        which vcgencmd
    """
    TEMP_READING = os.popen(VCGEN_CMD).readline()  # read the latest temperature from file
    CPU_TEMP = float((TEMP_READING.replace("temp=", "").replace("'C\n", "")))

    if FAN_ON and CPU_TEMP <= SETPOINT_LOW:
        GPIO.output(FAN_GPIO, False)  # send signal to NPN transistor to turn fan OFF
        FAN_ON = False
    elif not FAN_ON and CPU_TEMP >= SETPOINT_HIGH:
        GPIO.output(FAN_GPIO, True)  # send signal to NPN transistor to turn fan ON
        FAN_ON = True

    try:
        sleep(SLEEP_SEC)   # Wait before the next reading
    except KeyboardInterrupt:
        print(' ')
        break

GPIO.cleanup()
print('%s Exited. Bye ...' % PROG_NAME)
sys.exit(0)
