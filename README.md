# Installation

- installer le pyvenv avec `python -m venv pyvenv`
- installer les librairies nécessaire via `pip install flask flask-cors`
- lancer l'application via `./start.sh`
- lancer la page html dashbaord.html

# Ouvrir l'application en plein écran ssh 

Ouvrir avec

```bash
ssh -X user@ip_adress
export DISPLAY=:0
firefox --kiosk dashboard.html &
```
