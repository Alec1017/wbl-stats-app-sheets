from flask import render_template, request, jsonify
from sqlalchemy import case, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func
import operator

from app import db
from app.api import api
from app.models import Player, Game
from app.stats_helpers import calcHits, calcAtBats, calcAVG, calcERA, calcInningsPitched
from app.stats_compiler import clear_all_sheets, update_all_sheets


# Check the app status
@api.route('/status')
def status():
  return jsonify({'status': 'Up and running'})


# Update the stat sheet
@api.route('/update_sheet/<uid>')
def update_sheet(uid):
  admin_user = Player.query.filter(Player.admin == True, Player.id == uid).first()

  if not admin_user:
    return jsonify({'success': False})

  clear_all_sheets()

  return jsonify(update_all_sheets())


# Query the current standings
@api.route('/standings')
def standings():
  standings_dict = {}

  wins_case = case(
    [(and_(Game.game_won == True, Game.captain == True), 1)],
    else_=0
  )

  losses_case = case(
    [(and_(Game.game_won == False, Game.captain == True), 1)],
    else_=0
  )

  standings = db.session.query(Player.division, 
                               Player.first_name, 
                               Player.last_name, 
                               func.sum(wins_case).label('wins'), 
                               func.sum(losses_case).label('losses')) \
                .join(Game, Player.id == Game.player_id) \
                .group_by(Player.id).all()

  for division, first_name, last_name, wins, losses in standings:
    full_name = '{} {}'.format(first_name, last_name)

    if standings_dict.get(division):
      standings_dict[division].append([full_name, int(wins), int(losses)])
    else:
      standings_dict[division] = [[full_name, int(wins), int(losses)]]

  return jsonify(standings_dict)


# Query a list of opponents names
@api.route('/opponents/<uid>')
def opponents(uid):
  opponents = db.session.query(Player.first_name, Player.last_name).filter(Player.id != uid).all()
  full_name_opponents = ['{} {}'.format(first_name, last_name) for first_name, last_name in opponents]

  return jsonify(full_name_opponents)


# Query batting average analytics data
@api.route('/analytics/batting_average/<uid>')
def batting_average(uid):
  results = {}

  def get_average(stats):
    singles, doubles, triples, home_runs, outs, strikeouts = stats
    hits = calcHits(singles, doubles, triples, home_runs)
    at_bats = calcAtBats(hits, outs, strikeouts)
    
    # safeguard in case anything odd is happening
    if at_bats == 0:
      return 0
    
    return calcAVG(hits, at_bats)

  base_query = db.session.query(func.sum(Game.singles), 
                            func.sum(Game.doubles), 
                            func.sum(Game.triples), 
                            func.sum(Game.home_runs),
                            func.sum(Game.outs),
                            func.sum(Game.strikeouts)) \
                  .join(Player, Player.id == Game.player_id)

  player_stats = base_query.filter(Player.id == uid).first()
  league_stats = base_query.first()

  results['player_avg'] = get_average(player_stats)
  results['league_avg'] = get_average(league_stats)


  most_recent_games = db.session.query(Game.singles, Game.doubles, Game.triples, 
                                       Game.home_runs, Game.outs, Game.strikeouts) \
                        .join(Player, Player.id == Game.player_id) \
                        .filter(Player.id == uid) \
                        .order_by(Game.created_at).limit(10).all()

  rolling_averages = []
  cumulative_games = None
  for game in most_recent_games:
    if cumulative_games:
      cumulative_games = tuple(map(operator.add, cumulative_games, game))
    else:
      cumulative_games = game

    avg = get_average(cumulative_games)
    rolling_averages.append(avg)

  results['rolling_batting_averages'] = rolling_averages

  return jsonify(results)


# Query ERA analytics data
@api.route('/analytics/earned_run_average/<uid>')
def earned_run_average(uid):
  results = {}

  def get_earned_run_average(stats):
    earned_runs, outs_pitched = stats
    innings_pitched = calcInningsPitched(int(outs_pitched))
    
    # safeguard in case anything odd is happening
    if innings_pitched == 0:
      return 0
    
    return calcERA(int(earned_runs), innings_pitched)

  base_query = db.session.query(func.sum(Game.earned_runs), 
                            func.sum(Game.innings_pitched)) \
                  .join(Player, Player.id == Game.player_id)

  player_stats = base_query.filter(Player.id == uid).first()
  league_stats = base_query.first()

  results['player_avg'] = get_earned_run_average(player_stats)
  results['league_avg'] = get_earned_run_average(league_stats)


  most_recent_games = db.session.query(Game.earned_runs, Game.innings_pitched) \
                        .join(Player, Player.id == Game.player_id) \
                        .filter(Player.id == uid) \
                        .order_by(Game.created_at).limit(10).all()

  rolling_averages = []
  cumulative_games = None
  for game in most_recent_games:
    if cumulative_games:
      cumulative_games = tuple(map(operator.add, cumulative_games, game))
    else:
      cumulative_games = game

    avg = get_earned_run_average(cumulative_games)
    rolling_averages.append(avg)

  results['rolling_earned_run_averages'] = rolling_averages

  return jsonify(results)


# Query leaderboards
@api.route('/analytics/leaderboard/<stat>')
def leaderboard(stat):
  valid_stats = {
    'home_runs': Game.home_runs, 
    'stolen_bases': Game.stolen_bases, 
    'error': Game.error
  }

  if not valid_stats.get(stat):
    return jsonify({'success': False, 'completed': False})

  leaderboard = db.session.query(Player.first_name, 
                             Player.last_name,
                             func.sum(valid_stats.get(stat))) \
                .join(Game, Player.id == Game.player_id) \
                .group_by(Player.id).all()

  results = []
  for first_name, last_name, stat in leaderboard:
    results.append({
      'first_name': first_name,
      'last_name': last_name,
      'data': int(stat)
    })

  return jsonify(results)