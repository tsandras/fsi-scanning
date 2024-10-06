from pynput.keyboard import Key, Listener

import urllib.request
import urllib.parse
import re, os, json
import logging
from dotenv import load_dotenv

load_dotenv()

keys = []
identifier = None

GTIN_REGEX = r'\b\d{8}(?:\d{4,6})?\b'


def flush_input():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys, termios    #for linux/unix
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def on_press(key):
    global keys
    try:
        if key.char and key.char.isalnum():
            keys.append(key.char)
            print('alphanumeric key {0} pressed'.format(key.char))
        else:
            print('non-alphanumeric key {0} pressed'.format(key))
    except AttributeError:
        print('special key {0} pressed'.format(key))

def send_post_request(data):
    if identifier:
        url = os.getenv('API_REPORT_PREVIEW_URL')
    else:
        url = os.getenv('API_STOCK_URL')
    if url is None:
        print('API_URL is not set')
        logging.error('API_URL is not set')
        return None

    headers = {'Content-Type': 'application/json'}
    data = json.dumps(data).encode()
    req = urllib.request.Request(url, data=data, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.read()
    except urllib.error.HTTPError as e:
        logging.error(f'HTTP error occurred: {e.code} - {e.reason}')
        return None
    except urllib.error.URLError as e:
        logging.error(f'URL error occurred: {e.reason}')
        return None
    except Exception as e:
        logging.error(f'An unexpected error occurred: {e}')
        return None
    finally:
        logging.info('send_post_request execution completed')
			
def on_release(key):
    global keys
    				
    print('{0} released'.format(key))
    if key == Key.enter:
        logging.info('enter released')
        if re.match(GTIN_REGEX, ''.join(keys)):
            data = {
                'barcode': ''.join(keys),
                'action': 'scanning',
                'identifier': identifier
            }
            response = send_post_request(data)
            if response:
                print('Response:', response)
            else:
                print('Failed to get a response')
        keys = []
    elif key == Key.esc:
        keys = []
        return False    

def keyboard_listener():
    global identifier

    log_file = './keyboard_listener.log'
    logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s - %(message)s')
    
    identifier = None  # Réinitialiser identifier si restart_listener est True
    flush_input()
    identifier = input("Veuillez entrer votre identifiant (pour faire un rapport de commande) ou appuyez sur entrée (pour un ajout de stock) : ")
    print(f'Identifiant : {identifier}')
    
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    keyboard_listener()

if __name__ == "__main__":
    keyboard_listener()
