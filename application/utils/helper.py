import uuid
import flask
import string
import random
from functools import wraps, partial
from flask import request, jsonify, g 
from index import session
from index import app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature
from index import session

TWO_HOURS = 60*60*2
ONE_DAY = TWO_HOURS * 12
ONE_WEEK = ONE_DAY * 7
logger = app.logger

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
      logger.error('Parameters not compatible')
      return jsonify(success=False,
        message='Parameters not compatible'), 400
    for item in filter:
      if item not in incoming.keys():
        logger.error('Parameters not compatible')
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

    logger.error('Token is required to access this resource token is {}'.format(token))
    return jsonify(message="Token is required to access this resource"), 401
  return decorated

def requires_auth(f=None):
  if not f:
    return partial(requires_auth, role=role)
  @wraps(f)
  def decorated(*args, **kwargs):
    incoming = request.get_json()
    third_session = incoming['third_session']
    user = verify_token(third_session)
    if user and session[str(user['id'])]==third_session:
      g.current_user = user
      return f(*args, **kwargs)

    logger.error('Authorization is required to access this resource third_session is {}'.format(third_session))
    return jsonify(message="Authorization is required to access this resource"), 401
  return decorated

def generate_token(user, session_key, expiration=ONE_WEEK):
  s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
  token = s.dumps({
    'id': user.id,
    'phone': user.phone,
    'nick_name': user.nick_name,
    'session_key': session_key
  }).decode('utf-8')
  return token

def verify_token(token):
  s = Serializer(app.config['SECRET_KEY'])
  try:
    data = s.loads(token)
  except (BadSignature, SignatureExpired):
    return None
  return data

def id_generator(size=6, chars=string.digits):
  return ''.join(random.choice(chars) for x in range(size))