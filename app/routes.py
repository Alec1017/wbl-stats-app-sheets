from __future__ import division
from flask import jsonify

from app import app, db, sheet, spreadsheet_id, range_name
from app.email import send_email

EMAIL_LIST = []


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

def calcERA(earned_runs, innings_pitched):
  if innings_pitched == 0:
    return 'Undefined'

  return round(float((earned_runs * 3) / innings_pitched), 2)


def build_sheet():
  global EMAIL_LIST

  # get firebase users
  users = db.collection(u'users').stream()
  name_row = ['Player', 'H', 'AB', 'OBP', 'AVG', 'SLG', 'OPS', '1B', '2B', '3B', 'HR', 'HBP', 'BB', 'RBI', 'K', 'SB', 'OUTS', 'GP', '', 'IP', 'ER', 'R', 'K', 'BB', 'SV', 'W', 'L', 'ERA']
  values = [name_row, []]

  for user in users:
    player = user.to_dict()

    first_name = player.get('firstName')
    last_name = player.get('lastName')
    full_name = u'{} {}'.format(first_name, last_name)

    EMAIL_LIST.append((first_name, player.get('email')))
    
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

    innings_pitched = 0
    earned_runs = 0
    runs = 0
    pitching_strikeouts = 0
    pitching_base_on_balls = 0
    saves = 0
    wins = 0
    losses = 0

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

      innings_pitched += stats.get('inningsPitched')
      earned_runs += stats.get('earnedRuns')
      runs += stats.get('runs')
      pitching_strikeouts += stats.get('pitchingStrikeouts')
      pitching_base_on_balls += stats.get('pitchingBaseOnBalls')
      saves += stats.get('saves')
      wins += stats.get('win')
      losses += stats.get('loss')

    # Calculate stats
    hits = calcHits(singles, doubles, triples, home_runs)
    at_bats = calcAtBats(hits, outs)
    on_base_percentage = calcOBP(hits, at_bats, base_on_balls, hit_by_pitch)
    average = calcAVG(hits, at_bats)
    slugging = calcSLG(singles, doubles, triples, home_runs, at_bats)
    on_base_plus_slugging = calcOPS(on_base_percentage, slugging)
    earned_run_average = calcERA(earned_runs, innings_pitched)

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

    sheet_row.append('')

    sheet_row.append(round(innings_pitched / 3))
    sheet_row.append(earned_runs)
    sheet_row.append(runs)
    sheet_row.append(pitching_strikeouts)
    sheet_row.append(pitching_base_on_balls)
    sheet_row.append(saves)
    sheet_row.append(wins)
    sheet_row.append(losses)
    sheet_row.append(earned_run_average)

    values.append(sheet_row)
    values.append([])

  return values


def clear_sheet():
  try:
    sheet.values().batchClear(spreadsheetId=spreadsheet_id, body={'ranges': [range_name]}).execute()
  except:
    print('Sheet was not cleared successfully')
  else:
    print('Sheet cleared successfully!')


def update_sheet(db_values):
  global EMAIL_LIST

  try:
    result = sheet.values().update(
      spreadsheetId=spreadsheet_id, range=range_name,
      valueInputOption='USER_ENTERED', body={'values': db_values}).execute()
    print('Success! {0} cells updated.'.format(result.get('updatedCells')))
  except:
    print('Something went wrong! Stats were not uploaded to sheet')
    return {'success': False}
  else:
    for name, email in EMAIL_LIST:
      send_email(name, '2020 WBL Stats', email)
  
    EMAIL_LIST = []

    return {'success': True}
  

@app.route('/api/update_sheet')
def api():
  values = build_sheet()
  clear_sheet()
  return jsonify(update_sheet(values))