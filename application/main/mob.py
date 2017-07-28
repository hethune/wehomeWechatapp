from flask import request, jsonify, g
from flask import Blueprint
from index import app, db
from ..models import User
from ..utils.query import QueryHelper
from ..utils.helper import uuid_gen, json_validate, requires_token, generate_token, verify_token, requires_auth, id_generator

mob = Blueprint('mob', __name__)
logger = app.logger

@mob.route('/register', methods=['POST'])
@json_validate(filter=['token', 'userName', 'gender', 'country', 'phone', 'password', 'code'])
def register():
  incoming = request.get_json()
  user = User(openid=None, nick_name=incoming["userName"], gender=incoming['gender'], language=None, city=None, country=incoming["country"],
    province=None, avatar_url=None, phone=incoming["phone"], type=1, password=incoming["password"]
  )

  # Verify phone number
  if not QueryHelper.verify_sms_code(phone=incoming['phone'], country=incoming['country'], code=incoming['code']):
    logger.warning("Failed SMS Verification: {} entered a invalid code {}".format(incoming["phone"], incoming["country"], incoming["code"]))
    return jsonify(message="Phone has not been verified", success=False), 409

  db.session.add(user)

  try:
    db.session.commit()
  except IntegrityError as e:
    logger.warning("Failed User Creation: phone {}, email {}, {}".format(incoming["phone"], incoming["email"], e))
    return jsonify(message="User with that email or phone already exists"), 409

  return jsonify(
    third_session=generate_token(user=user, session_key=None),
    success=True
  )