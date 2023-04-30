#!/bin/bash

VENV=$HOME/var/venvirons/psychopy2

if [ -d $VENV ]; then
	rm -rf $VENV
fi

virtualenv $VENV

source $VENV/bin/activate

pip install --upgrade pip
pip install attrdict3
pip install wxpython
pip install numpy scipy jupyter pandas matplotlib
pip install pyyaml
pip install tables
pip install 'requests[security]'
pip install 'pyglet==1.5.10'
pip install arabic_reshaper
pip install freetype-py
pip install psutil
pip install json_tricks
pip install python-bidi
pip install psychopy --no-deps

