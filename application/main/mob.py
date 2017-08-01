from flask import request, jsonify, g
from flask import Blueprint
from index import app, db
from ..models import User
from sqlalchemy.exc import IntegrityError
from ..utils.query import QueryHelper
from ..utils.helper import uuid_gen, json_validate, requires_token, generate_token, verify_token, requires_auth, id_generator

mob = Blueprint('mob', __name__)
logger = app.logger

@mob.route('/register', methods=['POST'])
@json_validate(filter=['token', 'userName', 'gender', 'country', 'phone', 'password', 'code'])
@requires_token
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
    logger.warning("Failed User Creation: phone {}, {}".format(incoming["phone"], e))
    return jsonify(message="User with that phone already exists"), 409

  return jsonify(
    third_session=generate_token(user=user, session_key=None),
    success=True
  )

@mob.route('/login', methods=['POST'])
@json_validate(filter=['token', 'phone', 'password', 'country'])
@requires_token
def login():
  incoming = request.get_json()
  user = QueryHelper.get_user_with_phone_and_country_and_password(phone=incoming['phone'],
    country=incoming['country'], password=incoming['password'])
  if user:
    return jsonify(
      third_session=generate_token(user=user, session_key=None),
      success=True
    )
  return jsonify(success=True, message='login failed'), 403

@mob.route('/get_hot_cities', methods=['POST'])
@uuid_gen
@json_validate(filter=['token'])
@requires_token
def get_hot_cities():
  columns = ['city_id', 'city_name', 'pic_url', 'increase_radio', 'rental_income_radio']
  d = {}
  l = []
  try:
    cities = QueryHelper.get_cities_filter_id(min_id=1, max_id=10)
    for city in cities:
      l.append({
        'city_id': city.id,
        'city_name': city.city_name,
        'pic_url': QueryHelper.pares_qiniu_pic(city.citypage.pic_url) if city.citypage else None,
        'increase_radio': city.citypage.increase_radio  if city.citypage else None,
        'rental_income_radio': city.citypage.rental_income_radio if city.citypage else None,
        })
      d['hot_cities'] = l
  except Exception as e:
    logger.error("Failed to get hot city list {}".format(e))
    return jsonify(success=False,
      message='Failed to get hot city list')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)