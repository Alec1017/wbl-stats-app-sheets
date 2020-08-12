import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}'.format(
    os.environ.get('MYSQL_USERNAME'), os.environ.get('MYSQL_PASSWORD'), 
    os.environ.get('MYSQL_ENDPOINT'), os.environ.get('MYSQL_DB')
  )
  SECRET_KEY = os.environ.get('SECRET_KEY')
  SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

  # The ID and range of a sample spreadsheet.
  SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
  RANGE_NAME = 'Stats'
  RANGE_NAME_SHEET_TWO = 'Standings'
  RANGE_NAME_SHEET_THREE = 'Game Log'
  MAILGUN_API_TOKEN = os.getenv('MAILGUN_API_TOKEN')
  SLACK_TOKEN = os.getenv('SLACK_API_TOKEN')
