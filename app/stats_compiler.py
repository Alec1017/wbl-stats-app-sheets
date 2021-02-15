from datetime import datetime
from sqlalchemy.orm import joinedload

from app.models import Game, Player
import app.stats_helpers as sh


class StatsCompiler:

  def __init__(self, google_sheet):
    self.google_sheet = google_sheet
    self.slack_bot = None
    self.emailer = None
    self.spreadsheet_id = None
    self.range_name_sheet_one = None
    self.range_name_sheet_two = None
    self.range_name_sheet_three = None

  def init_app(self, app, slack_bot, emailer):
    self.slack_bot = slack_bot
    self.emailer = emailer
    self.spreadsheet_id = app.config['SPREADSHEET_ID']
    self.range_name_sheet_one = app.config['RANGE_NAME_SHEET_ONE']
    self.range_name_sheet_two = app.config['RANGE_NAME_SHEET_TWO']
    self.range_name_sheet_three = app.config['RANGE_NAME_SHEET_THREE']
    

  def build_game_log(self):
    log_values = [
      ['Game Log']
    ]

    games = Game.query.options(joinedload(Game.player), joinedload(Game.opponent)).filter(Game.game_won == True).all()

    for game in games:
      winner = f'{game.player.first_name} {game.player.last_name}'
      loser = f'{game.opponent.first_name} {game.opponent.last_name}'
      
      log_string = f'{winner} beat {loser} {game.winner_score}-{game.loser_score} in {game.total_innings} innings on {game.created_at}'

      log_values.append([log_string])

    return log_values


  def build_standings(self):
    standings_values = {}

    players = Player.query.options(joinedload(Player.games)).all()

    for player in players:
      games_won = 0
      games_lost = 0

      player_name = f'{player.first_name} {player.last_name}'

      for game in player.games:
        if game.captain and game.game_won:
          games_won += 1

        if game.captain and not game.game_won:
          games_lost += 1

      if standings_values.get(player.division):
        standings_values[player.division].append([player_name, games_won, games_lost])
      else:
        standings_values[player.division] = [[player_name, games_won, games_lost]]


    standings_tuple = [(div, row) for div, row in standings_values.items()] 
    standings_tuple.sort(key=lambda standings: standings[0])

    final_standings = [
      ['Player', 'W', 'L']
    ]

    for division, rows in standings_tuple:
      rows.sort(key=lambda x: x[1], reverse=True)
      final_standings.append([f'D{division}'])
      final_standings += rows
      final_standings.append([])

    return final_standings
      

  def build_stats(self):
    stats_title_row = [
      'Player', 'H', 'AB', 'OBP', 'AVG', 'SLG', 'OPS', '1B', '2B', '3B', 'HR', 'HBP', 'BB', 'RBI', 'K', 'SB', 'CS', 'OUTS', 'GP', 
      '', 'IP', 'ER', 'R', 'K', 'BB', 'SV', 'BS', 'W', 'L', 'ERA', 
      '', 'ERRORS'
    ]

    stats_values = [stats_title_row, []]

    players = Player.query.options(joinedload(Player.games)).all()

    for player in players:
      player_name = f'{player.first_name} {player.last_name}'

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
      for stats in player.games: 
        singles += stats.singles
        doubles += stats.doubles
        triples += stats.triples
        home_runs += stats.home_runs
        hit_by_pitch += stats.hit_by_pitch
        base_on_balls += stats.base_on_balls
        runs_batted_in += stats.runs_batted_in
        strikeouts += stats.strikeouts
        stolen_bases += stats.stolen_bases
        caught_stealing += stats.caught_stealing
        outs += stats.outs
        games_played += 1

        innings_pitched += stats.innings_pitched
        earned_runs += stats.earned_runs
        runs += stats.runs
        pitching_strikeouts += stats.pitching_strikeouts
        pitching_base_on_balls += stats.pitching_base_on_balls
        saves += stats.saves
        blown_saves += stats.blown_saves
        wins += stats.win
        losses += stats.loss

        errors += stats.error
      
      # Calculate stats
      hits = sh.calc_hits(singles, doubles, triples, home_runs)
      at_bats = sh.calc_at_bats(hits, outs, strikeouts)
      innings_pitched = sh.calc_innings_pitched(innings_pitched)
      on_base_percentage = sh.calc_obp(hits, at_bats, base_on_balls, hit_by_pitch)
      average = sh.calc_avg(hits, at_bats)
      slugging = sh.calc_slg(singles, doubles, triples, home_runs, at_bats)
      on_base_plus_slugging = sh.calc_ops(on_base_percentage, slugging)
      earned_run_average = sh.calc_era(earned_runs, innings_pitched)

      stats_sheet_row += [
        player_name,
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

    return stats_values 


  def clear_all_sheets(self):
    try:
      self.google_sheet.values().batchClear(
        spreadsheetId=self.spreadsheet_id, 
        body={'ranges': [self.range_name_sheet_one, self.range_name_sheet_two, self.range_name_sheet_three]}
      ).execute()
    except Exception as e:
      message = f'Google Sheet was not successfully cleared.\n\n{str(e)}'
      self.slack_bot.send_message(message=message)


  def update_all_sheets(self):
    try:
      result = self.google_sheet.values().update(
        spreadsheetId=self.spreadsheet_id, range=self.range_name_sheet_one,
        valueInputOption='USER_ENTERED', body={'values': self.build_stats()}).execute()

      standings_result = self.google_sheet.values().update(
        spreadsheetId=self.spreadsheet_id, range=self.range_name_sheet_two,
        valueInputOption='USER_ENTERED', body={'values': self.build_standings()}).execute()

      game_log_result = self.google_sheet.values().update(
        spreadsheetId=self.spreadsheet_id, range=self.range_name_sheet_three,
        valueInputOption='USER_ENTERED', body={'values': self.build_game_log()}).execute()
    except Exception as e:
      message = f'Google Sheet was not successfully updated.\n\n{str(e)}'
      self.slack_bot.send_message(message=message)
      return {'success': False, 'completed': False}
    else:
      players = Player.query.filter(Player.subscribed == True).all()
      self.emailer.send_all_emails(players)

      message = "Google Sheet was successfully updated!"
      self.slack_bot.send_message(message=message)
      return {'success': True}