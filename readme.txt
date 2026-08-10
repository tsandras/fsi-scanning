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
cp .env dist/.env
```

L’exécutable est dans `dist/scanner`. Le fichier `.env` doit être **à côté** de l’exécutable.
Ne pas utiliser `sudo` : cela ignore le venv et provoque `command not found`.

### macOS — Accessibilité (obligatoire)

Sans cette autorisation, le scan ne fonctionne pas hors focus (et plante souvent) :

1. Réglages Système → Confidentialité et sécurité → Accessibilité
2. Ajoutez `dist/scanner` (ou Terminal / iTerm si vous lancez via `python scanner.py`)
3. Relancez l’exécutable

### Utilisation

1. Lancer `dist/scanner`
2. Taper l’identifiant (ex. `AP`) puis Entrée — **ne pas scanner à cette étape**
3. Ensuite scanner librement, même sans focus sur le terminal
4. Ctrl+Escape pour changer d’identifiant
