#!/bin/bash
killall chromimum-browser
git add .
git commit -am "Automatic update"
git push origin

git pull origin
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 script.py
git add .
git commit -am "Automatic update"
git push origin
killall chromimum-browser
