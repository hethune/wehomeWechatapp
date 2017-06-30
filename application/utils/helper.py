import uuid
import flask
from functools import wraps, partial
from flask import request, jsonify
from index import app

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

def requires_auth(f=None):
  if not f:
    return partial(requires_auth, role=role)
  @wraps(f)
  def decorated(*args, **kwargs):
    incoming = request.get_json()
    token = incoming['token']
    if token == app.config['WECHAT_TOKEN']:
      return f(*args, **kwargs)
    return jsonify(message="Authentication is required to access this resource"), 401
  return decorated