from flask import render_template, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, emailer
from app.auth import auth
from app.models import Player
from app.utils import authorize_id


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
@authorize_id
def user_status(uid):
  player = Player.query.filter(Player.id == uid).first()

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


# Request a password reset link
@auth.route('/password_reset_request', methods=['POST'])
def password_reset_request():
  data = request.get_json()

  try: 
    player = Player.query.filter(Player.email == data.get('email')).first()

    # check if user actually exists
    # If not, don't reveal that an email wasn't sent
    if not player: 
        return jsonify({'success': True})

    # Generate token that is valid for 10 minutes
    auth_token = player.encode_auth_token(player.id, expiration=600)

    # Send password reset email
    emailer.send_password_reset_email(player.first_name, 'WBL Password Reset', player.email, auth_token.decode())

    return jsonify({'success': True})
  except Exception as e:
    return jsonify({'success': False})
