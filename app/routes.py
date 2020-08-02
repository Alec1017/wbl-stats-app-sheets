from flask import jsonify, render_template, request, flash, redirect, url_for

from app import app, db,sql_db
from app.models import Player, Game, GameLog
from app.stats_builder import StatsBuilder
from .forms import GameForm


stats_builder = StatsBuilder()

@app.route('/')
def index():

  stats_builder.query_database()

  return render_template('home.html', players=stats_builder.users)

@app.route('/player/<uid>')
def player(uid):
  current_player = None
  games = []

  if not stats_builder.users or not stats_builder.games:
    stats_builder.query_database()

  for player in stats_builder.users:
    if uid == player.get('uid'):
      current_player = player
      break

  for game in stats_builder.games:
    if uid == game.get('uid'):
      games.append(game)

  if current_player and games:
    games.sort(key=lambda timestamp: game.get('timestamp'))
    return render_template('player.html', player=current_player, games=games)
  else:
    return "no player data"


@app.route('/player/game/<game_id>', methods=['GET', 'POST'])
def game(game_id):
  game = None
  form = GameForm(request.form)

  for player_game in stats_builder.games:
    if game_id == player_game.get('id'):
      game = player_game
      break

  if game:
    form.isCaptain.data = game.get('isCaptain')
    form.loserScore.data = game.get('loserScore')
    form.totalInnings.data = game.get('totalInnings')
    form.error.data = game.get('error')
    form.pitchingStrikeouts.data = game.get('pitchingStrikeouts')
    form.blownSaves.data = game.get('blownSaves')
    form.inningsPitched.data = game.get('inningsPitched')
    form.loss.data = game.get('loss')
    form.winnerScore.data = game.get('winnerScore')
    form.selectedOpponent.data = game.get('selectedOpponent', '')
    form.saves.data = game.get('saves')
    form.baseOnBalls.data = game.get('baseOnBalls')
    form.hitByPitch.data = game.get('hitByPitch')
    form.outs.data = game.get('outs')
    form.singles.data = game.get('singles')
    form.win.data = game.get('win')
    form.isGameWon.data = game.get('isGameWon')
    form.runsBattedIn.data = game.get('runsBattedIn')
    form.earnedRuns.data = game.get('earnedRuns')
    form.strikeouts.data = game.get('strikeouts')
    form.stolenBases.data = game.get('stolenBases')
    form.homeRuns.data = game.get('homeRuns')
    form.pitchingBaseOnBalls.data = game.get('pitchingBaseOnBalls')
    form.caughtStealing.data = game.get('caughtStealing')
    form.triples.data = game.get('triples')
    form.runs.data = game.get('runs')
    form.player.data = game.get('player', '')
    form.doubles.data = game.get('doubles')

    if request.method == 'POST' and form.validate():

      # do the api call
      try:


        updated_game = {
          'isCaptain': request.form.get('isCaptain', False) == 'y',
          'loserScore': int(request.form['loserScore']),
          'totalInnings': int(request.form['totalInnings']),
          'error': int(request.form['error']),
          'pitchingStrikeouts': int(request.form['pitchingStrikeouts']),
          'blownSaves': int(request.form['blownSaves']),
          'inningsPitched': int(request.form['inningsPitched']),
          'loss': int(request.form['loss']),
          'winnerScore': int(request.form['winnerScore']),
          'selectedOpponent': str(request.form['selectedOpponent']),
          'saves': int(request.form['saves']),
          'baseOnBalls': int(request.form['baseOnBalls']),
          'hitByPitch': int(request.form['hitByPitch']),
          'outs': int(request.form['outs']),
          'singles': int(request.form['singles']),
          'win': int(request.form['win']),
          'isGameWon': request.form.get('isGameWon', False) == 'y',
          'runsBattedIn': int(request.form['runsBattedIn']),
          'earnedRuns': int(request.form['earnedRuns']),
          'strikeouts': int(request.form['strikeouts']),
          'stolenBases': int(request.form['stolenBases']),
          'homeRuns': int(request.form['homeRuns']),
          'pitchingBaseOnBalls': int(request.form['pitchingBaseOnBalls']),
          'caughtStealing': int(request.form['caughtStealing']),
          'triples': int(request.form['triples']),
          'runs': int(request.form['runs']),
          'player': str(request.form['player']),
          'doubles': int(request.form['doubles']),
        }

        first_name = str(request.form['player']).split(' ')[0]
        last_name = str(request.form['player']).split(' ')[1]

        op_first = str(request.form['selectedOpponent']).split(' ')[0]
        op_second = str(request.form['selectedOpponent']).split(' ')[1]

        player = Player.query.filter(Player.first_name == first_name, Player.last_name == last_name).one()
        opponent = Player.query.filter(Player.first_name == op_first, Player.last_name == op_second).one()

        game = Game(
          player_id = player.id,

          singles=int(request.form['singles']),
          doubles = int(request.form['doubles']),
          triples = int(request.form['triples']),
          home_runs = int(request.form['homeRuns']),
          strikeouts = int(request.form['strikeouts']),
          outs = int(request.form['outs']),
          base_on_balls = int(request.form['baseOnBalls']),
          hit_by_pitch = int(request.form['hitByPitch']),
          runs_batted_in =int(request.form['runsBattedIn']),
          error = int(request.form['error']),
          stolen_bases = int(request.form['stolenBases']),
          caught_stealing = int(request.form['caughtStealing']),

          innings_pitched = int(request.form['inningsPitched']),
          earned_runs = int(request.form['earnedRuns']),
          runs = int(request.form['runs']),
          pitching_strikeouts = int(request.form['pitchingStrikeouts']),
          pitching_base_on_balls = int(request.form['pitchingBaseOnBalls']),
          saves = int(request.form['saves']),
          blown_saves = int(request.form['blownSaves']),
          win = int(request.form['win']),
          loss = int(request.form['loss']),

          opponent_id = opponent.id,
          total_innings = int(request.form['totalInnings']),

          player = player,
          opponent = opponent
        )

        sql_db.session.add(game)
        sql_db.session.commit()

        # db.collection(u'games').document(u'{}'.format(game_id)).update(updated_game)
      except Exception as e:
        print(e)
        flash('Game update failed, try again', 'error')
        return redirect(url_for('index'))


      flash('Game updated', 'success')
      return redirect(url_for('index'))

    return render_template('game.html', game=game, form=form)
  else: 
    return "no game data"


@app.route('/api')
def status():
  return jsonify({'status': 'Up and running'})

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

@app.route('/sql_test')
def sql_test():
  players = Player.query.filter(Player.last_name == 'Brown').all()
  for player in players:
    print('{} {} {}'.format(player.id, player.first_name, player.admin))
  return "hello"
