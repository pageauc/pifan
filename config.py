# Variable Settings for t-fan.py
# ---------------------------------
VERBOSE = True      # logs when fan is turned on or off.
DEBUG_ON = True     # Add detailed fan and temp logging status messages.
LOG_TO_FILE = False # Send log messages to a log file.
FORCE_FAN_ON = False # Force the fan to stay on all the time then exit
FAN_GPIO = 25       # connect npn transistor center lead + resistor to this pin
SETPOINT_HIGH = 65  # deg C of fam os off turn it on at this temperature
SETPOINT_LOW  = 55  # deg C if fan is on turn it off at this temperature
SLEEP_SEC = 10      # seconds to wait between readings
VCGENCMD_PATH = '/usr/bin/vcgencmd' # Path to command to retrieve temperature data
