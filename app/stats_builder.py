from datetime import datetime

from app import db, sheet, spreadsheet_id, range_name, range_name_sheet_two, range_name_sheet_three
from app.email import send_email
from app.slack import SlackBot
from app.stats_helpers import calcHits, calcAtBats, calcOBP, calcAVG, calcSLG, calcOPS, calcERA, calcInningsPitched


class StatsBuilder:
  users = []
  games = []

  email_list = []
  admin_users = []

  slack_bot = None

  sheet_one_range = None
  sheet_two_range = None
  sheet_three_range = None

  sheet_api = None
  sheet_id = None

  built_stats = []
  built_standings = []
  built_game_log = []


  def __init__(self):
    self.slack_bot = SlackBot()
    self.sheet_one_range = range_name
    self.sheet_two_range = range_name_sheet_two
    self.sheet_three_range = range_name_sheet_three
    self.sheet_api = sheet
    self.sheet_id = spreadsheet_id


  def query_all_users(self):
    try:
      users = db.collection(u'users').stream()
      return [user.to_dict() for user in users]
    except Exception as e:
      message = "Could not get users from firebase.\n\n{}".format(str(e))
      self.slack_bot.send_message(message=message)


  def query_all_games(self):
    try:
      games = db.collection(u'games').stream()
      dict_games = [game.to_dict() for game in games]
      dict_games.sort(key=lambda game: datetime.strptime(game.get('date'), '%a %b %d %Y'))
      return dict_games
    except Exception as e:
      message = "Could not get games from firebase.\n\n{}".format(str(e))
      self.slack_bot.send_message(message=message)

  def query_database(self):
    self.users = self.query_all_users()
    self.games = self.query_all_games()


  def build_subscribed_users_and_admins(self):
    for user in self.users:
      if user.get('isAdmin'):
        self.admin_users.append(user.get('uid'))

      if user.get('subscribed'):
        self.email_list.append((user.get('firstName'), user.get('email')))

  
  def send_emails(self):
    for name, email in self.email_list:
      send_email(name, '2020 WBL Stats', email)
    
    self.email_list = []

  def build_game_log(self):
    log_title_row = ['Game Log']

    log_values = [log_title_row]

    for game in self.games:
      log_string = "{} beat {} {}-{} on {}"
      if game.get('isGameWon'):
        winner = game.get('player')
        loser = game.get('selectedOpponent')
        winner_score = game.get('winnerScore')
        loser_score = game.get('loserScore')
        date = game.get('date')
        
        log_string = "{} beat {} {}-{} on {}".format(
          winner, loser, winner_score, loser_score, date
        )

        log_values.append([log_string])
    
    self.built_game_log = log_values


  def build_standings(self):
    standings_title_row = ['Player', 'W', 'L']
    standings_values = {}

    for user in self.users:
      first_name = user.get('firstName')
      last_name = user.get('lastName')
      full_name = u'{} {}'.format(first_name, last_name)
      division = str(user.get('division'))

      games_won = 0
      games_lost = 0
      games = filter(lambda game: game.get('player') == full_name, self.games)

      for game in games:
        if game.get('isCaptain') and game.get('isGameWon'):
          games_won += 1

        if game.get('isCaptain') and not game.get('isGameWon'):
          games_lost += 1

      
      if standings_values.get(division):
        standings_values[division].append([full_name, games_won, games_lost])
      else:
        standings_values[division] = [[full_name, games_won, games_lost]]


    standings_tuple = [(div, row) for div, row in standings_values.items()] 
    standings_tuple.sort(key=lambda standings: standings[0])

    final_standings = [standings_title_row]

    for division, rows in standings_tuple:
      rows.sort(key=lambda x: x[1], reverse=True)
      final_standings.append(['D{}'.format(division)])
      final_standings +=rows
      final_standings.append([])

    self.built_standings = final_standings
      

  def build_stats(self):
    stats_title_row = [
      'Player', 'H', 'AB', 'OBP', 'AVG', 'SLG', 'OPS', '1B', '2B', '3B', 'HR', 'HBP', 'BB', 'RBI', 'K', 'SB', 'CS', 'OUTS', 'GP', 
      '', 'IP', 'ER', 'R', 'K', 'BB', 'SV', 'BS', 'W', 'L', 'ERA', 
      '', 'ERRORS'
    ]

    stats_values = [stats_title_row, []]

    for user in self.users:
      first_name = user.get('firstName')
      last_name = user.get('lastName')
      full_name = u'{} {}'.format(first_name, last_name)
      games = filter(lambda game: game.get('player') == full_name, self.games)
      
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
      caught_stealing = 0
      outs = 0
      games_played = 0

      innings_pitched = 0
      earned_runs = 0
      runs = 0
      pitching_strikeouts = 0
      pitching_base_on_balls = 0
      saves = 0
      blown_saves = 0
      wins = 0
      losses = 0

      errors = 0


      stats_sheet_row = []

      # Summing up all the stats for a player
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
        caught_stealing += stats.get('caughtStealing', 0)
        outs += stats.get('outs')
        games_played += 1

        innings_pitched += stats.get('inningsPitched')
        earned_runs += stats.get('earnedRuns')
        runs += stats.get('runs')
        pitching_strikeouts += stats.get('pitchingStrikeouts')
        pitching_base_on_balls += stats.get('pitchingBaseOnBalls')
        saves += stats.get('saves')
        blown_saves += stats.get('blownSaves', 0)
        wins += stats.get('win')
        losses += stats.get('loss')

        errors += stats.get('error')

      # Calculate stats
      hits = calcHits(singles, doubles, triples, home_runs)
      at_bats = calcAtBats(hits, outs, strikeouts)
      innings_pitched = calcInningsPitched(innings_pitched)
      on_base_percentage = calcOBP(hits, at_bats, base_on_balls, hit_by_pitch)
      average = calcAVG(hits, at_bats)
      slugging = calcSLG(singles, doubles, triples, home_runs, at_bats)
      on_base_plus_slugging = calcOPS(on_base_percentage, slugging)
      earned_run_average = calcERA(earned_runs, innings_pitched)

      stats_sheet_row += [
        full_name,
        hits,
        at_bats,
        on_base_percentage,
        average,
        slugging,
        on_base_plus_slugging,
        singles,
        doubles,
        triples,
        home_runs,
        hit_by_pitch,
        base_on_balls,
        runs_batted_in,
        strikeouts,
        stolen_bases,
        caught_stealing,
        outs,
        games_played,
        '',
        innings_pitched,
        earned_runs,
        runs,
        pitching_strikeouts,
        pitching_base_on_balls,
        saves,
        blown_saves,
        wins,
        losses,
        earned_run_average,
        '',
        errors
      ]

      stats_values += [stats_sheet_row, []]

    self.built_stats = stats_values 


  def clear_all_sheets(self):
    try:
      self.sheet_api.values().batchClear(spreadsheetId=self.sheet_id, body={'ranges': [self.sheet_one_range, self.sheet_two_range, self.sheet_three_range]}).execute()
    except Exception as e:
      message = "Google Sheet was not successfully cleared.\n\n{}".format(str(e))
      self.slack_bot.send_message(message=message)

  def update_all_sheets(self):
    try:
      result = self.sheet_api.values().update(
        spreadsheetId=self.sheet_id, range=self.sheet_one_range,
        valueInputOption='USER_ENTERED', body={'values': self.built_stats}).execute()

      standings_result = self.sheet_api.values().update(
        spreadsheetId=self.sheet_id, range=self.sheet_two_range,
        valueInputOption='USER_ENTERED', body={'values': self.built_standings}).execute()

      game_log_result = self.sheet_api.values().update(
        spreadsheetId=self.sheet_id, range=self.sheet_three_range,
        valueInputOption='USER_ENTERED', body={'values': self.built_game_log}).execute()
    except Exception as e:
      message = "Google Sheet was not successfully updated.\n\n{}".format(str(e))
      self.slack_bot.send_message(message=message)
      return {'success': False, 'completed': False}
    else:
      self.send_emails()
      self.admin_users = []

      message = "Google Sheet was successfully updated!"
      self.slack_bot.send_message(message=message)
      return {'success': True, 'completed': True}