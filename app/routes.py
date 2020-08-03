from flask import jsonify, render_template, request, flash, redirect, url_for

from app import app, db,sql_db
from app.email import send_email
from app.models import Player, Game, GameLog
from app.stats_builder import StatsBuilder
from .forms import GameForm


stats_builder = StatsBuilder()


@app.route('/')
def index():
  players = Player.query.all()

  return render_template('home.html', players=players)


@app.route('/api')
def status():
  return jsonify({'status': 'Up and running'})


@app.route('/player/<uid>')
def player(uid):

  current_player = Player.query.get(uid)
  player_games = Game.query.filter(Game.player_id == uid).order_by(Game.created_at).all()

  if current_player and player_games:
    return render_template('player.html', player=current_player, games=player_games)
  else:
    return "no player data"


@app.route('/player/game/<game_id>', methods=['GET', 'POST'])
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
          return redirect(url_for('index'))

      if request.form['opponent']:
        op_first, op_second = str(request.form['opponent']).split(' ')
        opponent = Player.query.filter(Player.first_name == op_first, Player.last_name == op_second).first()

        if not opponent:
          flash('No opponent with that name exists', 'danger')
          return redirect(url_for('index'))

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

        sql_db.session.commit()
      except Exception as e:
        print(e)
        flash('Game update failed, try again', 'danger')
        return redirect(url_for('index'))


      flash('Game updated', 'success')
      return redirect(url_for('index'))

    return render_template('game.html', game=game, form=form)
  else: 
    return "no game data"


@app.route('/api/update_sheet/<uid>')
def api(uid):
  stats_builder.query_database()
  stats_builder.build_subscribed_users_and_admins()

  if uid in stats_builder.admin_users:
    stats_builder.build_stats()
    stats_builder.build_standings()
    stats_builder.build_game_log()
    stats_builder.clear_all_sheets()

    results = stats_builder.update_all_sheets()

    return jsonify(results)
  else:
    return jsonify({'success': False, 'completed': False})


############ Util routes ############

@app.route('/migrate')
def migrate():
  stats_builder.query_database()

  for game in stats_builder.games:
    opponent = None

    first_name, last_name = game.get('player').split(' ')
    player = Player.query.filter(Player.first_name == first_name, Player.last_name == last_name).one()

    if game.get('selectedOpponent'):
      op_first, op_second = game.get('selectedOpponent').split(' ')
      opponent = Player.query.filter(Player.first_name == op_first, Player.last_name == op_second).one()

    game = Game(
      player_id = player.id,
      singles=game.get('singles'),
      doubles = game.get('doubles'),
      triples = game.get('triples'),
      home_runs = game.get('homeRuns'),
      strikeouts = game.get('strikeouts'),
      outs = game.get('outs'),
      base_on_balls = game.get('baseOnBalls'),
      hit_by_pitch = game.get('hitByPitch'),
      runs_batted_in =game.get('runsBattedIn'),
      error = game.get('error'),
      stolen_bases = game.get('stolenBases'),
      caught_stealing = game.get('caughtStealing'),
      innings_pitched = game.get('inningsPitched'),
      earned_runs = game.get('earnedRuns'),
      runs = game.get('runs'),
      pitching_strikeouts = game.get('pitchingStrikeouts'),
      pitching_base_on_balls = game.get('pitchingBaseOnBalls'),
      saves = game.get('saves'),
      blown_saves = game.get('blownSaves'),
      win = game.get('win'),
      loss = game.get('loss'),
      opponent_id = (opponent.id if opponent else None),
      total_innings = game.get('totalInnings'),
      player = player,
      opponent = opponent,
      captain=game.get('isCaptain'),
      game_won=game.get('isGameWon'),
      winner_score=game.get('winnerScore'),
      loser_score=game.get('loserScore')
    )

    sql_db.session.add(game)

  sql_db.session.commit()

  return "success"


@app.route('/delete')
def delete():
  sql_db.session.query(Game).delete()
  sql_db.session.commit()
  return "success"
  