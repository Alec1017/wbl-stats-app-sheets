from __future__ import print_function, division
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

import pickle
from dotenv import load_dotenv
import os
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

load_dotenv()


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(
  os.getenv('MYSQL_USERNAME'), os.getenv('MYSQL_PASSWORD'), os.getenv('MYSQL_ENDPOINT'), os.getenv('MYSQL_DB')
)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.secret_key = os.getenv("SECRET_KEY")

# If modifying these scopes, delete the file token.pickle.
scopes = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
spreadsheet_id = os.getenv("SPREADSHEET_ID")
test_spreadsheet_id = os.getenv("TEST_SPREADSHEET_ID")
range_name = 'Stats'
range_name_sheet_two = 'Standings'
range_name_sheet_three = 'Game Log'

email_address = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")
mailgun_api_token = os.getenv("MAILGUN_API_TOKEN")

slack_token = os.getenv("SLACK_API_TOKEN")

def authenticate_sheet():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'sheets-credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    return service.spreadsheets()
    

sheet = authenticate_sheet()


from app import routes