from pynput.keyboard import Key, Listener

import urllib.request
import urllib.parse
import re, os, json
import logging
from dotenv import load_dotenv

load_dotenv()

keys = []

GTIN_REGEX = r'\b\d{8}(?:\d{4,6})?\b'

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
    url = os.getenv('API_URL')
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
            data = {'barcode': ''.join(keys), 'action': 'scanning'}
            response = send_post_request(data)
            if response:
                print('Response:', response)
            else:
                print('Failed to get a response')
        keys = []

def keyboard_listener():
    log_file = './keyboard_listener.log'
    logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s - %(message)s')
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    keyboard_listener()
