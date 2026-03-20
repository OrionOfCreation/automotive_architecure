#!/bin/bash

git pull

source pyvenv/bin/activate

firefox --kiosk dashboard.html &

screen -S sensor
screen -r sensor -p 0 -X stuff "python read_sensor.py $(printf '\r')"

screen -S app
screen -r app -p 0 -X stuff "python app.py $(printf '\r')"