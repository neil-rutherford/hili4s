import os
from os.path import join, dirname
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

#dotenv_path = join(dirname(__file__), '.env')
#load_dotenv(dotenv_path)

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    database_uri = os.environ.get('DATABASE_URL')
    if database_uri[0:11] == 'postgres://':
        SQLALCHEMY_DATABASE_URI = 'postgresql://' + database_uri.split('//')[1]
    elif not database_uri:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    else:
        SQLALCHEMY_DATABASE_URI = database_uri


    SQLALCHEMY_TRACK_MODIFICATIONS = False

    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY') or '123'
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY') or '123'

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    TRAP_HTTP_EXCEPTIONS = True
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')