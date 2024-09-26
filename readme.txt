# Projet de Scanning API

pip install -r requirements.txt

## ugly restart on production

killall gunicorn
/var/www/fsi-scanning/fsi/bin/gunicorn -c gunicorn_config.py api:app

## Run on production without need to restart

/var/www/fsi-scanning/fsi/bin/gunicorn -c gunicorn_config.py api:app --reload --daemon