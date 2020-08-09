from flask import render_template, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.auth import auth
from app.models import Player, TokenDenylist
from app.utils import authorize


# Register a new user
@auth.route('/signup', methods=['POST'])
def sign_up():
  data = request.get_json()

  player = Player.query.filter(Player.email == data.get('email')).first()

  if player:
    return jsonify({'success': False, 'message': 'An account with that email already exists'})

  try:
    new_player = Player(email=data.get('email'), 
                        first_name=data.get('first_name'), 
                        last_name=data.get('last_name'), 
                        division=data.get('division'),
                        password=generate_password_hash(data.get('password'), method='sha256'))

    db.session.add(new_player)
    db.session.commit()
    auth_token = new_player.encode_auth_token(new_player.id)

    return jsonify({'success': True, 'token': auth_token.decode()})
  except Exception as e:
    return jsonify({'success': False, 'message': 'An error occurred. Please try again.'})


# Login a user
@auth.route('/login', methods=['POST'])
def login():
  data = request.get_json()

  try: 
    player = Player.query.filter(Player.email == data.get('email')).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not player or not check_password_hash(player.password, data.get('password')): 
        return jsonify({'success': False, 'message': 'Email/password is not correct'})

    auth_token = player.encode_auth_token(player.id)

    return jsonify({'success': True, 'token': auth_token.decode()})
  except Exception as e:
    return jsonify({'success': False, 'message': 'An error occurred. Please try again.'})


# Query information about the logged in player
@auth.route('/user_status')
@authorize
def user_status(decoded_token):
  player = Player.query.filter(Player.id == decoded_token).first()

  return jsonify({
    'success': True,
    'data': {
      'player_id': player.id,
      'first_name': player.first_name,
      'last_name': player.last_name,
      'email': player.email,
      'admin': player.admin,
      'subscribed': player.subscribed,
      'division': player.division
    }
  })


# Logout a user and deny the token from being used again
@auth.route('/logout', methods=['GET', 'POST'])
@authorize
def logout(token):
  denylist_token = TokenDenylist(token=token)
  try:
    db.session.add(denylist_token)
    db.session.commit()

    return jsonify({'success': True})
  except Exception as e:
    return jsonify({'success': False, 'message': e})