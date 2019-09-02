# pifan
### Control a Raspberry Pi case cooling fan on/off using CPU temperature

### Quick Install or Upgrade
**IMPORTANT** - It is suggested you do a Raspbian ***sudo apt-get update*** and ***sudo apt-get upgrade***
before curl install

***Step 1*** With mouse left button highlight curl command in code box below. Right click mouse in **highlighted** area and Copy.
***Step 2*** On RPI putty SSH or terminal session right click, select paste then Enter to download and run script.

    curl -L https://raw.github.com/pageauc/pifan/master/pifan-install.sh | bash

The command above will download and Run the GitHub ***pifan-install.sh*** script.
An upgrade will not overwrite ***config.py*** file.

### Description
Control a Raspberry 5v or 3.3v case cooling fan so it turns on
at a high temperature setpoint and off at a lower temperature setpoint.
This avoids running the fan when it is not required.  Might also help reduce
dust bunnies collecting in RPI case if you do not have a lint filter over cooling intake.

The pifan scripts utilizes an NPN transistor to switch fan power on and off based on temperature.
Transistors can be ***S8050***, ***2N4401*** or equivalent plus approx ***100-300 ohm resistor***.
I had a variety and some are close to 300 ohms and worked without problem.
I simply soldered the project together per the wiring diagram below and used
two small shrink wraps to cover resistor solder connections and
the second for one fan connection wire solder connection.
I then used one larger shrink wrap to encase the capacitor and all three soldered wires to insulate them.
Electrical tape can also be used.

On the ***pifan.py*** script I did some extra programming as a learning excercise. The extra features are
not necessary for operation but I enjoyed adding them. This script can be used for testing operation.

### Wiring Details
I used female jumper wires and cut one end off to a convenient length to avoid excess wire inside
the RPI case.

The RED fan wire is connected directly to a 3.3v or 5v gpio pin.
See [GPIO diagram](https://www.raspberrypi.org/documentation/usage/gpio/) for pin locations
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
   +5V >---------[X]---<<---NPN-----------< GPIO ground pin
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

### pifan.py Features
As a programming excercise I wrote some extra ***pifand.py*** features that
may not necessariy be functionally required.

* logging library for messaging.  This also allows redirecting output to a file.
* argparse library implemented to allow changing some parameters from command line
* Optional import of variables from a config.py file.
* Added auto detection to turn off logging if being run as daemon.
* A dictionary is used to store default variables and values.  This can
be used to check missing config.py settings or can replace importing from config.py

program optional arguments

usage: pifan.py [-h] [-f {on,off,auto}] [-p PINNUMBER] [-s] [-v] [-d] [-q]

Control Fan using NPN transistor and Temperature Settings
```
optional arguments:
  -h, --help            show this help message and exit
  -f {on,off,auto}, --fanmode {on,off,auto}
                        Fan Control modes. Valid values are on, off or auto
  -p PINNUMBER, --pinnumber PINNUMBER
                        Valid Fan BCM GPIO Control Pin Number (integer)
  -s, --status          Checks Status of Fan and Temperature readings from
                        pifand.service or Other Fan Control script.
  -v, --verbose         Turn on verbose logging
  -d, --debug           Add detailed fan and temp logging messages
  -q, --quiet           Turn off verbose logging
```

### pifand.py
I wrote pifand.py to be used as a systemd service daemon.  The file can be run as a
background task or installed as a systemd service per instructions below.
Note the differences between the pifan.py and pifand.py scripts.
Both do the same job but pifand.py is very minimalistic.

### Testing
To test, connect the soldered NPN transistor assembly to the appropriate pins.
***NOTE***: Power OFF the RPI just to be safe, then connect the soldered NPN transistor assembly per the following.

* Red fan wire to 5v GPIO pin 4
* Black NPN ground wire to GPIO pin 5
* Yellow (non black,red) wire to BCM GPIO pin 25

With the RPI running, open an ssh or terminal session and start the pifan.py script in debug mode.

    cd ~/pifan
    ./pifan.py -h   # display parameter options
    ./pifan.py -d   # Note. -v mode just displays message when fan turns ON or OFF at setpoints

Debug mode will display the temperature and fan status every 10 seconds by default.
You can change variable settings in config.py per comments using nano editor.

Open a second ssh or terminal session. In order to increase the RPI temperature
you will need to run a program to stress the cpu. Install and run stress per the
following commands.

    sudo apt-get install -y stress     # Installed as part of github curl install
    stress -c 4   # runs quad core cpu's at 100% or -c 2 for dual core

In the first terminal session you should see temperature rise. Fan should turn ON
at 65'C or greater. If not check connections and possibly solder joints.

Press cntrl-c to exit stress.  The temperature should decrease and
the fan should stop at 55'C or less.

To display help on stress program features execute

    stress
or
    stress --help

You can monitor cpu and other system data by opening another ssh or
terminal sessionby running and running htop per command below

   htop

type q or cntrl-c to exit htop

To check GPIO pin status while pifan.py is running you can run

    ./chkpins.py

select 1 for display by board pin order or 2 or enter for BCM GPIO order.
If pifan.py or pifand.py are running then you should see a GPIO.OUT on the
fan control pin (default BCM GPIO pin 25 or Board pin 22)

If everything runs OK you can install pifand.py as a systemd service.

### How to Manually Create a pifand Systemd Service

#### Step 1 Checks
Check that ***/usr/bin/vcgencmd*** command reads current RPI temperature per.

    /usr/bin/vcgencmd measure_temp

This should return the current cpu temperature.

If there is a problem, find path to ***vcgencmd*** using command below.

    which vcgencmd

If path is Not ***/usr/bin/vcgencmd*** Then nano edit ***config.py***
and ***pifand.py*** change ***VCGENCMD_PATH=*** variable

Check that pifand.service file ***ExecStart=*** entry is correct path and settings.

    cd ~/pifand
    more pifand.service

Change file pifand.service settings using nano if required.

Check that ***pifand.py*** variable settings are correct and change if required.
***NOTE:*** variables are hard coded in pifand.py and do NOT read config.py settings.
This is done to simplify script operations while running as service.  See Alternative Below.

    nano pifand.py

Edit the User Variable Settings as required then ctrl-x y to save and exit nano.

##### Alternative
Instead of using ***pifand.py*** you can run ***pifan.py -q*** in the pifand.service file.
***pifan.py*** can read variables settings from the ***config.py*** file.  
This makes it handy to change settings if require, rather than having to 
edit the variables in the ***~/pifan/pifand.py*** file.

***NOTE:*** If ***pifan.py*** file is used in the ***pifand.service*** file,
and a ***config.py*** file does not exist then the dictionary ***CONFIG_SETTINGS*** settings are used.

    cd ~/pifan
    nano pifand.service

In nano change ***ExecStart=/usr/bin/python /home/pi/pifan/pifan.py -q*** then ctr-x y to save and exit

#### Step 2
A template copy of the ***pifand.service*** is downloaded with github curl install of ***pifan-install.sh***
To install this copy perform the following

    cd ~/pifan
    sudo cp pifand.service /lib/systemd/system/pifand.service

Progress to Step 3

or

To manually Create or Edit the systemd pifand.service file use command below

    sudo nano /lib/systemd/system/pifand.service

If ***/lib/systemd/system/pifand.service*** file is blank Cut/Paste or Add text as shown below
(does not need to be indented).

```
[Unit]
Description=run fan when hot
After=meadiacenter.service

[Service]
User=root
Group=root
Type=simple
ExecStart=/usr/bin/python /home/pi/pifan/pifand.py
Restart=Always
# On OSMC use Restart=on-failure instead of Restart=Always

[Install]
WantedBy=multi-user.target
```

ctrl-x y to save file and exit the nano editor

#### Step 3
After any changes to ***/lib/systemd/system/pifand.service*** file,
execute commands below

    sudo systemctl daemon-reload
    sudo systemctl enable pifand.service
    sudo reboot

#### Step 4
Ensure the pifand.service in systemd is enabled and running, per commands below

    systemctl list-unit-files | grep enabled | grep pifand
    systemctl | grep running | grep pifand
    systemctl status pifand.service -l

If there are any issues with starting the script using systemd,
then examine the journal using commands below

    sudo journalctl -u pifand.service

### cpu-temp.py
If you have pifand.py running as a systemd service or background task,
you can check the RPI temperature using the ***cpu-temp.py*** script per

    cd ~/pifan
    ./cpu-temp.py

This will display the temperature every 5 seconds by default.
To change delay edit the ***cpu-temp.py*** file using nano.

    cd ~/pifan
    nano cpu-temp.py

Then change the ***sleep_seconds*** variable.  ctl-x y to save and exit

Alternatively you can check fan and temperature status by running the following
command

    cd ~/pifan
    ./pifan.py -s

***NOTE:*** If the fan control pin is not enabled then ***pifan.py*** ***-s*** will
display a warning message and exit.

### Get Help

Post an [issue](https://github.com/pageauc/pifan/issues) to github pifan repo if you need help.

Claude ....