class Config:
    SECRET_KEY = 'FitZone'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123@localhost/fitzone'

config = {
    'development': DevelopmentConfig
}
