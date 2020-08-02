from datetime import datetime

from app import sql_db

db = sql_db


class Player(db.Model):
  __tablename__ = 'player'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
  first_name = db.Column(db.String(45), index=True)
  last_name = db.Column(db.String(45), index=True)
  email = db.Column(db.String(100), index=True, unique=True)
  division = db.Column(db.Integer, index=True)
  admin = db.Column(db.Boolean, index=True, default=False)
  subscribed = db.Column(db.Boolean, index=True, default=True)
  games = db.relationship('Game', backref='player', lazy='dynamic')

  def __repr__(self):
    return '<Player {} {} {}>'.format(self.id, self.first_name, self.last_name)


class Game(db.Model):
  __tablename__ = 'game'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
  player_id = db.Column(db.Integer, db.ForeignKey('player.id'), index=True)
  created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

  singles = db.Column(db.Integer, default=0)
  doubles = db.Column(db.Integer, default=0)
  triples = db.Column(db.Integer, default=0)
  home_runs = db.Column(db.Integer, default=0)
  strikeouts = db.Column(db.Integer, default=0)
  outs = db.Column(db.Integer, default=0)
  base_on_balls = db.Column(db.Integer, default=0)
  hit_by_pitch = db.Column(db.Integer, default=0)
  runs_batted_in = db.Column(db.Integer, default=0)
  error = db.Column(db.Integer, default=0)
  stolen_bases = db.Column(db.Integer, default=0)
  caught_stealing = db.Column(db.Integer, default=0)

  innings_pitched = db.Column(db.Integer, default=0)
  earned_runs = db.Column(db.Integer, default=0)
  runs = db.Column(db.Integer, default=0)
  pitching_strikeouts = db.Column(db.Integer, default=0)
  pitching_base_on_balls = db.Column(db.Integer, default=0)
  saves = db.Column(db.Integer, default=0)
  blown_saves = db.Column(db.Integer, default=0)
  win = db.Column(db.Integer, default=0)
  loss = db.Column(db.Integer, default=0)

  captain = db.Column(db.Boolean, index=True, default=False)
  game_won = db.Column(db.Boolean, default=False)
  selected_opponent = db.Column(db.Integer, db.ForeignKey('player.id'))
  winner_score = db.Column(db.Integer, default=0)
  loser_score = db.Column(db.Integer, default=0)
  total_innings = db.Column(db.Integer, default=3)

  def __repr__(self):
    return '<Game {}>'.format(self.id)
