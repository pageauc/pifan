#!/bin/bash
# Convenient pi-timolo-install.sh script written by Claude Pageau 1-Jul-2016
ver="1.3"
progName=$(basename -- "$0")
PROG_DIR='pifan'  # Default folder install location

cd ~
is_upgrade=false
if [ -d "$PROG_DIR" ] ; then
  STATUS="Upgrade"
  echo "INFO  : Upgrade pifan files"
  is_upgrade=true
else
  echo "INFO  : New pifan Install"
  STATUS="New Install"
  mkdir -p $PROG_DIR
  echo "INFO  : $PROG_DIR Folder Created"
fi

cd $PROG_DIR
INSTALL_PATH=$( pwd )

# Remember where this script was launched from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "
-------------------------------------------------------------
INFO  : $progName $ver  written by Claude Pageau
        $STATUS from https://github.com/pageauc/pifan
-------------------------------------------------------------
"
# check if this is an upgrade and bypass update of configuration files
if $is_upgrade ; then
  progFiles=("pifan.py" "pifand.py" "cpu-temp.py" \
"chkpins.py" "pifand.service" "README.md")
  wget -O config.py.new -q https://raw.github.com/pageauc/pifan/master/config.py
else   # New Install
  progFiles=("config.py" "pifan.py" "pifand.py" "cpu-temp.py" \
"chkpins.py" "pifand.service" "README.md")
fi

for fname in "${progFiles[@]}" ; do
    wget_output=$(wget -O $fname -q --show-progress https://raw.github.com/pageauc/pifan/master/$fname)
    if [ $? -ne 0 ]; then
        wget_output=$(wget -O $fname -q https://raw.github.com/pageauc/pifan/master/$fname)
        if [ $? -ne 0 ]; then
            echo "ERROR : $fname wget Download Failed. Possible Cause Internet Problem."
        else
            wget -O $fname https://raw.github.com/pageauc/pifan/master/$fname
        fi
    fi
done

chmod +x cpu-temp.py pifan.py pifand.py chkpins.py

echo "INFO  : $STATUS Install Support Files  Wait ..."
sudo apt-get install -yq stress
sudo apt-get install -yq htop
echo "INFO  : $STATUS Done Support Files Install"

# Check if pifan-install.sh was launched from pifan folder
if [ "$DIR" != "$INSTALL_PATH" ]; then
  if [ -f 'pifan-install.sh' ]; then
    echo "INFO  : $STATUS Cleanup pifan-install.sh"
    rm pifan-install.sh
  fi
fi

echo "
-----------------------------------------------
INFO  : $STATUS Complete
-----------------------------------------------
Minimal Instructions:
1 - It is suggested you run sudo apt-get update and sudo apt-get upgrade
    Reboot RPI if there are significant Raspbian system updates.
2 - If config.py already exists then latest file is config.py.new
3 - To Test Run pifan.py after installing the NPN transitor fan switch assembly
    execute the following commands in RPI SSH or terminal session.

    cd ~/pifan
    ./pifan.py -v

For Full Instructions See https://github.com/pageauc/pifan/README.md

Good Luck Claude ...
Bye"

