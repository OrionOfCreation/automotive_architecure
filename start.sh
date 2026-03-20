#!/bin/bash

firefox --kiosk dashboard.html &

screen -S sensor
screen -r sensor -p 0 -X stuff "source pyvenv/bin/activate $(printf '\r')"
screen -r sensor -p 0 -X stuff "python read_sensor.py $(printf '\r')"

screen -S app
screen -r app -p 0 -X stuff "source pyvenv/bin/activate $(printf '\r')"
screen -r app -p 0 -X stuff "python app.py $(printf '\r')"