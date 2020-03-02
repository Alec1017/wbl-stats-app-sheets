from __future__ import print_function, division
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
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

RANGE_NAME = 'Sheet1'

def calcHits(singles, doubles, triples, home_runs):
  return singles + doubles + triples + home_runs

def calcAtBats(hits, outs):
  return hits + outs

def calcOBP(hits, at_bats, base_on_balls, hit_by_pitch):
  denom = at_bats + base_on_balls + hit_by_pitch
  if denom == 0:
    return 'Undefined'

  return round(float((hits + base_on_balls + hit_by_pitch) / denom), 3)

def calcAVG(hits, at_bats):
  if at_bats == 0:
    return 'Undefined'

  return round(float(hits / at_bats), 3)

def calcSLG(singles, doubles, triples, home_runs, at_bats):
  if at_bats == 0:
    return 'Undefined'

  return round(float((singles + (2 * doubles) + (3 * triples) + (4 * home_runs)) / at_bats), 3)

def calcOPS(obp, slg):
  if obp == 'Undefined' or slg == 'Undefined':
    return 'Undefined'

  return round(float(obp + slg), 3) if obp + slg != 0 else 'Undefined'

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
    

    # get firebase users
    users = db.collection(u'users').stream()
    name_row = ['Player', 'H', 'AB', 'OBP', 'AVG', 'SLG', 'OPS', '1B', '2B', '3B', 'HR', 'HBP', 'BB', 'RBI', 'K', 'SB', 'OUTS', 'GP']
    values = [name_row, []]

    for user in users:
      player = user.to_dict()

      first_name = player.get('firstName')
      last_name = player.get('lastName')
      full_name = u'{} {}'.format(first_name, last_name)
      

      games = db.collection(u'games').where(u'player', u'==', full_name).stream()
      
      hits = 0
      at_bats = 0
      on_base_percentage = 0
      slugging = 0
      on_base_plus_slugging = 0
      average = 0
      singles = 0
      doubles = 0
      triples = 0
      home_runs = 0
      hit_by_pitch = 0
      base_on_balls = 0
      runs_batted_in = 0
      strikeouts = 0
      stolen_bases = 0
      outs = 0

      games_played = 0

      sheet_row = []

      # Summing up all the stats for a player
      for game in games: 
        stats = game.to_dict()

        singles += stats.get('singles')
        doubles += stats.get('doubles')
        triples += stats.get('triples')
        home_runs += stats.get('homeRuns')
        hit_by_pitch += stats.get('hitByPitch')
        base_on_balls += stats.get('baseOnBalls')
        runs_batted_in += stats.get('runsBattedIn')
        strikeouts += stats.get('strikeouts')
        stolen_bases += stats.get('stolenBases')
        outs += stats.get('outs')

        games_played += 1

      # Calculate stats
      hits = calcHits(singles, doubles, triples, home_runs)
      at_bats = calcAtBats(hits, outs)
      on_base_percentage = calcOBP(hits, at_bats, base_on_balls, hit_by_pitch)
      average = calcAVG(hits, at_bats)
      slugging = calcSLG(singles, doubles, triples, home_runs, at_bats)
      on_base_plus_slugging = calcOPS(on_base_percentage, slugging)

      # append stats to row
      sheet_row.append(full_name)
      sheet_row.append(hits)
      sheet_row.append(at_bats)
      sheet_row.append(on_base_percentage)
      sheet_row.append(average)
      sheet_row.append(slugging)
      sheet_row.append(on_base_plus_slugging)
      sheet_row.append(singles)
      sheet_row.append(doubles)
      sheet_row.append(triples)
      sheet_row.append(home_runs)
      sheet_row.append(hit_by_pitch)
      sheet_row.append(base_on_balls)
      sheet_row.append(runs_batted_in)
      sheet_row.append(strikeouts)
      sheet_row.append(stolen_bases)
      sheet_row.append(stolen_bases)
      sheet_row.append(games_played)

      values.append(sheet_row)
      values.append([])
    

    # Clear the sheet
    result = sheet.values().batchClear(spreadsheetId=SPREADSHEET_ID, body={'ranges': ['Sheet1']}).execute()

    # Update the sheet
    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
        valueInputOption='USER_ENTERED', body={'values': values}).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))

if __name__ == '__main__':
    main()
