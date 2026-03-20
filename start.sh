#!/bin/bash

firefox --kiosk dashboard.html &

for component in can app; do
    screen -Sdm $component
    screen -r $component -p 0 -X stuff "source pyvenv/bin/activate $(printf '\r')"
    screen -r $component -p 0 -X stuff "python $component.py $(printf '\r')"
done