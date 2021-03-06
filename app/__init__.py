import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from flask.ext.mail import Mail
from .momentjs import momentjs
from config import *

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

app.jinja_env.globals['momentjs'] = momentjs

#setting up the email notifications in case of production server failure
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    mail = Mail(app)
    #setting up the log files
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/microblag.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('microblag startup')

from app import views, models
