#!/usr/bin/env python

"""
t-fand.py written by Claude Pageau:

To start t-fand.py automatically using systemd

Step 1 Create a systemd service file using command below

    sudo nano /lib/systemd/system/t-fand.service

    Cut/Paste or Add indented text as shown below

    [Unit]
    Description=run fan when hot
    After=meadiacenter.service

    [Service]
    # If User and Group are not specified as root, then it won't work
    User=root
    Group=root
    Type=simple
    ExecStart=/usr/bin/python /home/pi/t-fand.py
    # delete this line: on OSMC use Restart=on-failure instead of Restart=Always
    Restart=Always

    [Install]
    WantedBy=multi-user.target

    ctrl-o, ENTER, ctrl-x to save and exit the nano editor

Step 2 After any changes to /lib/systemd/system/t-fand.service file
       execute commands below

    sudo systemctl daemon-reload
    sudo systemctl enable t-fand.service
    sudo reboot

Step 3 Ensure the run-fan.service in systemd is enabled and running:
       per commands below

    systemctl list-unit-files | grep enabled | grep t-fand
    systemctl | grep running | grep fan
    systemctl status t-fand.service -l

    If there are any issues with starting the script using systemd,
    then examine the journal using:

    sudo journalctl -u t-fand.service

Wiring Details
==============

The RED fan wire is connected directly to a 3.3V or 5V gpio pin. (See gpio diagram for locations)

The BLACK Fan wire connects directly to one side of npn transistor.
A second black wire connects between other side of the npn transistor
then to a gpio ground pin (see a gpio diagram for locations)

A YELLOW wire (non black/red) is connected to the center lead of the npn transitor
then to one side of approx 100 - 200 ohm resistor. Other side of resistor is connected to
pin specifed by the BCM fan_GPIO variable below.
This pin turns the fan on/off based on appropriate setpoint temperatures.

Wiring Diagram
                 fan
   +5V >---------[x]--------NPN------------> GPIO GND pin
    or      red       blk    |      blk
  +3.3V                      |
   pin                       $ approx 100-200 ohm resistor
                             |
                             | yellow (non black or red)
                             |
                            GPIO
                         control pin

"""

# Import python libraries ...
import os
from time import sleep
import RPi.GPIO as GPIO

# User Variable Settings
# ----------------------

fan_GPIO = 25       # connect npn transistor center lead + resistor to this pin
setpoint_high = 65  # deg C of fam os off turn it on at this temperature
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
    command below reads the current temperature from the vcgencmd file.
    The command requires a path to the vcgencmd file location
    To find path use command below and edit vcgen_cmd variable above

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
