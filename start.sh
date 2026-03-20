git pull
source pyvenv/bin/activate
firefox --kiosk dashboard.html &
python read_sensor.py &
python app.py