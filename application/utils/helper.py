import uuid
import flask
from functools import wraps, partial
from flask import request, jsonify, g, session
from index import app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature

TWO_HOURS = 60*60*2

def uuid_gen(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    flask.g.uuid = str(uuid.uuid4()).split("-")[0]
    return f(*args, **kwargs)
  return decorated

def json_validate(f=None, filter=[]):
  if not f:
    return partial(json_validate, filter=filter)
  @wraps(f)
  def decorated(*args, **kwargs):
    incoming = request.get_json()
    if incoming is None:
      return jsonify(success=False,
        message='Parameters not compatible'), 400
    for item in filter:
      if item not in incoming.keys():
        return jsonify(success=False,
        message='Parameters not compatible'), 400
    return f(*args, **kwargs)
  return decorated

def requires_token(f=None):
  if not f:
    return partial(requires_auth, role=role)
  @wraps(f)
  def decorated(*args, **kwargs):
    incoming = request.get_json()
    token = incoming['token']
    if token == app.config['WECHAT_TOKEN']:
      return f(*args, **kwargs)
    return jsonify(message="Token is required to access this resource"), 401
  return decorated

def requires_auth(f=None):
  if not f:
    return partial(requires_auth, role=role)
  @wraps(f)
  def decorated(*args, **kwargs):
    incoming = request.get_json()
    third_session = incoming['thirdsession']
    user = verify_token(third_session)
    if user and session[str(user['id'])]==third_session:
      g.current_user = user
      return f(*args, **kwargs)
    return jsonify(message="Authorization is required to access this resource"), 401
  return decorated

def generate_token(user, expiration=TWO_HOURS):
  s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
  token = s.dumps({
    'id': user.id,
    'phone': user.phone,
    'nick_name': user.nick_name,
  }).decode('utf-8')
  return token

def verify_token(token):
  s = Serializer(app.config['SECRET_KEY'])
  try:
    data = s.loads(token)
  except (BadSignature, SignatureExpired):
    return None
  return data