# pifan
### Control Raspberry Pi case fan on/off using CPU temperature

### Quick Install or Upgrade
**IMPORTANT** - It is suggested you do a Raspbian ***sudo apt-get update*** and ***sudo apt-get upgrade***
before curl install

***Step 1*** With mouse left button highlight curl command in code box below. Right click mouse in **highlighted** area and Copy.
***Step 2*** On RPI putty SSH or terminal session right click, select paste then Enter to download and run script.

    curl -L https://raw.github.com/pageauc/pifan/master/pifan-install.sh | bash

The command above will download and Run the GitHub ***pifan-install.sh*** script.
An upgrade will not overwrite configuration files.

### Description
Control a Raspberry 5v or 3.3v case cooling fan so it turns on
at a high temperature setpoint and off at a lower temperature setpoint.
This avoids running the fan when it is not required.  Might help reduce
dust bunnies collecting in RPI case.

The pifan scripts utilizes an NPN transistor to switch power fan on and off based on temperature.
Transistors can be S8050, 2N4401 or equivalent plus approx 100-300 ohm resistor.  I had a variety
and some are close to 300 ohms without problem.  I simply soldered the project together per the
wiring diagram below and used two small shrink wraps to cover resistor solder connections and
the second for one fan connection wire solder connection.
I then used one larger shrink wrap to encase the capacitor and all three soldered wires to insulate them.

On the pifan.py script I did some extra programming as a learning excercise. The extra features are
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

### pifand.py
I wrote pifand.py to be used as a systemd service daemon.  The file can be run as a
background task or installed as a systemd service per instructions below.
Note the differences between the pifan.py and pifand.py scripts.
Both do the same job but pifand.py is very minimalistic.

### Testing
To test, connect the soldered NPN transistor assembly to the appropriate pins.
power off the RPI just to be safe then connect the soldered NPN transistor assembly per the following.

* Red fan wire to 5v GPIO pin 4
* Black NPN ground wire to GPIO pin 5
* Yellow (non black,red) wire to BCM GPIO pin 25

With the RPI running, open an ssh or terminal session and start the pifan.py script in debug mode.

    cd ~/pifan
    ./pifan.py -h   # display parameter options
    ./pifan.py -d   # Note. -v mode just display message when fan turns ON or OFF

Debug mode will display the temperature and fan status every 10 seconds by default.
You can change variable settings in config.py per comments using nano editor.

Open a second ssh or terminal session. In order to increase the RPI temperature
you will need to run a program to stress the cpu. Install and run stress per the
following commands.

    sudo apt-get install -y stress
    stress -c 4   # runs quad core cpu's at 100%

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

If everything runs OK you can install pifand.py as a systemd service.

### How to Manually Create a pifand Systemd Service

#### Step 1
A template copy of the pifand.service is downloaded with github curl install of pifan-install.sh
To install this copy perform the following

    cd ~/pifan
    sudo cp pifand.service /lib/systemd/system/pifand.service

Progress to Step 2

or

To manually Create or Edit the systemd pifand.service file use command below

    sudo nano /lib/systemd/system/pifand.service

If ***/lib/systemd/system/pifand.service*** file is blank Cut/Paste or Add text as shown below (does not need to be indented).

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

### cpu-temp.py
If you have pifand.py running as a systemd service or background task,
you can check the RPI temperature using the cpu-temp.py script per

    cd ~/pifan
    ./cpu-temp.py

This will display the temperature every 5 seconds by default.  To change delay edit
cpu-temp.py using nano and change the ***sleep_seconds*** variable.  ctl-x y to save and exit

Post an [issue](https://github.com/pageauc/pifan/issues) to github repo if you need help.

Good Luck ...