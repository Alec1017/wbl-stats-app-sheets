from __future__ import division
from flask import jsonify
from datetime import datetime

from app import app, db, sheet, spreadsheet_id, range_name, range_name_sheet_two, range_name_sheet_three
from app.email import send_email
from app.slack import SlackBot

EMAIL_LIST = []
ADMIN_USERS = []
slack_bot = SlackBot()


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
  global ADMIN_USERS

  # get firebase users
  users = []
  try:
    users = db.collection(u'users').stream()
  except Exception as e:
    message = "Could not get users from firebase.\n\n{}".format(str(e))
    slack_bot.send_message(message=message)
    return

  name_row = ['Player', 'H', 'AB', 'OBP', 'AVG', 'SLG', 'OPS', '1B', '2B', '3B', 'HR', 'HBP', 'BB', 'RBI', 'K', 'SB', 'OUTS', 'GP', '', 'IP', 'ER', 'R', 'K', 'BB', 'SV', 'W', 'L', 'ERA', '', 'ERRORS']
  standings_row = ['Player', 'W', 'L']

  values = [name_row, []]
  standings_values = []
  game_log_values = []

  for user in users:
    player = user.to_dict()

    first_name = player.get('firstName')
    last_name = player.get('lastName')
    full_name = u'{} {}'.format(first_name, last_name)

    if player.get('isAdmin'):
      ADMIN_USERS.append(player.get('uid'))

    if player.get('subscribed'):
      EMAIL_LIST.append((first_name, player.get('email')))
    
    games = []
    try:
      games = db.collection(u'games').where(u'player', u'==', full_name).stream()
    except Exception as e:
      message = "Could not get games from firebase.\n\n{}".format(str(e))
      #slack_bot.send_message(message=message)
      return

    
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

    errors = 0

    games_won = 0
    games_lost = 0

    sheet_row = []
    sheet_two_row = []

    # Summing up all the stats for a player
    games = [game.to_dict() for game in games]
    games.sort(key=lambda game: datetime.strptime(game.get('date'), '%a %b %d %Y'))
    for stats in games: 
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

      errors += stats.get('error')

      games_won = games_won + 1 if stats.get('isCaptain') and stats.get('isGameWon') else games_won
      games_lost = games_lost + 1 if stats.get('isCaptain') and not stats.get('isGameWon') else games_lost


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

    sheet_row.append('')

    sheet_row.append(errors)

    values.append(sheet_row)
    values.append([])


    # Standings

    sheet_two_row.append(full_name)
    sheet_two_row.append(games_won)
    sheet_two_row.append(games_lost)

    standings_values.append(sheet_two_row)

  # sort the standings
  standings_values.sort(key=lambda row: row[1], reverse=True)
  standings_values.insert(0, standings_row)
  return (values, standings_values)


def clear_sheet():
  try:
    sheet.values().batchClear(spreadsheetId=spreadsheet_id, body={'ranges': [range_name, range_name_sheet_two]}).execute()
  except Exception as e:
    message = "Google Sheet was not successfully cleared.\n\n{}".format(str(e))
    #slack_bot.send_message(message=message)


def update_sheet(db_values):
  global EMAIL_LIST

  try:
    pass
    # result = sheet.values().update(
    #   spreadsheetId=spreadsheet_id, range=range_name,
    #   valueInputOption='USER_ENTERED', body={'values': db_values[0]}).execute()

    # standings_result = sheet.values().update(
    #   spreadsheetId=spreadsheet_id, range=range_name_sheet_two,
    #   valueInputOption='USER_ENTERED', body={'values': db_values[1]}).execute()
  except Exception as e:
    message = "Google Sheet was not successfully updated.\n\n{}".format(str(e))
    #slack_bot.send_message(message=message)
    return {'success': False}
  else:
    for name, email in EMAIL_LIST:
      pass
      #send_email(name, '2020 WBL Stats', email)
  
    EMAIL_LIST = []

    message = 'Stats have been updated successfully!'
    #slack_bot.send_message(message=message)
    return {'success': True}
  

@app.route('/api/update_sheet/<uid>')
def api(uid):
  global ADMIN_USERS

  values = build_sheet()

  if uid in ADMIN_USERS:
    clear_sheet()
    ADMIN_USERS = []
    return jsonify(update_sheet(values))
  else:
    return jsonify({'success': False})