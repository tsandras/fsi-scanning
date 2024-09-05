from dotenv import load_dotenv
import os
from urllib.parse import urlparse, quote_plus, urlunparse

load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    raw_database_url = os.getenv('DATABASE_URL')

    if raw_database_url:
        parsed_url = urlparse(raw_database_url)
        username = parsed_url.username
        password = quote_plus(parsed_url.password)
        netloc = f"{username}:{password}@{parsed_url.hostname}"
        if parsed_url.port:
            netloc += f":{parsed_url.port}"
        DATABASE_URL = urlunparse((
            parsed_url.scheme,
            netloc,
            parsed_url.path,
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment
        ))
    else:
        DATABASE_URL = None

    SQLALCHEMY_DATABASE_URI = DATABASE_URL