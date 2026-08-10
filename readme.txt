# Projet de Scanning API

## Installation (macOS)

Utiliser Python 3.13 (pas 3.14) : certaines dépendances natives (`greenlet`, etc.)
ne compilent pas encore avec Python 3.14.

```bash
# Si besoin : brew install python@3.13
rm -rf fsi
python3.13 -m venv fsi
source fsi/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Pour vérifier la version du venv : `fsi/bin/python --version`

## ugly restart on production

killall gunicorn
/var/www/fsi-scanning/fsi/bin/gunicorn -c gunicorn_config.py api:app

## Run on production without need to restart

/var/www/fsi-scanning/fsi/bin/gunicorn -c gunicorn_config.py api:app --reload --daemon

## How to create exec

Avec le venv activé (`source fsi/bin/activate`) :

```bash
pip install pyinstaller
pyinstaller --onefile scanner.py
```

L’exécutable est généré dans `dist/scanner`.
Ne pas utiliser `sudo` : cela ignore le venv et provoque `command not found`.
