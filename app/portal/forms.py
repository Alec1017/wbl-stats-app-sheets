from wtforms import Form, BooleanField, IntegerField, PasswordField,StringField


class PasswordResetForm(Form):
  new_password = PasswordField('New password')


class GameForm(Form):
  player = StringField('Player')
  singles = IntegerField('1B')
  doubles = IntegerField('2B')
  triples = IntegerField('3B')
  home_runs = IntegerField('HR')
  strikeouts = IntegerField('Batting strikeouts')
  outs = IntegerField('OUTS')
  base_on_balls = IntegerField('BB')
  hit_by_pitch = IntegerField('HBP')
  runs_batted_in = IntegerField('RBI')
  error = IntegerField('Error')
  stolen_bases = IntegerField('SB')
  caught_stealing = IntegerField('CS')

  innings_pitched = IntegerField('Innings pitched (total number of outs)')
  earned_runs = IntegerField('ER')
  runs = IntegerField('R')
  pitching_strikeouts = IntegerField('Pitching strikeouts')
  pitching_base_on_balls = IntegerField('Pitching BB')
  saves = IntegerField('Saves')
  blown_saves = IntegerField('Blown saves')
  win = IntegerField('Pitching win')
  loss = IntegerField('Pitching loss')

  captain = BooleanField('Is captain?')
  game_won = BooleanField('Did you win the game?')
  opponent = StringField('Selected opponent')
  winner_score = IntegerField('Winning team score')
  loser_score = IntegerField('Losing team score')
  total_innings = IntegerField('Total innings played')