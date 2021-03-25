import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class BaseConfig:
    # Disable signaling of application every time a change is made in the database
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get('SECRET_KEY')

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    RANGE_NAME_SHEET_ONE = 'Stats'
    RANGE_NAME_SHEET_TWO = 'Standings'
    RANGE_NAME_SHEET_THREE = 'Game Log'

    MAILGUN_API_TOKEN = os.getenv('MAILGUN_API_TOKEN')
    SLACK_TOKEN = os.getenv('SLACK_API_TOKEN')

    MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    MYSQL_ENDPOINT = os.environ.get('MYSQL_ENDPOINT')


class Production(BaseConfig):
    MYSQL_DB = os.environ.get('MYSQL_DB')

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}'.format(
        BaseConfig.MYSQL_USERNAME,
        BaseConfig.MYSQL_PASSWORD, 
        BaseConfig.MYSQL_ENDPOINT, 
        MYSQL_DB
    )

    # The ID and range of a sample spreadsheet.
    SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')

    MUTE_EMAIL_NOTIFICATIONS = False


class Development(BaseConfig):
    TEST_MYSQL_DB = os.environ.get('TEST_MYSQL_DB')

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}'.format(
        BaseConfig.MYSQL_USERNAME,
        BaseConfig.MYSQL_PASSWORD, 
        BaseConfig.MYSQL_ENDPOINT, 
        TEST_MYSQL_DB
    )

    SPREADSHEET_ID = os.environ.get('TEST_SPREADSHEET_ID')

    MUTE_EMAIL_NOTIFICATIONS = True
  
    # Enable the TESTING flag to disable the error catching during request handling
    # so that you get better error reports when performing test requests against the application.
    TESTING = True
  
    # Disable CSRF tokens in the Forms (only valid for testing purposes!)
    WTF_CSRF_ENABLED = False
