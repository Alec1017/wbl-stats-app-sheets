from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config
from stats_compiler import StatsCompiler
from slack import SlackBot
from email import Emailer
from app.google_sheets import authenticate_sheet

db = SQLAlchemy()
migrate = Migrate()

sheet_api = authenticate_sheet()
slack_bot = SlackBot()
emailer = Emailer()

compiler = StatsCompiler(sheet_api)


def create_app(config_class=Config):
  app = Flask(__name__)
  app.config.from_object(Config)
 
  db.init_app(app)
  migrate.init_app(app, db)
  slack_bot.init_app(app)
  emailer.init_app(app)
  compiler.init_app(app, slack_bot, emailer)

  from app.api import api
  app.register_blueprint(api, url_prefix='/api')

  from app.auth import auth
  app.register_blueprint(auth, url_prefix='/auth')

  from app.portal import portal
  app.register_blueprint(portal)

  return app
