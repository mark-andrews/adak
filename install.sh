#!/bin/bash

# these instructions are primarily for Linux installs

VENV=$HOME/var/venvirons/psychopy2c

if [ -d $VENV ]; then
  rm -rf $VENV
fi

# because wxpython has some issue related to this:
# https://patchwork.yoctoproject.org/project/oe/patch/20240510005731.2074507-2-raj.khem@gmail.com/
# I need to use wxpython from the Arch system
python -m venv --system-site-packages $VENV

source $VENV/bin/activate

# the requirements.txt caused problems
# so I ran the individual pip commands below
#pip install setuptools
#pip install -r requirements.txt

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

# the pip version does not work with numpy 2.0 and maybe other things
# pip install psychopy --no-deps
# the current dev version of psychopy requires < 3.11
# pip install --no-deps git+https://github.com/psychopy/psychopy.git@dev
# clone the repo, change the restriction to use any Python > 3.8 and then
# pip install -e .
