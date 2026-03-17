# Installation

- installer le pyvenv avec `python -m venv pyvenv`
- installer les librairies nécessaire via `pip install flask flask-cors`

# Ouvrir l'application en plein écran ssh 

- créer un screen s'il n'y en a pas déjà `screen -S projet` (si "No Sockets..." quand on fait `screen ls`)
- ouvrir avec `firefox --kiosk dashboard.html &`
- lancer le serveur via `./start.sh`

# Screen

- on rejoint un screen existant via `screen -x [nom du screen]`
- on le quitte via 'ctrl+a' puis 'd'
- on le termine via 'ctrl+a' puis 'k'
- on les liste via `screen -ls`
