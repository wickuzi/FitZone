import os

class DevelopmentConfig:
    DEBUG = True
    SECRET_KEY = 'fitzone'
    DB_HOST = 'localhost'
    DB_NAME = 'fitzone_db'
    DB_USER = 'postgres'
    DB_PASSWORD = '123'
    DB_PORT = 5432
    DATABASE_URL = os.getenv('DATABASE_URL') or \
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

config = {
    'development': DevelopmentConfig
}

