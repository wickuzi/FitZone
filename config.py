class Config:
    SECRET_KEY = 'FitZone'

class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER='root'
    MYSQL_PASSWORD='123'
    MYSQL_DB = 'fitzone'


config = {
    'development': DevelopmentConfig
}