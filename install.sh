#!/bin/bash

VENV=$HOME/var/venvirons/psychopy2c

if [ -d $VENV ]; then
	rm -rf $VENV
fi

virtualenv $VENV

source $VENV/bin/activate

pip install -r requirements.txt

# Previously, I just ran the following individual pip commands.
# I preferred this because at least I knew which were the main 
# packages and not dependencies.
# However, running these commands recently, and you can see there are 
# now version numbers, lead to a breaking update somewhere.
# It would be good to know exactly what that bad update was, but
# for now, I will just use the requirements from a pip freeze
# of a previously working venv.
#
# pip install --upgrade pip
# pip install attrdict3
# pip install wxpython
# pip install numpy scipy jupyter pandas matplotlib
# pip install pyyaml
# pip install tables
# pip install 'requests[security]'
# pip install 'pyglet==1.5.10'
# pip install arabic_reshaper
# pip install freetype-py
# pip install psutil
# pip install json_tricks
# pip install python-bidi
# pip install psychopy --no-deps

