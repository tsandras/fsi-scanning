from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

load_dotenv()

def has_two_at_symbols(s):
    """
    Vérifie s'il y a exactement deux symboles '@' dans la chaîne de caractères.

    :param s: La chaîne de caractères à vérifier.
    :return: True s'il y a exactement deux '@', False sinon.
    """
    return s.count('@') == 2

def split_at_second_at_symbol(s):
    """
    Divise la chaîne à la deuxième occurrence de '@'.

    :param s: La chaîne de caractères à diviser.
    :return: Un tuple contenant deux parties de la chaîne.
    """
    parts = s.split('@', 2)
    if len(parts) > 2:
        return '@'.join(parts[:2]), parts[2]
    return s, ''

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    raw_database_url = os.getenv('DATABASE_URL')

    if raw_database_url and has_two_at_symbols(raw_database_url):
        scheme, rest = raw_database_url.split('://', 1)
        username, password_and_host_info = rest.split(':', 1)
        password, host_info = split_at_second_at_symbol(password_and_host_info)
        SQLALCHEMY_USER = username
        SQLALCHEMY_PASSWORD = password
        SQLALCHEMY_HOST = host_info.split('/')[0]
        SQLALCHEMY_DB = host_info.split('/')[1]
        encoded_password = quote_plus(SQLALCHEMY_PASSWORD)
        SQLALCHEMY_DATABASE_URI = f"{scheme}://{SQLALCHEMY_USER}:{encoded_password}@{SQLALCHEMY_HOST}/{SQLALCHEMY_DB}"
    else:
        SQLALCHEMY_DATABASE_URI = raw_database_url