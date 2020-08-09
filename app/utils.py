from flask import request
from functools import wraps
from app.models import Player


def authorize(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
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

    return f(decoded_token, *args, **kwargs)            
  return decorated_function