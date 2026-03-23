#!/bin/bash

cd /home/projetauto/Documents/automotive_architecure

for component in app can; do
    screen -X -S $component quit > /dev/null
    screen -Sdm $component
    screen -r $component -p 0 -X stuff "source pyvenv/bin/activate $(printf '\r')"
    screen -r $component -p 0 -X stuff "python $component.py $(printf '\r')"
done

firefox --kiosk dashboard.html
