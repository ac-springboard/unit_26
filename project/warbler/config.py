import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', "it's a secret")
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ConfigDev(Config):
    FLASK_ENV = 'development'
    FLASK_APP = 'app.py'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://acampos:root@localhost:3306/unit_26')
