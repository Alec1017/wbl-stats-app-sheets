from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_assets import Environment, Bundle
# from sassutils.wsgi import SassMiddleware
# import sass

from config import Production
from app.slack import SlackBot
from app.email import Emailer
from app.google_sheets import authenticate_sheet
from app.assets import bundles

db = SQLAlchemy()
migrate = Migrate()

sheet_api = authenticate_sheet()
slack_bot = SlackBot()
emailer = Emailer()

from app.stats_compiler import StatsCompiler
compiler = StatsCompiler(sheet_api)


def create_app(config_class):
  """ Application factory

    Args:
        config_class: loads the app configuration
    Returns:
        The Flask application object
  """

  app = Flask(__name__)
  app.config.from_object(config_class)
 
  db.init_app(app)
  migrate.init_app(app, db)
  slack_bot.init_app(app)
  emailer.init_app(app)
  compiler.init_app(app, slack_bot, emailer)

  assets = Environment(app)
  assets.register(bundles)

  from app.api import api
  app.register_blueprint(api, url_prefix='/api')

  from app.auth import auth
  app.register_blueprint(auth, url_prefix='/auth')

  from app.portal import portal
  app.register_blueprint(portal)

  # if app.config['TESTING']:
  #   app.wsgi_app = SassMiddleware(app.wsgi_app, {
  #     'app': ('assets', 'static', '/static')
  #   })
  # else:
  #   sass.compile(dirname=('app/static', 'app/assets'))

  return app
