from flask import request, abort
from functools import wraps
from app.models import Player


def get_token():
  auth_token = None
  auth_header = request.headers.get('Authorization')

  if not auth_header:
    abort(401)

  try:
    auth_token = auth_header.split(' ')[1]
  except IndexError:
    abort(401)

  decoded_token = Player.decode_auth_token(auth_token)

  # Make sure we get an ID and not an error message
  if isinstance(decoded_token, str):
    abort(401)

  return decoded_token


# Authorize and dont return the user id
def authorize(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    decoded_token = get_token()

    return f(*args, **kwargs)   
  return decorated_function


# Authorize and return the user id
def authorize_id(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    decoded_token = get_token()

    return f(decoded_token, *args, **kwargs)   
  return decorated_function
