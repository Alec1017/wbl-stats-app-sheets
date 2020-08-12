from flask import flash, render_template, redirect, request, url_for, abort
from werkzeug.security import generate_password_hash

from app import db
from app.portal import portal
from app.portal.forms import GameForm, PasswordResetForm
from app.models import Game, Player


# Landing page
@portal.route('/')
def index():
  players = Player.query.all()

  return render_template('home.html', players=players)


# Shows all player games
@portal.route('/player/<uid>')
def player(uid):

  current_player = Player.query.get(uid)
  player_games = Game.query.filter(Game.player_id == uid).order_by(Game.created_at).all()

  if current_player and player_games:
    return render_template('player.html', player=current_player, games=player_games)
  else:
    return "no player data"


# Shows all stats for a particular player's game
@portal.route('/player/game/<game_id>', methods=['GET', 'POST'])
def game(game_id):
  form = GameForm(request.form)
  game = Game.query.get(game_id)

  if game:
    form.captain.data = game.captain
    form.loser_score.data = game.loser_score
    form.total_innings.data = game.total_innings
    form.error.data = game.error
    form.pitching_strikeouts.data = game.pitching_strikeouts
    form.blown_saves.data = game.blown_saves
    form.innings_pitched.data = game.innings_pitched
    form.loss.data = game.loss
    form.winner_score.data = game.winner_score
    form.opponent.data = '{} {}'.format(game.opponent.first_name, game.opponent.last_name) if game.opponent else None
    form.saves.data = game.saves
    form.base_on_balls.data = game.base_on_balls
    form.hit_by_pitch.data = game.hit_by_pitch
    form.outs.data = game.outs
    form.singles.data = game.singles
    form.win.data = game.win
    form.game_won.data = game.game_won
    form.runs_batted_in.data = game.runs_batted_in
    form.earned_runs.data = game.earned_runs
    form.strikeouts.data = game.strikeouts
    form.stolen_bases.data = game.stolen_bases
    form.home_runs.data = game.home_runs
    form.pitching_base_on_balls.data = game.pitching_base_on_balls
    form.caught_stealing.data = game.caught_stealing
    form.triples.data = game.triples
    form.runs.data = game.runs
    form.player.data = '{} {}'.format(game.player.first_name, game.player.last_name)
    form.doubles.data = game.doubles

    if request.method == 'POST' and form.validate():
      player = None
      opponent = None

      if request.form['player']:
        first_name, last_name = str(request.form['player']).split(' ')
        player = Player.query.filter(Player.first_name == first_name, Player.last_name == last_name).first()

        if not player:
          flash('No player with that name exists', 'danger')
          return redirect(url_for('portal.index'))

      if request.form['opponent']:
        op_first, op_second = str(request.form['opponent']).split(' ')
        opponent = Player.query.filter(Player.first_name == op_first, Player.last_name == op_second).first()

        if not opponent:
          flash('No opponent with that name exists', 'danger')
          return redirect(url_for('portal.index'))

      try:
        game.player_id = player.id
        game.singles=int(request.form['singles'])
        game.doubles = int(request.form['doubles'])
        game.triples = int(request.form['triples'])
        game.home_runs = int(request.form['home_runs'])
        game.strikeouts = int(request.form['strikeouts'])
        game.outs = int(request.form['outs'])
        game.base_on_balls = int(request.form['base_on_balls'])
        game.hit_by_pitch = int(request.form['hit_by_pitch'])
        game.runs_batted_in =int(request.form['runs_batted_in'])
        game.error = int(request.form['error'])
        game.stolen_bases = int(request.form['stolen_bases'])
        game.caught_stealing = int(request.form['caught_stealing'])
        game.innings_pitched = int(request.form['innings_pitched'])
        game.earned_runs = int(request.form['earned_runs'])
        game.runs = int(request.form['runs'])
        game.pitching_strikeouts = int(request.form['pitching_strikeouts'])
        game.pitching_base_on_balls = int(request.form['pitching_base_on_balls'])
        game.saves = int(request.form['saves'])
        game.blown_saves = int(request.form['blown_saves'])
        game.win = int(request.form['win'])
        game.loss = int(request.form['loss'])
        game.opponent_id = (opponent.id if opponent else None)
        game.total_innings = int(request.form['total_innings'])
        game.captain=(request.form.get('captain', False) == 'y')
        game.game_won=(request.form.get('game_won', False) == 'y')
        game.winner_score=int(request.form['winner_score'])
        game.loser_score=int(request.form['loser_score'])
        game.player = player
        game.opponent = opponent

        db.session.commit()
      except Exception as e:
        print(e)
        flash('Game update failed, try again', 'danger')
        return redirect(url_for('portal.index'))


      flash('Game updated', 'success')
      return redirect(url_for('portal.index'))

    return render_template('game.html', game=game, form=form)
  else: 
    return "no game data"

# Reset a password
@portal.route('/password_reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
  form=PasswordResetForm(request.form)

  try:
    decoded_token = Player.decode_auth_token(token)

    # Make sure we get an ID and not an error message
    if isinstance(decoded_token, str):
      abort(401)

    player = Player.query.get(decoded_token)

    if request.method == 'POST' and form.validate():
      player.password = generate_password_hash(request.form['new_password'], method='sha256')

      db.session.commit()
      return render_template('password_reset_success.html')

    return render_template('password_reset.html', form=form)

  except Exception as e:
    abort(401)