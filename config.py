# Variable Settings for t-fan.py
# ---------------------------------
verbose = True      # logs when fan is turned on or off.
debug_on = True     # Add detailed fan and temp logging status messages.
log_to_file = False # Send log messages to a log file.
force_fan_on = False # Force the fan to stay on all the time then exit
fan_GPIO = 25       # connect npn transistor center lead + resistor to this pin
setpoint_high = 65  # deg C of fam os off turn it on at this temperature
setpoint_low  = 55  # deg C if fan is on turn it off at this temperature
sleep_sec = 10      # seconds to wait between readings
vcgencmd_path = '/usr/bin/vcgencmd' # Path to command to retrieve temperature data
