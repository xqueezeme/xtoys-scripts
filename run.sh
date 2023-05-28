#!/bin/bash
killall chromimum-browser
git pull origin
#python3 -m pip install --upgrade pip
#python3 -m pip install -r requirements.txt
unbuffer python3 script.py |& tee -a script.log
git add .
git commit -am "Automatic update"
git push origin
killall chromimum-browser
