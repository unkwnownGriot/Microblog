from flask import Flask, request,current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel, lazy_gettext as _l
from flask_migrate import Migrate
import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
from flask_moment import Moment
import os
from elasticsearch import Elasticsearch
from flask_login import LoginManager
from flask_mail import Mail

# Getting the user locale_selector settings

def get_locale():
     return request.accept_languages.best_match(current_app.config['LANGUAGES'])


## Creating instances of flask extension withiut initializing them

login = LoginManager()
login.login_view = 'auth.login'
login.login_message =_l('Please log in to access this page')
#E-Mail Logic initialisation
mail = Mail()
#Momentinitialisation for date formatting
moment = Moment()
# database initialisation
db = SQLAlchemy()
migrate = Migrate()
#Initializing the babel module
babel = Babel()

## creating a new instance of flask app instead of a global variable
def create_app(config_class=Config):
    # flask app initialisation
    flask_app = Flask(__name__)

    # flask app configuration
    flask_app.config.from_object(config_class)

    flask_app.elasticsearch = Elasticsearch(flask_app.config['ELASTICSEARCH_URL']) \
        if flask_app.config['ELASTICSEARCH_URL'] else None

    #initialisation
    db.init_app(flask_app)
    login.init_app(flask_app)
    moment.init_app(flask_app)
    babel.init_app(flask_app)
    migrate.init_app(flask_app,db)
    mail.init_app(flask_app)
    
    # Registering my blueprints 

    from app.errors import bp as errors_bp
    from app.auth import bp as auth_bp
    from app.main import bp as main_bp
    from app.cli import bp as cli_bp
    flask_app.register_blueprint(errors_bp)
    flask_app.register_blueprint(cli_bp)
    flask_app.register_blueprint(auth_bp,url_prefix='/auth')
    flask_app.register_blueprint(main_bp,url_prefix='/main')

    # email server intialisation

    if not flask_app.debug and not flask_app.testing:
        if flask_app.config['MAIL_SERVER']:
            auth = None
            if flask_app.config['MAIL_USERNAME'] or flask_app.config['MAIL_PASSWORD']:
                auth = (flask_app.config['MAIL_USERNAME'], flask_app.config['MAIL_PASSWORD'])
            secure = None
            if flask_app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(flask_app.config['MAIL_SERVER'], flask_app.config['MAIL_PORT']),
                fromaddr='no-reply@' + flask_app.config['MAIL_SERVER'],
                toaddrs=flask_app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            flask_app.logger.addHandler(mail_handler)

            # File error log initialisation
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/microblog.log',maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            flask_app.logger.addHandler(file_handler)

            flask_app.logger.setLevel(logging.INFO)
            flask_app.logger.info('Microblog startup')

    return flask_app



from app import models