from __future__ import print_function
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

cred = credentials.Certificate('firebase-credentials.json')
firebase_admin.initialize_app(cred)

db = firestore.client()


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

SAMPLE_RANGE_NAME = 'Sheet1'

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
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
                'sheets-credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    

    # get firebase user
    users = db.collection(u'users').stream()
    name_row = ['Player', '1B', '2B', '3B']
    values = [name_row, []]

    for user in users:
      player = user.to_dict()

      first_name = player.get('firstName')
      last_name = player.get('lastName')
      full_name = u'{} {}'.format(first_name, last_name)
      

      games = db.collection(u'games').where(u'player', u'==', full_name).stream()
      

      singles = 0
      doubles = 0
      triples = 0
      sheet_row = []

      for game in games: 
        stats = game.to_dict()
        singles += stats.get('singles')
        doubles += stats.get('doubles')
        triples += stats.get('triples')

      sheet_row.append(full_name)
      sheet_row.append(singles)
      sheet_row.append(doubles)
      sheet_row.append(triples)

      values.append(sheet_row)
      values.append([])



    # write to the sheet
    
    body = {
        'values': values
    }
    
    # clear the sheet
    # result = service.spreadsheets().values().clear(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
    batch_clear = {
      'ranges': ['Sheet1']
    }

    sheet.setFrozenColumns(1)
  
    result = service.spreadsheets().values().batchClear(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=batch_clear).execute()


    # Update the sheet
    result = service.spreadsheets().values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME,
        valueInputOption='USER_ENTERED', body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))

if __name__ == '__main__':
    main()
