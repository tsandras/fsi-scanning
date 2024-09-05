from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    raw_database_url = os.getenv('DATABASE_URL')

    if raw_database_url:
        parts = raw_database_url.split('@')
        user_info = parts[0].split('//')[1]
        user, password = user_info.split(':')
        encoded_password = quote_plus(password)
        user_info_encoded = f'{user}:{encoded_password}'
        DATABASE_URL = raw_database_url.replace(user_info, user_info_encoded)
    else:
        DATABASE_URL = None

    SQLALCHEMY_DATABASE_URI = DATABASE_URL