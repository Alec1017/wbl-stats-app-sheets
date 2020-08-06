from datetime import datetime, timedelta
import jwt

from app import app, db


class Player(db.Model):
  __tablename__ = 'player'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
  first_name = db.Column(db.String(45), index=True)
  last_name = db.Column(db.String(45), index=True)
  email = db.Column(db.String(100), index=True, unique=True)
  password = db.Column(db.String(100), nullable=True)
  division = db.Column(db.Integer, index=True)
  admin = db.Column(db.Boolean, index=True, default=False)
  subscribed = db.Column(db.Boolean, index=True, default=True)

  # Relationships
  games = db.relationship('Game', back_populates='player', foreign_keys='Game.player_id')

  def encode_auth_token(self, player_id):
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, seconds=5),
            'iat': datetime.utcnow(),
            'sub': player_id
        }
        return jwt.encode(
            payload,
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    except Exception as e:
        return e

  @staticmethod
  def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, app.config['SECRET_KEY'])

        if TokenDenylist.check_denylist(auth_token):
            return 'Token blacklisted. Please log in again.'

        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please login again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please login again.'

  def __repr__(self):
    return '<Player {} {} {}>'.format(self.id, self.first_name, self.last_name)


class GameLog(db.Model):
  __tablename__ = 'game_log'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
  created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
  winner_id = db.Column(db.Integer, db.ForeignKey('player.id'))
  loser_id = db.Column(db.Integer, db.ForeignKey('player.id'))
  winning_score = db.Column(db.Integer)
  losing_score = db.Column(db.Integer)

  # Relationships
  winner = db.relationship('Player', foreign_keys=[winner_id])
  loser = db.relationship('Player', foreign_keys=[loser_id])
  
  def __repr__(self):
    return '<GameLog {}>'.format(self.id)


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

  opponent_id = db.Column(db.Integer, db.ForeignKey('player.id'))
  captain = db.Column(db.Boolean, index=True, default=False)
  game_won = db.Column(db.Boolean, default=False)
  winner_score = db.Column(db.Integer, default=0)
  loser_score = db.Column(db.Integer, default=0)
  total_innings = db.Column(db.Integer, default=3)

  # Relationships
  player = db.relationship('Player', foreign_keys=[player_id])
  opponent = db.relationship('Player', foreign_keys=[opponent_id])

  def __repr__(self):
    return '<Game {}>'.format(self.id)


class TokenDenylist(db.Model):
  __tablename__ = 'token_denylist'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  token = db.Column(db.String(500), unique=True, nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)

  @staticmethod
  def check_denylist(auth_token):
    response = TokenDenylist.query.filter_by(token=str(auth_token)).first()
    if response:
        return True  
    else:
        return False

  def __repr__(self):
      return '<TokenDenylist {}>'.format(self.token)
