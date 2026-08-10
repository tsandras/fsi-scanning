from pynput.keyboard import Key, Listener

import urllib.request
import urllib.error
import re
import os
import sys
import json
import logging
from pathlib import Path

from dotenv import load_dotenv


def app_dir() -> Path:
    """Directory of the script, or of the PyInstaller binary."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


load_dotenv(app_dir() / '.env')

keys = []
identifier = None
ctrl_pressed = False

GTIN_REGEX = r'\b\d{8}(?:\d{4,6})?\b'
CTRL_KEYS = {Key.ctrl, Key.ctrl_l, Key.ctrl_r}


def flush_input():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import termios
        try:
            termios.tcflush(sys.stdin, termios.TCIOFLUSH)
        except Exception:
            pass


def is_accessibility_trusted() -> bool:
    if sys.platform != 'darwin':
        return True
    try:
        from ApplicationServices import AXIsProcessTrusted
        return bool(AXIsProcessTrusted())
    except Exception:
        return True


def warn_accessibility_if_needed():
    if is_accessibility_trusted():
        return
    exe = sys.executable if getattr(sys, 'frozen', False) else sys.executable
    print()
    print('=' * 60)
    print('macOS : autorisation Accessibilité manquante.')
    print('Sans elle, le scan ne marche PAS hors focus du terminal.')
    print()
    print('Réglages Système → Confidentialité et sécurité → Accessibilité')
    print(f'Ajoutez : {exe}')
    print('Puis relancez cette application.')
    print('=' * 60)
    print()


def on_press(key):
    global keys, ctrl_pressed
    if key in CTRL_KEYS:
        ctrl_pressed = True
        return
    try:
        if key.char and key.char.isalnum():
            keys.append(key.char)
    except AttributeError:
        pass


def send_post_request(data):
    if identifier:
        url = os.getenv('API_REPORT_PREVIEW_URL')
        target = 'report_preview'
    else:
        url = os.getenv('API_STOCK_URL')
        target = 'stock'

    if not url:
        print(f'API URL manquante pour {target} (vérifiez le fichier .env à côté de l’exécutable)')
        logging.error('API_URL is not set for %s', target)
        return None

    api_key = os.getenv('API_KEY')
    headers = {'Content-Type': 'application/json'}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'

    payload = json.dumps(data).encode()
    req = urllib.request.Request(url, data=payload, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            return response.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors='replace') if e.fp else ''
        logging.error('HTTP error: %s %s — %s', e.code, e.reason, body)
        print(f'Erreur HTTP {e.code}: {e.reason} {body}')
        return None
    except urllib.error.URLError as e:
        logging.error('URL error: %s', e.reason)
        print(f'Erreur réseau: {e.reason}')
        return None
    except Exception as e:
        logging.error('Unexpected error: %s', e)
        print(f'Erreur: {e}')
        return None


def on_release(key):
    global keys, ctrl_pressed

    if key in CTRL_KEYS:
        ctrl_pressed = False
        return

    if key == Key.enter:
        barcode = ''.join(keys)
        keys = []
        logging.info('enter released — buffer=%s identifier=%s', barcode, identifier)
        if not re.match(GTIN_REGEX, barcode):
            if barcode:
                print(f'Ignoré (pas un GTIN): {barcode!r}')
            return

        data = {
            'barcode': barcode,
            'action': 'scanning',
            'identifier': identifier,
        }
        mode = f'rapport ({identifier})' if identifier else 'stock'
        print(f'Scan {barcode} → {mode}')
        response = send_post_request(data)
        if response:
            print('Response:', response.decode(errors='replace') if isinstance(response, bytes) else response)
        else:
            print('Échec de l’envoi')
    elif key == Key.esc and ctrl_pressed:
        keys = []
        ctrl_pressed = False
        print('Ctrl+Escape : réinitialisation de l’identifiant…')
        return False


def prompt_identifier():
    flush_input()
    print()
    print('Entrez votre identifiant puis Entrée (rapport de commande),')
    print('ou Entrée seul (ajout de stock).')
    print('Ne scannez PAS encore un code-barres à cette étape.')
    value = input('Identifiant : ').strip()
    return value or None


def keyboard_listener():
    global identifier

    log_file = app_dir() / 'keyboard_listener.log'
    logging.basicConfig(
        filename=str(log_file),
        level=logging.DEBUG,
        format='%(asctime)s - %(message)s',
        force=True,
    )

    warn_accessibility_if_needed()

    while True:
        identifier = prompt_identifier()
        print(f'Identifiant actif : {identifier or "(aucun — mode stock)"}')
        print('Prêt à scanner (fonctionne même sans focus sur le terminal).')
        print('Ctrl+Escape = changer d’identifiant.')
        print()

        try:
            with Listener(on_press=on_press, on_release=on_release) as listener:
                listener.join()
        except Exception as e:
            logging.exception('Listener stopped with error')
            print(f'Écoute clavier interrompue: {e}')
            warn_accessibility_if_needed()
            print('Nouvelle tentative…')


if __name__ == '__main__':
    keyboard_listener()
