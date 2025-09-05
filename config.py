import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir,'.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "oh i'm pretty sure you'll never guess"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
    'sqlite:///' + os.path.join(basedir,'app.db')
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = True 
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['theo228boss@gmail.com']
    POSTS_PER_PAGE = 15
    LANGUAGES = ['en','fr']