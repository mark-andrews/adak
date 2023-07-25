#!/bin/bash

VENV=$HOME/var/venvirons/psychopy2c

if [ -d $VENV ]; then
	rm -rf $VENV
fi

virtualenv $VENV

source $VENV/bin/activate

pip install -r requirements.txt
