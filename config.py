from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://fsi:pass2pass2@localhost/fsi')
    SQLALCHEMY_TRACK_MODIFICATIONS = False