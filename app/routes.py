from flask import jsonify

from app import app
from app.stats_builder import StatsBuilder


stats_builder = StatsBuilder()

@app.route('/api')
def status():
  return jsonify('status': 'Up and running')

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
    return jsonify({'success': False})
