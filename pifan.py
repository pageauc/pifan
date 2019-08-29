#!/usr/bin/env python
"""
pifan.py  written by Claude Pageau

Control a Raspberry 5 or 3.3v case cooling fan so it turns on
at a high temperature setpoint and off at a lower temperature setpoint.
This avoids running the fan when it is not required.
This script utilizes an NPN transistor to switch power.

As a programming excercise I did some extra features that may
not necessariy be functionally required but I enjoyed the
learning experience.  Implemented logging library, argparse for changing some
settings via command line. Added reading variables from a dictionary and/or
importing from a config.py file if it exists (default install).

For details see https://github.com/pageauc/pifan
"""
# Import python libraries ...
from __future__ import print_function
print('INFO  - Loading Libraries.')
import os
import sys
import signal
import logging
import argparse
from time import sleep
import RPi.GPIO as GPIO

PROG_VER = 'ver 1.5'

# Dictionary of configuration settings variables
# will be superceded by config.py import or
# argparse parameters
CONFIG_SETTINGS = {
    'VERBOSE':True,
    'DEBUG_ON':True,
    'LOG_TO_FILE':False,
    'FORCE_FAN_ON':False,
    'FAN_GPIO':25,
    'SETPOINT_HIGH':65,
    'SETPOINT_LOW':55,
    'SLEEP_SEC':10,
    'VCGENCMD_PATH':'/usr/bin/vcgencmd'
}

# Get basic information about this script
PROG_NAME = os.path.basename(__file__)
MY_PATH = os.path.abspath(__file__)  # Find the full path of this python script
BASE_DIR = os.path.dirname(MY_PATH)  # get the path location only (excluding script name)
BASE_FILE_NAME = os.path.splitext(os.path.basename(MY_PATH))[0]
LOG_FILE_NAME = os.path.join(BASE_DIR, BASE_FILE_NAME + ".log")
CONFIG_FILE_PATH = os.path.join(BASE_DIR, "config.py")
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

def sigterm_handler(signal, frame):
    """ Exit Gracefully on kill """
    GPIO.cleanup()
    print('Killed Bye ...')
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)

# Read Configuration variables from config.py file
if os.path.exists(CONFIG_FILE_PATH):
    print('INFO  : Import Settings from {} File.'.format(CONFIG_FILE_PATH))
    try:
        from config import *
    except ImportError:
        print("ERROR : Problem Importing variables from {}".format(CONFIG_FILE_PATH))
else:
    print('ERROR :Configuration File Not Found {}'.format(CONFIG_FILE_PATH))

"""
Interate through dict listing of variables
and check if variable was imported via config.py file
If not then initialize variable and set to dict value."""
print('INFO  : Check for Missing Variables and Set to Default Value as Required')
for key, val in CONFIG_SETTINGS.items():
    try:
        exec(key)  # Try adding the variable
    except NameError:  # if not found then add variable and value from dictionary
        print('config.py Variable Not Found. Setting ' + key + ' = ' + str(val))
        exec(key + '=val')

parser = argparse.ArgumentParser(description=
                                 'Control Fan using NPN transistor and Temperature Settings')
parser.add_argument('-f', '--fanmode', type=str, choices=['on', 'off', 'auto'], required=False,
                    dest='fanmode',
                    help='Fan Control modes. Valid values are on, off or auto')
parser.add_argument('-p', '--pinnumber', type=int, required=False,
                    help='Valid Fan BCM GPIO Control Pin Number (integer)')
parser.add_argument('-s', '--status', action='store_true', required=False,
                    help='Checks Status of Fan and Temperature readings' +
                    ' from pifand.service or Other Fan Control script.')
parser.add_argument('-v', '--verbose', action='store_true', required=False,
                    help='Turn on verbose logging')
parser.add_argument('-d', '--debug', action='store_true', required=False,
                    help='Add detailed fan and temp logging messages')
parser.add_argument('-q', '--quiet', action='store_true', required=False,
                    help='Turn off verbose logging')
args = parser.parse_args()

# Setup logging
if LOG_TO_FILE:
    print("Sending Logging Data to {} (Console Messages Disabled)"
          .format(LOG_FILE_NAME))
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s%(levelname)-8s%(funcName)-10s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=LOG_FILE_NAME,
                        filemode='w')
elif VERBOSE:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
else:
    logging.basicConfig(level=logging.CRITICAL,
                        format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

def prog_exit(error_level):
    """
    Exit program back to command prompt.
    """
    logging.warn('Fan Temperature Control is NOT Active.')
    print('{} {}'.format(PROG_NAME, PROG_VER))
    print('Bye ...')
    sys.exit(error_level)

# Check if verbose turned on or off from -v or -q on command line
# Note -q overrides -v
if args.verbose:  # Display logging messages excluding only temperature changes
    VERBOSE = True
    DEBUG_ON = False
if args.debug:  # Display All logging messages
    VERBOSE = True
    DEBUG_ON = True
if args.quiet:  # Do not display any logging messages
    VERBOSE = False
    DEBUG_ON = False

# Check if this script is running in background
# and if so turn off debug logging messages
if not os.getpgrp() == os.tcgetpgrp(sys.stdout.fileno()):
    DEBUG_ON = False
    VERBOSE = False

if args.pinnumber:
    PREV_FAN_GPIO = FAN_GPIO
    FAN_GPIO = args.pinnumber
    logging.info('%s -p Option Selected. Change Default GPIO pin from %i to %i',
                 PROG_NAME, PREV_FAN_GPIO, FAN_GPIO)

logging.info('-------------------------------------------------------------')
logging.info('%s %s', PROG_NAME, PROG_VER)
logging.info("Controls a RPI Cooling Fan ON at %i'C and OFF at %i'C",
             SETPOINT_HIGH, SETPOINT_LOW)
logging.info('Using Temperature Readings and NPN transistor via GPIO pin %i',
             FAN_GPIO)
logging.info('-------------------------------------------------------------')

VCGEN_CMD = VCGENCMD_PATH + ' measure_temp'

# Monitor the status of Another Fan Control Program
if args.status:
    logging.info('%s --status Option Selected.', PROG_NAME)
    logging.info('Check Status of pifand.service or another Fan Control Script')
    VERBOSE = True
    DEBUG_ON = True
    PIN_USAGE = GPIO.gpio_function(FAN_GPIO)
    if PIN_USAGE == 0:  # Set for GPIO.OUT
        logging.info('Fan Control is Active. pin %i Set to GPIO.OUT', FAN_GPIO)
        GPIO.setup(FAN_GPIO, GPIO.OUT)  # sends signal to npn transistor center lead
    # Report Fan Staus and Temperature
    # while Fan Control pin is in GPIO.OUT state
    logging.info('Press ctrl-c to Exit Fan Control Status Checking.')
    while True:
        PIN_USAGE = GPIO.gpio_function(FAN_GPIO)
        if PIN_USAGE == 0:  # Set for GPIO.OUT
            TEMP_READING = os.popen(VCGEN_CMD).readline()  # read the latest temperature from file
            CPU_TEMP = float((TEMP_READING.replace("temp=", "").replace("'C\n", "")))
            if GPIO.input(FAN_GPIO):
                logging.info("Fan is ON ... CPU at %i'C  ... sleep %i sec",
                             CPU_TEMP, SLEEP_SEC)
            else:
                logging.info("Fan is OFF .. CPU at %i'C  ... sleep %i sec",
                             CPU_TEMP, SLEEP_SEC)
            try:
                sleep(SLEEP_SEC)   # Wait before the next reading
            except KeyboardInterrupt:
                print(' ')
                logging.warn('User Pressed cntrl-c to Exit Fan Status Checking')
                break
        elif PIN_USAGE == 1:  # Set for GPIO.IN
            logging.warn('Fan Control is NOT Active. GPIO pin %i is NOT set as GPIO.OUT',
                         FAN_GPIO)
            logging.warn('Install/Start pifand.service or ' +
                         'start fan control script pifan.py or pifand.py')
            logging.warn('eg sudo systemctl start pifand.service')
            break
    print('{} {}'.format(PROG_NAME, PROG_VER))
    print('Bye ...')
    sys.exit(0)

# Setup pin designated by FAN_GPIO variable above
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)   # set mode for GPIO numbering scheme
PIN_USAGE = GPIO.gpio_function(FAN_GPIO)
if PIN_USAGE == 0:  # Set for GPIO.OUT
    logging.warn('BCM pin %i In Use. Fan Control is Already Active Somewhere Else',
                 FAN_GPIO)
    logging.warn('pifand.service, pifand.py or pifan.py may be running.')
    logging.info('Check PID with command: pgrep -fa fan')
    logging.info('Check Fan Status with command: ./%s --status', PROG_NAME)
    print('{} {}'.format(PROG_NAME, PROG_VER))
    print('Bye ...')
    sys.exit(0)

GPIO.setup(FAN_GPIO, GPIO.OUT)  # sends signal to npn transistor center lead
if args.fanmode == 'on':
    GPIO.output(FAN_GPIO, True)
    logging.info('%s -f %s Option Selected. Forced Fan ON and Exit',
                 PROG_NAME, args.fanmode)
    prog_exit(0)
elif args.fanmode == 'off':
    GPIO.output(FAN_GPIO, False)
    logging.info('%s -f %s Option Selected. Forced Fan OFF and Exit',
                 PROG_NAME, args.fanmode)
    prog_exit(0)

if FORCE_FAN_ON:
    GPIO.output(FAN_GPIO, True)
    logging.warning('Fan has been forced to ON with No Temperature Control')
    logging.info('To Change Setting Edit config.py variable FORCE_FAN_ON = False')
    prog_exit(0)

if not os.path.isfile(VCGENCMD_PATH):
    logging.error('%s File Not Found.', VCGENCMD_PATH)
    logging.error('To Locate Path Run command: which vcgencmd')
    logging.error('Then Edit VCGENCMD_PATH variable in %s', CONFIG_FILE_PATH)
    prog_exit(1)

logging.info('Fan Temperature Control is Active.')
FAN_ON = False  # initialize fan status boolean
GPIO.output(FAN_GPIO, FAN_ON)  # make sure fan is off. overrides and previous setting
while True:     # Loop forever
    """
    command below reads the current temperature from the vcgencmd file.
    The command requires a path to the vcgencmd file location
    To find path use command below and edit VCGEN_CMD variable above

        which vcgencmd"""

    TEMP_READING = os.popen(VCGEN_CMD).readline()  # read the latest temperature from file
    try:
        CPU_TEMP = float((TEMP_READING.replace("temp=", "").replace("'C\n", "")))
    except:
        logging.error('Could NOT read temperature with command %s', VCGEN_CMD)
        logging.error('Please Investigate problem')
        prog_exit(1)

    if FAN_ON and CPU_TEMP <= SETPOINT_LOW:
        if VERBOSE:
            logging.info("Turn Fan OFF .. %i'C SETPOINT_LOW reached.",
                         SETPOINT_LOW)
        GPIO.output(FAN_GPIO, False)  # send signal to NPN transistor to turn fan OFF
        FAN_ON = False
    elif not FAN_ON and CPU_TEMP >= SETPOINT_HIGH:
        if VERBOSE:
            logging.info("Turn Fan ON ... %i'C SETPOINT_HIGH reached.",
                         SETPOINT_HIGH)
        GPIO.output(FAN_GPIO, True)  # send signal to NPN transistor to turn fan ON
        FAN_ON = True

    if DEBUG_ON:
        if FAN_ON:
            logging.info("Fan is ON ... CPU at %s'C  ... sleep %i sec",
                         CPU_TEMP, SLEEP_SEC)
        else:
            logging.info("Fan is OFF .. CPU at %i'C  ... sleep %i sec",
                         CPU_TEMP, SLEEP_SEC)

    try:
        sleep(SLEEP_SEC)   # Wait before the next reading
    except KeyboardInterrupt:
        print(' ')
        logging.info('Shutdown and cleanup GPIO settings')
        GPIO.cleanup()
        break

prog_exit(0)
