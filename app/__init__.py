from __future__ import print_function, division
from flask import Flask

import pickle
from dotenv import load_dotenv
import os
import os.path
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

load_dotenv()


app = Flask(__name__)

cred = credentials.Certificate('firebase-credentials.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

# If modifying these scopes, delete the file token.pickle.
scopes = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
spreadsheet_id = os.getenv("SPREADSHEET_ID")
range_name = 'Sheet1'
range_name_sheet_two = 'Sheet2'

email_address = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")

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