import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://fsi:pass2pass2@localhost/fsi')
    SQLALCHEMY_TRACK_MODIFICATIONS = False