# pifan
### Control Raspberry Pi case fan on/off using CPU temperature

### Description
Control a Raspberry 5v or 3.3v case cooling fan so it turns on
at a high temperature setpoint and off at a lower temperature setpoint.
This avoids running the fan when it is not required.  Might help reduce
dust bunnies collecting in RPI case.

This script utilizes an NPN transistor to switch power.
These can be a S8050, 2N4401 or equivalent plus approx 100-300 ohm resistor.  I had a variety
and some are close to 300 ohm without problem.  I simply soldered them together per the
wiring diagram below and used two small shrink wraps to cover resistor and connections
plus a second one for one of the remaining legs.
Then used one larger shrink wrap to encase the capacitor and all remaining wires to insulate them.

As a programming excercise I did some extra features that may
not necessariy be functionally required.

* logging library for messaging.  This also allows redirecting output to a file.
* argparse library implemented to allow changing some parameters from command line
* Optional import of variables from a config.py file.
* Added auto detection to turn off logging if being run as daemon.
* A dictionary is used to store default variables and values.  This can
be used to check missing config.py settings or can replace importing from config.py

I wrote a simple pifand.py to be used as a daemon.  This can be installed as a systemd service.

### Wiring Details
I used female jumper wires and cut one end off

The RED fan wire is connected directly to a 3.3v or 5v gpio pin.
[See gpio diagram for locations](https://www.raspberrypi.org/documentation/usage/gpio/)
also [Interactive pinout diagram](http://pinout.xyz/)

The BLACK Fan wire connects directly to one side of npn transistor.
A second black wire connects between other side of the npn transistor
then to a gpio ground pin (see a gpio diagram for locations)

A YELLOW wire (non black/red) is connected to the center lead of the npn transitor
then to one side of approx 100 - 300 ohm resistor. Other side of resistor is connected to
pin specifed by the BCM fan_GPIO variable below.
This pin turns the fan on/off based on appropriate setpoint temperatures.

```
Wiring Diagram
                       << is a male to female jumper wire
                          joint to allow easy fan connect, disconnect
                 fan
   +5V >---------[X]---<<---NPN-----------< GPIO gnd pin
    or        red   blk      |      blk
  +3.3V                      |
   pin                       $ approx 100-300 ohm resistor
                             |
                             | yellow (non black or red wire)
                             |
                            GPIO
                         control pin
```
See [Interactive pinout diagram](http://pinout.xyz/) for pin details.
Default control pin is BCM 25.  I used pin 4 for 5v power and pin 5 for ground.
They are beside each other so easier to locate.

### How to Create a Systemd Service

#### Step 1
Create a systemd service file using command below

    sudo nano /lib/systemd/system/pifand.service

Cut/Paste or Add indented text as shown below

    [Unit]
    Description=run fan when hot
    After=meadiacenter.service

    [Service]
    User=root
    Group=root
    Type=simple
    ExecStart=/usr/bin/python /home/pi/pifand.py
    Restart=Always
    # On OSMC use Restart=on-failure instead of Restart=Always
    [Install]
    WantedBy=multi-user.target

ctrl-o, ENTER, ctrl-x to save and exit the nano editor

#### Step 2
After any changes to /lib/systemd/system/pifand.service file,
execute commands below

    sudo systemctl daemon-reload
    sudo systemctl enable pifand.service
    sudo reboot

#### Step 3
Ensure the pifand.service in systemd is enabled and running, per commands below

    systemctl list-unit-files | grep enabled | grep pifand
    systemctl | grep running | grep pifand
    systemctl status pifand.service -l

If there are any issues with starting the script using systemd,
then examine the journal using commands below

    sudo journalctl -u pifand.service


