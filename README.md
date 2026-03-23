# Installation

- installer le pyvenv avec `python -m venv pyvenv`
- installer les librairies nécessaire via `pip install flask flask-cors spidev requests python-can`
- préparer le service qui permettra le lancement automatique via la création d'un fichier service `dashboard_auto.service` dans le dossier `~/.config/systemd/user/`
- y coller le contenu du fichier service présent dans ce repo
- l'activer via :
```bash
sudo chmod 664 /etc/systemd/system/dashboard_auto.service
systemctl --user daemon-reload
systemctl --user enable dashboard_auto.service
sudo loginctl enable-linger $USER
```
- on peut vérifier l'état du service après le démarrage via `systemctl --user startus dashboard_auto.service`

# How To Screen

- on rejoint un screen existant via `screen -x [nom du screen]`
- on le quitte via 'ctrl+a' puis 'd'
- on le termine via 'ctrl+a' puis 'k'
- on les liste via `screen -ls`
