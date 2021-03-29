from flask import render_template, request, jsonify
from sqlalchemy import case, and_

from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func

import operator

import app.stats_helpers as sh
from app import db, compiler
from app.api import api
from app.models import Player, Game, Team
from app.utils import authorize, authorize_id


# Check the app status
@api.route('/status')
def status():
    return jsonify({'status': 'Up and running'})


# Update the stat sheet
@api.route('/update_sheet')
@authorize_id
def update_sheet(uid):
    admin_user = Player.query.filter(Player.admin == True, Player.id == uid).first()

    if not admin_user:
        return jsonify({'success': False})

    compiler.clear_all_sheets()

    return jsonify(compiler.update_all_sheets())


@api.route('/teams')
def teams():
    teams = db.session.query(Team).all()

    teams_data = []
    for team in teams:
        teams_data.append({
            'id': team.id,
            'abbreviation': team.abbreviation,
            'name': team.name
        })

    return jsonify(teams_data)


# Query a list of opponent teams
@api.route('/opponents')
@authorize_id
def opponents(team_id):
    teams = Team.query.filter(Team.id != team_id).all()
    all_teams = [{'id': team.id, 'name': team.abbreviation} for team in teams]

    return jsonify(all_teams)


# Query the current standings
@api.route('/standings')
@authorize
def standings():
    teams = Team.query.all()
    standings = [{'id': team.id, 'name': team.name, 'wins': team.wins, 'losses': team.losses} for team in teams]

    standings.sort(key=lambda team: team['wins'], reverse=True)

    return jsonify(standings)


# Query batting average analytics data
@api.route('/analytics/batting_average')
@authorize_id
def batting_average(uid):
    results = {}

    def get_average(stats):
        singles, doubles, triples, home_runs, outs, strikeouts = stats
        hits = sh.calc_hits(singles, doubles, triples, home_runs)
        at_bats = sh.calc_at_bats(hits, outs, strikeouts)
        
        # safeguard in case anything odd is happening
        if at_bats == 0:
            return 0
        
        return sh.calc_avg(hits, at_bats)

    base_query = db.session.query(func.coalesce(func.sum(Game.singles), 0), 
                              func.coalesce(func.sum(Game.doubles), 0), 
                              func.coalesce(func.sum(Game.triples), 0), 
                              func.coalesce(func.sum(Game.home_runs), 0),
                              func.coalesce(func.sum(Game.outs), 0),
                              func.coalesce(func.sum(Game.strikeouts), 0)) \
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
@api.route('/analytics/earned_run_average')
@authorize_id
def earned_run_average(uid):
    results = {}

    def get_earned_run_average(stats):
        earned_runs, outs_pitched = stats
        innings_pitched = sh.calc_innings_pitched(int(outs_pitched))
        
        # safeguard in case anything odd is happening
        if innings_pitched == 0:
            return 0
        
        return sh.calc_era(int(earned_runs), innings_pitched)

    base_query = db.session.query(func.coalesce(func.sum(Game.earned_runs), 0), 
                              func.coalesce(func.sum(Game.innings_pitched), 0)) \
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
@authorize
def leaderboard(stat):
    singular_stats = {
        'home_runs': Game.home_runs, 
        'stolen_bases': Game.stolen_bases, 
        'error': Game.error,
        'runs_batted_in': Game.runs_batted_in,
        'wins': Game.win,
        'pitching_strikeouts': Game.pitching_strikeouts
    }

    calculated_stats = {
        'batting_avg': 'test',
        'earned_run_average': 'test'
    }

    if not singular_stats.get(stat):
        return jsonify({'success': False, 'completed': False})

    leaderboard = db.session.query(Player.first_name, 
                              Player.last_name,
                              func.sum(singular_stats.get(stat))) \
                  .join(PlayerGame, Player.id == PlayerGame.player_id) \
                  .group_by(Player.id).all()

    results = []
    for first_name, last_name, stat in leaderboard:
        results.append({
            'first_name': first_name,
            'last_name': last_name,
            'data': int(stat)
        })

    return jsonify(results)


# Add a game to the database
@api.route('/add_player_game', methods=['POST'])
@authorize
def add_game():
    try:
        data = request.get_json()

        data['player'] = Player.query.get(data.get('player_id'))
        data['opponent'] = Player.query.get(data.get('opponent_id'))

        game = Game(**data)

        db.session.add(game)
        db.session.commit()

        # create the player game and game at the same time
        # push game first, then push player game so they can reference each other

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Something went wrong. Try submitting again.'})


@api.route('/add_game', methods=['POST'])
@authorize
def add_game():
    try:
        data = request.get_json()

        data['player_games'] = None
        data['team_winner']  = None
        data['team_loser']   = None

        game = Game(**data)

        db.session.add(game)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Something went wrong. Try submitting again.'})


# Toggle email subscription
@api.route('/toggle_email')
@authorize_id
def toggle_email(uid):
    try:
        player = Player.query.get(uid)

        player.subscribed = not player.subscribed
        db.session.commit()

        return jsonify({'success': True, 'data': player.subscribed})
    except Exception as e:
        return jsonify({'success': False})
