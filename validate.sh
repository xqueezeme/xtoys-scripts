#!/bin/bash
killall chromimum-browser
git add .
git commit -am "Automatic update"
git push origin

git pull origin
#python3 -m pip install --upgrade pip
#python3 -m pip install -r requirements.txt
python3 validate.py
git add .
git commit -am "Automatic update"
git push origin
killall chromimum-browser