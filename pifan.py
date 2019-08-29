#!/usr/bin/env python
# Import python libraries ...
from __future__ import print_function
print('INFO  - Loading Libraries.')
import os
import sys
import logging
import argparse
from time import sleep
import RPi.GPIO as GPIO

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
prog_ver = 'ver 1.3'

# Dictionary of configuration settings variables
# will be superceded by config.py import or
# argparse parameters
config_settings = {
'verbose':True,
'debug_on':True,
'log_to_file':False,
'force_fan_on':False,
'fan_GPIO':25,
'setpoint_high':65,
'setpoint_low':55,
'sleep_sec':10,
'vcgencmd_path':'/usr/bin/vcgencmd'
}

# Get basic information about this script
prog_name = os.path.basename(__file__)
my_path = os.path.abspath(__file__)  # Find the full path of this python script
base_dir = os.path.dirname(my_path)  # get the path location only (excluding script name)
base_file_name = os.path.splitext(os.path.basename(my_path))[0]
log_file_path = os.path.join(base_dir, base_file_name + ".log")
config_file_path = os.path.join(base_dir, "config.py")
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Read Configuration variables from config.py file
if os.path.exists(config_file_path):
    print('INFO  : Import Settings from {} File.'.format(config_file_path))
    try:
        from config import *
    except ImportError:
        print("ERROR : Problem Importing variables from {}".format(config_file_path))
else:
    print('ERROR :Configuration File Not Found {}'.format(config_file_path))

"""
Interate through dict listing of variables
and check if variable was imported via config.py file
If not then initialize variable and set to dict value.
"""
print('INFO  : Check for Missing Variables and Set to Default Value as Required')
for key,val in config_settings.items():
    try:
        exec(key)  # Try adding the variable
    except NameError:  # if not found then add variable and value from dictionary
        print('config.py Variable Not Found. Setting ' + key + ' = ' + str(val))
        exec(key + '=val')

parser = argparse.ArgumentParser(description='Control Fan using NPN transistor and Temperature Settings')
parser.add_argument('-f', '--fanmode', type=str, choices=['on', 'off', 'auto'], required=False,
                    dest='fanmode',
                    help='Fan Control modes. Valid values are on, off or auto')
parser.add_argument('-p', '--pinnumber', type=int, required=False,
                    help='Valid Fan BCM GPIO Control Pin Number (integer)')
parser.add_argument('-s', '--status', action='store_true', required=False,
                    help='Checks Status of Fan and Temperature readings from pifand.service or Other Fan Control script.')
parser.add_argument('-v', '--verbose', action='store_true', required=False,
                    help='Turn on verbose logging')
parser.add_argument('-d', '--debug', action='store_true', required=False,
                    help='Add detailed fan and temp logging messages')
parser.add_argument('-q', '--quiet', action='store_true', required=False,
                    help='Turn off verbose logging')
args = parser.parse_args()

# Setup logging
if log_to_file:
    print("Sending Logging Data to %s  (Console Messages Disabled)" %( log_file_path ))
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=log_file_path,
                    filemode='w')
elif verbose:
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
    print('{} {}'.format(prog_name, prog_ver))
    print('Bye ...')
    sys.exit(error_level)

# Check if verbose turned on or off from -v or -q on command line
# Note -q overrides -v
if args.verbose:  # Display logging messages excluding only temperature changes
    verbose = True
    debug_on = False
if args.debug:  # Display All logging messages
    verbose = True
    debug_on = True
if args.quiet:  # Do not display any logging messages
    verbose = False
    debug_on = False

# Check if this script is running in background
# and if so turn off debug logging messages
if not os.getpgrp() == os.tcgetpgrp(sys.stdout.fileno()):
    debug_on = False
    verbose = False

if args.pinnumber:
    prev_fan_GPIO = fan_GPIO
    fan_GPIO = args.pinnumber
    logging.info('{} -p Option Selected. Change Default GPIO pin from {} to {}'
                 .format(prog_name, prev_fan_GPIO, fan_GPIO))

logging.info('-------------------------------------------------------------')
logging.info('{} {}'.format(prog_name, prog_ver))
logging.info("Controls a RPI Cooling Fan ON at {}'C and OFF at {}'C"
             .format(setpoint_high, setpoint_low))
logging.info('Using Temperature Readings and NPN transistor via GPIO pin {}'
             .format(fan_GPIO))
logging.info('-------------------------------------------------------------')

vcgen_cmd = vcgencmd_path + ' measure_temp'

# Monitor the status of Another Fan Control Program
if args.status:
    logging.info('{} --status Option Selected.'.format(prog_name))
    logging.info('Check Status of pifand.service or another Fan Control Script')
    verbose = True
    debug_on = True
    usage = GPIO.gpio_function(fan_GPIO)
    if usage == 0:  # Set for GPIO.OUT
        logging.info('Fan Control is Active. pin {} Set to GPIO.OUT'.format(fan_GPIO))
        GPIO.setup(fan_GPIO, GPIO.OUT)  # sends signal to npn transistor center lead
    # Report Fan Staus and Temperature
    # while Fan Control pin is in GPIO.OUT state
    logging.info('Press ctrl-c to Exit Fan Control Status Checking.')
    while True:
        usage = GPIO.gpio_function(fan_GPIO)
        if usage == 0:  # Set for GPIO.OUT
            res = os.popen(vcgen_cmd).readline()  # read the latest temperature from file
            temp = float((res.replace("temp=","").replace("'C\n","")))
            if GPIO.input(fan_GPIO):
                logging.info('Fan is ON ... CPU at {} C  ... sleep {} sec'
                             .format(temp, sleep_sec))
            else:
                logging.info('Fan is OFF .. CPU at {} C  ... sleep {} sec'
                             .format(temp, sleep_sec))
            try:
               sleep(sleep_sec)   # Wait before the next reading
            except KeyboardInterrupt:
                print(' ')
                logging.warn('User Pressed cntrl-c to Exit Fan Status Checking')
                break
        elif usage == 1:  # Set for GPIO.IN
            logging.warn('Fan Control is NOT Active. GPIO pin {} is NOT set as GPIO.OUT'.format(fan_GPIO))
            logging.info('Install/Start pifand.service or start fan control script pifan.py or pifand.py')
            logging.info('eg sudo systemctl start pifand.service')
            break
    print('{} {}'.format(prog_name, prog_ver))
    print('Bye ...')
    sys.exit(0)

# Setup pin designated by fan_GPIO variable above
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)   # set mode for GPIO numbering scheme
GPIO.setup(fan_GPIO, GPIO.OUT)  # sends signal to npn transistor center lead

if args.fanmode == 'on':
    GPIO.output(fan_GPIO, True)
    logging.info('{} -f {} Option Selected. Forced Fan ON and Exit'.format(
                 prog_name, args.fanmode))
    prog_exit(0)
elif args.fanmode == 'off':
    GPIO.output(fan_GPIO, False)
    logging.info('{} -f {} Option Selected. Forced Fan OFF and Exit'.format(
                 prog_name, args.fanmode))
    prog_exit(0)

if force_fan_on:
    GPIO.output(fan_GPIO, True)
    logging.warning('Fan has been forced to ON with No Temperature Control')
    logging.info('To Change Setting Edit config.py variable force_fan_on = False')
    prog_exit(0)

if not os.path.isfile(vcgencmd_path):
    logging.error('{} File Not Found.'.format(vcgencmd_path))
    logging.info('    1 - Run which command below to locate file path')
    logging.info('            which vcgencmd')
    logging.info('    2 - nano Edit vcgencmd_path variable in this script per output')
    prog_exit(1)

logging.info('Fan Temperature Control is Active.')
fan_on = False  # initialize fan status boolean
GPIO.output(fan_GPIO, fan_on)  # make sure fan is off. overrides and previous setting
while True:     # Loop forever
    """
    command below reads the current temperature from the vcgencmd file.
    The command requires a path to the vcgencmd file location
    To find path use command below and edit vcgen_cmd variable above

        which vcgencmd

    """
    res = os.popen(vcgen_cmd).readline()  # read the latest temperature from file
    try:
        temp = float((res.replace("temp=","").replace("'C\n","")))
    except:
        logging.error('Could NOT read temperature with command {}'.format(vcgen_cmd))
        logging.info('Please Investigate problem')
        prog_exit(1)

    if fan_on and temp <= setpoint_low:
        logging.info("Turn Fan OFF .. {}'C setpoint_low reached."
                     .format(setpoint_low))
        GPIO.output(fan_GPIO, False)  # send signal to NPN transistor to turn fan OFF
        fan_on = False
    elif not fan_on and temp >= setpoint_high:
        logging.info("Turn Fan ON ... {}'C setpoint_high reached."
                     .format(setpoint_high))
        GPIO.output(fan_GPIO, True)  # send signal to NPN transistor to turn fan ON
        fan_on = True

    if debug_on:
        if fan_on:
            logging.info("Fan is ON ... CPU at {}'C  ... sleep {} sec"
                         .format(temp, sleep_sec))
        else:
            logging.info("Fan is OFF .. CPU at {}'C  ... sleep {} sec"
                         .format(temp, sleep_sec))

    try:
       sleep(sleep_sec)   # Wait before the next reading
    except KeyboardInterrupt:
        print(' ')
        logging.info('Shutdown and cleanup GPIO settings')
        GPIO.cleanup()
        break

prog_exit(0)
